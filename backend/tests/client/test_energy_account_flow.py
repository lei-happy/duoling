"""能源中心 · 资金闭环（租户库，事务回滚不落库）

覆盖：开账户 → 发卡绑定 → 充值入账 → 调账 → 撤销充值 → 有余额不能删。

对应需求：doc/02.需求文档/02.企业端/15.能源中心/01.产品方案与功能设计.md
对应接口：/api/client/energy/accounts|cards|recharges
覆盖用例：TC-CLI-ENERGY-021 ~ TC-CLI-ENERGY-040
"""

from __future__ import annotations

import random
import uuid
from decimal import Decimal

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.capacity.self_capacity.vehicle import VehicleCreate
from app.modules.client.schemas.energy.account import (
    EnergyAccountCreate,
    EnergyAccountOut,
    EnergyAdjustIn,
)
from app.modules.client.schemas.energy.card import EnergyCardBindIn, EnergyCardCreate, EnergyCardOut
from app.modules.client.schemas.energy.recharge import (
    EnergyRechargeCreate,
    EnergyRechargeOut,
    EnergyRechargePayIn,
)
from app.modules.client.schemas.energy.supplier import EnergySupplierCreate
from app.modules.client.services.capacity.self_capacity.vehicle_service import VehicleService
from app.modules.client.services.energy.account_service import EnergyAccountService
from app.modules.client.services.energy.card_service import EnergyCardService
from app.modules.client.services.energy.constants import DOC_CANCELLED, DOC_DRAFT, DOC_PAID
from app.modules.client.services.energy.recharge_service import EnergyRechargeService
from app.modules.client.services.energy.supplier_service import EnergySupplierService


def _name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _plate() -> str:
    prov = random.choice("京沪粤浙苏鲁")
    letter = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
    tail = "".join(random.choice("0123456789") for _ in range(5))
    return f"{prov}{letter}{tail}"


async def _open_account(db, *, account_type: str = "PREPAID"):
    sup = await EnergySupplierService.create(
        db, EnergySupplierCreate(supplierName=_name("资金供应商")),
    )
    acc = await EnergyAccountService.create(
        db,
        EnergyAccountCreate(
            accountName=_name("预付账户"),
            supplierId=sup.id,
            energyType="OIL",
            accountType=account_type,
        ),
    )
    return sup, acc


class TestAccountCreateSerialize:
    async def test_create_then_serialize_out(self, tenant_session):
        _, acc = await _open_account(tenant_session)
        assert acc.account_code.startswith("EA")
        out = EnergyAccountOut.from_model(acc).model_dump()
        assert out["createdAt"] is not None
        assert out["ledgerBalance"] == Decimal("0")
        assert out["availableBalance"] == Decimal("0")


class TestAccountAndCard:
    async def test_duplicate_account_code_rejected(self, tenant_session):
        sup, acc = await _open_account(tenant_session)
        with pytest.raises(BizException, match="账户编码已存在"):
            await EnergyAccountService.create(
                tenant_session,
                EnergyAccountCreate(
                    accountCode=acc.account_code,
                    accountName=_name("另一账户"),
                    supplierId=sup.id,
                    energyType="OIL",
                ),
            )

    async def test_card_create_bind_unbind(self, tenant_session):
        _, acc = await _open_account(tenant_session)
        card = await EnergyCardService.create(
            tenant_session,
            EnergyCardCreate(accountId=acc.id, cardNo=f"CARD{uuid.uuid4().hex[:8]}"),
        )
        out = EnergyCardOut.from_model(card).model_dump()
        assert out["createdAt"] is not None
        assert out["cardNo"] == card.card_no

        vehicle = await VehicleService.create_vehicle(
            tenant_session,
            VehicleCreate(plateNumber=_plate(), plateCategory="BLUE"),
        )
        binding = await EnergyCardService.bind(
            tenant_session, card.id, EnergyCardBindIn(vehicleId=vehicle.id),
        )
        assert binding.vehicle_id == vehicle.id
        assert binding.end_time is None

        await EnergyCardService.unbind(tenant_session, card.id)
        current = await EnergyCardService._current_bindings(tenant_session, [card.id])
        assert card.id not in current

    async def test_card_duplicate_and_empty_rejected(self, tenant_session):
        _, acc = await _open_account(tenant_session)
        no = f"CARD{uuid.uuid4().hex[:8]}"
        await EnergyCardService.create(
            tenant_session, EnergyCardCreate(accountId=acc.id, cardNo=no),
        )
        with pytest.raises(BizException, match="卡号已存在"):
            await EnergyCardService.create(
                tenant_session, EnergyCardCreate(accountId=acc.id, cardNo=no),
            )
        with pytest.raises(BizException, match="请填写卡号"):
            await EnergyCardService.create(
                tenant_session, EnergyCardCreate(accountId=acc.id, cardNo="  "),
            )
        card = await EnergyCardService.create(
            tenant_session,
            EnergyCardCreate(accountId=acc.id, cardNo=f"CARD{uuid.uuid4().hex[:8]}"),
        )
        with pytest.raises(BizException, match="至少选择"):
            await EnergyCardService.bind(
                tenant_session, card.id, EnergyCardBindIn(),
            )


