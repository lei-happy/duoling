"""车辆资产 · 资产成本服务集成测试（租户库，事务回滚）

覆盖：续期生效回写到期日、资产卡片折旧、成本汇总四类勾稽。

对应需求：doc/02.需求文档/02.企业端/14.车辆资产模块/
对应代码：backend/app/modules/client/services/capacity/maintenance/fleet_asset_cost_service.py
"""

from __future__ import annotations

import random
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.modules.client.models.capacity.maintenance.work_order import FleetWorkOrder
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.models.compliance.compliance_alert import BizComplianceAlert
from app.modules.client.schemas.capacity.maintenance import (
    AssetCardUpdate,
    RenewalCreate,
    WorkOrderCompleteBody,
    WorkOrderCreate,
)
from app.modules.client.schemas.capacity.self_capacity.vehicle import VehicleCreate
from app.modules.client.services.capacity.maintenance.fleet_asset_cost_service import (
    FleetAssetCostService,
)
from app.modules.client.services.capacity.maintenance.fleet_maintenance_service import (
    FleetMaintenanceService,
)
from app.modules.client.services.capacity.self_capacity.vehicle_service import (
    VehicleService,
)

pytestmark = pytest.mark.asyncio

_PROVINCES = "京沪粤浙苏鲁川鄂湘皖"


def _ensure_tables_sync() -> None:
    from sqlalchemy import create_engine

    from app.core.config import get_settings
    from app.modules.client.models.base import TenantBase
    from app.modules.client.models.capacity.maintenance.maintain_plan import (
        FleetMaintainPlan,
    )
    from app.modules.client.models.capacity.maintenance.renewal import FleetRenewal
    from app.modules.client.models.capacity.maintenance.work_order import (
        FleetWorkOrder as WO,
    )
    from tests.client.conftest import TENANT_CODE

    settings = get_settings()
    url = settings.tenant_db_url(TENANT_CODE).replace("+aiomysql", "+pymysql")
    engine = create_engine(url)
    try:
        TenantBase.metadata.create_all(
            engine,
            tables=[WO.__table__, FleetMaintainPlan.__table__, FleetRenewal.__table__],
        )
        # 资产卡片字段：Phase1.5 / 迁移负责；此处幂等补列
        with engine.begin() as conn:
            for col, ddl in [
                ("original_value", "NUMERIC(14,2) NULL"),
                ("residual_value", "NUMERIC(14,2) NULL"),
                ("depreciable_months", "INTEGER NULL"),
                ("depreciation_method", "VARCHAR(32) NULL"),
                ("depreciation_start_date", "DATE NULL"),
            ]:
                exists = conn.exec_driver_sql(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_schema = DATABASE() AND table_name='biz_vehicle_ext' "
                    f"AND column_name='{col}' LIMIT 1"
                ).fetchone()
                if not exists:
                    conn.exec_driver_sql(
                        f"ALTER TABLE biz_vehicle_ext ADD COLUMN `{col}` {ddl}"
                    )
    finally:
        engine.dispose()


@pytest.fixture(scope="module", autouse=True)
def _ensure_tables():
    try:
        _ensure_tables_sync()
    except Exception as e:  # pragma: no cover
        pytest.skip(f"无法补建资产成本相关表：{e}")


def _rand_plate() -> str:
    prov = random.choice(_PROVINCES)
    letter = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
    tail = "".join(random.choice("0123456789") for _ in range(5))
    return f"{prov}{letter}{tail}"


async def _make_vehicle(session) -> Vehicle:
    out = await VehicleService.create_vehicle(
        session,
        VehicleCreate(plateNumber=_rand_plate(), plateCategory="YELLOW"),
    )
    result = await session.execute(select(Vehicle).where(Vehicle.id == out.id))
    return result.scalar_one()


