"""进项发票 Service（文档 11）

收票是**被动登记**，不是审批流：票拿到手就是客观事实，故状态集只有
``{0 草稿, 3 已收票, 4 已撤销, 5 已核销, 9 已作废}``，没有待审批与已审批。

三条口径值得单独记住，因为它们是这块最容易写错的地方：

1. **金额自洽**：``不含税 + 税额 = 含税``（容差一分）。多税率票以行明细为准，主表
   三个金额由行汇总回填、税率留空。
2. **核销不许超额**：既不能超过票面含税金额，也不能让某张结算单的已收票额超过它的
   应付金额。后者尤其重要——票超额说明承运商多开了票，放过去就是税务风险。
3. **作废全额回退**：票作废时核销明细一并失效，并回写每张受影响结算单的收票进度。
   漏了回写，结算单会永远显示「票款相符」，催票池里再也看不到它。
"""

from datetime import date as ddate, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.carrier_settlement_doc import (
    CarrierSettlementDoc,
)
from app.modules.client.models.finance.vendor_invoice import (
    VENDOR_INVOICE_DOC_KIND,
    VendorInvoice,
    VendorInvoiceItem,
    VendorInvoiceSettleLink,
)
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.services.finance.base.constants import (
    FinanceDirection,
    InvoiceType,
    VendorType,
)
from app.modules.client.services.finance.base.finance_doc_event_writer import (
    FinanceDocEventWriter,
    FinanceEventType,
)
from app.modules.client.services.finance.base.finance_doc_service import (
    FinanceDocService,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    FIN_CANCELLED,
    FIN_DRAFT,
    FIN_PAID,
    FIN_REVIEWED,
    FIN_SETTLED,
    FIN_VOIDED,
    label as status_label,
)
from app.modules.client.services.finance.carrier.carrier_settlement_doc_service import (  # noqa: E501
    CarrierSettlementDocService,
)

_CENT = Decimal("0.01")
AMOUNT_TOLERANCE = Decimal("0.01")
# 已收票（含部分核销）用通用 3；票面全额核销用 5
INVOICE_RECEIVED = FIN_PAID


