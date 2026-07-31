"""车辆资产 · 维修保养服务集成测试（租户库，事务回滚）

覆盖：工单创建/开工/完工、运输中禁止开工、保养计划生成工单、看板汇总。

对应需求：doc/02.需求文档/02.企业端/14.车辆资产模块/
对应代码：backend/app/modules/client/services/capacity/maintenance/
覆盖用例：TC-CLI-FLEETMAINT-001 ~ TC-CLI-FLEETMAINT-020
"""

from __future__ import annotations

import random

import pytest
from sqlalchemy import select

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from decimal import Decimal

from app.modules.client.models.capacity.maintenance.part import FleetPart
from app.modules.client.models.capacity.maintenance.stock_txn import FleetStockTxn
from app.modules.client.schemas.capacity.maintenance import (
    MaintainPlanCreate,
    PartCreate,
    StockInboundBody,
    WorkOrderCreate,
    WorkOrderLineIn,
)
from app.modules.client.services.capacity.maintenance.fleet_parts_service import (
    FleetPartsService,
)
from app.modules.client.schemas.capacity.self_capacity.vehicle import VehicleCreate
from app.modules.client.services.capacity.maintenance.fleet_maintenance_service import (
    FleetMaintenanceService,
)
from app.modules.client.services.capacity.self_capacity.vehicle_service import (
    VehicleService,
)

pytestmark = pytest.mark.asyncio

_PROVINCES = "京沪粤浙苏鲁川鄂湘皖"
def _ensure_fleet_tables_sync() -> None:
    """同步引擎幂等建表（避免 async greenlet 问题）。"""
    from sqlalchemy import create_engine

    from app.core.config import get_settings
    from app.modules.client.models.base import TenantBase
    from app.modules.client.models.capacity.maintenance.maintain_plan import (
        FleetMaintainPlan,
    )
    from app.modules.client.models.capacity.maintenance.part import FleetPart
    from app.modules.client.models.capacity.maintenance.stock_txn import (
        FleetStockTxn,
    )
    from app.modules.client.models.capacity.maintenance.work_order import (
        FleetWorkOrder,
    )
    from app.modules.client.models.capacity.maintenance.work_order_line import (
        FleetWorkOrderLine,
    )
    from app.modules.client.models.capacity.maintenance.workshop import (
        FleetWorkshop,
    )
    from tests.client.conftest import TENANT_CODE

    settings = get_settings()
    url = settings.tenant_db_url(TENANT_CODE).replace("+aiomysql", "+pymysql")
    engine = create_engine(url)
    try:
        TenantBase.metadata.create_all(
            engine,
            tables=[
                FleetWorkOrder.__table__,
                FleetWorkOrderLine.__table__,
                FleetMaintainPlan.__table__,
                FleetPart.__table__,
                FleetStockTxn.__table__,
                FleetWorkshop.__table__,
            ],
        )
    finally:
        engine.dispose()


@pytest.fixture(scope="module", autouse=True)
def _ensure_fleet_tables():
    try:
        _ensure_fleet_tables_sync()
    except Exception as e:  # pragma: no cover
        pytest.skip(f"无法补建维保表：{e}")


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
    result = await session.execute(
        select(Vehicle).where(Vehicle.id == out.id)
    )
    return result.scalar_one()


async def _bind_capacity(session, vehicle: Vehicle, op_status: int = 1) -> Capacity:
    cap = Capacity(
        driver_id=910001,
        driver_name="测试司机",
        driver_phone="13800000001",
        vehicle_id=vehicle.id,
        plate_number=vehicle.plate_number,
        status=1,
        operation_status=op_status,
    )
    session.add(cap)
    await session.flush()
    return cap


async def test_create_start_complete_work_order(tenant_session):
    """TC-CLI-FLEETMAINT-001/003/005：创建草稿 → 开工联动 → 完工回落"""
    vehicle = await _make_vehicle(tenant_session)
    cap = await _bind_capacity(tenant_session, vehicle, op_status=1)

    created = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id,
            orderType="repair",
            title="变速箱异响",
        ),
        operator_user_id=1,
    )
    assert created["status"] == "draft"
    assert created["workOrderNo"].startswith("WO")

    started = await FleetMaintenanceService.start_work_order(
        tenant_session, created["id"], operator_user_id=1
    )
    assert started["status"] == "in_progress"

    vehicle = (
        await tenant_session.execute(
            select(Vehicle).where(Vehicle.id == vehicle.id)
        )
    ).scalar_one()
    cap = (
        await tenant_session.execute(
            select(Capacity).where(Capacity.id == cap.id)
        )
    ).scalar_one()
    assert vehicle.status == 2
    assert vehicle.status_source == "maintenance"
    assert cap.operation_status == 5

    completed = await FleetMaintenanceService.complete_work_order(
        tenant_session, created["id"], None, operator_user_id=1
    )
    assert completed["status"] == "completed"

    vehicle = (
        await tenant_session.execute(
            select(Vehicle).where(Vehicle.id == vehicle.id)
        )
    ).scalar_one()
    cap = (
        await tenant_session.execute(
            select(Capacity).where(Capacity.id == cap.id)
        )
    ).scalar_one()
    assert vehicle.status == 1
    assert cap.operation_status == 1


