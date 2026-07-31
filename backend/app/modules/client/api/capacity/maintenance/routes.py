"""
车辆资产 - 维修保养 / 资产成本 API

前缀：/capacity/maintenance
门控：fleet_maintenance（专业版）
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.database import db_manager
from app.core.dependencies import get_current_user, get_tenant_code, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.capacity.maintenance import (
    AssetCardUpdate,
    MaintainPlanCreate,
    MaintainPlanUpdate,
    PartCreate,
    PartUpdate,
    RenewalCreate,
    RenewalUpdate,
    StockAdjustBody,
    StockInboundBody,
    WorkOrderCompleteBody,
    WorkOrderCreate,
    WorkOrderUpdate,
    WorkshopCreate,
    WorkshopUpdate,
)
from app.modules.client.services.capacity.maintenance.fleet_asset_cost_service import (
    FleetAssetCostService,
)
from app.modules.client.services.capacity.maintenance.fleet_maintenance_service import (
    FleetMaintenanceService,
)
from app.modules.client.services.capacity.maintenance.fleet_parts_service import (
    FleetPartsService,
)

router = APIRouter()

_TABLES = [
    "biz_fleet_work_order",
    "biz_fleet_work_order_line",
    "biz_fleet_maintain_plan",
    "biz_fleet_renewal",
    "biz_fleet_part",
    "biz_fleet_stock_txn",
    "biz_fleet_workshop",
]


async def _ensure_tables(tenant_code: str = Depends(get_tenant_code)) -> None:
    await db_manager.ensure_tenant_tables(tenant_code, _TABLES)


@router.get("/board")
async def board(
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetMaintenanceService.board(db)
    return success(data=data)


@router.get("/work-orders")
async def page_work_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    status: Optional[str] = None,
    orderType: Optional[str] = None,
    vehicleId: Optional[int] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetMaintenanceService.page_work_orders(
        db,
        page=page,
        page_size=page_size,
        status=status,
        order_type=orderType,
        vehicle_id=vehicleId,
        keyword=keyword,
    )
    return success(data=data)


@router.post("/work-orders")
async def create_work_order(
    body: WorkOrderCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetMaintenanceService.create_work_order(
        db, body, current_user.user_id
    )
    return success(data=data, message="工单已创建")


@router.get("/work-orders/{wo_id}")
async def get_work_order(
    wo_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetMaintenanceService.get_work_order(db, wo_id)
    return success(data=data)


@router.put("/work-orders/{wo_id}")
async def update_work_order(
    wo_id: int,
    body: WorkOrderUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetMaintenanceService.update_work_order(db, wo_id, body)
    return success(data=data, message="工单已保存")


@router.post("/work-orders/{wo_id}/start")
async def start_work_order(
    wo_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetMaintenanceService.start_work_order(
        db, wo_id, current_user.user_id
    )
    return success(data=data, message="已开工，运力已同步为维修保养中")


@router.post("/work-orders/{wo_id}/complete")
async def complete_work_order(
    wo_id: int,
    body: Optional[WorkOrderCompleteBody] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetMaintenanceService.complete_work_order(
        db, wo_id, body, current_user.user_id
    )
    return success(data=data, message="工单已完工")


@router.post("/work-orders/{wo_id}/cancel")
async def cancel_work_order(
    wo_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetMaintenanceService.cancel_work_order(
        db, wo_id, current_user.user_id
    )
    return success(data=data, message="工单已取消")


@router.get("/plans")
async def page_plans(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    vehicleId: Optional[int] = None,
    enabled: Optional[int] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetMaintenanceService.page_plans(
        db,
        page=page,
        page_size=page_size,
        vehicle_id=vehicleId,
        enabled=enabled,
        keyword=keyword,
    )
    return success(data=data)


@router.post("/plans")
async def create_plan(
    body: MaintainPlanCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetMaintenanceService.create_plan(
        db, body, current_user.user_id
    )
    return success(data=data, message="保养计划已创建")


@router.put("/plans/{plan_id}")
async def update_plan(
    plan_id: int,
    body: MaintainPlanUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetMaintenanceService.update_plan(db, plan_id, body)
    return success(data=data, message="保养计划已保存")


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    await FleetMaintenanceService.delete_plan(db, plan_id)
    return success(message="保养计划已删除")


@router.post("/plans/{plan_id}/generate-work-order")
async def generate_work_order(
    plan_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetMaintenanceService.generate_work_order_from_plan(
        db, plan_id, current_user.user_id
    )
    return success(data=data, message="已生成保养工单草稿")


# ---------- 二期：续期 / 资产卡片 / 成本 ----------


@router.get("/renewals")
async def page_renewals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    renewalType: Optional[str] = None,
    status: Optional[str] = None,
    vehicleId: Optional[int] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetAssetCostService.page_renewals(
        db,
        page=page,
        page_size=page_size,
        renewal_type=renewalType,
        status=status,
        vehicle_id=vehicleId,
        keyword=keyword,
    )
    return success(data=data)


@router.post("/renewals")
async def create_renewal(
    body: RenewalCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetAssetCostService.create_renewal(
        db, body, current_user.user_id
    )
    msg = "续期已登记并生效" if data.get("status") == "effective" else "续期草稿已保存"
    return success(data=data, message=msg)


@router.put("/renewals/{renewal_id}")
async def update_renewal(
    renewal_id: int,
    body: RenewalUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetAssetCostService.update_renewal(db, renewal_id, body)
    return success(data=data, message="续期记录已保存")


@router.post("/renewals/{renewal_id}/effect")
async def effect_renewal(
    renewal_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetAssetCostService.effect_renewal(
        db, renewal_id, current_user.user_id
    )
    return success(data=data, message="续期已生效，到期日已更新")


@router.post("/renewals/{renewal_id}/cancel")
async def cancel_renewal(
    renewal_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetAssetCostService.cancel_renewal(
        db, renewal_id, current_user.user_id
    )
    return success(data=data, message="续期记录已取消")


@router.get("/vehicles/{vehicle_id}/asset-card")
async def get_asset_card(
    vehicle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetAssetCostService.get_asset_card(db, vehicle_id)
    return success(data=data)


@router.put("/vehicles/{vehicle_id}/asset-card")
async def update_asset_card(
    vehicle_id: int,
    body: AssetCardUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetAssetCostService.update_asset_card(db, vehicle_id, body)
    return success(data=data, message="资产卡片已保存")


@router.get("/cost/summary")
async def cost_summary(
    dateFrom: date = Query(...),
    dateTo: date = Query(...),
    vehicleId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetAssetCostService.cost_summary(
        db,
        date_from=dateFrom,
        date_to=dateTo,
        vehicle_id=vehicleId,
    )
    return success(data=data)


@router.get("/cost/details")
async def cost_details(
    dateFrom: date = Query(...),
    dateTo: date = Query(...),
    vehicleId: Optional[int] = None,
    costType: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetAssetCostService.cost_details(
        db,
        date_from=dateFrom,
        date_to=dateTo,
        vehicle_id=vehicleId,
        cost_type=costType,
    )
    return success(data=data)


# ---------- 备件 / 库存 / 维修厂 ----------


@router.get("/parts")
async def page_parts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    lowStockOnly: bool = False,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetPartsService.page_parts(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
        low_stock_only=lowStockOnly,
    )
    return success(data=data)


@router.post("/parts")
async def create_part(
    body: PartCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetPartsService.create_part(db, body)
    return success(data=data, message="备件已创建")


@router.put("/parts/{part_id}")
async def update_part(
    part_id: int,
    body: PartUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetPartsService.update_part(db, part_id, body)
    return success(data=data, message="备件已保存")


@router.post("/parts/{part_id}/inbound")
async def inbound_part(
    part_id: int,
    body: StockInboundBody,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetPartsService.inbound(
        db, part_id, body, current_user.user_id
    )
    return success(data=data, message="入库成功")


@router.post("/parts/{part_id}/adjust")
async def adjust_part(
    part_id: int,
    body: StockAdjustBody,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _t=Depends(_ensure_tables),
):
    data = await FleetPartsService.adjust(
        db, part_id, body, current_user.user_id
    )
    return success(data=data, message="库存已调整")


@router.get("/stock-txns")
async def page_stock_txns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    partId: Optional[int] = None,
    txnType: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetPartsService.page_stock_txns(
        db,
        page=page,
        page_size=page_size,
        part_id=partId,
        txn_type=txnType,
        keyword=keyword,
    )
    return success(data=data)


@router.get("/workshops")
async def page_workshops(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, alias="limit", ge=1, le=200),
    keyword: Optional[str] = None,
    enabled: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetPartsService.page_workshops(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        enabled=enabled,
    )
    return success(data=data)


@router.post("/workshops")
async def create_workshop(
    body: WorkshopCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetPartsService.create_workshop(db, body)
    return success(data=data, message="维修厂已创建")


@router.put("/workshops/{workshop_id}")
async def update_workshop(
    workshop_id: int,
    body: WorkshopUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _t=Depends(_ensure_tables),
    _=Depends(get_current_user),
):
    data = await FleetPartsService.update_workshop(db, workshop_id, body)
    return success(data=data, message="维修厂已保存")