class VendorInvoiceService(FinanceDocService):
    """进项发票"""

    model = VendorInvoice
    doc_kind = VENDOR_INVOICE_DOC_KIND
    doc_label = "进项发票"
    doc_no_prefix = "VI"
    direction = FinanceDirection.PAY
    editable_statuses = (FIN_DRAFT, INVOICE_RECEIVED)

    # ------------------------------------------------------------------
    # 登记与编辑
    # ------------------------------------------------------------------
    @classmethod
    async def register(
        cls,
        db: AsyncSession,
        *,
        invoice_no: str,
        amount_incl_tax: Optional[Decimal] = None,
        amount_excl_tax: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None,
        tax_rate: Optional[Decimal] = None,
        invoice_code: Optional[str] = None,
        invoice_type: int = InvoiceType.SPECIAL,
        invoice_date: Optional[ddate] = None,
        received_at: Optional[datetime] = None,
        vendor_type: int = VendorType.CARRIER,
        vendor_id: Optional[int] = None,
        seller_title: Optional[str] = None,
        seller_tax_no: Optional[str] = None,
        buyer_entity_id: Optional[int] = None,
        buyer_title: Optional[str] = None,
        buyer_tax_no: Optional[str] = None,
        deductible: Optional[int] = None,
        deduct_period: Optional[str] = None,
        attachment_url: Optional[str] = None,
        items: Optional[Sequence[dict]] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> VendorInvoice:
        """登记一张收到的发票。

        金额三项任填两项即可，第三项由服务端推算；三项都给则校验自洽。多税率票传
        ``items``，此时主表金额一律以行汇总为准，避免出现「表头与明细对不上」。
        """
        no = (invoice_no or "").strip()
        if not no:
            raise BizException("请填写发票号码")
        code = (invoice_code or "").strip() or None
        await cls._assert_no_duplicate(db, code, no)

        vendor_name = None
        if int(vendor_type) == VendorType.CARRIER:
            if not vendor_id:
                raise BizException("承运商发票需要选择对应的承运商")
            carrier = await cls._get_carrier_or_404(db, int(vendor_id))
            vendor_name = carrier.carrier_name
            seller_title = seller_title or carrier.carrier_name
        elif not (seller_title or "").strip():
            raise BizException("请填写票面上的销方名称")

        rows = list(items or [])
        if rows:
            excl, tax, incl = cls._sum_items(rows)
            rate = None
        else:
            excl, tax, incl = cls._resolve_amounts(
                amount_excl_tax, tax_amount, amount_incl_tax,
            )
            rate = (
                Decimal(str(tax_rate)) if tax_rate is not None else None
            )

        deduct = (
            int(deductible)
            if deductible is not None
            else (1 if int(invoice_type) in InvoiceType.DEDUCTIBLE_DEFAULT else 0)
        )
        invoice = VendorInvoice(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.PAY,
            status=FIN_DRAFT,
            vendor_type=int(vendor_type),
            vendor_id=vendor_id,
            vendor_name=vendor_name,
            seller_title=seller_title,
            seller_tax_no=seller_tax_no,
            buyer_entity_id=buyer_entity_id,
            buyer_title=buyer_title,
            buyer_tax_no=buyer_tax_no,
            invoice_type=int(invoice_type),
            invoice_no=no,
            invoice_code=code,
            invoice_date=invoice_date,
            received_at=received_at or datetime.now(),
            amount_excl_tax=excl,
            tax_rate=rate,
            tax_amount=tax,
            amount_incl_tax=incl,
            is_multi_rate=1 if rows else 0,
            planned_amount=incl,
            settled_amount=Decimal("0"),
            unsettled_amount=incl,
            deductible=deduct,
            deduct_period=_norm_period(deduct_period),
            attachment_url=attachment_url,
            created_by=operator_id,
            remark=remark,
            dedup_key=VendorInvoice.build_dedup_key(code, no),
        )
        db.add(invoice)
        await db.flush()

        for row in rows:
            db.add(VendorInvoiceItem(
                invoice_id=invoice.id,
                item_name=row.get("itemName"),
                tax_rate=_dec(row.get("taxRate")),
                amount_excl_tax=_money(_dec(row.get("amountExclTax")) or 0),
                tax_amount=_money(_dec(row.get("taxAmount")) or 0),
                amount_incl_tax=_money(_dec(row.get("amountInclTax")) or 0),
                remark=row.get("remark"),
            ))
        if rows:
            await db.flush()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=invoice.id,
            event_type=FinanceEventType.INVOICE_IN,
            to_status=FIN_DRAFT,
            direction=FinanceDirection.PAY,
            occurred_amount=incl,
            operator_id=operator_id,
            reason=f"登记进项发票 {no}",
            payload_snapshot={
                "invoiceNo": no,
                "invoiceCode": code,
                "amountInclTax": float(incl),
                "taxAmount": float(tax),
            },
        )
        await db.flush()
        return invoice

    @classmethod
    async def update_invoice(
        cls,
        db: AsyncSession,
        invoice_id: int,
        *,
        amount_incl_tax: Optional[Decimal] = None,
        amount_excl_tax: Optional[Decimal] = None,
        tax_amount: Optional[Decimal] = None,
        tax_rate: Optional[Decimal] = None,
        invoice_type: Optional[int] = None,
        invoice_date: Optional[ddate] = None,
        buyer_entity_id: Optional[int] = None,
        buyer_title: Optional[str] = None,
        buyer_tax_no: Optional[str] = None,
        seller_title: Optional[str] = None,
        seller_tax_no: Optional[str] = None,
        deductible: Optional[int] = None,
        deduct_period: Optional[str] = None,
        attachment_url: Optional[str] = None,
        items: Optional[Sequence[dict]] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> VendorInvoice:
        """编辑票面信息。已核销过的票不允许改金额（否则核销额可能反超票面）。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) in (FIN_CANCELLED, FIN_VOIDED):
            raise BizException(
                f"发票当前是「{cls.status_text(invoice)}」，不能再修改"
            )
        settled = Decimal(str(invoice.settled_amount or 0))
        amount_touched = any(
            x is not None
            for x in (amount_incl_tax, amount_excl_tax, tax_amount)
        ) or items is not None
        if amount_touched and settled > 0:
            raise BizException(
                "本票已核销过，不能改金额；请先撤销核销再修改票面金额"
            )

        if items is not None:
            await cls._replace_items(db, invoice_id, items)
            rows = list(items)
            if rows:
                excl, tax, incl = cls._sum_items(rows)
                invoice.is_multi_rate = 1
                invoice.tax_rate = None
            else:
                excl, tax, incl = cls._resolve_amounts(
                    amount_excl_tax, tax_amount, amount_incl_tax,
                )
                invoice.is_multi_rate = 0
            invoice.amount_excl_tax = excl
            invoice.tax_amount = tax
            invoice.amount_incl_tax = incl
            invoice.planned_amount = incl
        elif amount_touched:
            excl, tax, incl = cls._resolve_amounts(
                amount_excl_tax if amount_excl_tax is not None
                else invoice.amount_excl_tax,
                tax_amount if tax_amount is not None else invoice.tax_amount,
                amount_incl_tax,
            )
            invoice.amount_excl_tax = excl
            invoice.tax_amount = tax
            invoice.amount_incl_tax = incl
            invoice.planned_amount = incl

        if tax_rate is not None and not int(invoice.is_multi_rate or 0):
            invoice.tax_rate = Decimal(str(tax_rate))
        if invoice_type is not None:
            invoice.invoice_type = int(invoice_type)
        if invoice_date is not None:
            invoice.invoice_date = invoice_date
        if buyer_entity_id is not None:
            invoice.buyer_entity_id = buyer_entity_id
        if buyer_title is not None:
            invoice.buyer_title = buyer_title
        if buyer_tax_no is not None:
            invoice.buyer_tax_no = buyer_tax_no
        if seller_title is not None:
            invoice.seller_title = seller_title
        if seller_tax_no is not None:
            invoice.seller_tax_no = seller_tax_no
        if deductible is not None:
            invoice.deductible = int(deductible)
        if deduct_period is not None:
            invoice.deduct_period = _norm_period(deduct_period)
        if attachment_url is not None:
            invoice.attachment_url = attachment_url
        if remark is not None:
            invoice.remark = remark

        await db.flush()
        await cls.refresh_progress(db, invoice_id, operator_id=operator_id)
        return invoice

    # ------------------------------------------------------------------
    # 核销
    # ------------------------------------------------------------------
    @classmethod
    async def list_candidates(
        cls,
        db: AsyncSession,
        invoice_id: int,
        *,
        keyword: Optional[str] = None,
        limit: int = 200,
    ) -> List[dict]:
        """可核销的承运商结算单：同承运商、已审批或已付款、还有收票缺口的单。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.vendor_type or 0) != VendorType.CARRIER or not invoice.vendor_id:
            return []
        stmt = select(CarrierSettlementDoc).where(
            CarrierSettlementDoc.carrier_id == int(invoice.vendor_id),
            CarrierSettlementDoc.is_deleted == 0,
            CarrierSettlementDoc.status.in_((FIN_REVIEWED, FIN_PAID)),
        )
        if keyword:
            stmt = stmt.where(
                CarrierSettlementDoc.doc_no.like(f"%{keyword.strip()}%")
            )
        r = await db.execute(
            stmt.order_by(CarrierSettlementDoc.id.desc()).limit(max(1, int(limit)))
        )
        settles = list(r.scalars().all())
        if not settles:
            return []
        mine = await cls._applied_by_invoice(
            db, invoice_id, [int(x.id) for x in settles],
        )

        out: List[dict] = []
        for s in settles:
            planned = Decimal(str(s.planned_amount or 0))
            invoiced = Decimal(str(s.invoice_amount_total or 0))
            gap = planned - invoiced + Decimal(str(mine.get(int(s.id)) or 0))
            if gap <= 0:
                continue
            out.append({
                "settleId": int(s.id),
                "docNo": s.doc_no,
                "plannedAmount": float(planned),
                "invoiceAmountTotal": float(invoiced),
                "gapAmount": float(gap),
                "status": int(s.status or 0),
                "paidAt": s.paid_at,
                "dueDate": s.due_date,
            })
        return out

    @classmethod
    async def match(
        cls,
        db: AsyncSession,
        invoice_id: int,
        allocations: Sequence[dict],
        *,
        operator_id: Optional[int] = None,
    ) -> List[VendorInvoiceSettleLink]:
        """把票面金额核销到一张或多张结算单（已存在的关系按新金额更新）。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) in (FIN_CANCELLED, FIN_VOIDED):
            raise BizException(
                f"发票当前是「{cls.status_text(invoice)}」，不能核销"
            )
        if not allocations:
            raise BizException("请选择要核销的结算单并填写金额")

        incl = Decimal(str(invoice.amount_incl_tax or 0))
        if incl <= 0:
            raise BizException("票面含税金额为 0，请先补全票面金额再核销")

        existing = {
            int(x.settle_id): x for x in await cls.list_links(db, invoice_id)
        }
        settle_ids = [
            int(a.get("settleId")) for a in allocations if a.get("settleId")
        ]
        settles = await cls._load_settles(db, settle_ids)

        rows: List[VendorInvoiceSettleLink] = []
        touched: List[int] = []
        for item in allocations:
            sid = int(item.get("settleId"))
            settle = settles.get(sid)
            if settle is None:
                raise BizException("结算单不存在或已删除，请刷新后重试")
            cls._assert_matchable(invoice, settle)

            amount = _money(_dec(item.get("appliedAmount")) or Decimal("0"))
            if amount <= 0:
                raise BizException(
                    f"结算单 {settle.doc_no} 的核销金额必须大于 0"
                )
            planned = Decimal(str(settle.planned_amount or 0))
            invoiced = Decimal(str(settle.invoice_amount_total or 0))
            mine = Decimal(
                str(getattr(existing.get(sid), "applied_amount", 0) or 0)
            )
            gap = planned - invoiced + mine
            if amount > gap + AMOUNT_TOLERANCE:
                raise BizException(
                    f"结算单 {settle.doc_no} 还差 {gap:.2f} 元发票，"
                    f"本次最多核销这么多；票面多出的金额请核销到其他结算单"
                )

            row = existing.get(sid)
            if row is None:
                row = VendorInvoiceSettleLink(
                    invoice_id=invoice_id,
                    settle_id=sid,
                    settle_doc_no=settle.doc_no,
                    applied_amount=amount,
                    matched_at=datetime.now(),
                    matched_by=operator_id,
                    dedup_key=VendorInvoiceSettleLink.build_dedup_key(
                        invoice_id, sid,
                    ),
                )
                db.add(row)
            else:
                row.applied_amount = amount
                row.matched_at = datetime.now()
                row.matched_by = operator_id
            if item.get("remark") is not None:
                row.remark = item.get("remark")
            rows.append(row)
            touched.append(sid)
        await db.flush()

        total = await cls._applied_total(db, invoice_id)
        if total > incl + AMOUNT_TOLERANCE:
            raise BizException(
                f"核销总额 {total:.2f} 元超过票面含税金额 {incl:.2f} 元，"
                "请调整分配金额"
            )

        for sid in set(touched):
            await CarrierSettlementDocService.refresh_invoice_progress(
                db, sid, operator_id=operator_id,
            )
        await cls.refresh_progress(db, invoice_id, operator_id=operator_id)
        return rows

    @classmethod
    async def unmatch(
        cls,
        db: AsyncSession,
        invoice_id: int,
        link_id: int,
        *,
        operator_id: Optional[int] = None,
    ) -> None:
        """撤销单条核销（软删并释放去重键，结算单收票进度回退）。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) == FIN_VOIDED:
            raise BizException("已作废的发票无需再撤销核销")
        r = await db.execute(
            select(VendorInvoiceSettleLink).where(
                VendorInvoiceSettleLink.id == link_id,
                VendorInvoiceSettleLink.invoice_id == invoice_id,
                VendorInvoiceSettleLink.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("这条核销记录不存在或已撤销")
        settle_id = int(row.settle_id)
        amount = Decimal(str(row.applied_amount or 0))
        row.is_deleted = 1
        row.dedup_key = None
        await db.flush()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=invoice_id,
            event_type=FinanceEventType.UNSETTLE,
            direction=FinanceDirection.PAY,
            occurred_amount=-amount,
            operator_id=operator_id,
            reason=f"撤销对结算单 #{settle_id} 的核销",
        )
        await db.flush()
        await CarrierSettlementDocService.refresh_invoice_progress(
            db, settle_id, operator_id=operator_id,
        )
        await cls.refresh_progress(db, invoice_id, operator_id=operator_id)

    @classmethod
    async def refresh_progress(
        cls,
        db: AsyncSession,
        invoice_id: int,
        *,
        operator_id: Optional[int] = None,
    ) -> VendorInvoice:
        """按核销明细重算票的核销进度与状态。

        状态由金额推导，不额外设人工开关：全额核销为「已核销」，部分为「已收票」，
        一分没核销回到「草稿」（登记完还没配对的票就该待在草稿里等人处理）。
        """
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) in (FIN_CANCELLED, FIN_VOIDED):
            return invoice
        r = await db.execute(
            select(
                func.count(VendorInvoiceSettleLink.id),
                func.coalesce(
                    func.sum(VendorInvoiceSettleLink.applied_amount), 0
                ),
            ).where(
                VendorInvoiceSettleLink.invoice_id == invoice_id,
                VendorInvoiceSettleLink.is_deleted == 0,
            )
        )
        count, total = r.one()
        applied = Decimal(str(total or 0))
        incl = Decimal(str(invoice.amount_incl_tax or 0))
        invoice.settle_count = int(count or 0)
        invoice.settled_amount = applied
        invoice.unsettled_amount = _money(max(incl - applied, Decimal("0")))
        await db.flush()

        if applied <= 0:
            target = FIN_DRAFT
        elif applied + AMOUNT_TOLERANCE >= incl:
            target = FIN_SETTLED
        else:
            target = INVOICE_RECEIVED
        if target != int(invoice.status):
            await cls.change_status(
                db, invoice, target,
                event_type=(
                    FinanceEventType.INVOICE_MATCH
                    if target == FIN_SETTLED
                    else FinanceEventType.SETTLE
                ),
                operator_id=operator_id,
                occurred_amount=applied,
                skip_lock_check=True,
            )
        return invoice

    # ------------------------------------------------------------------
    # 作废与撤销
    # ------------------------------------------------------------------
    @classmethod
    async def void(
        cls,
        db: AsyncSession,
        invoice_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> Tuple[VendorInvoice, Optional[str]]:
        """作废 / 退票：清空核销明细并回退各结算单的收票进度。

        返回 ``(发票, 警示文案)``。已登记抵扣税期的票允许作废，但要把警示带回前端，
        让财务知道申报那边也得跟着处理。
        """
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) == FIN_VOIDED:
            raise BizException("该发票已作废，无需重复操作")
        if int(invoice.status) == FIN_CANCELLED:
            raise BizException("该发票已撤销，如需作废请先重新登记")
        text = cls.assert_reason(reason, action="作废")

        links = await cls.list_links(db, invoice_id)
        settle_ids = [int(x.settle_id) for x in links]
        for row in links:
            row.is_deleted = 1
            row.dedup_key = None
        invoice.void_reason = text
        invoice.voided_at = datetime.now()
        invoice.settled_amount = Decimal("0")
        invoice.settle_count = 0
        invoice.unsettled_amount = Decimal(str(invoice.amount_incl_tax or 0))
        invoice.dedup_key = None
        await db.flush()

        await cls.change_status(
            db, invoice, FIN_VOIDED,
            event_type=FinanceEventType.VOID,
            operator_id=operator_id,
            reason=text,
            skip_lock_check=True,
        )
        for sid in set(settle_ids):
            await CarrierSettlementDocService.refresh_invoice_progress(
                db, sid, operator_id=operator_id,
            )

        warn = None
        if invoice.deduct_period:
            warn = (
                f"这张票已登记 {invoice.deduct_period} 抵扣，"
                "作废后请同步处理当期申报"
            )
        return invoice, warn

    @classmethod
    async def cancel_invoice(
        cls,
        db: AsyncSession,
        invoice_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> VendorInvoice:
        """撤销登记（录错票）：要求先撤销全部核销，避免结算单进度悄悄失真。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) == FIN_CANCELLED:
            raise BizException("该发票已撤销，无需重复操作")
        if int(invoice.status) == FIN_VOIDED:
            raise BizException("已作废的发票不需要再撤销")
        if Decimal(str(invoice.settled_amount or 0)) > 0:
            raise BizException(
                "本票还有核销记录，请先撤销核销再撤销登记；"
                "若是承运商作废重开，请用「作废」"
            )
        text = cls.assert_reason(reason)
        await cls.change_status(
            db, invoice, FIN_CANCELLED,
            event_type=FinanceEventType.CANCEL,
            operator_id=operator_id,
            reason=text,
            skip_lock_check=True,
        )
        invoice.dedup_key = None
        await db.flush()
        return invoice

    # ------------------------------------------------------------------
    # 查询与台账
    # ------------------------------------------------------------------
    @classmethod
    async def page_list(
        cls,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        vendor_id: Optional[int] = None,
        vendor_type: Optional[int] = None,
        buyer_entity_id: Optional[int] = None,
        status: Optional[int] = None,
        invoice_type: Optional[int] = None,
        deductible: Optional[int] = None,
        deduct_period: Optional[str] = None,
        date_from: Optional[ddate] = None,
        date_to: Optional[ddate] = None,
        only_unsettled: bool = False,
    ) -> Tuple[List[VendorInvoice], int]:
        stmt = select(VendorInvoice).where(VendorInvoice.is_deleted == 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                VendorInvoice.invoice_no.like(kw)
                | VendorInvoice.doc_no.like(kw)
                | VendorInvoice.vendor_name.like(kw)
                | VendorInvoice.seller_title.like(kw)
            )
        if vendor_id:
            stmt = stmt.where(VendorInvoice.vendor_id == vendor_id)
        if vendor_type is not None:
            stmt = stmt.where(VendorInvoice.vendor_type == vendor_type)
        if buyer_entity_id:
            stmt = stmt.where(VendorInvoice.buyer_entity_id == buyer_entity_id)
        if status is not None:
            stmt = stmt.where(VendorInvoice.status == status)
        if invoice_type is not None:
            stmt = stmt.where(VendorInvoice.invoice_type == invoice_type)
        if deductible is not None:
            stmt = stmt.where(VendorInvoice.deductible == deductible)
        if deduct_period:
            stmt = stmt.where(VendorInvoice.deduct_period == deduct_period)
        if date_from:
            stmt = stmt.where(VendorInvoice.invoice_date >= date_from)
        if date_to:
            stmt = stmt.where(VendorInvoice.invoice_date <= date_to)
        if only_unsettled:
            stmt = stmt.where(
                VendorInvoice.unsettled_amount > 0,
                VendorInvoice.status.notin_((FIN_CANCELLED, FIN_VOIDED)),
            )

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(VendorInvoice.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_links(
        cls, db: AsyncSession, invoice_id: int,
    ) -> List[VendorInvoiceSettleLink]:
        r = await db.execute(
            select(VendorInvoiceSettleLink)
            .where(
                VendorInvoiceSettleLink.invoice_id == invoice_id,
                VendorInvoiceSettleLink.is_deleted == 0,
            )
            .order_by(VendorInvoiceSettleLink.id.asc())
        )
        return list(r.scalars().all())

    @classmethod
    async def list_items(
        cls, db: AsyncSession, invoice_id: int,
    ) -> List[VendorInvoiceItem]:
        r = await db.execute(
            select(VendorInvoiceItem)
            .where(
                VendorInvoiceItem.invoice_id == invoice_id,
                VendorInvoiceItem.is_deleted == 0,
            )
            .order_by(VendorInvoiceItem.id.asc())
        )
        return list(r.scalars().all())

    @classmethod
    async def deduct_summary(
        cls,
        db: AsyncSession,
        *,
        group_by: str = "period",
        buyer_entity_id: Optional[int] = None,
        period_from: Optional[str] = None,
        period_to: Optional[str] = None,
    ) -> List[dict]:
        """抵扣台账汇总（纯查询，不建汇总表）。

        ``group_by`` 支持 ``period`` / ``entity`` / ``rate`` / ``deductible``，
        对应文档 11 §五的四个汇总维度。
        """
        columns = {
            "period": VendorInvoice.deduct_period,
            "entity": VendorInvoice.buyer_entity_id,
            "rate": VendorInvoice.tax_rate,
            "deductible": VendorInvoice.deductible,
        }
        col = columns.get(group_by)
        if col is None:
            raise BizException("汇总维度不支持，请选择税期、主体、税率或可抵扣性")

        stmt = select(
            col.label("group_key"),
            func.count(VendorInvoice.id),
            func.coalesce(func.sum(VendorInvoice.amount_excl_tax), 0),
            func.coalesce(func.sum(VendorInvoice.tax_amount), 0),
            func.coalesce(func.sum(VendorInvoice.amount_incl_tax), 0),
        ).where(
            VendorInvoice.is_deleted == 0,
            VendorInvoice.status.notin_((FIN_CANCELLED, FIN_VOIDED)),
        )
        if buyer_entity_id:
            stmt = stmt.where(VendorInvoice.buyer_entity_id == buyer_entity_id)
        if period_from:
            stmt = stmt.where(VendorInvoice.deduct_period >= period_from)
        if period_to:
            stmt = stmt.where(VendorInvoice.deduct_period <= period_to)

        r = await db.execute(stmt.group_by(col).order_by(col.asc()))
        return [
            {
                "groupBy": group_by,
                "groupKey": (
                    float(key) if isinstance(key, Decimal) else key
                ),
                "invoiceCount": int(cnt or 0),
                "amountExclTax": float(excl or 0),
                "taxAmount": float(tax or 0),
                "amountInclTax": float(incl or 0),
            }
            for key, cnt, excl, tax, incl in r.all()
        ]

    @classmethod
    async def pending_settles(
        cls,
        db: AsyncSession,
        *,
        carrier_id: Optional[int] = None,
        limit: int = 200,
    ) -> List[dict]:
        """待收票池：已付款但票没收齐的结算单，按已付款天数倒序催票。"""
        stmt = select(CarrierSettlementDoc).where(
            CarrierSettlementDoc.is_deleted == 0,
            CarrierSettlementDoc.status == FIN_PAID,
            CarrierSettlementDoc.invoice_matched == 0,
        )
        if carrier_id:
            stmt = stmt.where(CarrierSettlementDoc.carrier_id == carrier_id)
        r = await db.execute(
            stmt.order_by(CarrierSettlementDoc.paid_at.asc())
            .limit(max(1, int(limit)))
        )
        now = datetime.now()
        out: List[dict] = []
        for s in r.scalars().all():
            planned = Decimal(str(s.planned_amount or 0))
            invoiced = Decimal(str(s.invoice_amount_total or 0))
            days = (now - s.paid_at).days if s.paid_at else None
            out.append({
                "settleId": int(s.id),
                "docNo": s.doc_no,
                "carrierId": s.carrier_id,
                "carrierName": s.carrier_name,
                "plannedAmount": float(planned),
                "invoiceAmountTotal": float(invoiced),
                "gapAmount": float(max(planned - invoiced, Decimal("0"))),
                "paidAt": s.paid_at,
                "paidDays": days,
            })
        return out

    @classmethod
    def status_text(cls, invoice: Any) -> str:
        return status_label(int(invoice.status or 0), cls.doc_kind)

    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        flags = super().action_flags(doc)
        status = int(doc.status)
        settled = Decimal(str(doc.settled_amount or 0))
        unsettled = Decimal(str(doc.unsettled_amount or 0))
        active = status not in (FIN_CANCELLED, FIN_VOIDED)
        flags.update({
            "canEdit": active,
            "canEditAmount": active and settled <= 0,
            "canMatch": active and unsettled > 0,
            "canUnmatch": active and settled > 0,
            "canVoid": active,
            "canCancel": active and settled <= 0,
            "unsettledAmount": float(unsettled),
        })
        return flags

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @staticmethod
    def _resolve_amounts(
        excl: Optional[Decimal],
        tax: Optional[Decimal],
        incl: Optional[Decimal],
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """三项金额任填两项算第三项；三项都给则校验自洽（容差一分）。"""
        e = _dec(excl)
        t = _dec(tax)
        i = _dec(incl)
        given = [x for x in (e, t, i) if x is not None]
        if len(given) < 2:
            raise BizException(
                "请至少填写不含税金额、税额、含税金额中的两项，第三项会自动算出"
            )
        if i is None:
            i = e + t
        elif e is None:
            e = i - t
        elif t is None:
            t = i - e
        elif abs((e + t) - i) > AMOUNT_TOLERANCE:
            raise BizException(
                f"票面金额对不上：不含税 {e:.2f} + 税额 {t:.2f} "
                f"应等于含税 {i:.2f}，请核对后重填"
            )
        for name, value in (("不含税金额", e), ("税额", t), ("含税金额", i)):
            if value < 0:
                raise BizException(f"{name}不能为负数")
        if i <= 0:
            raise BizException("含税金额必须大于 0")
        return _money(e), _money(t), _money(i)

    @classmethod
    def _sum_items(
        cls, items: Sequence[dict],
    ) -> Tuple[Decimal, Decimal, Decimal]:
        excl = Decimal("0")
        tax = Decimal("0")
        incl = Decimal("0")
        for idx, row in enumerate(items, start=1):
            e, t, i = cls._resolve_amounts(
                row.get("amountExclTax"),
                row.get("taxAmount"),
                row.get("amountInclTax"),
            )
            row["amountExclTax"] = e
            row["taxAmount"] = t
            row["amountInclTax"] = i
            if row.get("taxRate") is None:
                raise BizException(f"第 {idx} 行没填税率，多税率发票每行都要填")
            excl += e
            tax += t
            incl += i
        if incl <= 0:
            raise BizException("发票明细的含税合计必须大于 0")
        return _money(excl), _money(tax), _money(incl)

    @classmethod
    async def _replace_items(
        cls, db: AsyncSession, invoice_id: int, items: Sequence[dict],
    ) -> None:
        for row in await cls.list_items(db, invoice_id):
            row.is_deleted = 1
        await db.flush()
        for row in items or []:
            db.add(VendorInvoiceItem(
                invoice_id=invoice_id,
                item_name=row.get("itemName"),
                tax_rate=_dec(row.get("taxRate")),
                amount_excl_tax=_money(_dec(row.get("amountExclTax")) or 0),
                tax_amount=_money(_dec(row.get("taxAmount")) or 0),
                amount_incl_tax=_money(_dec(row.get("amountInclTax")) or 0),
                remark=row.get("remark"),
            ))
        await db.flush()

    @staticmethod
    def _assert_matchable(invoice: VendorInvoice, settle: Any) -> None:
        if int(settle.carrier_id or 0) != int(invoice.vendor_id or 0):
            raise BizException(
                f"结算单 {settle.doc_no} 不是这家承运商的，不能用这张票核销"
            )
        if int(settle.status or 0) not in (FIN_REVIEWED, FIN_PAID):
            raise BizException(
                f"结算单 {settle.doc_no} 还没审批通过，请先走完审批再核销发票"
            )

    @classmethod
    async def _assert_no_duplicate(
        cls, db: AsyncSession, invoice_code: Optional[str], invoice_no: str,
    ) -> None:
        r = await db.execute(
            select(VendorInvoice.id, VendorInvoice.doc_no).where(
                VendorInvoice.dedup_key == VendorInvoice.build_dedup_key(
                    invoice_code, invoice_no,
                ),
                VendorInvoice.is_deleted == 0,
            ).limit(1)
        )
        row = r.one_or_none()
        if row is not None:
            raise BizException(
                f"这张发票已经登记过了（单据 {row[1]}），"
                "请直接在那张单上处理，不用重复录入"
            )

    @staticmethod
    async def _get_carrier_or_404(db: AsyncSession, carrier_id: int) -> Carrier:
        r = await db.execute(
            select(Carrier).where(
                Carrier.id == carrier_id, Carrier.is_deleted == 0,
            )
        )
        carrier = r.scalar_one_or_none()
        if carrier is None:
            raise BizException("承运商不存在或已停用，请重新选择")
        return carrier

    @staticmethod
    async def _load_settles(
        db: AsyncSession, settle_ids: Sequence[int],
    ) -> Dict[int, CarrierSettlementDoc]:
        if not settle_ids:
            return {}
        r = await db.execute(
            select(CarrierSettlementDoc).where(
                CarrierSettlementDoc.id.in_(list(settle_ids)),
                CarrierSettlementDoc.is_deleted == 0,
            )
        )
        return {int(x.id): x for x in r.scalars().all()}

    @staticmethod
    async def _applied_total(db: AsyncSession, invoice_id: int) -> Decimal:
        r = await db.execute(
            select(
                func.coalesce(
                    func.sum(VendorInvoiceSettleLink.applied_amount), 0
                )
            ).where(
                VendorInvoiceSettleLink.invoice_id == invoice_id,
                VendorInvoiceSettleLink.is_deleted == 0,
            )
        )
        return Decimal(str(r.scalar() or 0))

    @staticmethod
    async def _applied_by_invoice(
        db: AsyncSession, invoice_id: int, settle_ids: Sequence[int],
    ) -> Dict[int, Decimal]:
        if not settle_ids:
            return {}
        r = await db.execute(
            select(
                VendorInvoiceSettleLink.settle_id,
                VendorInvoiceSettleLink.applied_amount,
            ).where(
                VendorInvoiceSettleLink.invoice_id == invoice_id,
                VendorInvoiceSettleLink.settle_id.in_(list(settle_ids)),
                VendorInvoiceSettleLink.is_deleted == 0,
            )
        )
        return {int(sid): Decimal(str(amt or 0)) for sid, amt in r.all()}


def _money(v: Any) -> Decimal:
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v: Any) -> Optional[Decimal]:
    if v is None or v == "":
        return None
    return Decimal(str(v))


def _norm_period(value: Optional[str]) -> Optional[str]:
    """抵扣税期归一为 ``YYYY-MM``，容忍用户填成 ``YYYY/MM`` 或 ``YYYYMM``。"""
    if not value:
        return None
    text = str(value).strip().replace("/", "-")
    if len(text) == 6 and text.isdigit():
        text = f"{text[:4]}-{text[4:]}"
    parts = text.split("-")
    if len(parts) != 2 or len(parts[0]) != 4 or not parts[0].isdigit():
        raise BizException("抵扣税期请填成 2026-08 这样的年月格式")
    month = int(parts[1])
    if not 1 <= month <= 12:
        raise BizException("抵扣税期的月份不正确，请填 1 到 12 之间的月份")
    return f"{parts[0]}-{month:02d}"