async def test_start_rejected_when_in_transit(tenant_session):
    """TC-CLI-FLEETMAINT-004：运输中禁止开工"""
    vehicle = await _make_vehicle(tenant_session)
    await _bind_capacity(tenant_session, vehicle, op_status=2)
    created = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id,
            orderType="repair",
            title="刹车片更换",
        ),
        operator_user_id=1,
    )
    with pytest.raises(BizException) as ei:
        await FleetMaintenanceService.start_work_order(
            tenant_session, created["id"], operator_user_id=1
        )
    assert "运输任务尚未结束" in str(ei.value)


async def test_second_in_progress_rejected(tenant_session):
    """TC-CLI-FLEETMAINT-007：同车第二张进行中工单拒绝"""
    vehicle = await _make_vehicle(tenant_session)
    await _bind_capacity(tenant_session, vehicle, op_status=1)
    wo1 = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id, orderType="repair", title="工单1"
        ),
        operator_user_id=1,
    )
    await FleetMaintenanceService.start_work_order(
        tenant_session, wo1["id"], operator_user_id=1
    )
    wo2 = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id, orderType="repair", title="工单2"
        ),
        operator_user_id=1,
    )
    with pytest.raises(BizException) as ei:
        await FleetMaintenanceService.start_work_order(
            tenant_session, wo2["id"], operator_user_id=1
        )
    assert "进行中的维保工单" in str(ei.value)


async def test_plan_generate_and_board(tenant_session):
    """TC-CLI-FLEETMAINT-008/009：保养计划生成工单 + 看板"""
    vehicle = await _make_vehicle(tenant_session)
    plan = await FleetMaintenanceService.create_plan(
        tenant_session,
        MaintainPlanCreate(
            vehicleId=vehicle.id,
            name="常规保养",
            cycleType="time",
            intervalDays=1,
            remindDays=7,
        ),
        operator_user_id=1,
    )
    assert plan["nextMaintainDate"]

    wo = await FleetMaintenanceService.generate_work_order_from_plan(
        tenant_session, plan["id"], operator_user_id=1
    )
    assert wo["orderType"] == "maintenance"
    assert wo["planId"] == plan["id"]
    assert wo["status"] == "draft"

    board = await FleetMaintenanceService.board(tenant_session)
    assert "duePlans" in board and "inProgressOrders" in board
    assert "weekSummary" in board


async def test_start_without_capacity(tenant_session):
    """TC-CLI-FLEETMAINT-010：无绑定运力仅改车辆状态"""
    vehicle = await _make_vehicle(tenant_session)
    created = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id, orderType="repair", title="无运力开工"
        ),
        operator_user_id=1,
    )
    started = await FleetMaintenanceService.start_work_order(
        tenant_session, created["id"], operator_user_id=1
    )
    assert started["status"] == "in_progress"
    vehicle = (
        await tenant_session.execute(
            select(Vehicle).where(Vehicle.id == vehicle.id)
        )
    ).scalar_one()
    assert vehicle.status == 2


async def _make_part(session, *, code: str, qty: str = "10") -> dict:
    part = await FleetPartsService.create_part(
        session,
        PartCreate(
            partCode=code,
            partName=f"备件-{code}",
            unit="个",
            refPrice=Decimal("100"),
            safetyStock=2,
        ),
    )
    await FleetPartsService.inbound(
        session,
        part["id"],
        StockInboundBody(qty=Decimal(qty), unitCost=Decimal("100")),
        operator_user_id=1,
    )
    return part


