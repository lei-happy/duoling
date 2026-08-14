"""客户发票（销项）Service（文档 02 §五）

与进项票最大的差别是**销项票是我们的主动行为**：要走「草稿 → 申请中 → 已开票」，
金额必须与关联结算单严丝合缝，开票后结算单锁定。因此这里没有进项票那种「金额自由
录、核销进度驱动状态」的玩法。

三条容易写错的口径：

1. **开票金额 = 关联结算单认领额之和**：提交申请时校验，差一分都不放过；否则开出去
   的票与应收对不上，客户拿票入账时会被打回。
2. **开票即锁结算单**：金额锁死，后续要改只能作废/红冲重开。锁定来源记在
   ``locked_by_doc_id``，避免作废 A 票把 B 票的锁解了。
3. **红冲不是删除**：原票转「已作废」但保留可见，同时生成一张金额取负的红冲票；
   结算单的开票进度按两张票的净额回退（正负相加为 0）。
"""

from datetime import date as ddate, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.customer_invoice import (
    CUSTOMER_INVOICE_DOC_KIND,
    CustomerInvoice,
    CustomerInvoiceItem,
    CustomerInvoiceSettleLink,
)
from app.modules.client.models.finance.customer_settlement import CustomerSettlement
from app.modules.client.models.partner.customer import Customer
from app.modules.client.services.finance.base.constants import (
    FinanceDirection,
    InvoiceType,
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
    FIN_PENDING_REVIEW,
    FIN_REVIEWED,
    FIN_VOIDED,
    label as status_label,
)
from app.modules.client.services.finance.linkage.lock_orchestrator import (
    LockOrchestrator,
)

_CENT = Decimal("0.01")
AMOUNT_TOLERANCE = Decimal("0.01")
# 销项票的「已开票」用通用 3；1 是「申请中」
INVOICE_APPLYING = FIN_PENDING_REVIEW
INVOICE_ISSUED = FIN_PAID
# 可开票的结算单状态：已审批（票结客户先开票后收款）与已收款
INVOICEABLE_SETTLE_STATUSES = (FIN_REVIEWED, FIN_PAID)


