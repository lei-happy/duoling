"""合作伙伴 · 承运商主体（租户库，事务回滚不落库）集成测试

覆盖 CarrierService 核心链路：新增、查询、编码唯一、联系电话唯一、更新。

对应需求：doc/02.需求文档/02.企业端/09.合作伙伴/承运商管理.md
对应接口：/api/client/partner/carrier
对应代码：backend/app/modules/client/services/partner/carrier_service.py
覆盖用例：TC-CLI-CARRIER-001 ~ TC-CLI-CARRIER-010
"""

from __future__ import annotations

import random
import uuid

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.partner.carrier import CarrierCreate, CarrierUpdate
from app.modules.client.services.partner.carrier_service import CarrierService


def _rand_phone():
    return "13" + "".join(random.choice("0123456789") for _ in range(9))


def _name():
    return f"测试承运商_{uuid.uuid4().hex[:8]}"


class TestCarrierCrud:
    async def test_create_and_get(self, tenant_session):
        phone = _rand_phone()
        c = await CarrierService.create(
            tenant_session,
            CarrierCreate(carrierName=_name(), contactPhone=phone, carrierType=0),
        )
        assert c.id is not None
        assert c.status == 1
        assert c.invite_status == 0

        got = await CarrierService.get_or_404(tenant_session, c.id)
        assert got.contact_phone == phone

    async def test_duplicate_phone_rejected(self, tenant_session):
        phone = _rand_phone()
        await CarrierService.create(
            tenant_session, CarrierCreate(carrierName=_name(), contactPhone=phone)
        )
        with pytest.raises(BizException):
            await CarrierService.create(
                tenant_session, CarrierCreate(carrierName=_name(), contactPhone=phone)
            )

    async def test_duplicate_code_rejected(self, tenant_session):
        code = f"CAR{uuid.uuid4().hex[:6].upper()}"
        await CarrierService.create(
            tenant_session,
            CarrierCreate(carrierName=_name(), contactPhone=_rand_phone(),
                         carrierCode=code),
        )
        with pytest.raises(BizException):
            await CarrierService.create(
                tenant_session,
                CarrierCreate(carrierName=_name(), contactPhone=_rand_phone(),
                             carrierCode=code),
            )

    async def test_update_carrier(self, tenant_session):
        c = await CarrierService.create(
            tenant_session, CarrierCreate(carrierName=_name(), contactPhone=_rand_phone())
        )
        updated = await CarrierService.update(
            tenant_session, c.id, CarrierUpdate(shortName="简称A", status=0)
        )
        assert updated.short_name == "简称A"
        assert updated.status == 0

    async def test_get_nonexistent_raises(self, tenant_session):
        with pytest.raises(BizException):
            await CarrierService.get_or_404(tenant_session, 987_654_321)
