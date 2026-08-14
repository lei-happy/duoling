"""收款单 API（出纳台到账认领）

接口前缀：``/api/client/finance/receipt``

收款单没有独立菜单，操作入口在出纳工作台，故 KPI 接口 ``/stats`` 也放在这里。
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
from app.modules.client.schemas.finance.receipt_voucher import (
    ReceiptClaimRequest,
    ReceiptCreateRequest,
    ReceiptListItem,
    ReceiptOut,
    ReceiptReasonRequest,
    ReceiptUnclaimRequest,
    ReceiptUpdateRequest,
)
from app.modules.client.services.finance.customer.receipt_voucher_service import (
    ReceiptVoucherService as Svc,
)

router = APIRouter()

_MODULE = "收款到账"


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


async def _detail(db: AsyncSession, receipt_id: int) -> dict:
    receipt = await Svc.get_or_404(db, receipt_id)
    return ReceiptOut.from_model(
        receipt,
        links=await Svc.list_links(db, receipt_id),
        actions=Svc.action_flags(receipt),
    ).model_dump()


@router.get("/stats")
async def cashier_stats(
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """出纳台 KPI：待认领笔数与金额、今日到账金额。"""
    return success(data=await Svc.cashier_stats(db))


@router.get("")
async def page_receipts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    status: Optional[int] = None,
    receivedStart: Optional[date] = None,
    receivedEnd: Optional[date] = None,
    onlyUnsettled: bool = False,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await Svc.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        customer_id=customerId, status=status,
        received_start=receivedStart, received_end=receivedEnd,
        only_unsettled=onlyUnsettled,
    )
    return success(data={
        "list": [ReceiptListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.post("")
@operation_log(module=_MODULE, action="登记到账", description="登记一笔银行到账")
async def create_receipt(
    request: Request,
    data: ReceiptCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    receipt = await Svc.create(
        db,
        amount=data.amount,
        received_at=data.receivedAt,
        receive_method=data.receiveMethod,
        customer_id=data.customerId,
        payer_name=data.payerName,
        bank_account_id=data.bankAccountId,
        bank_account_label=data.bankAccountLabel,
        bank_serial_no=data.bankSerialNo,
        voucher_url=data.voucherUrl,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, receipt.id), message="已登记到账")


@router.get("/{receipt_id}")
async def get_receipt(
    receipt_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _detail(db, receipt_id))


@router.put("/{receipt_id}")
@operation_log(module=_MODULE, action="编辑到账", description="编辑到账信息")
async def update_receipt(
    request: Request,
    receipt_id: int,
    data: ReceiptUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.update(
        db, receipt_id,
        amount=data.amount,
        received_at=data.receivedAt,
        receive_method=data.receiveMethod,
        customer_id=data.customerId,
        payer_name=data.payerName,
        bank_account_id=data.bankAccountId,
        bank_account_label=data.bankAccountLabel,
        bank_serial_no=data.bankSerialNo,
        voucher_url=data.voucherUrl,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, receipt_id))


@router.delete("/{receipt_id}")
@operation_log(module=_MODULE, action="删除到账", description="删除收款单")
async def delete_receipt(
    request: Request,
    receipt_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.assert_no_settled(db, receipt_id, action="删除")
    await Svc.soft_delete(db, receipt_id)
    return success()


# ============================================================
# 认领核销
# ============================================================

@router.get("/{receipt_id}/claim-candidates")
async def list_claim_candidates(
    receipt_id: int,
    keyword: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """可核销的结算单候选（按金额接近度排序，仅推荐不自动核销）。"""
    rows = await Svc.list_claim_candidates(
        db, receipt_id, keyword=keyword, limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


@router.get("/{receipt_id}/suggest-allocation")
async def suggest_allocation(
    receipt_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """一键按顺序填满：按到期日先后分配未核销余额。"""
    rows = await Svc.suggest_allocation(db, receipt_id)
    return success(data={"list": rows, "count": len(rows)})


@router.post("/{receipt_id}/claim")
@operation_log(module=_MODULE, action="核销到账", description="到账核销到结算单")
async def claim_receipt(
    request: Request,
    receipt_id: int,
    data: ReceiptClaimRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.claim(
        db, receipt_id, [x.model_dump() for x in data.allocations],
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, receipt_id), message="已完成核销")


@router.post("/{receipt_id}/unclaim")
@operation_log(module=_MODULE, action="撤销核销", description="撤销一条核销记录")
async def unclaim_receipt(
    request: Request,
    receipt_id: int,
    data: ReceiptUnclaimRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.unclaim(
        db, receipt_id, data.settleId,
        reason=data.reason, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, receipt_id), message="已撤销核销")


@router.post("/{receipt_id}/cancel")
@operation_log(module=_MODULE, action="撤销到账", description="撤销收款单")
async def cancel_receipt(
    request: Request,
    receipt_id: int,
    data: ReceiptReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await Svc.cancel_receipt(
        db, receipt_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, receipt_id), message="收款单已撤销")


@router.get("/{receipt_id}/events")
async def list_events(
    receipt_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    events = await Svc.list_events(db, receipt_id)
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
