"""承运商结算单 API

接口前缀：``/api/client/finance/carrier-settlement``

``/payable`` 是出纳台专用的只读口径（已审批未入批），单独开一个 GET 而不是让前端
拼一堆过滤参数——出纳台的语义未来会变（如加账期临近排序），收敛在后端更好改。
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
from app.modules.client.schemas.finance.carrier_settlement import (
    CarrierAccountOut,
    CarrierSettleAccountRequest,
    CarrierSettleCreateRequest,
    CarrierSettleLinkReconsRequest,
    CarrierSettleListItem,
    CarrierSettleOut,
    CarrierSettlePayRequest,
    CarrierSettleReasonRequest,
    CarrierSettleUpdateRequest,
)
from app.modules.client.services.finance.carrier.carrier_settlement_doc_service import (  # noqa: E501
    CarrierSettlementDocService,
)

router = APIRouter()

_MODULE = "承运商结算"
_SVC = CarrierSettlementDocService


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


async def _detail(db: AsyncSession, settle_id: int) -> dict:
    settle = await _SVC.get_or_404(db, settle_id)
    recons = await _SVC.list_links(db, settle_id)
    invoices = await _SVC.list_invoice_links(db, settle_id)
    return CarrierSettleOut.from_model(
        settle,
        recons=recons,
        invoices=invoices,
        actions=_SVC.action_flags(settle),
    ).model_dump()


# ============================================================
# 候选与账户
# ============================================================

@router.get("/recon-candidates")
async def list_recon_candidates(
    carrierId: int = Query(description="承运商 ID"),
    settleId: Optional[int] = Query(
        default=None, description="给已存在的结算单补挂时传入，本单已认领的额度不算冲突",
    ),
    keyword: Optional[str] = None,
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """该承运商还有未结金额的已确认对账单。"""
    rows = await _SVC.list_recon_candidates(
        db, carrier_id=carrierId, settle_id=settleId,
        keyword=keyword, limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


@router.get("/accounts")
async def list_accounts(
    carrierId: int = Query(description="承运商 ID"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """付款账户下拉（只返回启用中的，账号只给后四位）。"""
    rows = await _SVC.list_accounts(db, carrierId)
    return success(data=[CarrierAccountOut.from_dict(x).model_dump() for x in rows])


@router.get("/payable")
async def list_payable(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    carrierId: Optional[int] = None,
    dueBefore: Optional[date] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """出纳台待付池：已审批且尚未进入打款批次的结算单。"""
    rows, total = await _SVC.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        carrier_id=carrierId, due_before=dueBefore, only_payable=True,
    )
    return success(data={
        "list": [CarrierSettleListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


# ============================================================
# 结算单主体
# ============================================================

@router.get("")
async def page_settles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    carrierId: Optional[int] = None,
    enterpriseId: Optional[int] = None,
    status: Optional[int] = None,
    dueBefore: Optional[date] = None,
    invoiceMatched: Optional[int] = Query(
        default=None, ge=0, le=1, description="0 只看未收齐票 1 只看票款相符",
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await _SVC.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        carrier_id=carrierId, enterprise_id=enterpriseId, status=status,
        due_before=dueBefore, invoice_matched=invoiceMatched,
    )
    return success(data={
        "list": [CarrierSettleListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("")
@operation_log(module=_MODULE, action="新增结算单", description="按对账单生成结算单")
async def create_settle(
    request: Request,
    data: CarrierSettleCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    settle = await _SVC.create_from_recons(
        db,
        carrier_id=data.carrierId,
        recons=[x.model_dump() for x in data.recons],
        settlement_account_id=data.settlementAccountId,
        due_date=data.dueDate,
        is_offset_only=data.isOffsetOnly,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle.id))


@router.get("/{settle_id}")
async def get_settle(
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _detail(db, settle_id))


@router.put("/{settle_id}")
@operation_log(module=_MODULE, action="编辑结算单", description="编辑结算单表头")
async def update_settle(
    request: Request,
    settle_id: int,
    data: CarrierSettleUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    settle = await _SVC.get_or_404(db, settle_id)
    _SVC.assert_editable(settle)
    if data.dueDate is not None:
        settle.due_date = data.dueDate
    if data.isOffsetOnly is not None:
        settle.is_offset_only = int(data.isOffsetOnly)
    if data.remark is not None:
        settle.remark = data.remark
    await db.flush()
    return success(data=await _detail(db, settle_id))


@router.delete("/{settle_id}")
@operation_log(module=_MODULE, action="删除结算单", description="删除结算单")
async def delete_settle(
    request: Request,
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.soft_delete(db, settle_id)
    return success()


# ============================================================
# 对账单关联
# ============================================================

@router.post("/{settle_id}/recons")
@operation_log(module=_MODULE, action="关联对账单", description="结算单关联对账单")
async def link_recons(
    request: Request,
    settle_id: int,
    data: CarrierSettleLinkReconsRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.link_recons(
        db, settle_id, [x.model_dump() for x in data.recons],
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle_id))


@router.delete("/{settle_id}/recons/{link_id}")
@operation_log(module=_MODULE, action="解除对账单", description="结算单解除对账单关联")
async def unlink_recon(
    request: Request,
    settle_id: int,
    link_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.unlink_recon(
        db, settle_id, link_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle_id))


@router.put("/{settle_id}/account")
@operation_log(module=_MODULE, action="更换付款账户", description="更换结算单付款账户")
async def update_account(
    request: Request,
    settle_id: int,
    data: CarrierSettleAccountRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.update_account(
        db, settle_id,
        settlement_account_id=data.settlementAccountId,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle_id), message="已更换付款账户")


# ============================================================
# 状态流转
# ============================================================

@router.post("/{settle_id}/submit")
@operation_log(module=_MODULE, action="提交结算单", description="提交结算单待审批")
async def submit_settle(
    request: Request,
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.submit(db, settle_id, current_user.user_id)
    return success(data=await _detail(db, settle_id), message="已提交，等待审批")


@router.post("/{settle_id}/approve")
@operation_log(module=_MODULE, action="审批通过", description="结算单审批通过")
async def approve_settle(
    request: Request,
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.approve(db, settle_id, current_user.user_id)
    return success(data=await _detail(db, settle_id), message="已审批通过，可安排付款")


@router.post("/{settle_id}/reject")
@operation_log(module=_MODULE, action="审批拒绝", description="结算单审批拒绝")
async def reject_settle(
    request: Request,
    settle_id: int,
    data: CarrierSettleReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.reject(db, settle_id, data.reason, current_user.user_id)
    return success(data=await _detail(db, settle_id))


@router.post("/{settle_id}/withdraw")
@operation_log(module=_MODULE, action="退回草稿", description="结算单退回草稿")
async def withdraw_settle(
    request: Request,
    settle_id: int,
    data: CarrierSettleReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.withdraw_to_draft(
        db, settle_id, current_user.user_id, reason=data.reason,
    )
    return success(data=await _detail(db, settle_id), message="已退回草稿")


@router.post("/{settle_id}/pay")
@operation_log(module=_MODULE, action="登记付款", description="登记结算单付款")
async def pay_settle(
    request: Request,
    settle_id: int,
    data: Optional[CarrierSettlePayRequest] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    payload = data or CarrierSettlePayRequest()
    await _SVC.pay(
        db, settle_id,
        actual_amount=payload.actualAmount,
        paid_at=payload.paidAt,
        pay_method=payload.payMethod,
        pay_voucher_url=payload.payVoucherUrl,
        settlement_account_id=payload.settlementAccountId,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, settle_id), message="已登记付款")


@router.post("/{settle_id}/cancel-pay")
@operation_log(module=_MODULE, action="撤销付款", description="撤销结算单付款")
async def cancel_pay(
    request: Request,
    settle_id: int,
    data: CarrierSettleReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.cancel_payment(
        db, settle_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, settle_id), message="已撤销付款，任务成本已解锁")


@router.post("/{settle_id}/cancel")
@operation_log(module=_MODULE, action="撤销结算单", description="撤销承运商结算单")
async def cancel_settle(
    request: Request,
    settle_id: int,
    data: CarrierSettleReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.cancel_settlement(
        db, settle_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, settle_id), message="结算单已撤销")


@router.get("/{settle_id}/tasks")
async def list_tasks(
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """本单覆盖的任务 ID（详情页「锁定范围」用）。"""
    ids = await _SVC.task_ids_of(db, settle_id)
    return success(data={"taskIds": ids, "count": len(ids)})


@router.get("/{settle_id}/events")
async def list_events(
    settle_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    events = await _SVC.list_events(db, settle_id)
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
