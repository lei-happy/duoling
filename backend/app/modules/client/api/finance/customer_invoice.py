"""客户发票（销项）API

接口前缀：``/api/client/finance/customer-invoice``

``/pending-list`` 是待开票池（按结算单看开票缺口），与台账列表是两种看法：一个催
「该开的票还没开」，一个查「已经开过的票」。
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
from app.modules.client.schemas.finance.customer_invoice import (
    CustomerInvoiceCreateRequest,
    CustomerInvoiceListItem,
    CustomerInvoiceOut,
    CustomerInvoiceUpdateRequest,
    InvoiceIssueRequest,
    InvoiceItemsRequest,
    InvoiceLinkRequest,
    InvoiceReasonRequest,
    InvoiceSettleLinkOut,
)
from app.modules.client.services.finance.customer.customer_invoice_service import (
    CustomerInvoiceService,
)

router = APIRouter()

_MODULE = "客户发票"
_SVC = CustomerInvoiceService


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


async def _detail(
    db: AsyncSession, invoice_id: int, *, warning: Optional[str] = None,
) -> dict:
    invoice = await _SVC.get_or_404(db, invoice_id)
    items = await _SVC.list_items(db, invoice_id)
    settles = await _SVC.list_links(db, invoice_id)
    return CustomerInvoiceOut.from_model(
        invoice, items=items, settles=settles,
        actions=_SVC.action_flags(invoice), warning=warning,
    ).model_dump()


# ============================================================
# 台账与待开票池
# ============================================================

@router.get("")
async def page_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    sellerEntityId: Optional[int] = None,
    status: Optional[int] = None,
    invoiceType: Optional[int] = None,
    dateFrom: Optional[date] = None,
    dateTo: Optional[date] = None,
    onlyRed: Optional[bool] = Query(default=None, description="只看红冲票"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await _SVC.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        customer_id=customerId, seller_entity_id=sellerEntityId,
        status=status, invoice_type=invoiceType,
        date_from=dateFrom, date_to=dateTo, only_red=onlyRed,
    )
    return success(data={
        "list": [CustomerInvoiceListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/pending-list")
async def pending_list(
    customerId: Optional[int] = None,
    onlyRequired: bool = Query(
        default=True, description="只看客户要求开票的结算单",
    ),
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """待开票池：已审批 / 已收款但票还没开齐的结算单。"""
    rows = await _SVC.pending_settles(
        db, customer_id=customerId, only_required=onlyRequired, limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


@router.get("/candidates")
async def list_candidates(
    customerId: int = Query(..., description="客户 ID"),
    keyword: Optional[str] = None,
    invoiceId: Optional[int] = Query(
        default=None, description="给已有发票补挂时传入，本票已占额度不计",
    ),
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """可开票的结算单候选。"""
    rows = await _SVC.list_candidates(
        db, customer_id=customerId, keyword=keyword,
        invoice_id=invoiceId, limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


# ============================================================
# 创建与编辑
# ============================================================

@router.post("")
@operation_log(module=_MODULE, action="新建开票申请", description="按结算单创建开票申请")
async def create_invoice(
    request: Request,
    data: CustomerInvoiceCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    invoice = await _SVC.create_from_settles(
        db,
        customer_id=data.customerId,
        allocations=[x.model_dump() for x in data.allocations],
        invoice_type=data.invoiceType,
        seller_entity_id=data.sellerEntityId,
        seller_title=data.sellerTitle,
        seller_tax_no=data.sellerTaxNo,
        buyer_title=data.buyerTitle,
        buyer_tax_no=data.buyerTaxNo,
        buyer_address=data.buyerAddress,
        buyer_phone=data.buyerPhone,
        buyer_bank=data.buyerBank,
        buyer_account=data.buyerAccount,
        items=[x.model_dump() for x in data.items],
        tax_rate=data.taxRate,
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, invoice.id), message="开票申请已创建")


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _detail(db, invoice_id))


@router.put("/{invoice_id}")
@operation_log(module=_MODULE, action="编辑开票申请", description="编辑销项发票票面信息")
async def update_invoice(
    request: Request,
    invoice_id: int,
    data: CustomerInvoiceUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.update_invoice(
        db, invoice_id,
        invoice_type=data.invoiceType,
        seller_entity_id=data.sellerEntityId,
        seller_title=data.sellerTitle,
        seller_tax_no=data.sellerTaxNo,
        buyer_title=data.buyerTitle,
        buyer_tax_no=data.buyerTaxNo,
        buyer_address=data.buyerAddress,
        buyer_phone=data.buyerPhone,
        buyer_bank=data.buyerBank,
        buyer_account=data.buyerAccount,
        tax_rate=data.taxRate,
        items=(
            [x.model_dump() for x in data.items]
            if data.items is not None else None
        ),
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, invoice_id))


@router.delete("/{invoice_id}")
@operation_log(module=_MODULE, action="删除开票申请", description="删除销项发票草稿")
async def delete_invoice(
    request: Request,
    invoice_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.soft_delete(db, invoice_id)
    return success()


# ============================================================
# 关联结算单与行明细
# ============================================================

@router.get("/{invoice_id}/settles")
async def list_settles(
    invoice_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await _SVC.get_or_404(db, invoice_id)
    rows = await _SVC.list_links(db, invoice_id)
    return success(data=[
        InvoiceSettleLinkOut.from_model(x).model_dump() for x in rows
    ])


@router.post("/{invoice_id}/settles")
@operation_log(module=_MODULE, action="关联结算单", description="发票关联结算单并分配金额")
async def link_settles(
    request: Request,
    invoice_id: int,
    data: InvoiceLinkRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.link_settles(
        db, invoice_id, [x.model_dump() for x in data.allocations],
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, invoice_id), message="已更新关联结算单")


@router.delete("/{invoice_id}/settles/{link_id}")
@operation_log(module=_MODULE, action="解除关联", description="解除发票与结算单的关联")
async def unlink_settle(
    request: Request,
    invoice_id: int,
    link_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.unlink_settle(
        db, invoice_id, link_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, invoice_id), message="已解除关联")


@router.put("/{invoice_id}/items")
@operation_log(module=_MODULE, action="维护开票明细", description="整体替换开票行明细")
async def replace_items(
    request: Request,
    invoice_id: int,
    data: InvoiceItemsRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.replace_items(db, invoice_id, [x.model_dump() for x in data.items])
    return success(data=await _detail(db, invoice_id), message="已更新开票明细")


# ============================================================
# 状态流转
# ============================================================

@router.post("/{invoice_id}/submit")
@operation_log(module=_MODULE, action="提交开票申请", description="提交销项开票申请")
async def submit_invoice(
    request: Request,
    invoice_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.submit_apply(db, invoice_id, current_user.user_id)
    return success(data=await _detail(db, invoice_id), message="开票申请已提交")


@router.post("/{invoice_id}/withdraw")
@operation_log(module=_MODULE, action="退回草稿", description="开票申请退回草稿")
async def withdraw_invoice(
    request: Request,
    invoice_id: int,
    data: InvoiceReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.withdraw_apply(
        db, invoice_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, invoice_id), message="已退回草稿")


@router.post("/{invoice_id}/issue")
@operation_log(module=_MODULE, action="登记开票", description="登记开票结果并锁定结算单")
async def issue_invoice(
    request: Request,
    invoice_id: int,
    data: InvoiceIssueRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.issue(
        db, invoice_id,
        invoice_no=data.invoiceNo,
        invoice_code=data.invoiceCode,
        invoice_date=data.invoiceDate,
        pdf_url=data.pdfUrl,
        operator_id=current_user.user_id,
    )
    return success(
        data=await _detail(db, invoice_id),
        message="已登记开票，关联结算单已锁定",
    )


@router.post("/{invoice_id}/void")
@operation_log(module=_MODULE, action="作废发票", description="作废销项发票")
async def void_invoice(
    request: Request,
    invoice_id: int,
    data: InvoiceReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    _, warn = await _SVC.void(db, invoice_id, data.reason, current_user.user_id)
    return success(
        data=await _detail(db, invoice_id, warning=warn),
        message=(warn or "发票已作废，结算单已解锁并回退开票进度"),
    )


@router.post("/{invoice_id}/red-flush")
@operation_log(module=_MODULE, action="红冲发票", description="红冲销项发票并生成红字票")
async def red_flush_invoice(
    request: Request,
    invoice_id: int,
    data: InvoiceReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    _, red = await _SVC.red_flush(
        db, invoice_id, data.reason, current_user.user_id,
    )
    detail = await _detail(db, invoice_id)
    detail["redInvoice"] = CustomerInvoiceListItem.from_model(red).model_dump()
    return success(data=detail, message=f"已红冲，红字票 {red.doc_no}")


@router.post("/{invoice_id}/cancel")
@operation_log(module=_MODULE, action="撤销开票申请", description="撤销销项开票申请")
async def cancel_invoice(
    request: Request,
    invoice_id: int,
    data: InvoiceReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.cancel_invoice(
        db, invoice_id, data.reason, current_user.user_id,
    )
    return success(data=await _detail(db, invoice_id), message="已撤销开票申请")


@router.get("/{invoice_id}/events")
async def list_events(
    invoice_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    events = await _SVC.list_events(db, invoice_id)
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
