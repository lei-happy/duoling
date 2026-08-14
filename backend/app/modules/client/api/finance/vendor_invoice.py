"""进项发票 API

接口前缀：``/api/client/finance/vendor-invoice``

``/deduct-summary`` 与 ``/pending-list`` 放在同一棵路由树下但语义不同：前者是抵扣底稿
（按税期汇总票），后者是催票清单（按结算单看缺口），两者都属于「进项票管理」这件事。
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
from app.modules.client.schemas.finance.vendor_invoice import (
    DeductSummaryOut,
    InvoiceMatchRequest,
    InvoiceReasonRequest,
    InvoiceSettleLinkOut,
    VendorInvoiceCreateRequest,
    VendorInvoiceListItem,
    VendorInvoiceOut,
    VendorInvoiceUpdateRequest,
)
from app.modules.client.services.finance.invoice.vendor_invoice_service import (
    VendorInvoiceService,
)

router = APIRouter()

_MODULE = "进项发票"
_SVC = VendorInvoiceService


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


async def _detail(db: AsyncSession, invoice_id: int) -> dict:
    invoice = await _SVC.get_or_404(db, invoice_id)
    items = await _SVC.list_items(db, invoice_id)
    settles = await _SVC.list_links(db, invoice_id)
    return VendorInvoiceOut.from_model(
        invoice, items=items, settles=settles,
        actions=_SVC.action_flags(invoice),
    ).model_dump()


# ============================================================
# 台账与汇总
# ============================================================

@router.get("")
async def page_invoices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    vendorId: Optional[int] = None,
    vendorType: Optional[int] = None,
    buyerEntityId: Optional[int] = None,
    status: Optional[int] = None,
    invoiceType: Optional[int] = None,
    deductible: Optional[int] = Query(default=None, ge=0, le=1),
    deductPeriod: Optional[str] = None,
    dateFrom: Optional[date] = None,
    dateTo: Optional[date] = None,
    onlyUnsettled: bool = Query(
        default=False, description="只看还有未核销金额的票",
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await _SVC.page_list(
        db,
        page=page, page_size=page_size, keyword=keyword,
        vendor_id=vendorId, vendor_type=vendorType,
        buyer_entity_id=buyerEntityId, status=status,
        invoice_type=invoiceType, deductible=deductible,
        deduct_period=deductPeriod, date_from=dateFrom, date_to=dateTo,
        only_unsettled=onlyUnsettled,
    )
    return success(data={
        "list": [VendorInvoiceListItem.from_model(m).model_dump() for m in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/deduct-summary")
async def deduct_summary(
    groupBy: str = Query(
        default="period", description="period-税期 entity-主体 rate-税率 deductible-可抵扣性",
    ),
    buyerEntityId: Optional[int] = None,
    periodFrom: Optional[str] = None,
    periodTo: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """抵扣台账汇总（申报底稿数据）。"""
    rows = await _SVC.deduct_summary(
        db,
        group_by=groupBy,
        buyer_entity_id=buyerEntityId,
        period_from=periodFrom,
        period_to=periodTo,
    )
    return success(data={
        "list": [DeductSummaryOut(**x).model_dump() for x in rows],
        "count": len(rows),
    })


@router.get("/pending-list")
async def pending_list(
    carrierId: Optional[int] = None,
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """待收票池：已付款但没收齐票的结算单，按已付款天数倒序。"""
    rows = await _SVC.pending_settles(db, carrier_id=carrierId, limit=limit)
    return success(data={"list": rows, "count": len(rows)})


# ============================================================
# 登记与编辑
# ============================================================

@router.post("")
@operation_log(module=_MODULE, action="登记收票", description="登记进项发票")
async def register_invoice(
    request: Request,
    data: VendorInvoiceCreateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    invoice = await _SVC.register(
        db,
        invoice_no=data.invoiceNo,
        invoice_code=data.invoiceCode,
        invoice_type=data.invoiceType,
        invoice_date=data.invoiceDate,
        received_at=data.receivedAt,
        vendor_type=data.vendorType,
        vendor_id=data.vendorId,
        seller_title=data.sellerTitle,
        seller_tax_no=data.sellerTaxNo,
        buyer_entity_id=data.buyerEntityId,
        buyer_title=data.buyerTitle,
        buyer_tax_no=data.buyerTaxNo,
        amount_excl_tax=data.amountExclTax,
        tax_amount=data.taxAmount,
        amount_incl_tax=data.amountInclTax,
        tax_rate=data.taxRate,
        deductible=data.deductible,
        deduct_period=data.deductPeriod,
        attachment_url=data.attachmentUrl,
        items=[x.model_dump() for x in data.items],
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, invoice.id), message="已登记发票")


@router.get("/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    return success(data=await _detail(db, invoice_id))


@router.put("/{invoice_id}")
@operation_log(module=_MODULE, action="编辑发票", description="编辑进项发票票面信息")
async def update_invoice(
    request: Request,
    invoice_id: int,
    data: VendorInvoiceUpdateRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.update_invoice(
        db, invoice_id,
        invoice_type=data.invoiceType,
        invoice_date=data.invoiceDate,
        seller_title=data.sellerTitle,
        seller_tax_no=data.sellerTaxNo,
        buyer_entity_id=data.buyerEntityId,
        buyer_title=data.buyerTitle,
        buyer_tax_no=data.buyerTaxNo,
        amount_excl_tax=data.amountExclTax,
        tax_amount=data.taxAmount,
        amount_incl_tax=data.amountInclTax,
        tax_rate=data.taxRate,
        deductible=data.deductible,
        deduct_period=data.deductPeriod,
        attachment_url=data.attachmentUrl,
        items=(
            [x.model_dump() for x in data.items]
            if data.items is not None else None
        ),
        remark=data.remark,
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, invoice_id))


@router.delete("/{invoice_id}")
@operation_log(module=_MODULE, action="删除发票", description="删除进项发票登记")
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
# 核销
# ============================================================

@router.get("/{invoice_id}/candidates")
async def list_candidates(
    invoice_id: int,
    keyword: Optional[str] = None,
    limit: int = Query(default=200, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """可核销的承运商结算单（同承运商、还有收票缺口）。"""
    rows = await _SVC.list_candidates(
        db, invoice_id, keyword=keyword, limit=limit,
    )
    return success(data={"list": rows, "count": len(rows)})


@router.post("/{invoice_id}/match")
@operation_log(module=_MODULE, action="核销发票", description="进项票核销到结算单")
async def match_invoice(
    request: Request,
    invoice_id: int,
    data: InvoiceMatchRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.match(
        db, invoice_id, [x.model_dump() for x in data.allocations],
        operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, invoice_id), message="已完成核销")


@router.get("/{invoice_id}/match")
async def list_match(
    invoice_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await _SVC.get_or_404(db, invoice_id)
    rows = await _SVC.list_links(db, invoice_id)
    return success(data=[InvoiceSettleLinkOut.from_model(x).model_dump() for x in rows])


@router.delete("/{invoice_id}/match/{link_id}")
@operation_log(module=_MODULE, action="撤销核销", description="撤销一条进项票核销")
async def unmatch_invoice(
    request: Request,
    invoice_id: int,
    link_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await _SVC.unmatch(
        db, invoice_id, link_id, operator_id=current_user.user_id,
    )
    return success(data=await _detail(db, invoice_id), message="已撤销核销")


# ============================================================
# 作废与撤销
# ============================================================

@router.post("/{invoice_id}/void")
@operation_log(module=_MODULE, action="作废发票", description="作废或退回进项发票")
async def void_invoice(
    request: Request,
    invoice_id: int,
    data: InvoiceReasonRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    _, warn = await _SVC.void(
        db, invoice_id, data.reason, current_user.user_id,
    )
    detail = await _detail(db, invoice_id)
    detail["deductWarning"] = warn
    return success(
        data=detail,
        message=(warn or "发票已作废，相关结算单的收票进度已回退"),
    )


@router.post("/{invoice_id}/cancel")
@operation_log(module=_MODULE, action="撤销登记", description="撤销进项发票登记")
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
    return success(data=await _detail(db, invoice_id), message="已撤销登记")


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
