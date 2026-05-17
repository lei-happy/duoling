"""
企业端任务单财务费用单 API

接口前缀：/business/task-finance
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import TenantException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.task.task_finance_doc import (
    TaskFinanceDocBatchActionRequest,
    TaskFinanceDocCancelRequest,
    TaskFinanceDocCreate,
    TaskFinanceDocListItem,
    TaskFinanceDocOut,
    TaskFinanceDocPayRequest,
    TaskFinanceDocUpdate,
)
from app.modules.client.services.task.task_finance_service import (
    TaskFinanceService,
)
from app.modules.client.services.task.task_service import TaskService

router = APIRouter()


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


# ============================================================
# 跨任务单的费用单中心
# ============================================================

@router.get("")
async def page_docs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    taskId: Optional[int] = None,
    docType: Optional[int] = None,
    status: Optional[int] = None,
    payeeType: Optional[int] = None,
    createdAtStart: Optional[date] = None,
    createdAtEnd: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    docs, total = await TaskFinanceService.page_docs(
        db,
        page=page, page_size=page_size, keyword=keyword,
        task_id=taskId, doc_type=docType, status=status, payee_type=payeeType,
        created_at_start=createdAtStart, created_at_end=createdAtEnd,
    )
    # 一次查询所属任务单 task_no，回填到列表行
    from app.modules.client.models.task.task import Task
    from sqlalchemy import select
    task_ids = list({int(d.task_id) for d in docs})
    task_no_map: dict[int, str] = {}
    if task_ids:
        r = await db.execute(
            select(Task.id, Task.task_no).where(Task.id.in_(task_ids))
        )
        for tid, tno in r.all():
            task_no_map[int(tid)] = tno

    rows = [TaskFinanceDocListItem(
        id=d.id,
        taskId=d.task_id,
        taskNo=task_no_map.get(int(d.task_id)),
        docNo=d.doc_no,
        docType=d.doc_type,
        isFinal=d.is_final,
        payeeType=d.payee_type,
        payeeName=d.payee_name,
        plannedAmount=float(d.planned_amount or 0),
        actualAmount=float(d.actual_amount) if d.actual_amount is not None else None,
        payMethod=d.pay_method,
        status=d.status,
        createdAt=d.created_at,
        plannedPayTime=d.planned_pay_time,
        actualPayTime=d.actual_pay_time,
    ).model_dump() for d in docs]

    return success(data={
        "list": rows,
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/workbench-stats")
async def get_workbench_stats(
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """费用工作台 KPI：草稿/待审批/待支付计数 + 待审批/待支付/今日已支付金额"""
    stats = await TaskFinanceService.workbench_stats(db)
    return success(data=stats)


@router.post("/batch-action")
@operation_log(module="任务单财务", action="批量动作", description="批量审批/支付/撤销/提交")
async def batch_action(
    request: Request,
    data: TaskFinanceDocBatchActionRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    pay_payload = None
    if data.action == "pay":
        if (
            data.actualAmount is None
            or data.payMethod is None
            or data.actualPayTime is None
        ):
            from app.common.exceptions import BizException
            raise BizException("批量支付必须传入 actualAmount / payMethod / actualPayTime")
        pay_payload = TaskFinanceDocPayRequest(
            actualAmount=data.actualAmount,
            payMethod=data.payMethod,
            actualPayTime=data.actualPayTime,
            payVoucherUrl=data.payVoucherUrl,
            remark=data.remark,
        )
    result = await TaskFinanceService.batch_action(
        db,
        ids=data.ids,
        action=data.action,
        current_user_id=current_user.user_id,
        pay_payload=pay_payload,
        cancel_reason=data.reason,
    )
    return success(data=result)


@router.get("/by-task/{task_id}")
async def list_docs_of_task(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    docs = await TaskFinanceService.list_docs_by_task(db, task_id)
    out = []
    for d in docs:
        items = await TaskFinanceService.list_items(db, d.id)
        out.append(TaskFinanceDocOut.from_model(d, items=items).model_dump())
    return success(data=out)


@router.post("/by-task/{task_id}")
@operation_log(module="任务单财务", action="新增费用单", description="任务单新增费用单")
async def create_doc(
    request: Request,
    task_id: int,
    data: TaskFinanceDocCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    doc = await TaskFinanceService.create_doc(
        db, task_id, data, current_user_id=current_user.user_id,
    )
    items = await TaskFinanceService.list_items(db, doc.id)
    return success(data=TaskFinanceDocOut.from_model(doc, items=items).model_dump())


@router.get("/{doc_id}")
async def get_doc(
    doc_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    doc = await TaskFinanceService.get_or_404(db, doc_id)
    items = await TaskFinanceService.list_items(db, doc.id)
    return success(data=TaskFinanceDocOut.from_model(doc, items=items).model_dump())


@router.put("/{doc_id}")
@operation_log(module="任务单财务", action="编辑费用单", description="编辑费用单")
async def update_doc(
    request: Request,
    doc_id: int,
    data: TaskFinanceDocUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    doc = await TaskFinanceService.update_doc(db, doc_id, data)
    items = await TaskFinanceService.list_items(db, doc.id)
    return success(data=TaskFinanceDocOut.from_model(doc, items=items).model_dump())


@router.delete("/{doc_id}")
@operation_log(module="任务单财务", action="删除费用单", description="删除费用单")
async def delete_doc(
    request: Request,
    doc_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await TaskFinanceService.delete_doc(db, doc_id)
    return success()


@router.post("/{doc_id}/submit")
@operation_log(module="任务单财务", action="提交审批", description="费用单提交审批")
async def submit_doc(
    request: Request,
    doc_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    doc = await TaskFinanceService.submit_doc(db, doc_id, current_user.user_id)
    items = await TaskFinanceService.list_items(db, doc.id)
    return success(data=TaskFinanceDocOut.from_model(doc, items=items).model_dump())


@router.post("/{doc_id}/approve")
@operation_log(module="任务单财务", action="审批通过", description="费用单审批通过")
async def approve_doc(
    request: Request,
    doc_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    doc = await TaskFinanceService.approve_doc(db, doc_id, current_user.user_id)
    items = await TaskFinanceService.list_items(db, doc.id)
    return success(data=TaskFinanceDocOut.from_model(doc, items=items).model_dump())


@router.post("/{doc_id}/pay")
@operation_log(module="任务单财务", action="标记已支付", description="费用单标记已支付")
async def pay_doc(
    request: Request,
    doc_id: int,
    data: TaskFinanceDocPayRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    doc = await TaskFinanceService.pay_doc(
        db, doc_id, data, current_user.user_id
    )
    items = await TaskFinanceService.list_items(db, doc.id)
    return success(data=TaskFinanceDocOut.from_model(doc, items=items).model_dump())


@router.post("/{doc_id}/cancel")
@operation_log(module="任务单财务", action="撤销", description="撤销费用单")
async def cancel_doc(
    request: Request,
    doc_id: int,
    data: Optional[TaskFinanceDocCancelRequest] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    payload = data or TaskFinanceDocCancelRequest()
    doc = await TaskFinanceService.cancel_doc(db, doc_id, payload)
    items = await TaskFinanceService.list_items(db, doc.id)
    return success(data=TaskFinanceDocOut.from_model(doc, items=items).model_dump())
