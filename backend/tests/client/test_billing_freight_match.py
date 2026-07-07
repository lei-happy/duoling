"""计费引擎 · 运价合同命中（租户库，事务回滚不落库）集成测试

在真实 biz_region / 合同 / 费率数据上验证 FreightCalcService 编排层能命中规则。

对应需求：项目文档/02.需求文档/02.企业端/05.计费引擎模块/**
对应代码：backend/app/modules/client/services/billing/freight_calc_service.py
覆盖用例：TC-CLI-BILLING-101
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.schemas.billing.freight_contract import FreightContractCreate
from app.modules.client.schemas.billing.freight_rate import FreightRateCreate
from app.modules.client.schemas.partner.customer import CustomerCreate
from app.modules.client.services.billing.freight_calc_service import FreightCalcService
from app.modules.client.services.billing.freight_contract_service import (
    FreightContractService,
)
from app.modules.client.services.billing.freight_rate_service import FreightRateService
from app.modules.client.services.partner.customer_service import CustomerService
from tests.client.conftest import unique_code, unique_suffix


async def _pick_two_regions(session):
    """选取两条不同区级 region 作为运价起终点。"""
    result = await session.execute(
        select(BizRegion)
        .where(BizRegion.is_deleted == 0, BizRegion.level == 3)
        .order_by(BizRegion.id.asc())
        .limit(2)
    )
    regions = list(result.scalars().all())
    if len(regions) < 2:
        pytest.skip("租户库区级 region 样本不足")
    return regions[0], regions[1]


class TestFreightContractMatch:
    async def test_preview_hits_created_rate(self, tenant_session):
        origin, dest = await _pick_two_regions(tenant_session)
        today = date.today()

        customer = await CustomerService.create_customer(
            tenant_session,
            CustomerCreate(customerName=f"计费客户_{unique_suffix()}"),
        )
        contract = await FreightContractService.create_contract(
            tenant_session,
            FreightContractCreate(
                contractNo=unique_code("HT"),
                contractName="集成测试合同",
                customerId=customer.id,
                customerName=customer.customer_name,
                effectiveDate=today,
                expiryDate=today.replace(year=today.year + 1),
            ),
        )
        await FreightContractService.activate_contract(tenant_session, contract.id)

        await FreightRateService.create_rate(
            tenant_session,
            FreightRateCreate(
                contractId=contract.id,
                customerId=customer.id,
                origin=origin.name,
                originCode=origin.code,
                originRegionId=origin.id,
                destination=dest.name,
                destinationCode=dest.code,
                destinationRegionId=dest.id,
                unitPrice=Decimal("500"),
                billingMode=0,
                effectiveDate=today,
                expiryDate=today.replace(year=today.year + 1),
            ),
        )

        waybill = Waybill(
            waybill_no=f"YDTEST{unique_suffix()}",
            customer_id=customer.id,
            origin=origin.name,
            origin_code=origin.code,
            origin_region_id=origin.id,
            destination=dest.name,
            destination_code=dest.code,
            destination_region_id=dest.id,
            plan_issue_time=datetime.now(),
            status=1,
        )
        cargo = WaybillCargo(
            waybill_id=0,
            quantity=2,
            vehicle_brand="测试品牌",
            vehicle_model="测试车型",
        )
        cargo.id = 1

        summary = await FreightCalcService.preview_for_waybill(
            tenant_session, waybill, [cargo], billing_date=today
        )

        assert summary.calc_status == "success"
        assert summary.total_amount == Decimal("1000")
        assert len(summary.cargo_results) == 1
        cr = summary.cargo_results[0]
        assert cr.calc_status == "success"
        assert cr.matched_contract is not None
        assert cr.matched_contract.id == contract.id
        assert cr.amount == Decimal("1000")
