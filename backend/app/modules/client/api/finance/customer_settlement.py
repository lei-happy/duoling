"""客户结算单 API

接口前缀：``/api/client/finance/customer-settlement``
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import BizException, TenantException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.finance.customer_settlement import (
    SettleCreateRequest,
    SettleLinkReconsRequest,
    SettleListItem,
    SettleOut,
    SettleReasonRequest,
    SettleReceiveRequest,
    SettleUpdateRequest,
)
from app.modules.client.services.finance.customer.customer_settlement_service import (
    CustomerSettlementService as Svc,
)

router = APIRouter()

_MODULE = "客户结算"


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


async def _detail(db: AsyncSession, settle_id: int) -> dict:
    settle = await Svc.get_or_404(db, settle_id)
    return SettleOut.from_model(
        settle,
        recons=await Svc.list_links(db, settle_id),
        receipts=await Svc.list_receipt_links(db, settle_id),
        actions=Svc.action_flags(settle),
    ).model_dump()


@router.get("/recon-candidates")
async def list_recon_candidates(
    customerId: int = Query(description="客户 ID"),
    settleId: Optional[int] = Query(
        default=None, description="编辑既有结算单时传入，本单已认领金额算可用额度"
    ),
    keyword: Optional[str] = None,
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """该客户还有未结金额的已确认对账单。"""
    rows = await Svc.list_recon_candidates(
        db, customer_id=customerId, settle_id=settleId,
        keyword=keyword, limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


@router.get("")
async def page_settlements(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    enterpriseId: Optional[int] = None,
    status: Optional[int] = None,
    dueBefore: Optional[date] = None,
    onlyUnreceived: bool = False,
    invoiceRequired: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await Svc.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        customer_id=customerId, enterprise_id=enterpriseId, status=status,
        due_before=dueBefore, only_unreceived=onlyUnreceived,
        invoice_required=invoiceRequired,
    )
    return success(data={
        "list": [SettleListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("")
@operation_log(module=_MODULE, action="新增结算单", description="生成客户结算单")
async def create_settlement(
    request: Request,
    data: SettleCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    settle = await Svc.create_from_recons(
        db,
        customer_id=data.customerId,
        recons=[x.model_dump() for x in data.recons],
        due_date=data.dueDate,
        invoice_required=data.invoiceRequired,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle.id))


@router.get("/{settle_id}")
async def get_settlement(
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _detail(db, settle_id))


@router.put("/{settle_id}")
@operation_log(module=_MODULE, action="编辑结算单", description="编辑结算单表头")
async def update_settlement(
    request: Request,
    settle_id: int,
    data: SettleUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    settle = await Svc.get_or_404(db, settle_id)
    Svc.assert_editable(settle)
    if data.dueDate is not None:
        settle.due_date = data.dueDate
    if data.invoiceRequired is not None:
        settle.invoice_required = data.invoiceRequired
    if data.remark is not None:
        settle.remark = data.remark
    await db.flush()
    return success(data=await _detail(db, settle_id))


@router.delete("/{settle_id}")
@operation_log(module=_MODULE, action="删除结算单", description="删除结算单")
async def delete_settlement(
    request: Request,
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    if await Svc.settled_amount_of(db, settle_id) > 0:
        raise BizException("本单已有到账核销记录，请先在出纳台撤销核销")
    await Svc.soft_delete(db, settle_id)
    return success()


# ============================================================
# 关联对账单
# ============================================================

@router.post("/{settle_id}/recons")
@operation_log(module=_MODULE, action="关联对账单", description="结算单关联对账单")
async def link_recons(
    request: Request,
    settle_id: int,
    data: SettleLinkReconsRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.link_recons(
        db, settle_id, [x.model_dump() for x in data.recons],
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle_id))


@router.delete("/{settle_id}/recons/{link_id}")
@operation_log(module=_MODULE, action="解除对账单关联", description="解除结算单与对账单关联")
async def unlink_recon(
    request: Request,
    settle_id: int,
    link_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.unlink_recon(
        db, settle_id, link_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle_id))


# ============================================================
# 状态流转
# ============================================================

@router.post("/{settle_id}/submit")
@operation_log(module=_MODULE, action="提交审批", description="结算单提交审批")
async def submit_settlement(
    request: Request,
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.submit(db, settle_id, current_user.user_id)
    return success(data=await _detail(db, settle_id), message="已提交审批")


@router.post("/{settle_id}/approve")
@operation_log(module=_MODULE, action="审批通过", description="结算单审批通过")
async def approve_settlement(
    request: Request,
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.approve(db, settle_id, current_user.user_id)
    return success(data=await _detail(db, settle_id), message="已审批通过")


@router.post("/{settle_id}/reject")
@operation_log(module=_MODULE, action="审批拒绝", description="结算单审批拒绝")
async def reject_settlement(
    request: Request,
    settle_id: int,
    data: SettleReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.reject(db, settle_id, data.reason, current_user.user_id)
    return success(data=await _detail(db, settle_id))


@router.post("/{settle_id}/withdraw")
@operation_log(module=_MODULE, action="退回草稿", description="结算单退回草稿")
async def withdraw_settlement(
    request: Request,
    settle_id: int,
    data: SettleReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.withdraw_to_draft(
        db, settle_id, current_user.user_id, reason=data.reason,
    )
    return success(data=await _detail(db, settle_id), message="已退回草稿")


@router.post("/{settle_id}/receive")
@operation_log(module=_MODULE, action="登记收款", description="结算单登记收款并锁定运单")
async def receive_settlement(
    request: Request,
    settle_id: int,
    data: SettleReceiveRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.receive(
        db, settle_id,
        actual_amount=data.actualAmount,
        received_at=data.receivedAt,
        receive_method=data.receiveMethod,
        received_account_id=data.receivedAccountId,
        received_account_label=data.receivedAccountLabel,
        voucher_url=data.voucherUrl,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle_id), message="已登记收款")


@router.post("/{settle_id}/cancel-receive")
@operation_log(module=_MODULE, action="撤销收款", description="结算单撤销收款并解锁运单")
async def cancel_receive(
    request: Request,
    settle_id: int,
    data: SettleReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.cancel_receive(
        db, settle_id, data.reason, current_user.user_id,
    )
    return success(
        data=await _detail(db, settle_id), message="已撤销收款，关联运单已解锁",
    )


@router.post("/{settle_id}/cancel")
@operation_log(module=_MODULE, action="撤销结算单", description="撤销客户结算单")
async def cancel_settlement(
    request: Request,
    settle_id: int,
    data: SettleReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.cancel_settlement(
        db, settle_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, settle_id), message="结算单已撤销")


@router.get("/{settle_id}/events")
async def list_events(
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    events = await Svc.list_events(db, settle_id)
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