async def test_renewal_effect_writes_expire_and_resolves_alert(tenant_session):
    vehicle = await _make_vehicle(tenant_session)
    ext = (
        await tenant_session.execute(
            select(VehicleExt).where(
                VehicleExt.vehicle_id == vehicle.id,
                VehicleExt.is_deleted == 0,
            )
        )
    ).scalar_one()
    ext.insurance_expire = date.today() - timedelta(days=1)
    alert = BizComplianceAlert(
        subject_type="vehicle",
        subject_id=vehicle.id,
        subject_name=vehicle.plate_number,
        doc_type="insurance",
        level="expired",
        status="open",
        expire_date=date.today() - timedelta(days=1),
        days_left=-1,
    )
    tenant_session.add(alert)
    await tenant_session.flush()

    new_expire = date.today() + timedelta(days=365)
    created = await FleetAssetCostService.create_renewal(
        tenant_session,
        RenewalCreate(
            vehicleId=vehicle.id,
            renewalType="insurance",
            effectiveDate=date.today(),
            expireDate=new_expire,
            amount=Decimal("12000.00"),
            policyNo="POL-TEST-001",
            effectNow=True,
        ),
        operator_user_id=1,
    )
    assert created["status"] == "effective"

    await tenant_session.refresh(ext)
    assert ext.insurance_expire == new_expire

    await tenant_session.refresh(alert)
    assert alert.status == "resolved"


async def test_asset_card_straight_line_depreciation(tenant_session):
    vehicle = await _make_vehicle(tenant_session)
    card = await FleetAssetCostService.update_asset_card(
        tenant_session,
        vehicle.id,
        AssetCardUpdate(
            purchaseDate=date(2024, 1, 15),
            originalValue=Decimal("120000"),
            residualValue=Decimal("12000"),
            depreciableMonths=36,
            depreciationMethod="straight_line",
            depreciationStartDate=date(2024, 1, 1),
        ),
    )
    assert Decimal(str(card["monthlyDepreciation"])) == Decimal("3000.00")
    assert card["depreciationMethod"] == "straight_line"
    assert card["netValue"] is not None


async def test_cost_summary_aggregates_four_types(tenant_session):
    vehicle = await _make_vehicle(tenant_session)
    await FleetAssetCostService.update_asset_card(
        tenant_session,
        vehicle.id,
        AssetCardUpdate(
            purchaseDate=date.today().replace(day=1) - timedelta(days=60),
            originalValue=Decimal("36000"),
            residualValue=Decimal("0"),
            depreciableMonths=12,
            depreciationStartDate=date.today().replace(day=1) - timedelta(days=40),
        ),
    )

    wo = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id,
            orderType="repair",
            title="刹车片更换",
            costAmount=Decimal("800"),
        ),
        operator_user_id=1,
    )
    await FleetMaintenanceService.start_work_order(
        tenant_session, wo["id"], operator_user_id=1
    )
    await FleetMaintenanceService.complete_work_order(
        tenant_session,
        wo["id"],
        WorkOrderCompleteBody(costAmount=Decimal("800")),
        operator_user_id=1,
    )

    # 强制完工日在本月（避免跨日边界）
    result = await tenant_session.execute(
        select(FleetWorkOrder).where(FleetWorkOrder.id == wo["id"])
    )
    row = result.scalar_one()
    row.finished_at = datetime.now()
    await tenant_session.flush()

    await FleetAssetCostService.create_renewal(
        tenant_session,
        RenewalCreate(
            vehicleId=vehicle.id,
            renewalType="inspection",
            effectiveDate=date.today(),
            expireDate=date.today() + timedelta(days=365),
            amount=Decimal("500"),
            effectNow=True,
        ),
        operator_user_id=1,
    )

    summary = await FleetAssetCostService.cost_summary(
        tenant_session,
        date_from=date.today().replace(day=1),
        date_to=date.today(),
        vehicle_id=vehicle.id,
    )
    assert summary["totals"]["maintenance"] == 800.0
    assert summary["totals"]["inspection"] == 500.0
    assert summary["totals"]["depreciation"] > 0
    assert summary["totals"]["total"] > 1300.0
    assert "不等于会计总账" in summary["disclaimer"]
