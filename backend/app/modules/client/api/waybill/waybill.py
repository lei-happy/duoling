"""
企业端运单管理 API
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import TenantException
from app.common.mask_display import mask_organization_name
from app.common.operation_log import operation_log
from app.core.dependencies import (
    ensure_biz_company_activity_table,
    get_current_user,
    get_tenant_db,
)
from app.common.response import success
from app.core.security import TokenData
from app.modules.client.schemas.waybill.waybill import (
    WaybillCreate,
    WaybillUpdate,
    WaybillStatusUpdate,
    WaybillOut,
)
from app.modules.client.services.company_activity_service import CompanyActivityService
from app.modules.client.services.waybill.waybill_service import WaybillService

router = APIRouter()

_WAYBILL_STATUS_LABELS = {
    0: "待确认",
    1: "已确认",
    2: "已调度",
    3: "运输中",
    4: "已送达",
    5: "已完成",
    6: "已取消",
}


def _require_tenant_for_activity(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


def _waybill_summary_customer_suffix(customer_name: Optional[str]) -> str:
    """摘要中客户片段（已脱敏）；无客户名则返回空串。"""
    if not (customer_name and str(customer_name).strip()):
        return ""
    return f"（客户：{mask_organization_name(customer_name)}）"


@router.get("")
async def page_waybills(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    status: Optional[int] = None,
    originKeyword: Optional[str] = None,
    destinationKeyword: Optional[str] = None,
    vehicleKeyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await WaybillService.page_waybills(
        db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        customer_id=customerId,
        status=status,
        origin_keyword=originKeyword,
        destination_keyword=destinationKeyword,
        vehicle_keyword=vehicleKeyword,
    )
    return success(data=data)


@router.get("/{waybill_id}")
async def get_waybill(
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    waybill = await WaybillService.get_waybill(db, waybill_id)
    return success(data=WaybillOut.from_model(waybill).model_dump())


@router.post("")
@operation_log(module="运单管理", action="新增", description="新增运单")
async def create_waybill(
    request: Request,
    data: WaybillCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    _require_tenant_for_activity(current_user)
    waybill = await WaybillService.create_waybill(db, data, current_user.user_id)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    label = op_name or "用户"
    suffix = _waybill_summary_customer_suffix(waybill.customer_name)
    summary = f"{label} 创建了运单「{waybill.waybill_no}」{suffix}"
    payload = {
        "waybill_id": waybill.id,
        "waybill_no": waybill.waybill_no,
    }
    if waybill.customer_id is not None:
        payload["customer_id"] = waybill.customer_id

    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="waybill.created",
        summary=summary,
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload=payload,
    )
    return success(data=WaybillOut.from_model(waybill).model_dump())


@router.put("/{waybill_id}")
@operation_log(module="运单管理", action="编辑", description="编辑运单")
async def update_waybill(
    request: Request,
    waybill_id: int,
    data: WaybillUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    _require_tenant_for_activity(current_user)
    waybill = await WaybillService.update_waybill(db, waybill_id, data)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    label = op_name or "用户"
    suffix = _waybill_summary_customer_suffix(waybill.customer_name)
    summary = f"{label} 编辑了运单「{waybill.waybill_no}」{suffix}"
    payload = {
        "waybill_id": waybill.id,
        "waybill_no": waybill.waybill_no,
    }
    if waybill.customer_id is not None:
        payload["customer_id"] = waybill.customer_id

    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="waybill.updated",
        summary=summary,
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload=payload,
    )
    return success(data=WaybillOut.from_model(waybill).model_dump())


@router.put("/{waybill_id}/status")
@operation_log(module="运单管理", action="状态变更", description="变更运单状态")
async def update_waybill_status(
    request: Request,
    waybill_id: int,
    data: WaybillStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    _require_tenant_for_activity(current_user)
    waybill = await WaybillService.update_status(db, waybill_id, data)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    label = op_name or "用户"
    status_label = _WAYBILL_STATUS_LABELS.get(
        data.status, f"状态{data.status}"
    )
    suffix = _waybill_summary_customer_suffix(waybill.customer_name)
    summary = (
        f"{label} 将运单「{waybill.waybill_no}」状态变更为「{status_label}」"
        f"{suffix}"
    )
    payload = {
        "waybill_id": waybill.id,
        "waybill_no": waybill.waybill_no,
        "status": data.status,
    }
    if waybill.customer_id is not None:
        payload["customer_id"] = waybill.customer_id

    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="waybill.status_changed",
        summary=summary,
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload=payload,
    )
    return success(data=WaybillOut.from_model(waybill).model_dump())


@router.delete("/{waybill_id}")
@operation_log(module="运单管理", action="删除", description="删除运单")
async def delete_waybill(
    request: Request,
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    _require_tenant_for_activity(current_user)
    waybill = await WaybillService.get_waybill(db, waybill_id)
    wb_no = waybill.waybill_no
    cust_name = waybill.customer_name
    cid = waybill.customer_id
    await WaybillService.delete_waybill(db, waybill_id)

    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    label = op_name or "用户"
    suffix = _waybill_summary_customer_suffix(cust_name)
    summary = f"{label} 删除了运单「{wb_no}」{suffix}"
    payload = {"waybill_id": waybill_id, "waybill_no": wb_no}
    if cid is not None:
        payload["customer_id"] = cid

    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="waybill.deleted",
        summary=summary,
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload=payload,
    )
    return success()
