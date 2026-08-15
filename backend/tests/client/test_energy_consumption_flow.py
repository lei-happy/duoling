"""能源中心 · 消费 / 对账 / 分析冒烟（租户库，事务回滚不落库）

覆盖：手工入账扣余额、垫付不扣账、人工归属、Excel 导入、余额对账、分析概览。

对应需求：doc/02.需求文档/02.企业端/15.能源中心/01.产品方案与功能设计.md
对应接口：/api/client/energy/consumptions|connectors|recons|analysis
覆盖用例：TC-CLI-ENERGY-041 ~ TC-CLI-ENERGY-055
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from io import BytesIO

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.capacity.self_capacity.vehicle import VehicleCreate
from app.modules.client.schemas.energy.account import EnergyAccountCreate, EnergyAdjustIn
from app.modules.client.schemas.energy.consumption import (
    EnergyConsumptionAssignIn,
    EnergyConsumptionCreate,
    EnergyConsumptionOut,
)
from app.modules.client.schemas.energy.supplier import EnergySupplierCreate
from app.modules.client.services.capacity.self_capacity.vehicle_service import VehicleService
from app.modules.client.services.energy.account_service import EnergyAccountService
from app.modules.client.services.energy.analysis_service import EnergyAnalysisService
from app.modules.client.services.energy.connector_service import EnergyConnectorService
from app.modules.client.services.energy.connectors.excel import ExcelConnector
from app.modules.client.services.energy.constants import CHANNEL_DRIVER_ADVANCE
from app.modules.client.services.energy.consumption_service import EnergyConsumptionService
from app.modules.client.services.energy.recon_service import EnergyReconService
from app.modules.client.services.energy.supplier_service import EnergySupplierService


def _name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


async def _funded_account(db, amount: Decimal = Decimal("1000")):
    sup = await EnergySupplierService.create(
        db, EnergySupplierCreate(supplierName=_name("消费供应商")),
    )
    acc = await EnergyAccountService.create(
        db,
        EnergyAccountCreate(
            accountName=_name("消费账户"),
            supplierId=sup.id,
            energyType="OIL",
        ),
    )
    await EnergyAccountService.adjust(
        db, acc.id, EnergyAdjustIn(amount=amount, remark="测试充入可用余额"),
    )
    return sup, acc


class TestManualConsumption:
    async def test_ledger_affecting_deducts(self, tenant_session):
        sup, acc = await _funded_account(tenant_session)
        now = datetime.now()
        obj = await EnergyConsumptionService.create_manual(
            tenant_session,
            EnergyConsumptionCreate(
                accountId=acc.id,
                supplierId=sup.id,
                amount=Decimal("120.5"),
                consumptionTime=now,
                energyType="OIL",
                isLedgerAffecting=1,
            ),
        )
        out = EnergyConsumptionOut.from_model(obj).model_dump()
        assert out["consumptionNo"].startswith("EC")
        assert obj.ledger_txn_id is not None
        assert obj.is_ledger_affecting == 1
        got = await EnergyAccountService.get(tenant_session, acc.id)
        assert got.ledger_balance == Decimal("879.5")

    async def test_driver_advance_skips_ledger(self, tenant_session):
        sup, acc = await _funded_account(tenant_session)
        obj = await EnergyConsumptionService.create_manual(
            tenant_session,
            EnergyConsumptionCreate(
                accountId=acc.id,
                supplierId=sup.id,
                amount=Decimal("80"),
                consumptionTime=datetime.now(),
                sourceChannel=CHANNEL_DRIVER_ADVANCE,
                isLedgerAffecting=1,
            ),
        )
        assert obj.is_ledger_affecting == 0
        assert obj.ledger_txn_id is None
        got = await EnergyAccountService.get(tenant_session, acc.id)
        assert got.ledger_balance == Decimal("1000")

    async def test_prepaid_insufficient_rejected(self, tenant_session):
        sup, acc = await _funded_account(tenant_session, Decimal("10"))
        with pytest.raises(BizException, match="余额不足"):
            await EnergyConsumptionService.create_manual(
                tenant_session,
                EnergyConsumptionCreate(
                    accountId=acc.id,
                    supplierId=sup.id,
                    amount=Decimal("50"),
                    consumptionTime=datetime.now(),
                    isLedgerAffecting=1,
                ),
            )

    async def test_assign_unmatched(self, tenant_session):
        import random

        prov = random.choice("京沪粤浙苏鲁")
        letter = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
        tail = "".join(random.choice("0123456789") for _ in range(5))
        plate = f"{prov}{letter}{tail}"

        sup, acc = await _funded_account(tenant_session)
        obj = await EnergyConsumptionService.create_manual(
            tenant_session,
            EnergyConsumptionCreate(
                supplierId=sup.id,
                amount=Decimal("30"),
                consumptionTime=datetime.now(),
                isLedgerAffecting=0,
            ),
        )
        assert obj.match_status in ("UNMATCHED", "PARTIAL")
        vehicle = await VehicleService.create_vehicle(
            tenant_session,
            VehicleCreate(plateNumber=plate, plateCategory="BLUE"),
        )
        assigned = await EnergyConsumptionService.assign(
            tenant_session,
            obj.id,
            EnergyConsumptionAssignIn(vehicleId=vehicle.id, accountId=acc.id),
        )
        assert assigned.vehicle_id == vehicle.id
        assert assigned.plate_number == plate
        assert assigned.match_status == "MATCHED"


class TestExcelImportAndRecon:
    async def test_parse_and_import(self, tenant_session):
        from openpyxl import Workbook

        sup, acc = await _funded_account(tenant_session)
        conn = await EnergyConnectorService.create(tenant_session, {
            "connectorCode": "excel",
            "connectorName": "测试导入",
            "supplierId": sup.id,
            "accountId": acc.id,
        })
        wb = Workbook()
        ws = wb.active
        ws.append(ExcelConnector.TEMPLATE_HEADERS)
        ws.append([
            f"EXT{uuid.uuid4().hex[:6]}", "C001", "", "东站", "柴油",
            "0#柴油", 20, "L", 7.2, 144, datetime.now(), 100,
        ])
        buf = BytesIO()
        wb.save(buf)
        rows = ExcelConnector.parse_workbook(buf.getvalue())
        assert len(rows) == 1
        assert rows[0]["金额"] == 144

        result = await EnergyConnectorService.run_import(tenant_session, conn.id, rows)
        assert result["imported"] == 1
        assert result["failed"] == 0

        again = await EnergyConnectorService.run_import(tenant_session, conn.id, rows)
        assert again["duplicated"] == 1

    async def test_balance_recon_and_overview(self, tenant_session):
        _, acc = await _funded_account(tenant_session, Decimal("500"))
        recon = await EnergyReconService.create_balance_recon(
            tenant_session, acc.id, Decimal("480"),
        )
        assert recon.internal_amount == Decimal("500")
        assert recon.external_amount == Decimal("480")
        assert recon.difference_amount == Decimal("20")
        assert recon.created_at is not None

        overview = await EnergyAnalysisService.overview(tenant_session)
        for key in (
            "accountCount", "ledgerBalance", "availableBalance",
            "monthRecharge", "monthConsumption", "todayConsumption",
        ):
            assert key in overview
        assert overview["accountCount"] >= 1
        page = await EnergyReconService.page(tenant_session, account_id=acc.id)
        assert page["count"] >= 1
        assert page["list"][0]["createdAt"] is not None
