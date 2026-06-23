"""
企业端运单管理 API
"""

import io
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import StreamingResponse
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
from app.common.response import fail, success
from app.core.security import TokenData
from app.modules.client.schemas.waybill.waybill import (
    WaybillCreate,
    WaybillUpdate,
    WaybillStatusUpdate,
)
from app.modules.client.schemas.waybill.waybill_receipt import (
    WaybillReceiptConfirm,
)
from app.modules.client.services.company_activity_service import CompanyActivityService
from app.modules.client.services.state_machine.waybill_state_machine import (
    WAYBILL_STATUS_LABELS as _WAYBILL_STATUS_LABELS,
)
from app.modules.client.services.waybill.waybill_receipt_service import (
    WaybillReceiptService,
)
from app.modules.client.services.waybill.waybill_service import WaybillService

router = APIRouter()


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
    createdAtStart: Optional[date] = Query(None, description="创建日期起（含当日 0 点）"),
    createdAtEnd: Optional[date] = Query(None, description="创建日期止（含当日结束）"),
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
        created_at_start=createdAtStart,
        created_at_end=createdAtEnd,
    )
    return success(data=data)


@router.get("/workbench-stats")
async def get_waybill_workbench_stats(
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    originKeyword: Optional[str] = None,
    destinationKeyword: Optional[str] = None,
    vehicleKeyword: Optional[str] = None,
    createdAtStart: Optional[date] = Query(None, description="创建日期起（含当日 0 点）"),
    createdAtEnd: Optional[date] = Query(None, description="创建日期止（含当日结束）"),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """运单工作台 KPI 聚合：各状态计数 + totals 别名（支持与列表相同的筛选条件）。"""
    stats = await WaybillService.workbench_stats(
        db,
        keyword=keyword,
        customer_id=customerId,
        origin_keyword=originKeyword,
        destination_keyword=destinationKeyword,
        vehicle_keyword=vehicleKeyword,
        created_at_start=createdAtStart,
        created_at_end=createdAtEnd,
    )
    return success(data=stats)


@router.get("/check-waybill-no")
async def check_waybill_no(
    waybillNo: str = Query(..., min_length=1, max_length=50),
    excludeId: Optional[int] = Query(None, ge=1),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """校验运单号是否可用（未被占用）。编辑时可传 excludeId 排除当前运单。"""
    taken = await WaybillService.waybill_no_exists(db, waybillNo, excludeId)
    return success(data={"available": not taken})


@router.get("/{waybill_id}")
async def get_waybill(
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    waybill = await WaybillService.get_waybill(db, waybill_id)
    out = await WaybillService.waybill_to_out(db, waybill)
    return success(data=out.model_dump())


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
    waybill, _cargoes = await WaybillService.create_waybill(
        db, data, current_user.user_id
    )
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
    out = await WaybillService.waybill_to_out(db, waybill)
    return success(data=out.model_dump())


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
    waybill, _cargoes = await WaybillService.update_waybill(
        db, waybill_id, data, current_user_id=current_user.user_id,
    )
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
    out = await WaybillService.waybill_to_out(db, waybill)
    return success(data=out.model_dump())


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
    out = await WaybillService.waybill_to_out(db, waybill)
    return success(data=out.model_dump())


@router.get("/{waybill_id}/receipts")
async def list_waybill_receipts(
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """列举运单的回单凭证。"""
    receipts = await WaybillReceiptService.list_receipts(db, waybill_id)
    return success(data=[r.model_dump() for r in receipts])


@router.post("/{waybill_id}/receipt")
@operation_log(module="运单管理", action="确认回单", description="确认运单回单")
async def confirm_waybill_receipt(
    request: Request,
    waybill_id: int,
    data: WaybillReceiptConfirm,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    """确认回单：运单 5 已签收 → 6 已回单。"""
    _require_tenant_for_activity(current_user)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    receipt = await WaybillReceiptService.confirm(
        db, waybill_id, data,
        operator_id=current_user.user_id,
        operator_name=op_name,
    )
    waybill = await WaybillService.get_waybill(db, waybill_id)
    label = op_name or "用户"
    suffix = _waybill_summary_customer_suffix(waybill.customer_name)
    summary = f"{label} 确认运单「{waybill.waybill_no}」回单{suffix}"
    payload = {
        "waybill_id": waybill.id,
        "waybill_no": waybill.waybill_no,
        "status": waybill.status,
        "receipt_id": receipt.id,
    }
    if waybill.customer_id is not None:
        payload["customer_id"] = waybill.customer_id
    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="waybill.receipt_confirmed",
        summary=summary,
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload=payload,
    )
    out = await WaybillService.waybill_to_out(db, waybill)
    return success(data=out.model_dump())


@router.delete("/{waybill_id}/receipt")
@operation_log(module="运单管理", action="撤销回单", description="撤销运单回单")
async def revoke_waybill_receipt(
    request: Request,
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    """撤销回单：运单 6 已回单 → 5 已签收。"""
    _require_tenant_for_activity(current_user)
    await WaybillReceiptService.revoke(db, waybill_id)
    waybill = await WaybillService.get_waybill(db, waybill_id)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    label = op_name or "用户"
    suffix = _waybill_summary_customer_suffix(waybill.customer_name)
    summary = f"{label} 撤销运单「{waybill.waybill_no}」回单{suffix}"
    payload = {
        "waybill_id": waybill.id,
        "waybill_no": waybill.waybill_no,
        "status": waybill.status,
    }
    if waybill.customer_id is not None:
        payload["customer_id"] = waybill.customer_id
    await CompanyActivityService.record(
        db,
        occurred_at=datetime.now(),
        event_code="waybill.receipt_revoked",
        summary=summary,
        actor_user_id=current_user.user_id,
        actor_display_name=op_name,
        payload=payload,
    )
    out = await WaybillService.waybill_to_out(db, waybill)
    return success(data=out.model_dump())


@router.post("/{waybill_id}/recalculate")
@operation_log(module="运单管理", action="重算运费", description="手动触发运费重算")
async def recalculate_waybill(
    request: Request,
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """手动触发运费重算（写入高优先级 task，由 worker 异步执行）"""
    task_id = await WaybillService.request_recalc(
        db, waybill_id, current_user_id=current_user.user_id,
    )
    return success(data={"taskId": task_id})


@router.get("/{waybill_id}/freight-result")
async def get_waybill_freight_result(
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    """获取运单的最新计算结果（含明细 + match_trace_json）"""
    from app.modules.client.services.billing.freight_result_service import (
        FreightResultService,
    )
    data = await FreightResultService.get_active_result_with_detail(db, waybill_id)
    return success(data=data)


@router.put("/{waybill_id}/lock")
@operation_log(module="运单管理", action="锁定", description="锁定运单（禁止重算）")
async def lock_waybill(
    request: Request,
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    waybill = await WaybillService.get_waybill(db, waybill_id)
    waybill.is_locked = 1
    waybill.calc_status = "locked"
    await db.flush()
    out = await WaybillService.waybill_to_out(db, waybill)
    return success(data=out.model_dump())


@router.put("/{waybill_id}/unlock")
@operation_log(module="运单管理", action="解锁", description="解锁运单")
async def unlock_waybill(
    request: Request,
    waybill_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    waybill = await WaybillService.get_waybill(db, waybill_id)
    waybill.is_locked = 0
    if waybill.calc_status == "locked":
        waybill.calc_status = "pending"
    await db.flush()
    out = await WaybillService.waybill_to_out(db, waybill)
    return success(data=out.model_dump())


@router.post("/import")
@operation_log(module="运单管理", action="批量导入", description="Excel 批量导入运单")
async def import_waybills(
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """上传 Excel 批量导入运单（同步解析，行级失败不影响其他行）。"""
    file_bytes = await file.read()
    if not file_bytes:
        from app.common.exceptions import BizException
        raise BizException("上传文件为空")
    from app.modules.client.services.waybill.waybill_import_service import (
        WaybillImportService,
    )
    batch = await WaybillImportService.import_excel(
        db,
        file_name=file.filename or "import.xlsx",
        file_bytes=file_bytes,
        current_user_id=current_user.user_id,
    )
    return success(data={
        "batchId": batch.id,
        "totalCount": batch.total_count,
        "successCount": batch.success_count,
        "failCount": batch.fail_count,
        "status": batch.status,
    })


@router.get("/import/template")
async def download_waybill_import_template(_=Depends(get_current_user)):
    """下载运单批量导入 Excel 模板（表头与解析逻辑一致）。"""
    from app.modules.client.services.waybill.waybill_import_service import (
        WaybillImportService,
    )

    data = WaybillImportService.build_template_workbook_bytes()
    return StreamingResponse(
        io.BytesIO(data),
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": 'attachment; filename="waybill-import-template.xlsx"'
        },
    )


@router.get("/import/batches")
async def page_import_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    from app.modules.client.services.waybill.waybill_import_service import (
        WaybillImportService,
    )
    data = await WaybillImportService.page_batches(db, page=page, limit=page_size)
    return success(data=data)


@router.get("/import/batch/{batch_id}")
async def get_import_batch(
    batch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    from app.modules.client.services.waybill.waybill_import_service import (
        WaybillImportService,
    )
    batch = await WaybillImportService.get_batch(db, batch_id)
    if not batch:
        return fail(message="批次不存在", code=404)
    return success(data={
        "id": batch.id,
        "fileName": batch.file_name,
        "totalCount": batch.total_count,
        "successCount": batch.success_count,
        "failCount": batch.fail_count,
        "calcSuccessCount": batch.calc_success_count,
        "calcExceptionCount": batch.calc_exception_count,
        "status": batch.status,
        "errorMessage": batch.error_message,
        "createdBy": batch.created_by,
        "createdAt": batch.created_at,
    })


@router.get("/import/batch/{batch_id}/rows")
async def list_import_rows(
    batch_id: int,
    validateStatus: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, alias="limit", ge=1, le=200),
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    from app.modules.client.services.waybill.waybill_import_service import (
        WaybillImportService,
    )
    data = await WaybillImportService.list_rows(
        db, batch_id, validate_status=validateStatus,
        page=page, limit=page_size,
    )
    return success(data=data)


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