class TestRechargeAndAdjust:
    async def test_pay_increases_ledger(self, tenant_session):
        _, acc = await _open_account(tenant_session)
        doc = await EnergyRechargeService.create(
            tenant_session,
            EnergyRechargeCreate(accountId=acc.id, plannedAmount=Decimal("1000")),
        )
        out = EnergyRechargeOut.from_model(doc).model_dump()
        assert out["createdAt"] is not None
        assert doc.status == DOC_DRAFT

        paid = await EnergyRechargeService.register_pay(
            tenant_session, doc.id, EnergyRechargePayIn(),
        )
        assert paid.status == DOC_PAID
        assert paid.actual_amount == Decimal("1000")
        assert paid.ledger_txn_id is not None

        got = await EnergyAccountService.get(tenant_session, acc.id)
        assert got.ledger_balance == Decimal("1000")

        txns = await EnergyAccountService.page_txns(tenant_session, acc.id)
        assert txns["count"] >= 1

    async def test_adjust_and_delete_guard(self, tenant_session):
        _, acc = await _open_account(tenant_session)
        await EnergyAccountService.adjust(
            tenant_session,
            acc.id,
            EnergyAdjustIn(amount=Decimal("200"), remark="期初余额调入测试"),
        )
        got = await EnergyAccountService.get(tenant_session, acc.id)
        assert got.ledger_balance == Decimal("200")

        with pytest.raises(BizException, match="仍有余额"):
            await EnergyAccountService.delete(tenant_session, acc.id)

        await EnergyAccountService.adjust(
            tenant_session,
            acc.id,
            EnergyAdjustIn(amount=Decimal("-200"), remark="结清账户余额测试"),
        )
        await EnergyAccountService.delete(tenant_session, acc.id)
        with pytest.raises(BizException, match="不存在"):
            await EnergyAccountService.get(tenant_session, acc.id)

    async def test_cancel_paid_reverses_ledger(self, tenant_session):
        _, acc = await _open_account(tenant_session)
        doc = await EnergyRechargeService.create(
            tenant_session,
            EnergyRechargeCreate(accountId=acc.id, plannedAmount=Decimal("300")),
        )
        await EnergyRechargeService.register_pay(
            tenant_session, doc.id, EnergyRechargePayIn(),
        )
        cancelled = await EnergyRechargeService.cancel(
            tenant_session, doc.id, "测试撤销已入账充值",
        )
        assert cancelled.status == DOC_CANCELLED
        got = await EnergyAccountService.get(tenant_session, acc.id)
        assert got.ledger_balance == Decimal("0")

    async def test_cancel_reason_too_short(self, tenant_session):
        _, acc = await _open_account(tenant_session)
        doc = await EnergyRechargeService.create(
            tenant_session,
            EnergyRechargeCreate(accountId=acc.id, plannedAmount=Decimal("10")),
        )
        with pytest.raises(BizException, match="5 个字"):
            await EnergyRechargeService.cancel(tenant_session, doc.id, "短")
