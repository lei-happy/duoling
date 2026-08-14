"""打款批次与出纳台 API

接口前缀：``/api/client/finance/payment-batch``

出纳台的聚合读接口（``/workbench/*``）也挂在这里：它们读的就是批次与流水，单独开一棵
路由树只会让前端多记一个前缀。
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import TenantException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.finance.payment_batch import (
    FundFlowOut,
    PayCalendarDayOut,
    PayableCandidateOut,
    PaymentBatchAddItemsRequest,
    PaymentBatchCreateRequest,
    PaymentBatchExecuteRequest,
    PaymentBatchItemOut,
    PaymentBatchListItem,
    PaymentBatchOut,
    PaymentBatchReasonRequest,
    PaymentBatchUpdateRequest,
)
from app.modules.client.services.finance.cashier.cashier_service import CashierService
from app.modules.client.services.finance.cashier.payment_batch_service import (
    PaymentBatchService,
)

router = APIRouter()

_MODULE = "打款批次"
_SVC = PaymentBatchService


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


async def _detail(db: AsyncSession, batch_id: int) -> dict:
    batch = await _SVC.get_or_404(db, batch_id)
    items = await _SVC.list_items(db, batch_id)
    return PaymentBatchOut.from_model(
        batch, items=items, actions=_SVC.action_flags(batch),
    ).model_dump()


# ============================================================
# 出纳台聚合
# ============================================================

@router.get("/workbench/overview")
async def workbench_overview(
    enterpriseId: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """出纳台指标：待认领到账、待付款、在批待执行、账面余额。"""
    return success(data=await CashierService.overview(
        db, enterprise_id=enterpriseId,
    ))


@router.get("/workbench/flow")
async def fund_flow(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    direction: Optional[int] = Query(
        default=None, ge=1, le=2, description="1-收款 2-付款",
    ),
    bankAccountId: Optional[int] = None,
    dateFrom: Optional[date] = None,
    dateTo: Optional[date] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """收付款流水（收款到账 + 打款批次成功笔）。"""
    rows, total, summary = await CashierService.flow_list(
        db,
        page=page, page_size=page_size, direction=direction,
        bank_account_id=bankAccountId, date_from=dateFrom, date_to=dateTo,
        keyword=keyword,
    )
    return success(data={
        "list": [FundFlowOut(**x).model_dump() for x in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
        "summary": summary,
    })


@router.get("/workbench/calendar")
async def pay_calendar(
    days: int = Query(default=14, ge=1, le=60),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """付款日历：未来若干天要准备的资金。"""
    rows = await CashierService.pay_calendar(db, days=days)
    return success(data=[PayCalendarDayOut(**x).model_dump() for x in rows])


# ============================================================
# 候选与列表
# ============================================================

@router.get("/candidates")
async def list_candidates(
    docKinds: Optional[str] = Query(
        default=None,
        description="逗号分隔：task_finance,carrier_settle,driver_payroll",
    ),
    keyword: Optional[str] = None,
    dueBefore: Optional[date] = None,
    limit: int = Query(default=300, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """可入批的应付单（已审批、未入批）。"""
    kinds = (
        [x.strip() for x in docKinds.split(",") if x.strip()]
        if docKinds else None
    )
    rows = await _SVC.list_candidates(
        db, doc_kinds=kinds, keyword=keyword, due_before=dueBefore, limit=limit,
    )
    return success(data={
        "list": [PayableCandidateOut(**x).model_dump() for x in rows],
        "count": len(rows),
    })


@router.get("")
async def page_batches(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    bankAccountId: Optional[int] = None,
    enterpriseId: Optional[int] = None,
    dateFrom: Optional[date] = None,
    dateTo: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await _SVC.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword, status=status,
        bank_account_id=bankAccountId, enterprise_id=enterpriseId,
        date_from=dateFrom, date_to=dateTo,
    )
    return success(data={
        "list": [PaymentBatchListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


# ============================================================
# 建批与明细
# ============================================================

@router.post("")
@operation_log(module=_MODULE, action="新建批次", description="按应付单创建打款批次")
async def create_batch(
    request: Request,
    data: PaymentBatchCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    batch = await _SVC.create_batch(
        db,
        docs=[x.model_dump() for x in data.docs],
        bank_account_id=data.bankAccountId,
        enterprise_id=data.enterpriseId,
        pay_method=data.payMethod,
        plan_pay_date=data.planPayDate,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, batch.id), message="批次已创建")


@router.get("/{batch_id}")
async def get_batch(
    batch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _detail(db, batch_id))


@router.put("/{batch_id}")
@operation_log(module=_MODULE, action="编辑批次", description="编辑打款批次信息")
async def update_batch(
    request: Request,
    batch_id: int,
    data: PaymentBatchUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.update_batch(
        db, batch_id,
        bank_account_id=data.bankAccountId,
        pay_method=data.payMethod,
        plan_pay_date=data.planPayDate,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, batch_id))


@router.delete("/{batch_id}")
@operation_log(module=_MODULE, action="删除批次", description="删除打款批次草稿")
async def delete_batch(
    request: Request,
    batch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.soft_delete(db, batch_id)
    return success()


@router.get("/{batch_id}/items")
async def list_items(
    batch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await _SVC.get_or_404(db, batch_id)
    rows = await _SVC.list_items(db, batch_id)
    return success(data=[PaymentBatchItemOut.from_model(x).model_dump() for x in rows])


@router.post("/{batch_id}/items")
@operation_log(module=_MODULE, action="添加明细", description="向打款批次添加应付单")
async def add_items(
    request: Request,
    batch_id: int,
    data: PaymentBatchAddItemsRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    rows = await _SVC.add_items(
        db, batch_id, [x.model_dump() for x in data.docs],
        operator_id=current_user.user_id,
    )
    return success(
        data=await _detail(db, batch_id),
        message=f"已加入 {len(rows)} 笔",
    )


@router.delete("/{batch_id}/items/{item_id}")
@operation_log(module=_MODULE, action="移出明细", description="把某笔移出打款批次")
async def remove_item(
    request: Request,
    batch_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.remove_item(
        db, batch_id, item_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, batch_id), message="已移出批次")


# ============================================================
# 状态流转
# ============================================================

@router.post("/{batch_id}/submit")
@operation_log(module=_MODULE, action="提交批次", description="提交打款批次待审批")
async def submit_batch(
    request: Request,
    batch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.submit(db, batch_id, current_user.user_id)
    return success(data=await _detail(db, batch_id), message="批次已提交审批")


@router.post("/{batch_id}/approve")
@operation_log(module=_MODULE, action="审批批次", description="审批通过打款批次")
async def approve_batch(
    request: Request,
    batch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.approve(db, batch_id, current_user.user_id)
    return success(data=await _detail(db, batch_id), message="批次已审批，可以打款")


@router.post("/{batch_id}/reject")
@operation_log(module=_MODULE, action="拒绝批次", description="审批拒绝打款批次")
async def reject_batch(
    request: Request,
    batch_id: int,
    data: PaymentBatchReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.reject(db, batch_id, data.reason, current_user.user_id)
    return success(data=await _detail(db, batch_id), message="已拒绝该批次")


@router.post("/{batch_id}/execute")
@operation_log(module=_MODULE, action="执行打款", description="登记打款批次执行结果")
async def execute_batch(
    request: Request,
    batch_id: int,
    data: PaymentBatchExecuteRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    batch = await _SVC.execute(
        db, batch_id,
        [x.model_dump() for x in data.results] if data.results else None,
        paid_at=data.paidAt,
        operator_id=current_user.user_id,
    )
    message = (
        f"已登记 {batch.success_count} 笔成功"
        + (f"、{batch.fail_count} 笔失败，请稍后补打" if batch.fail_count else "")
    )
    return success(data=await _detail(db, batch_id), message=message)


@router.post("/{batch_id}/cancel")
@operation_log(module=_MODULE, action="撤销批次", description="撤销打款批次")
async def cancel_batch(
    request: Request,
    batch_id: int,
    data: PaymentBatchReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.cancel_batch(db, batch_id, data.reason, current_user.user_id)
    return success(
        data=await _detail(db, batch_id),
        message="批次已撤销，里面的单已放回待付池",
    )


@router.get("/{batch_id}/events")
async def list_events(
    batch_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    events = await _SVC.list_events(db, batch_id)
    return success(data=[
        {
            "id": e.id,
            "eventType": e.event_type,
            "fromStatus": e.from_status,
            "toStatus": e.to_status,
            "occurredAmount": (
                float(e.occurred_amount) if e.occurred_amount is not None else None
            ),
            "operatorId": e.operator_id,
            "operatorName": e.operator_name,
            "reason": e.reason,
            "eventTime": e.event_time,
        }
        for e in events
    ])
