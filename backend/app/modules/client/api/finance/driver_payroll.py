"""司机工资单 API

接口前缀：``/api/client/finance/driver-payroll``

``/{id}/payslip`` 返回的是工资条渲染数据而不是 PDF：PDF 生成是远期能力（文档 04
§十一），先把数据结构定下来，前端可直接排版打印。
"""

from datetime import date, datetime, time as dtime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from starlette.requests import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import TenantException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.finance.driver_payroll import (
    DriverAccountOut,
    PayrollAccountRequest,
    PayrollAddTasksRequest,
    PayrollCreateRequest,
    PayrollItemCreateRequest,
    PayrollItemOut,
    PayrollItemUpdateRequest,
    PayrollListItem,
    PayrollOut,
    PayrollPayRequest,
    PayrollReasonRequest,
    PayrollTaskAdjustRequest,
    PayrollTaskLinkOut,
    PayrollUpdateRequest,
)
from app.modules.client.services.finance.driver.driver_payroll_service import (
    DriverPayrollService,
)

router = APIRouter()

_MODULE = "司机工资"
_SVC = DriverPayrollService


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


def _day_start(d: Optional[date]) -> Optional[datetime]:
    return datetime.combine(d, dtime.min) if d else None


def _day_end(d: Optional[date]) -> Optional[datetime]:
    return datetime.combine(d, dtime.max) if d else None


async def _detail(db: AsyncSession, payroll_id: int) -> dict:
    payroll = await _SVC.get_or_404(db, payroll_id)
    tasks = await _SVC.list_task_links(db, payroll_id)
    items = await _SVC.list_items(db, payroll_id)
    return PayrollOut.from_model(
        payroll, tasks=tasks, items=items, actions=_SVC.action_flags(payroll),
    ).model_dump()


# ============================================================
# 候选与账户
# ============================================================