class CustomerInvoiceService(FinanceDocService):
    """客户发票（销项）"""

    model = CustomerInvoice
    doc_kind = CUSTOMER_INVOICE_DOC_KIND
    doc_label = "客户发票"
    doc_no_prefix = "CI"
    direction = FinanceDirection.RECEIVE
    editable_statuses = (FIN_DRAFT,)
    deletable_statuses = (FIN_DRAFT, FIN_CANCELLED)

    # ------------------------------------------------------------------
    # 候选与创建
    # ------------------------------------------------------------------
    @classmethod
    async def list_candidates(
        cls,
        db: AsyncSession,
        *,
        customer_id: int,
        keyword: Optional[str] = None,
        invoice_id: Optional[int] = None,
        limit: int = 200,
    ) -> List[dict]:
        """可开票的客户结算单：同客户、已审批或已收款、还有未开票金额的单。

        ``invoice_id`` 用于给已存在的发票补挂结算单——本票已认领的额度不算占用，
        否则编辑时会看不到自己已经挂上的那张。
        """
        stmt = select(CustomerSettlement).where(
            CustomerSettlement.customer_id == int(customer_id),
            CustomerSettlement.is_deleted == 0,
            CustomerSettlement.status.in_(INVOICEABLE_SETTLE_STATUSES),
        )
        if keyword:
            stmt = stmt.where(CustomerSettlement.doc_no.like(f"%{keyword.strip()}%"))
        r = await db.execute(
            stmt.order_by(CustomerSettlement.id.desc()).limit(max(1, int(limit)))
        )
        settles = list(r.scalars().all())
        if not settles:
            return []
        mine: Dict[int, Decimal] = {}
        if invoice_id:
            mine = await cls._applied_by_invoice(
                db, int(invoice_id), [int(x.id) for x in settles],
            )

        out: List[dict] = []
        for s in settles:
            planned = Decimal(str(s.planned_amount or 0))
            invoiced = Decimal(str(s.invoice_amount_total or 0))
            available = planned - invoiced + Decimal(str(mine.get(int(s.id)) or 0))
            if available <= 0:
                continue
            out.append({
                "settleId": int(s.id),
                "docNo": s.doc_no,
                "plannedAmount": float(planned),
                "invoicedAmount": float(invoiced),
                "availableAmount": float(available),
                "appliedAmount": float(mine.get(int(s.id)) or 0),
                "status": int(s.status or 0),
                "dueDate": s.due_date,
                "receivedAt": s.received_at,
                "invoiceRequired": int(s.invoice_required or 0),
            })
        return out

    @classmethod
    async def create_from_settles(
        cls,
        db: AsyncSession,
        *,
        customer_id: int,
        allocations: Sequence[dict],
        invoice_type: int = InvoiceType.SPECIAL,
        seller_entity_id: Optional[int] = None,
        seller_title: Optional[str] = None,
        seller_tax_no: Optional[str] = None,
        buyer_title: Optional[str] = None,
        buyer_tax_no: Optional[str] = None,
        buyer_address: Optional[str] = None,
        buyer_phone: Optional[str] = None,
        buyer_bank: Optional[str] = None,
        buyer_account: Optional[str] = None,
        items: Optional[Sequence[dict]] = None,
        tax_rate: Optional[Decimal] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerInvoice:
        """按选中的结算单建一张发票草稿。

        购方信息不传时从客户档案带出：抬头、税号是开票必需项，让用户每次手抄一遍
        既慢又容易错。带出后冻结在票上，客户改档案不影响已开的票。
        """
        customer = await cls._get_customer_or_404(db, int(customer_id))
        if not allocations:
            raise BizException("请选择要开票的结算单")

        invoice = CustomerInvoice(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.RECEIVE,
            status=FIN_DRAFT,
            customer_id=int(customer_id),
            customer_name=customer.customer_name,
            seller_entity_id=seller_entity_id,
            seller_title=seller_title,
            seller_tax_no=seller_tax_no,
            buyer_title=buyer_title or customer.customer_name,
            # 客户档案里没有独立税号列，统一社会信用代码即开票税号
            buyer_tax_no=buyer_tax_no or customer.credit_code,
            buyer_address=buyer_address or customer.address,
            buyer_phone=buyer_phone or customer.contact_phone,
            buyer_bank=buyer_bank,
            buyer_account=buyer_account,
            invoice_type=int(invoice_type),
            tax_rate=(Decimal(str(tax_rate)) if tax_rate is not None else None),
            # 票面金额由关联行汇总而来，先占位 0，link_settles 后由 _refresh_amounts 回填
            planned_amount=Decimal("0"),
            created_by=operator_id,
            remark=remark,
        )
        db.add(invoice)
        await db.flush()

        await cls.link_settles(
            db, invoice.id, allocations, operator_id=operator_id,
        )
        if items:
            await cls.replace_items(db, invoice.id, items)
        else:
            await cls._build_default_item(db, invoice, tax_rate)
        await cls._refresh_amounts(db, invoice.id)

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=invoice.id,
            event_type=FinanceEventType.CREATE,
            to_status=FIN_DRAFT,
            direction=FinanceDirection.RECEIVE,
            occurred_amount=invoice.amount_incl_tax,
            operator_id=operator_id,
            reason=f"按 {len(allocations)} 张结算单创建开票申请",
        )
        await db.flush()
        return invoice

    @classmethod
    async def update_invoice(
        cls,
        db: AsyncSession,
        invoice_id: int,
        *,
        invoice_type: Optional[int] = None,
        seller_entity_id: Optional[int] = None,
        seller_title: Optional[str] = None,
        seller_tax_no: Optional[str] = None,
        buyer_title: Optional[str] = None,
        buyer_tax_no: Optional[str] = None,
        buyer_address: Optional[str] = None,
        buyer_phone: Optional[str] = None,
        buyer_bank: Optional[str] = None,
        buyer_account: Optional[str] = None,
        tax_rate: Optional[Decimal] = None,
        items: Optional[Sequence[dict]] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerInvoice:
        """编辑草稿票面（购方信息、票种、行明细）。"""
        invoice = await cls.get_or_404(db, invoice_id)
        cls.assert_editable(invoice)

        if invoice_type is not None:
            invoice.invoice_type = int(invoice_type)
        if seller_entity_id is not None:
            invoice.seller_entity_id = seller_entity_id
        if seller_title is not None:
            invoice.seller_title = seller_title
        if seller_tax_no is not None:
            invoice.seller_tax_no = seller_tax_no
        if buyer_title is not None:
            invoice.buyer_title = buyer_title
        if buyer_tax_no is not None:
            invoice.buyer_tax_no = buyer_tax_no
        if buyer_address is not None:
            invoice.buyer_address = buyer_address
        if buyer_phone is not None:
            invoice.buyer_phone = buyer_phone
        if buyer_bank is not None:
            invoice.buyer_bank = buyer_bank
        if buyer_account is not None:
            invoice.buyer_account = buyer_account
        if tax_rate is not None:
            invoice.tax_rate = Decimal(str(tax_rate))
        if remark is not None:
            invoice.remark = remark
        await db.flush()

        if items is not None:
            await cls.replace_items(db, invoice_id, items)
        return invoice

    # ------------------------------------------------------------------
    # 关联结算单
    # ------------------------------------------------------------------
    @classmethod
    async def link_settles(
        cls,
        db: AsyncSession,
        invoice_id: int,
        allocations: Sequence[dict],
        *,
        operator_id: Optional[int] = None,
    ) -> List[CustomerInvoiceSettleLink]:
        """关联结算单并分配开票金额（已存在的关系按新金额更新）。"""
        invoice = await cls.get_or_404(db, invoice_id)
        cls.assert_editable(invoice)
        if not allocations:
            raise BizException("请选择要开票的结算单")

        existing = {
            int(x.settle_id): x for x in await cls.list_links(db, invoice_id)
        }
        settle_ids = [
            int(a.get("settleId")) for a in allocations if a.get("settleId")
        ]
        settles = await cls._load_settles(db, settle_ids)

        rows: List[CustomerInvoiceSettleLink] = []
        for item in allocations:
            sid = int(item.get("settleId"))
            settle = settles.get(sid)
            if settle is None:
                raise BizException("结算单不存在或已删除，请刷新后重试")
            cls._assert_invoiceable(invoice, settle)

            planned = Decimal(str(settle.planned_amount or 0))
            invoiced = Decimal(str(settle.invoice_amount_total or 0))
            mine = Decimal(
                str(getattr(existing.get(sid), "applied_amount_incl_tax", 0) or 0)
            )
            available = planned - invoiced + mine
            raw = _dec(item.get("appliedAmount"))
            amount = _money(raw if raw is not None else available)
            if amount <= 0:
                raise BizException(f"结算单 {settle.doc_no} 的开票金额必须大于 0")
            if amount > available + AMOUNT_TOLERANCE:
                raise BizException(
                    f"结算单 {settle.doc_no} 还能开 {available:.2f} 元的票，"
                    "请调小开票金额或换一张结算单"
                )

            row = existing.get(sid)
            if row is None:
                row = CustomerInvoiceSettleLink(
                    invoice_id=invoice_id,
                    settle_id=sid,
                    settle_doc_no=settle.doc_no,
                    applied_amount_incl_tax=amount,
                    dedup_key=CustomerInvoiceSettleLink.build_dedup_key(
                        invoice_id, sid,
                    ),
                )
                db.add(row)
            else:
                row.applied_amount_incl_tax = amount
            if item.get("remark") is not None:
                row.remark = item.get("remark")
            rows.append(row)
        await db.flush()
        await cls._refresh_amounts(db, invoice_id)
        return rows

    @classmethod
    async def unlink_settle(
        cls,
        db: AsyncSession,
        invoice_id: int,
        link_id: int,
        *,
        operator_id: Optional[int] = None,
    ) -> None:
        """解除一张结算单的关联（仅草稿）。"""
        invoice = await cls.get_or_404(db, invoice_id)
        cls.assert_editable(invoice)
        r = await db.execute(
            select(CustomerInvoiceSettleLink).where(
                CustomerInvoiceSettleLink.id == link_id,
                CustomerInvoiceSettleLink.invoice_id == invoice_id,
                CustomerInvoiceSettleLink.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("这条关联不存在或已解除")
        row.is_deleted = 1
        row.dedup_key = None
        await db.flush()
        await cls._refresh_amounts(db, invoice_id)

    # ------------------------------------------------------------------
    # 行明细
    # ------------------------------------------------------------------
    @classmethod
    async def replace_items(
        cls, db: AsyncSession, invoice_id: int, items: Sequence[dict],
    ) -> None:
        """整体替换行明细（票面按行打印，逐行增删对用户没意义）。"""
        invoice = await cls.get_or_404(db, invoice_id)
        cls.assert_editable(invoice)
        for row in await cls.list_items(db, invoice_id):
            row.is_deleted = 1
        await db.flush()
        for idx, row in enumerate(items or [], start=1):
            excl, tax, incl = cls._resolve_amounts(
                row.get("amountExclTax"),
                row.get("taxAmount"),
                row.get("amountInclTax"),
            )
            db.add(CustomerInvoiceItem(
                invoice_id=invoice_id,
                item_name=row.get("itemName") or "运输服务",
                tax_rate=_dec(row.get("taxRate")),
                amount_excl_tax=excl,
                tax_amount=tax,
                amount_incl_tax=incl,
                sort_order=int(row.get("sortOrder") or idx),
                remark=row.get("remark"),
            ))
        await db.flush()
        await cls._refresh_amounts(db, invoice_id)

    # ------------------------------------------------------------------
    # 状态流转
    # ------------------------------------------------------------------
    @classmethod
    async def submit_apply(
        cls, db: AsyncSession, invoice_id: int, operator_id: Optional[int] = None,
    ) -> CustomerInvoice:
        """草稿 → 申请中：校验行明细合计与关联结算单金额一致。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) != FIN_DRAFT:
            raise BizException(
                f"只有草稿才能提交开票申请（当前：{cls.status_text(invoice)}）"
            )
        linked = await cls._linked_total(db, invoice_id)
        if linked <= 0:
            raise BizException("这张票还没关联结算单，请先选要开票的结算单")
        items_total = await cls._items_total(db, invoice_id)
        if items_total <= 0:
            raise BizException("这张票还没有开票明细，请先填品名与金额")
        if abs(items_total - linked) > AMOUNT_TOLERANCE:
            raise BizException(
                f"开票明细合计 {items_total:.2f} 元与关联结算单金额 "
                f"{linked:.2f} 元不一致，请核对后再提交"
            )
        if not (invoice.buyer_title or "").strip():
            raise BizException("请填写购方开票名称")

        invoice.applicant_at = datetime.now()
        await db.flush()
        await cls.change_status(
            db, invoice, INVOICE_APPLYING,
            event_type=FinanceEventType.SUBMIT,
            operator_id=operator_id,
            occurred_amount=invoice.amount_incl_tax,
        )
        return invoice

    @classmethod
    async def withdraw_apply(
        cls,
        db: AsyncSession,
        invoice_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CustomerInvoice:
        """申请中 → 草稿（退回修改）。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) != INVOICE_APPLYING:
            raise BizException(
                f"只有「申请中」的发票可以退回修改（当前：{cls.status_text(invoice)}）"
            )
        text = cls.assert_reason(reason, action="退回")
        await cls.change_status(
            db, invoice, FIN_DRAFT,
            event_type=FinanceEventType.WITHDRAW,
            operator_id=operator_id,
            reason=text,
        )
        return invoice

    @classmethod
    async def issue(
        cls,
        db: AsyncSession,
        invoice_id: int,
        *,
        invoice_no: str,
        invoice_code: Optional[str] = None,
        invoice_date: Optional[ddate] = None,
        pdf_url: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerInvoice:
        """申请中 → 已开票：录入票号并锁定关联结算单。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) != INVOICE_APPLYING:
            raise BizException(
                f"只有「申请中」的发票可以登记开票结果"
                f"（当前：{cls.status_text(invoice)}）"
            )
        no = (invoice_no or "").strip()
        if not no:
            raise BizException("请填写发票号码")
        code = (invoice_code or "").strip() or None
        await cls._assert_no_duplicate(db, code, no, exclude_id=invoice_id)

        invoice.invoice_no = no
        invoice.invoice_code = code
        invoice.invoice_date = invoice_date or ddate.today()
        invoice.issued_at = datetime.now()
        invoice.dedup_key = CustomerInvoice.build_dedup_key(code, no)
        if pdf_url:
            invoice.pdf_url = pdf_url
        await db.flush()

        await cls.change_status(
            db, invoice, INVOICE_ISSUED,
            event_type=FinanceEventType.INVOICE,
            operator_id=operator_id,
            occurred_amount=invoice.amount_incl_tax,
            payload_snapshot={"invoiceNo": no, "invoiceCode": code},
        )
        settle_ids = [int(x.settle_id) for x in await cls.list_links(db, invoice_id)]
        for sid in settle_ids:
            await cls.refresh_settle_invoice_progress(db, sid)
        await LockOrchestrator.lock_settlements(
            db, settle_ids, by_doc_id=invoice_id,
        )
        return invoice

    @classmethod
    async def void(
        cls,
        db: AsyncSession,
        invoice_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> Tuple[CustomerInvoice, Optional[str]]:
        """已开票 → 已作废：回退结算单开票进度并解锁。

        返回 ``(发票, 警示文案)``：跨月作废在税务上要走红字流程，这里不硬拦，但把
        提醒带回前端——最终以金税平台为准（文档 02 §5.4）。
        """
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) == FIN_VOIDED:
            raise BizException("这张票已作废，无需重复操作")
        if int(invoice.status) != INVOICE_ISSUED:
            raise BizException(
                f"只有「已开票」的发票需要作废；当前是"
                f"「{cls.status_text(invoice)}」，请用「撤销」"
            )
        text = cls.assert_reason(reason, action="作废")

        settle_ids = [int(x.settle_id) for x in await cls.list_links(db, invoice_id)]
        invoice.void_reason = text
        invoice.voided_at = datetime.now()
        invoice.dedup_key = None
        await db.flush()
        await cls.change_status(
            db, invoice, FIN_VOIDED,
            event_type=FinanceEventType.VOID,
            operator_id=operator_id,
            reason=text,
            skip_lock_check=True,
        )
        await LockOrchestrator.unlock_settlements(
            db, by_doc_id=invoice_id, settle_ids=settle_ids,
        )
        for sid in settle_ids:
            await cls.refresh_settle_invoice_progress(db, sid)

        warn = None
        issued = invoice.invoice_date or (
            invoice.issued_at.date() if invoice.issued_at else None
        )
        today = ddate.today()
        if issued and (issued.year, issued.month) != (today.year, today.month):
            warn = (
                f"这张票是 {issued.strftime('%Y-%m')} 开的，已经跨月；"
                "请在开票系统里走红字发票流程，不要只在这里作废"
            )
        return invoice, warn

    @classmethod
    async def red_flush(
        cls,
        db: AsyncSession,
        invoice_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> Tuple[CustomerInvoice, CustomerInvoice]:
        """红冲：原票转作废，另生成一张金额取负的红冲票。

        返回 ``(原票, 红冲票)``。红冲票不再关联结算单——两张票净额为 0，结算单的开票
        进度按原票回退即可，多挂一遍关系只会让「还能开多少票」算重。
        """
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) != INVOICE_ISSUED:
            raise BizException(
                f"只有「已开票」的发票可以红冲（当前：{cls.status_text(invoice)}）"
            )
        if int(invoice.is_red_flush or 0) == 1:
            raise BizException("红冲票本身不能再红冲")
        text = cls.assert_reason(reason, action="红冲")

        red = CustomerInvoice(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.RECEIVE,
            status=INVOICE_ISSUED,
            customer_id=invoice.customer_id,
            customer_name=invoice.customer_name,
            seller_entity_id=invoice.seller_entity_id,
            seller_title=invoice.seller_title,
            seller_tax_no=invoice.seller_tax_no,
            buyer_title=invoice.buyer_title,
            buyer_tax_no=invoice.buyer_tax_no,
            buyer_address=invoice.buyer_address,
            buyer_phone=invoice.buyer_phone,
            buyer_bank=invoice.buyer_bank,
            buyer_account=invoice.buyer_account,
            invoice_type=invoice.invoice_type,
            invoice_date=ddate.today(),
            issued_at=datetime.now(),
            amount_excl_tax=-Decimal(str(invoice.amount_excl_tax or 0)),
            tax_amount=-Decimal(str(invoice.tax_amount or 0)),
            amount_incl_tax=-Decimal(str(invoice.amount_incl_tax or 0)),
            planned_amount=-Decimal(str(invoice.amount_incl_tax or 0)),
            tax_rate=invoice.tax_rate,
            is_red_flush=1,
            red_flush_from_id=invoice.id,
            created_by=operator_id,
            remark=f"红冲 {invoice.doc_no}：{text}",
        )
        db.add(red)
        await db.flush()

        for item in await cls.list_items(db, invoice_id):
            db.add(CustomerInvoiceItem(
                invoice_id=red.id,
                item_name=item.item_name,
                tax_rate=item.tax_rate,
                amount_excl_tax=-Decimal(str(item.amount_excl_tax or 0)),
                tax_amount=-Decimal(str(item.tax_amount or 0)),
                amount_incl_tax=-Decimal(str(item.amount_incl_tax or 0)),
                sort_order=item.sort_order,
                remark=item.remark,
            ))
        await db.flush()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=red.id,
            event_type=FinanceEventType.RED_OFFSET,
            to_status=INVOICE_ISSUED,
            direction=FinanceDirection.RECEIVE,
            occurred_amount=red.amount_incl_tax,
            operator_id=operator_id,
            reason=f"红冲原票 {invoice.doc_no}：{text}",
            payload_snapshot={"originInvoiceId": int(invoice.id)},
        )

        settle_ids = [int(x.settle_id) for x in await cls.list_links(db, invoice_id)]
        invoice.void_reason = text
        invoice.voided_at = datetime.now()
        invoice.dedup_key = None
        await db.flush()
        await cls.change_status(
            db, invoice, FIN_VOIDED,
            event_type=FinanceEventType.RED_OFFSET,
            operator_id=operator_id,
            reason=text,
            skip_lock_check=True,
            payload_snapshot={"redInvoiceId": int(red.id)},
        )
        await LockOrchestrator.unlock_settlements(
            db, by_doc_id=invoice_id, settle_ids=settle_ids,
        )
        for sid in settle_ids:
            await cls.refresh_settle_invoice_progress(db, sid)
        return invoice, red

    @classmethod
    async def cancel_invoice(
        cls,
        db: AsyncSession,
        invoice_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CustomerInvoice:
        """撤销开票申请（草稿 / 申请中）。已开票的要走作废或红冲。"""
        invoice = await cls.get_or_404(db, invoice_id)
        if int(invoice.status) not in (FIN_DRAFT, INVOICE_APPLYING):
            raise BizException(
                f"当前是「{cls.status_text(invoice)}」，"
                "已开票的发票请用「作废」或「红冲」"
            )
        text = cls.assert_reason(reason)
        for row in await cls.list_links(db, invoice_id):
            row.is_deleted = 1
            row.dedup_key = None
        await db.flush()
        await cls.change_status(
            db, invoice, FIN_CANCELLED,
            event_type=FinanceEventType.CANCEL,
            operator_id=operator_id,
            reason=text,
        )
        return invoice

    # ------------------------------------------------------------------
    # 结算单开票进度
    # ------------------------------------------------------------------
    @classmethod
    async def refresh_settle_invoice_progress(
        cls, db: AsyncSession, settle_id: int,
    ) -> None:
        """按有效发票重算某张结算单的开票计数与金额。

        「有效」= 未撤销未作废；红冲票金额为负，天然让净额回到未开票状态。
        """
        r = await db.execute(
            select(
                func.count(CustomerInvoiceSettleLink.id),
                func.coalesce(
                    func.sum(CustomerInvoiceSettleLink.applied_amount_incl_tax), 0
                ),
            )
            .join(
                CustomerInvoice,
                CustomerInvoice.id == CustomerInvoiceSettleLink.invoice_id,
            )
            .where(
                CustomerInvoiceSettleLink.settle_id == settle_id,
                CustomerInvoiceSettleLink.is_deleted == 0,
                CustomerInvoice.is_deleted == 0,
                CustomerInvoice.status.notin_((FIN_CANCELLED, FIN_VOIDED)),
            )
        )
        count, total = r.one()
        settle = (await db.execute(
            select(CustomerSettlement).where(
                CustomerSettlement.id == settle_id,
                CustomerSettlement.is_deleted == 0,
            )
        )).scalar_one_or_none()
        if settle is None:
            return
        settle.invoice_count = int(count or 0)
        settle.invoice_amount_total = _money(Decimal(str(total or 0)))
        await db.flush()

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    @classmethod
    async def page_list(
        cls,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        seller_entity_id: Optional[int] = None,
        status: Optional[int] = None,
        invoice_type: Optional[int] = None,
        date_from: Optional[ddate] = None,
        date_to: Optional[ddate] = None,
        only_red: Optional[bool] = None,
    ) -> Tuple[List[CustomerInvoice], int]:
        stmt = select(CustomerInvoice).where(CustomerInvoice.is_deleted == 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                CustomerInvoice.doc_no.like(kw)
                | CustomerInvoice.invoice_no.like(kw)
                | CustomerInvoice.customer_name.like(kw)
                | CustomerInvoice.buyer_title.like(kw)
            )
        if customer_id:
            stmt = stmt.where(CustomerInvoice.customer_id == customer_id)
        if seller_entity_id:
            stmt = stmt.where(CustomerInvoice.seller_entity_id == seller_entity_id)
        if status is not None:
            stmt = stmt.where(CustomerInvoice.status == status)
        if invoice_type is not None:
            stmt = stmt.where(CustomerInvoice.invoice_type == invoice_type)
        if date_from:
            stmt = stmt.where(CustomerInvoice.invoice_date >= date_from)
        if date_to:
            stmt = stmt.where(CustomerInvoice.invoice_date <= date_to)
        if only_red is not None:
            stmt = stmt.where(
                CustomerInvoice.is_red_flush == (1 if only_red else 0)
            )

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(CustomerInvoice.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_links(
        cls, db: AsyncSession, invoice_id: int,
    ) -> List[CustomerInvoiceSettleLink]:
        r = await db.execute(
            select(CustomerInvoiceSettleLink)
            .where(
                CustomerInvoiceSettleLink.invoice_id == invoice_id,
                CustomerInvoiceSettleLink.is_deleted == 0,
            )
            .order_by(CustomerInvoiceSettleLink.id.asc())
        )
        return list(r.scalars().all())

    @classmethod
    async def list_items(
        cls, db: AsyncSession, invoice_id: int,
    ) -> List[CustomerInvoiceItem]:
        r = await db.execute(
            select(CustomerInvoiceItem)
            .where(
                CustomerInvoiceItem.invoice_id == invoice_id,
                CustomerInvoiceItem.is_deleted == 0,
            )
            .order_by(
                CustomerInvoiceItem.sort_order.asc(),
                CustomerInvoiceItem.id.asc(),
            )
        )
        return list(r.scalars().all())

    @classmethod
    async def pending_settles(
        cls,
        db: AsyncSession,
        *,
        customer_id: Optional[int] = None,
        only_required: bool = True,
        limit: int = 200,
    ) -> List[dict]:
        """待开票池：已审批/已收款但票没开齐的结算单，催开票用。

        ``only_required=True`` 时只看客户要求开票的单——不要票的客户混进来会让这个池
        永远清不空。
        """
        stmt = select(CustomerSettlement).where(
            CustomerSettlement.is_deleted == 0,
            CustomerSettlement.status.in_(INVOICEABLE_SETTLE_STATUSES),
            CustomerSettlement.planned_amount
            > CustomerSettlement.invoice_amount_total,
        )
        if only_required:
            stmt = stmt.where(CustomerSettlement.invoice_required == 1)
        if customer_id:
            stmt = stmt.where(CustomerSettlement.customer_id == customer_id)
        r = await db.execute(
            # MySQL 不支持 NULLS LAST，用「是否为空」先排一轮把无账期的压到后面
            stmt.order_by(
                CustomerSettlement.due_date.is_(None),
                CustomerSettlement.due_date.asc(),
            ).limit(max(1, int(limit)))
        )
        out: List[dict] = []
        for s in r.scalars().all():
            planned = Decimal(str(s.planned_amount or 0))
            invoiced = Decimal(str(s.invoice_amount_total or 0))
            out.append({
                "settleId": int(s.id),
                "docNo": s.doc_no,
                "customerId": s.customer_id,
                "customerName": s.customer_name,
                "plannedAmount": float(planned),
                "invoicedAmount": float(invoiced),
                "gapAmount": float(max(planned - invoiced, Decimal("0"))),
                "status": int(s.status or 0),
                "dueDate": s.due_date,
                "receivedAt": s.received_at,
            })
        return out

    @classmethod
    def status_text(cls, invoice: Any) -> str:
        return status_label(int(invoice.status or 0), cls.doc_kind)

    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        flags = super().action_flags(doc)
        status = int(doc.status)
        flags.update({
            "canEdit": status == FIN_DRAFT,
            "canDelete": status in (FIN_DRAFT, FIN_CANCELLED),
            "canSubmit": status == FIN_DRAFT,
            "canWithdraw": status == INVOICE_APPLYING,
            "canIssue": status == INVOICE_APPLYING,
            "canVoid": status == INVOICE_ISSUED,
            "canRedFlush": (
                status == INVOICE_ISSUED and int(doc.is_red_flush or 0) == 0
            ),
            "canCancel": status in (FIN_DRAFT, INVOICE_APPLYING),
        })
        return flags

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @classmethod
    async def _refresh_amounts(cls, db: AsyncSession, invoice_id: int) -> None:
        """主表金额按行明细汇总回填；没有行时退回按关联结算单金额。"""
        invoice = await cls.get_or_404(db, invoice_id)
        items = await cls.list_items(db, invoice_id)
        if items:
            excl = sum((Decimal(str(x.amount_excl_tax or 0)) for x in items), Decimal("0"))
            tax = sum((Decimal(str(x.tax_amount or 0)) for x in items), Decimal("0"))
            incl = sum((Decimal(str(x.amount_incl_tax or 0)) for x in items), Decimal("0"))
            rates = {x.tax_rate for x in items if x.tax_rate is not None}
            invoice.tax_rate = rates.pop() if len(rates) == 1 else None
        else:
            incl = await cls._linked_total(db, invoice_id)
            rate = Decimal(str(invoice.tax_rate or 0))
            excl = _money(incl / (1 + rate / 100)) if rate else incl
            tax = _money(incl - excl)
        invoice.amount_excl_tax = _money(excl)
        invoice.tax_amount = _money(tax)
        invoice.amount_incl_tax = _money(incl)
        invoice.planned_amount = _money(incl)
        invoice.settle_count = len(await cls.list_links(db, invoice_id))
        await db.flush()

    @classmethod
    async def _build_default_item(
        cls,
        db: AsyncSession,
        invoice: CustomerInvoice,
        tax_rate: Optional[Decimal],
    ) -> None:
        """没给行明细时按关联金额建一行「运输服务」，省去手工填一行。"""
        incl = await cls._linked_total(db, invoice.id)
        if incl <= 0:
            return
        rate = Decimal(str(tax_rate or 0))
        excl = _money(incl / (1 + rate / 100)) if rate else incl
        db.add(CustomerInvoiceItem(
            invoice_id=invoice.id,
            item_name="运输服务",
            tax_rate=(rate if tax_rate is not None else None),
            amount_excl_tax=excl,
            tax_amount=_money(incl - excl),
            amount_incl_tax=_money(incl),
            sort_order=1,
        ))
        await db.flush()

    @staticmethod
    def _resolve_amounts(
        excl: Any, tax: Any, incl: Any,
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """行金额三项任填两项算第三项；都给则校验自洽（容差一分）。"""
        e = _dec(excl)
        t = _dec(tax)
        i = _dec(incl)
        given = [x for x in (e, t, i) if x is not None]
        if len(given) < 2:
            raise BizException(
                "开票明细请至少填不含税金额、税额、含税金额中的两项"
            )
        if i is None:
            i = e + t
        elif e is None:
            e = i - t
        elif t is None:
            t = i - e
        elif abs((e + t) - i) > AMOUNT_TOLERANCE:
            raise BizException(
                f"开票明细金额对不上：不含税 {e:.2f} + 税额 {t:.2f} "
                f"应等于含税 {i:.2f}"
            )
        return _money(e), _money(t), _money(i)

    @staticmethod
    def _assert_invoiceable(invoice: CustomerInvoice, settle: Any) -> None:
        if int(settle.customer_id or 0) != int(invoice.customer_id or 0):
            raise BizException(
                f"结算单 {settle.doc_no} 不是这家客户的，不能开在同一张票上"
            )
        if int(settle.status or 0) not in INVOICEABLE_SETTLE_STATUSES:
            raise BizException(
                f"结算单 {settle.doc_no} 还没审批通过，请先走完审批再开票"
            )

    @classmethod
    async def _linked_total(cls, db: AsyncSession, invoice_id: int) -> Decimal:
        r = await db.execute(
            select(
                func.coalesce(
                    func.sum(CustomerInvoiceSettleLink.applied_amount_incl_tax), 0
                )
            ).where(
                CustomerInvoiceSettleLink.invoice_id == invoice_id,
                CustomerInvoiceSettleLink.is_deleted == 0,
            )
        )
        return _money(Decimal(str(r.scalar() or 0)))

    @classmethod
    async def _items_total(cls, db: AsyncSession, invoice_id: int) -> Decimal:
        r = await db.execute(
            select(
                func.coalesce(func.sum(CustomerInvoiceItem.amount_incl_tax), 0)
            ).where(
                CustomerInvoiceItem.invoice_id == invoice_id,
                CustomerInvoiceItem.is_deleted == 0,
            )
        )
        return _money(Decimal(str(r.scalar() or 0)))

    @staticmethod
    async def _load_settles(
        db: AsyncSession, settle_ids: Sequence[int],
    ) -> Dict[int, CustomerSettlement]:
        if not settle_ids:
            return {}
        r = await db.execute(
            select(CustomerSettlement).where(
                CustomerSettlement.id.in_(list(settle_ids)),
                CustomerSettlement.is_deleted == 0,
            )
        )
        return {int(x.id): x for x in r.scalars().all()}

    @staticmethod
    async def _applied_by_invoice(
        db: AsyncSession, invoice_id: int, settle_ids: Sequence[int],
    ) -> Dict[int, Decimal]:
        if not settle_ids:
            return {}
        r = await db.execute(
            select(
                CustomerInvoiceSettleLink.settle_id,
                CustomerInvoiceSettleLink.applied_amount_incl_tax,
            ).where(
                CustomerInvoiceSettleLink.invoice_id == invoice_id,
                CustomerInvoiceSettleLink.settle_id.in_(list(settle_ids)),
                CustomerInvoiceSettleLink.is_deleted == 0,
            )
        )
        return {int(sid): Decimal(str(amt or 0)) for sid, amt in r.all()}

    @classmethod
    async def _assert_no_duplicate(
        cls,
        db: AsyncSession,
        invoice_code: Optional[str],
        invoice_no: str,
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        stmt = select(CustomerInvoice.id, CustomerInvoice.doc_no).where(
            CustomerInvoice.dedup_key == CustomerInvoice.build_dedup_key(
                invoice_code, invoice_no,
            ),
            CustomerInvoice.is_deleted == 0,
        )
        if exclude_id:
            stmt = stmt.where(CustomerInvoice.id != exclude_id)
        row = (await db.execute(stmt.limit(1))).one_or_none()
        if row is not None:
            raise BizException(
                f"这个发票号已经登记在 {row[1]} 上了，请核对票号后重填"
            )

    @staticmethod
    async def _get_customer_or_404(db: AsyncSession, customer_id: int) -> Customer:
        r = await db.execute(
            select(Customer).where(
                Customer.id == customer_id, Customer.is_deleted == 0,
            )
        )
        customer = r.scalar_one_or_none()
        if customer is None:
            raise BizException("客户不存在或已停用，请重新选择")
        return customer


def _money(v: Any) -> Decimal:
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)


def _dec(v: Any) -> Optional[Decimal]:
    if v is None or v == "":
        return None
    return Decimal(str(v))