async def test_work_order_lines_complete_deducts_stock(tenant_session):
    """TC-CLI-FLEETMAINT-021：含明细行创建，完工扣库存并汇总费用"""
    vehicle = await _make_vehicle(tenant_session)
    await _bind_capacity(tenant_session, vehicle, op_status=1)
    part = await _make_part(
        tenant_session, code=f"P{random.randint(10000, 99999)}", qty="5"
    )

    created = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id,
            orderType="repair",
            title="刹车片更换",
            faultCategory="brake",
            lines=[
                WorkOrderLineIn(
                    lineType="labor",
                    title="工时",
                    qty=Decimal("1"),
                    unitPrice=Decimal("200"),
                    laborHours=Decimal("2"),
                    amount=Decimal("400"),
                ),
                WorkOrderLineIn(
                    lineType="part",
                    partId=part["id"],
                    title=part["partName"],
                    qty=Decimal("2"),
                    unitPrice=Decimal("100"),
                ),
            ],
        ),
        operator_user_id=1,
    )
    assert created["laborAmount"] == "400.00" or Decimal(
        str(created["laborAmount"])
    ) == Decimal("400")
    assert Decimal(str(created["partsAmount"])) == Decimal("200")
    assert Decimal(str(created["costAmount"])) == Decimal("600")
    assert created.get("lines") and len(created["lines"]) == 2

    await FleetMaintenanceService.start_work_order(
        tenant_session, created["id"], operator_user_id=1
    )
    completed = await FleetMaintenanceService.complete_work_order(
        tenant_session, created["id"], None, operator_user_id=1
    )
    assert completed["status"] == "completed"
    assert Decimal(str(completed["costAmount"])) == Decimal("600")

    part_row = (
        await tenant_session.execute(
            select(FleetPart).where(FleetPart.id == part["id"])
        )
    ).scalar_one()
    assert Decimal(str(part_row.qty_on_hand)) == Decimal("3")

    txn_cnt = (
        await tenant_session.execute(
            select(FleetStockTxn)
            .where(
                FleetStockTxn.part_id == part["id"],
                FleetStockTxn.txn_type == "out",
                FleetStockTxn.ref_type == "work_order",
                FleetStockTxn.ref_id == created["id"],
                FleetStockTxn.is_deleted == 0,
            )
        )
    ).scalars().all()
    assert len(txn_cnt) == 1


async def test_complete_rejected_when_stock_insufficient(tenant_session):
    """TC-CLI-FLEETMAINT-022：库存不足拒绝完工"""
    vehicle = await _make_vehicle(tenant_session)
    await _bind_capacity(tenant_session, vehicle, op_status=1)
    part = await _make_part(
        tenant_session, code=f"P{random.randint(10000, 99999)}", qty="1"
    )

    created = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id,
            orderType="repair",
            title="库存不足场景",
            lines=[
                WorkOrderLineIn(
                    lineType="part",
                    partId=part["id"],
                    title=part["partName"],
                    qty=Decimal("3"),
                    unitPrice=Decimal("100"),
                ),
            ],
        ),
        operator_user_id=1,
    )
    await FleetMaintenanceService.start_work_order(
        tenant_session, created["id"], operator_user_id=1
    )
    with pytest.raises(BizException) as ei:
        await FleetMaintenanceService.complete_work_order(
            tenant_session, created["id"], None, operator_user_id=1
        )
    assert "库存不足" in str(ei.value)


async def test_inbound_increases_stock(tenant_session):
    """TC-CLI-FLEETMAINT-023：入库增加库存"""
    part = await FleetPartsService.create_part(
        tenant_session,
        PartCreate(
            partCode=f"IN{random.randint(10000, 99999)}",
            partName="机油滤芯",
            unit="个",
            refPrice=Decimal("35"),
            safetyStock=5,
        ),
    )
    assert Decimal(str(part["qtyOnHand"])) == Decimal("0")
    updated = await FleetPartsService.inbound(
        tenant_session,
        part["id"],
        StockInboundBody(qty=Decimal("12"), unitCost=Decimal("30")),
        operator_user_id=1,
    )
    assert Decimal(str(updated["qtyOnHand"])) == Decimal("12")


async def test_cancel_in_progress_does_not_deduct_stock(tenant_session):
    """TC-CLI-FLEETMAINT-024：取消进行中工单不扣库存"""
    vehicle = await _make_vehicle(tenant_session)
    await _bind_capacity(tenant_session, vehicle, op_status=1)
    part = await _make_part(
        tenant_session, code=f"P{random.randint(10000, 99999)}", qty="8"
    )

    created = await FleetMaintenanceService.create_work_order(
        tenant_session,
        WorkOrderCreate(
            vehicleId=vehicle.id,
            orderType="repair",
            title="取消不扣库",
            lines=[
                WorkOrderLineIn(
                    lineType="part",
                    partId=part["id"],
                    title=part["partName"],
                    qty=Decimal("2"),
                    unitPrice=Decimal("100"),
                ),
            ],
        ),
        operator_user_id=1,
    )
    await FleetMaintenanceService.start_work_order(
        tenant_session, created["id"], operator_user_id=1
    )
    await FleetMaintenanceService.cancel_work_order(
        tenant_session, created["id"], operator_user_id=1
    )

    part_row = (
        await tenant_session.execute(
            select(FleetPart).where(FleetPart.id == part["id"])
        )
    ).scalar_one()
    assert Decimal(str(part_row.qty_on_hand)) == Decimal("8")

    out_txns = (
        await tenant_session.execute(
            select(FleetStockTxn).where(
                FleetStockTxn.part_id == part["id"],
                FleetStockTxn.txn_type == "out",
                FleetStockTxn.ref_id == created["id"],
                FleetStockTxn.is_deleted == 0,
            )
        )
    ).scalars().all()
    assert len(out_txns) == 0