@router.get("/candidates")
async def list_candidates(
    driverId: int = Query(description="司机 ID"),
    periodStart: Optional[date] = None,
    periodEnd: Optional[date] = None,
    limit: int = Query(default=500, ge=1, le=1000),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """该司机本周期可计提成的任务（自有车、已交车、未挂其他工资单）。"""
    rows = await _SVC.list_candidates(
        db,
        driver_id=driverId,
        period_start=_day_start(periodStart),
        period_end=_day_end(periodEnd),
        limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


@router.get("/accounts")
async def list_accounts(
    driverId: int = Query(description="司机 ID"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """发薪账户下拉（只返回可用账户，账号只给后四位）。"""
    rows = await _SVC.list_accounts(db, driverId)
    return success(data=[DriverAccountOut.from_dict(x).model_dump() for x in rows])


# ============================================================
# 工资单主体
# ============================================================

@router.get("")
async def page_payrolls(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    driverId: Optional[int] = None,
    enterpriseId: Optional[int] = None,
    status: Optional[int] = None,
    payrollModel: Optional[int] = None,
    periodStart: Optional[date] = None,
    periodEnd: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await _SVC.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        driver_id=driverId, enterprise_id=enterpriseId, status=status,
        payroll_model=payrollModel,
        period_start=_day_start(periodStart),
        period_end=_day_end(periodEnd),
    )
    return success(data={
        "list": [PayrollListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("")
@operation_log(module=_MODULE, action="新增工资单", description="生成司机工资单")
async def create_payroll(
    request: Request,
    data: PayrollCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    payroll = await _SVC.create_from_candidates(
        db,
        driver_id=data.driverId,
        period_start=_day_start(data.periodStart),
        period_end=_day_end(data.periodEnd),
        task_ids=data.taskIds,
        payroll_model=data.payrollModel,
        period_type=data.periodType,
        unit_price=data.unitPrice,
        billing_base=data.billingBase,
        account_id=data.accountId,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll.id))


@router.get("/{payroll_id}")
async def get_payroll(
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _detail(db, payroll_id))


@router.put("/{payroll_id}")
@operation_log(module=_MODULE, action="编辑工资单", description="编辑工资单表头")
async def update_payroll(
    request: Request,
    payroll_id: int,
    data: PayrollUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    payroll = await _SVC.get_or_404(db, payroll_id)
    _SVC.assert_editable(payroll)
    if data.payrollModel is not None:
        payroll.payroll_model = int(data.payrollModel)
    if data.periodType is not None:
        payroll.period_type = int(data.periodType)
    if data.remark is not None:
        payroll.remark = data.remark
    await db.flush()
    return success(data=await _detail(db, payroll_id))


@router.delete("/{payroll_id}")
@operation_log(module=_MODULE, action="删除工资单", description="删除工资单")
async def delete_payroll(
    request: Request,
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.soft_delete(db, payroll_id)
    return success()


@router.get("/{payroll_id}/payslip")
async def get_payslip(
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """工资条数据（应发项 / 扣减项 / 抵账项分区）。"""
    return success(data=await _SVC.payslip(db, payroll_id))


# ============================================================
# 任务提成行
# ============================================================

@router.get("/{payroll_id}/tasks")
async def list_tasks(
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await _SVC.get_or_404(db, payroll_id)
    rows = await _SVC.list_task_links(db, payroll_id)
    return success(data=[PayrollTaskLinkOut.from_model(x).model_dump() for x in rows])


@router.post("/{payroll_id}/tasks")
@operation_log(module=_MODULE, action="添加任务提成", description="批量添加任务提成行")
async def add_tasks(
    request: Request,
    payroll_id: int,
    data: PayrollAddTasksRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.add_tasks(
        db, payroll_id, data.taskIds,
        unit_price=data.unitPrice,
        billing_base=data.billingBase,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id))


@router.put("/{payroll_id}/tasks/{link_id}")
@operation_log(module=_MODULE, action="调整任务提成", description="调整任务提成行")
async def adjust_task(
    request: Request,
    payroll_id: int,
    link_id: int,
    data: PayrollTaskAdjustRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.adjust_task(
        db, payroll_id, link_id,
        quantity=data.quantity,
        unit_price=data.unitPrice,
        adjust_amount=data.adjustAmount,
        adjust_reason=data.adjustReason,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id))


@router.delete("/{payroll_id}/tasks/{link_id}")
@operation_log(module=_MODULE, action="移除任务提成", description="移除任务提成行")
async def remove_task(
    request: Request,
    payroll_id: int,
    link_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.remove_task(
        db, payroll_id, link_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id))


# ============================================================
# 工资项
# ============================================================

@router.get("/{payroll_id}/items")
async def list_items(
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await _SVC.get_or_404(db, payroll_id)
    rows = await _SVC.list_items(db, payroll_id)
    return success(data=[PayrollItemOut.from_model(x).model_dump() for x in rows])


@router.post("/{payroll_id}/items")
@operation_log(module=_MODULE, action="添加工资项", description="添加工资项")
async def add_item(
    request: Request,
    payroll_id: int,
    data: PayrollItemCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.add_item(
        db, payroll_id,
        item_type=data.itemType,
        amount=data.amount,
        item_name=data.itemName,
        category=data.category,
        formula=data.formula,
        sort_order=data.sortOrder,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id))


@router.put("/{payroll_id}/items/{item_id}")
@operation_log(module=_MODULE, action="编辑工资项", description="编辑工资项")
async def update_item(
    request: Request,
    payroll_id: int,
    item_id: int,
    data: PayrollItemUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.update_item(
        db, payroll_id, item_id,
        amount=data.amount,
        item_name=data.itemName,
        formula=data.formula,
        sort_order=data.sortOrder,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id))


@router.delete("/{payroll_id}/items/{item_id}")
@operation_log(module=_MODULE, action="删除工资项", description="删除工资项")
async def remove_item(
    request: Request,
    payroll_id: int,
    item_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.remove_item(db, payroll_id, item_id)
    return success(data=await _detail(db, payroll_id))


# ============================================================
# 状态流转
# ============================================================

@router.put("/{payroll_id}/account")
@operation_log(module=_MODULE, action="更换发薪账户", description="更换发薪账户")
async def update_account(
    request: Request,
    payroll_id: int,
    data: PayrollAccountRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.update_account(
        db, payroll_id, account_id=data.accountId,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id), message="已更换发薪账户")


@router.post("/{payroll_id}/approve-adjust")
@operation_log(module=_MODULE, action="审批大额调整", description="主管审批大额提成调整")
async def approve_adjust(
    request: Request,
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.approve_adjust(
        db, payroll_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id), message="大额调整已审批通过")


@router.post("/{payroll_id}/submit")
@operation_log(module=_MODULE, action="提交工资单", description="提交工资单待审批")
async def submit_payroll(
    request: Request,
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.submit(db, payroll_id, current_user.user_id)
    return success(data=await _detail(db, payroll_id), message="已提交，等待审批")


@router.post("/{payroll_id}/approve")
@operation_log(module=_MODULE, action="审批通过", description="工资单审批通过")
async def approve_payroll(
    request: Request,
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.approve(db, payroll_id, current_user.user_id)
    return success(data=await _detail(db, payroll_id), message="已审批通过，可安排发放")


@router.post("/{payroll_id}/reject")
@operation_log(module=_MODULE, action="审批拒绝", description="工资单审批拒绝")
async def reject_payroll(
    request: Request,
    payroll_id: int,
    data: PayrollReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.reject(db, payroll_id, data.reason, current_user.user_id)
    return success(data=await _detail(db, payroll_id))


@router.post("/{payroll_id}/withdraw")
@operation_log(module=_MODULE, action="退回草稿", description="工资单退回草稿")
async def withdraw_payroll(
    request: Request,
    payroll_id: int,
    data: PayrollReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.withdraw_to_draft(
        db, payroll_id, current_user.user_id, reason=data.reason,
    )
    return success(data=await _detail(db, payroll_id), message="已退回草稿")


@router.post("/{payroll_id}/pay")
@operation_log(module=_MODULE, action="登记发放", description="登记工资发放")
async def pay_payroll(
    request: Request,
    payroll_id: int,
    data: Optional[PayrollPayRequest] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    payload = data or PayrollPayRequest()
    await _SVC.pay(
        db, payroll_id,
        actual_amount=payload.actualAmount,
        paid_at=payload.paidAt,
        pay_method=payload.payMethod,
        account_id=payload.accountId,
        pay_voucher_url=payload.payVoucherUrl,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id), message="已登记发放")


@router.post("/{payroll_id}/cancel-pay")
@operation_log(module=_MODULE, action="撤销发放", description="撤销工资发放")
async def cancel_pay(
    request: Request,
    payroll_id: int,
    data: PayrollReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.cancel_payment(
        db, payroll_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id), message="已撤销发放")


@router.post("/{payroll_id}/cancel")
@operation_log(module=_MODULE, action="撤销工资单", description="撤销司机工资单")
async def cancel_payroll(
    request: Request,
    payroll_id: int,
    data: PayrollReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.cancel_payroll(
        db, payroll_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, payroll_id), message="工资单已撤销")


@router.get("/{payroll_id}/events")
async def list_events(
    payroll_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    events = await _SVC.list_events(db, payroll_id)
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
