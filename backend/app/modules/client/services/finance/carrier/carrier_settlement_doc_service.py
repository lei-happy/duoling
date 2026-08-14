"""承运商结算单 Service（文档 03 §四）

对账单确认「事项」，结算单确认「要付多少钱」——它是唯一会锁任务成本的应付单据，
也是打款批次与进项票核销的对象。

与客户结算单对称，四处应付侧特有：

1. **付款账户必填且要校验状态**：付错账户的代价是钱进了别人的口袋，故付款时强制
   校验账户属于本承运商且处于启用中。
2. **纯抵账单**（``is_offset_only=1``）：任务级预付已把钱付完，对账净额为 0，这张
   单只做账面闭环，不校验金额为正、不要求付款凭证。
3. **付妥锁任务**：``lock_orchestrator.lock_tasks`` 批量锁定，撤销付款时按锁定来源
   精确解锁，不会误解他单的锁。
4. **进项票**：``invoice_matched`` / ``invoice_amount_total`` 由进项票 service 维护，
   本模块只在付款与撤销时读它给警示（票结未收票不阻断，见文档 11 §4.2）。
"""

from datetime import date as ddate, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.carrier_recon import (
    CarrierRecon,
    CarrierReconTaskLink,
)
from app.modules.client.models.finance.carrier_settlement_doc import (
    CARRIER_SETTLE_DOC_KIND,
    CarrierSettleReconLink,
    CarrierSettlementDoc,
)
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.models.partner.carrier_settlement import CarrierSettlement
from app.modules.client.services.finance.base.constants import (
    CarrierSettlementType,
    FinanceDirection,
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
    FinanceStateMachine,
    label as status_label,
)
from app.modules.client.services.finance.carrier.carrier_recon_service import (
    AMOUNT_TOLERANCE,
    CarrierReconService,
)
from app.modules.client.services.finance.linkage.lock_orchestrator import (
    LockOrchestrator,
)


class CarrierSettlementDocService(FinanceDocService):
    """承运商结算单"""

    model = CarrierSettlementDoc
    doc_kind = CARRIER_SETTLE_DOC_KIND
    doc_label = "承运商结算单"
    doc_no_prefix = "PS"
    direction = FinanceDirection.PAY

    # ------------------------------------------------------------------
    # 候选：可并入结算的已确认对账单
    # ------------------------------------------------------------------
    @classmethod
    async def list_recon_candidates(
        cls,
        db: AsyncSession,
        *,
        carrier_id: int,
        settle_id: Optional[int] = None,
        keyword: Optional[str] = None,
        limit: int = 200,
    ) -> List[dict]:
        """该承运商还有未结金额的「已确认」对账单。"""
        stmt = select(CarrierRecon).where(
            CarrierRecon.carrier_id == carrier_id,
            CarrierRecon.is_deleted == 0,
            CarrierRecon.status == FIN_REVIEWED,
        )
        if keyword:
            stmt = stmt.where(CarrierRecon.doc_no.like(f"%{keyword.strip()}%"))
        r = await db.execute(
            stmt.order_by(CarrierRecon.id.desc()).limit(max(1, int(limit)))
        )
        recons = list(r.scalars().all())
        if not recons:
            return []

        mine = await cls._applied_by_settle(
            db, settle_id, [int(x.id) for x in recons],
        )
        out = []
        for m in recons:
            available = cls._available_amount(m, mine.get(int(m.id)))
            if available <= 0:
                continue
            out.append({
                "reconId": int(m.id),
                "docNo": m.doc_no,
                "periodStart": m.period_start,
                "periodEnd": m.period_end,
                "taskCount": int(m.task_count or 0),
                "grossAmountTotal": float(m.gross_amount_total or 0),
                "prepaidOffsetTotal": float(m.prepaid_offset_total or 0),
                "plannedAmount": float(m.planned_amount or 0),
                "appliedAmountTotal": float(m.applied_amount_total or 0),
                "availableAmount": float(available),
                "confirmedByCarrierAt": m.confirmed_by_carrier_at,
                "diffForcedCount": int(m.diff_forced_count or 0),
            })
        return out

    @classmethod
    async def list_accounts(
        cls, db: AsyncSession, carrier_id: int,
    ) -> List[dict]:
        """该承运商可用的结算账户（付款弹窗的下拉数据）。"""
        r = await db.execute(
            select(CarrierSettlement)
            .where(
                CarrierSettlement.carrier_id == carrier_id,
                CarrierSettlement.is_deleted == 0,
                CarrierSettlement.status == 1,
            )
            .order_by(
                CarrierSettlement.is_default.desc(),
                CarrierSettlement.sort_order.asc(),
                CarrierSettlement.id.asc(),
            )
        )
        return [
            {
                "accountId": int(a.id),
                "accountLabel": a.account_label,
                "accountType": int(a.account_type or 0),
                "settlementType": int(a.settlement_type or 0),
                "bankName": a.bank_name,
                "bankAccountMasked": _mask_account(a.bank_account),
                "bankAccountName": a.bank_account_name,
                "isDefault": int(a.is_default or 0),
            }
            for a in r.scalars().all()
        ]

    # ------------------------------------------------------------------
    # 创建与关联维护
    # ------------------------------------------------------------------
    @classmethod
    async def create_from_recons(
        cls,
        db: AsyncSession,
        *,
        carrier_id: int,
        recons: Sequence[dict],
        settlement_account_id: Optional[int] = None,
        due_date: Optional[ddate] = None,
        is_offset_only: int = 0,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CarrierSettlementDoc:
        """按选中对账单生成草稿结算单。

        ``recons`` 每项 ``{"reconId": int, "appliedAmount": Decimal | None}``，
        金额留空表示「认领该对账单的全部未结金额」。
        """
        carrier = await cls._get_carrier_or_404(db, carrier_id)
        if not recons:
            raise BizException("请至少选择一张已确认的对账单")

        account = None
        if settlement_account_id:
            account = await cls._get_account_or_404(
                db, carrier_id, int(settlement_account_id),
            )
        else:
            account = await CarrierReconService.default_account(db, carrier_id)

        settle = CarrierSettlementDoc(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.PAY,
            status=FIN_DRAFT,
            carrier_id=carrier_id,
            carrier_name=carrier.carrier_name,
            enterprise_id=carrier.enterprise_id,
            settlement_account_id=(int(account.id) if account else None),
            settlement_account_label=(account.account_label if account else None),
            bank_name=(account.bank_name if account else None),
            bank_account_masked=(
                _mask_account(account.bank_account) if account else None
            ),
            planned_amount=Decimal("0"),
            due_date=due_date,
            is_offset_only=1 if is_offset_only else 0,
            created_by=operator_id,
            remark=remark,
        )
        db.add(settle)
        await db.flush()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=settle.id,
            event_type=FinanceEventType.CREATE,
            to_status=FIN_DRAFT,
            direction=FinanceDirection.PAY,
            operator_id=operator_id,
            payload_snapshot={"carrierId": carrier_id},
        )
        await cls.link_recons(db, settle.id, recons, operator_id=operator_id)
        return settle

    @classmethod
    async def link_recons(
        cls,
        db: AsyncSession,
        settle_id: int,
        recons: Sequence[dict],
        *,
        operator_id: Optional[int] = None,
    ) -> List[CarrierSettleReconLink]:
        """关联对账单（已关联的按新金额更新）。"""
        settle = await cls.get_or_404(db, settle_id)
        cls.assert_editable(settle)
        if not recons:
            raise BizException("请选择要关联的对账单")

        existing = {
            int(x.recon_id): x
            for x in await cls._load_links(db, settle_id)
        }
        recon_ids = [int(x.get("reconId")) for x in recons if x.get("reconId")]
        models = await cls._load_recons(db, recon_ids)
        mine = await cls._applied_by_settle(db, settle_id, recon_ids)

        rows: List[CarrierSettleReconLink] = []
        for item in recons:
            rid = int(item.get("reconId"))
            recon = models.get(rid)
            if recon is None:
                raise BizException("对账单不存在或已删除，请刷新后重试")
            cls._assert_linkable(recon, int(settle.carrier_id))

            available = cls._available_amount(recon, mine.get(rid))
            if available <= 0:
                raise BizException(
                    f"对账单 {recon.doc_no} 的金额已被其他结算单认领完，"
                    "无需再结算；如需调整请先撤销那张结算单"
                )
            raw = item.get("appliedAmount")
            amount = (
                Decimal(str(raw)) if raw is not None else available
            ).quantize(Decimal("0.01"))
            if amount <= 0:
                raise BizException(
                    f"对账单 {recon.doc_no} 的认领金额必须大于 0"
                )
            if amount > available + AMOUNT_TOLERANCE:
                raise BizException(
                    f"对账单 {recon.doc_no} 还剩 {available:.2f} 元未结算，"
                    f"最多只能认领这么多"
                )

            row = existing.get(rid)
            if row is None:
                row = CarrierSettleReconLink(
                    settle_id=settle_id,
                    recon_id=rid,
                    recon_doc_no=recon.doc_no,
                    applied_amount=amount,
                    dedup_key=CarrierSettleReconLink.build_dedup_key(
                        settle_id, rid,
                    ),
                )
                db.add(row)
            else:
                row.applied_amount = amount
            if item.get("remark") is not None:
                row.remark = item.get("remark")
            rows.append(row)
        await db.flush()

        await cls.refresh_totals(db, settle_id)
        for rid in {int(x.recon_id) for x in rows}:
            await CarrierReconService.refresh_settle_progress(
                db, rid, operator_id=operator_id,
            )
        return rows

    @classmethod
    async def unlink_recon(
        cls,
        db: AsyncSession,
        settle_id: int,
        link_id: int,
        *,
        operator_id: Optional[int] = None,
    ) -> None:
        """解除一条对账单关联（软删并释放去重键）。"""
        settle = await cls.get_or_404(db, settle_id)
        cls.assert_editable(settle)
        r = await db.execute(
            select(CarrierSettleReconLink).where(
                CarrierSettleReconLink.id == link_id,
                CarrierSettleReconLink.settle_id == settle_id,
                CarrierSettleReconLink.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("关联的对账单不存在或已解除")
        recon_id = int(row.recon_id)
        row.is_deleted = 1
        row.dedup_key = None
        await db.flush()
        await cls.refresh_totals(db, settle_id)
        await CarrierReconService.refresh_settle_progress(
            db, recon_id, operator_id=operator_id,
        )

    @classmethod
    async def refresh_totals(cls, db: AsyncSession, settle_id: int) -> None:
        """重算计划付款额与关联数（桥接行变动后调用）。"""
        r = await db.execute(
            select(
                func.count(CarrierSettleReconLink.id),
                func.coalesce(
                    func.sum(CarrierSettleReconLink.applied_amount), 0
                ),
            ).where(
                CarrierSettleReconLink.settle_id == settle_id,
                CarrierSettleReconLink.is_deleted == 0,
            )
        )
        count, amount = r.one()
        settle = await cls.get_or_404(db, settle_id)
        settle.recon_count = int(count or 0)
        settle.planned_amount = Decimal(str(amount or 0))
        await db.flush()

    @classmethod
    async def update_account(
        cls,
        db: AsyncSession,
        settle_id: int,
        *,
        settlement_account_id: int,
        operator_id: Optional[int] = None,
    ) -> CarrierSettlementDoc:
        """改付款账户（草稿与已审批都允许：出纳临付款前换账户是常态）。"""
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) not in (FIN_DRAFT, FIN_PENDING_REVIEW, FIN_REVIEWED):
            raise BizException(
                f"结算单当前是「{cls.status_text(settle)}」，不能再改付款账户"
            )
        account = await cls._get_account_or_404(
            db, int(settle.carrier_id), int(settlement_account_id),
        )
        settle.settlement_account_id = int(account.id)
        settle.settlement_account_label = account.account_label
        settle.bank_name = account.bank_name
        settle.bank_account_masked = _mask_account(account.bank_account)
        await db.flush()
        return settle

    # ------------------------------------------------------------------
    # 状态流转
    # ------------------------------------------------------------------
    @classmethod
    async def submit(
        cls, db: AsyncSession, doc_id: int, operator_id: Optional[int] = None,
    ) -> CarrierSettlementDoc:
        """草稿 → 待审批（至少 1 张对账单；纯抵账单允许金额为 0）。"""
        settle = await cls.get_or_404(db, doc_id)
        if int(settle.recon_count or 0) <= 0:
            raise BizException("请先关联至少一张已确认的对账单再提交")
        if int(settle.is_offset_only or 0) == 1:
            if Decimal(str(settle.planned_amount or 0)) < 0:
                raise BizException("抵账单的金额不能为负数，请检查对账明细")
        else:
            FinanceStateMachine.assert_submittable(
                planned_amount=settle.planned_amount,
            )
        await cls.change_status(
            db, settle, FIN_PENDING_REVIEW,
            event_type=FinanceEventType.SUBMIT,
            operator_id=operator_id,
            occurred_amount=settle.planned_amount,
        )
        return settle

    @classmethod
    async def pay(
        cls,
        db: AsyncSession,
        settle_id: int,
        *,
        actual_amount: Optional[Decimal] = None,
        paid_at: Optional[datetime] = None,
        pay_method: Optional[int] = None,
        pay_voucher_url: Optional[str] = None,
        settlement_account_id: Optional[int] = None,
        operator_id: Optional[int] = None,
    ) -> CarrierSettlementDoc:
        """已审批 → 已支付，并锁定关联任务的成本字段。

        纯抵账单不校验金额与凭证：账上本来就没有钱要动。其余情况要求金额、时间、
        方式齐全，且付款账户属于本承运商并处于启用中。
        """
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) != FIN_REVIEWED:
            raise BizException(
                f"只有已审批的结算单可以登记付款"
                f"（当前：{cls.status_text(settle)}）"
            )
        offset_only = int(settle.is_offset_only or 0) == 1
        planned = Decimal(str(settle.planned_amount or 0))
        when = paid_at or datetime.now()

        if offset_only:
            amount = Decimal(str(actual_amount or planned))
        else:
            if settlement_account_id:
                await cls.update_account(
                    db, settle_id,
                    settlement_account_id=int(settlement_account_id),
                    operator_id=operator_id,
                )
            await cls._assert_account_payable(db, settle)
            amount = Decimal(str(actual_amount if actual_amount is not None else planned))
            FinanceStateMachine.assert_payable(
                actual_amount=amount, paid_at=when, pay_method=pay_method,
            )
            if amount > planned + AMOUNT_TOLERANCE:
                raise BizException(
                    f"付款金额不能超过应付金额 {planned:.2f} 元；"
                    "确需多付请先调整对账单金额"
                )
            if amount + AMOUNT_TOLERANCE < planned:
                raise BizException(
                    f"本次付款 {amount:.2f} 元少于应付 {planned:.2f} 元；"
                    "分批付款请到出纳台用打款批次执行"
                )

        settle.actual_amount = amount
        settle.paid_at = when
        settle.pay_method = pay_method
        settle.paid_amount_total = amount
        if pay_voucher_url:
            settle.pay_voucher_url = pay_voucher_url

        warn = await cls._invoice_warning(db, settle)
        await cls.change_status(
            db, settle, FIN_PAID,
            event_type=FinanceEventType.PAY,
            operator_id=operator_id,
            occurred_amount=amount,
            payload_snapshot={
                "isOffsetOnly": 1 if offset_only else 0,
                "accountId": settle.settlement_account_id,
                "invoiceWarning": warn,
            },
        )

        task_ids = await cls.task_ids_of(db, settle_id)
        locked = await LockOrchestrator.lock_tasks(
            db, task_ids, by_doc_id=settle_id,
        )
        if locked:
            await FinanceDocEventWriter.write(
                db,
                doc_kind=cls.doc_kind,
                doc_id=settle_id,
                event_type=FinanceEventType.LOCK,
                direction=FinanceDirection.PAY,
                operator_id=operator_id,
                reason=f"付款完成，已锁定 {locked} 个任务的成本",
            )
            await db.flush()
        await cls._refresh_recon_progress(db, settle_id, operator_id)
        return settle

    @classmethod
    async def cancel_payment(
        cls,
        db: AsyncSession,
        settle_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CarrierSettlementDoc:
        """撤销付款（3→2，高权限）：解锁任务、清空付款字段。"""
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) != FIN_PAID:
            raise BizException(
                f"只有已支付的结算单可以撤销付款"
                f"（当前：{cls.status_text(settle)}）"
            )
        if Decimal(str(settle.invoice_amount_total or 0)) > 0:
            raise BizException(
                "本单已核销进项发票，不能撤销付款；请先在进项发票里撤销核销"
            )
        if settle.batch_id:
            raise BizException(
                "本单已进入打款批次，请先在出纳台把它从批次中移出再撤销付款"
            )
        text = cls.assert_reason(reason, action="撤销付款")
        amount = settle.actual_amount

        await cls.change_status(
            db, settle, FIN_REVIEWED,
            event_type=FinanceEventType.CANCEL_PAY,
            operator_id=operator_id,
            reason=text,
            occurred_amount=(-amount if amount is not None else None),
            skip_lock_check=True,
        )
        settle.actual_amount = None
        settle.paid_at = None
        settle.pay_method = None
        settle.pay_voucher_url = None
        settle.paid_amount_total = Decimal("0")
        await db.flush()

        await LockOrchestrator.unlock_tasks(db, by_doc_id=settle_id)
        await cls._refresh_recon_progress(db, settle_id, operator_id)
        return settle

    @classmethod
    async def cancel_settlement(
        cls,
        db: AsyncSession,
        settle_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CarrierSettlementDoc:
        """撤销结算单：释放对账单认领额度、解除去重键。"""
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) == FIN_CANCELLED:
            raise BizException("该结算单已撤销，无需重复操作")
        if int(settle.status) == FIN_PAID:
            raise BizException("已支付的结算单请先撤销付款，再撤销单据")
        text = cls.assert_reason(reason)
        recon_ids = [int(x.recon_id) for x in await cls._load_links(db, settle_id)]

        await cls.change_status(
            db, settle, FIN_CANCELLED,
            event_type=FinanceEventType.CANCEL,
            operator_id=operator_id,
            reason=text,
        )
        for row in await cls._load_links(db, settle_id):
            row.dedup_key = None
        await db.flush()
        for rid in set(recon_ids):
            await CarrierReconService.refresh_settle_progress(
                db, rid, operator_id=operator_id,
            )
        return settle

    # ------------------------------------------------------------------
    # 进项票联动（由 VendorInvoiceService 调用）
    # ------------------------------------------------------------------
    @classmethod
    async def refresh_invoice_progress(
        cls,
        db: AsyncSession,
        settle_id: int,
        *,
        operator_id: Optional[int] = None,
    ) -> CarrierSettlementDoc:
        """按已核销进项票重算收票进度，收齐则置 ``invoice_matched=1`` 并写事件 25。"""
        from app.modules.client.models.finance.vendor_invoice import (
            VendorInvoiceSettleLink,
        )

        settle = await cls.get_or_404(db, settle_id)
        r = await db.execute(
            select(
                func.coalesce(
                    func.sum(VendorInvoiceSettleLink.applied_amount), 0
                )
            ).where(
                VendorInvoiceSettleLink.settle_id == settle_id,
                VendorInvoiceSettleLink.is_deleted == 0,
            )
        )
        total = Decimal(str(r.scalar() or 0))
        planned = Decimal(str(settle.planned_amount or 0))
        was_matched = int(settle.invoice_matched or 0) == 1
        matched = planned > 0 and total + AMOUNT_TOLERANCE >= planned

        settle.invoice_amount_total = total
        settle.invoice_matched = 1 if matched else 0
        await db.flush()

        if matched and not was_matched:
            await FinanceDocEventWriter.write(
                db,
                doc_kind=cls.doc_kind,
                doc_id=settle_id,
                event_type=FinanceEventType.INVOICE_MATCH,
                direction=FinanceDirection.PAY,
                occurred_amount=total,
                operator_id=operator_id,
                reason="进项发票已收齐，票款相符",
                payload_snapshot={
                    "plannedAmount": float(planned),
                    "invoiceAmountTotal": float(total),
                },
            )
            await db.flush()
        return settle

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
        carrier_id: Optional[int] = None,
        enterprise_id: Optional[int] = None,
        status: Optional[int] = None,
        due_before: Optional[ddate] = None,
        invoice_matched: Optional[int] = None,
        only_payable: bool = False,
    ) -> Tuple[List[CarrierSettlementDoc], int]:
        stmt = select(CarrierSettlementDoc).where(
            CarrierSettlementDoc.is_deleted == 0
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                CarrierSettlementDoc.doc_no.like(kw)
                | CarrierSettlementDoc.carrier_name.like(kw)
            )
        if carrier_id:
            stmt = stmt.where(CarrierSettlementDoc.carrier_id == carrier_id)
        if enterprise_id:
            stmt = stmt.where(CarrierSettlementDoc.enterprise_id == enterprise_id)
        if status is not None:
            stmt = stmt.where(CarrierSettlementDoc.status == status)
        if due_before:
            stmt = stmt.where(CarrierSettlementDoc.due_date <= due_before)
        if invoice_matched is not None:
            stmt = stmt.where(
                CarrierSettlementDoc.invoice_matched == invoice_matched
            )
        if only_payable:
            # 出纳台「可付款」口径：已审批且未入批
            stmt = stmt.where(
                CarrierSettlementDoc.status == FIN_REVIEWED,
                CarrierSettlementDoc.batch_id.is_(None),
            )

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(CarrierSettlementDoc.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_links(
        cls, db: AsyncSession, settle_id: int,
    ) -> List[CarrierSettleReconLink]:
        return await cls._load_links(db, settle_id)

    @classmethod
    async def list_invoice_links(cls, db: AsyncSession, settle_id: int) -> List:
        """本单的进项票构成（详情页「发票」区块）。"""
        from app.modules.client.models.finance.vendor_invoice import (
            VendorInvoiceSettleLink,
        )

        r = await db.execute(
            select(VendorInvoiceSettleLink)
            .where(
                VendorInvoiceSettleLink.settle_id == settle_id,
                VendorInvoiceSettleLink.is_deleted == 0,
            )
            .order_by(VendorInvoiceSettleLink.id.asc())
        )
        return list(r.scalars().all())

    @classmethod
    async def task_ids_of(cls, db: AsyncSession, settle_id: int) -> List[int]:
        """本结算单覆盖的任务（经对账单桥接两跳取得）。"""
        r = await db.execute(
            select(CarrierReconTaskLink.task_id)
            .join(
                CarrierSettleReconLink,
                CarrierSettleReconLink.recon_id == CarrierReconTaskLink.recon_id,
            )
            .where(
                CarrierSettleReconLink.settle_id == settle_id,
                CarrierSettleReconLink.is_deleted == 0,
                CarrierReconTaskLink.is_deleted == 0,
            )
        )
        return [int(x) for x in r.scalars().all()]

    @classmethod
    def status_text(cls, settle: Any) -> str:
        return status_label(int(settle.status or 0), cls.doc_kind)

    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        flags = super().action_flags(doc)
        status = int(doc.status)
        planned = Decimal(str(doc.planned_amount or 0))
        invoiced = Decimal(str(doc.invoice_amount_total or 0))
        flags.update({
            "canLinkRecon": status == FIN_DRAFT,
            "canChangeAccount": status in (
                FIN_DRAFT, FIN_PENDING_REVIEW, FIN_REVIEWED,
            ),
            "canPay": status == FIN_REVIEWED,
            "canCancelPay": (
                status == FIN_PAID and invoiced <= 0 and not doc.batch_id
            ),
            "canMatchInvoice": status in (FIN_REVIEWED, FIN_PAID),
            "invoiceGapAmount": float(max(planned - invoiced, Decimal("0"))),
        })
        return flags

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @classmethod
    async def _invoice_warning(
        cls, db: AsyncSession, settle: CarrierSettlementDoc,
    ) -> Optional[str]:
        """票结承运商未收齐票时的警示文案（只提示，不阻断付款）。"""
        if int(settle.invoice_matched or 0) == 1:
            return None
        if not settle.settlement_account_id:
            return None
        r = await db.execute(
            select(CarrierSettlement.settlement_type).where(
                CarrierSettlement.id == settle.settlement_account_id,
            )
        )
        stype = r.scalar_one_or_none()
        if stype is not None and int(stype) == CarrierSettlementType.BY_INVOICE:
            return "该承运商为票结，付款时尚未收齐进项发票，请及时催票"
        return None

    @classmethod
    async def _assert_account_payable(
        cls, db: AsyncSession, settle: CarrierSettlementDoc,
    ) -> None:
        if not settle.settlement_account_id:
            raise BizException("请先选择付款账户，再登记付款")
        await cls._get_account_or_404(
            db, int(settle.carrier_id), int(settle.settlement_account_id),
        )

    @staticmethod
    async def _get_account_or_404(
        db: AsyncSession, carrier_id: int, account_id: int,
    ) -> CarrierSettlement:
        return await CarrierReconService.get_account_or_404(
            db, carrier_id, account_id,
        )

    @classmethod
    async def _refresh_recon_progress(
        cls, db: AsyncSession, settle_id: int, operator_id: Optional[int],
    ) -> None:
        for row in await cls._load_links(db, settle_id):
            await CarrierReconService.refresh_settle_progress(
                db, int(row.recon_id), operator_id=operator_id,
            )

    @staticmethod
    def _available_amount(
        recon: CarrierRecon, mine: Optional[Decimal],
    ) -> Decimal:
        planned = Decimal(str(recon.planned_amount or 0))
        applied = Decimal(str(recon.applied_amount_total or 0))
        return planned - applied + Decimal(str(mine or 0))

    @staticmethod
    def _assert_linkable(recon: CarrierRecon, carrier_id: int) -> None:
        if int(recon.carrier_id or 0) != int(carrier_id):
            raise BizException(
                f"对账单 {recon.doc_no} 属于其他承运商，不能并入本结算单"
            )
        if int(recon.status) not in (FIN_REVIEWED, FIN_PAID):
            raise BizException(
                f"对账单 {recon.doc_no} 还未确认，请先确认对账单再结算"
            )

    @staticmethod
    async def _get_carrier_or_404(db: AsyncSession, carrier_id: int) -> Carrier:
        r = await db.execute(
            select(Carrier).where(
                Carrier.id == carrier_id, Carrier.is_deleted == 0,
            )
        )
        c = r.scalar_one_or_none()
        if c is None:
            raise BizException("承运商不存在或已停用，请重新选择")
        return c

    @staticmethod
    async def _load_links(
        db: AsyncSession, settle_id: int,
    ) -> List[CarrierSettleReconLink]:
        r = await db.execute(
            select(CarrierSettleReconLink)
            .where(
                CarrierSettleReconLink.settle_id == settle_id,
                CarrierSettleReconLink.is_deleted == 0,
            )
            .order_by(CarrierSettleReconLink.id.asc())
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_recons(
        db: AsyncSession, recon_ids: Sequence[int],
    ) -> Dict[int, CarrierRecon]:
        if not recon_ids:
            return {}
        r = await db.execute(
            select(CarrierRecon).where(
                CarrierRecon.id.in_(list(recon_ids)),
                CarrierRecon.is_deleted == 0,
            )
        )
        return {int(x.id): x for x in r.scalars().all()}

    @staticmethod
    async def _applied_by_settle(
        db: AsyncSession,
        settle_id: Optional[int],
        recon_ids: Sequence[int],
    ) -> Dict[int, Decimal]:
        if settle_id is None or not recon_ids:
            return {}
        r = await db.execute(
            select(
                CarrierSettleReconLink.recon_id,
                CarrierSettleReconLink.applied_amount,
            ).where(
                CarrierSettleReconLink.settle_id == settle_id,
                CarrierSettleReconLink.recon_id.in_(list(recon_ids)),
                CarrierSettleReconLink.is_deleted == 0,
            )
        )
        return {int(rid): Decimal(str(amt or 0)) for rid, amt in r.all()}


def _mask_account(account_no: Optional[str]) -> Optional[str]:
    """账号脱敏：只留后四位。付款账户要能核对，但不该在列表页全量暴露。"""
    if not account_no:
        return None
    text = str(account_no).strip()
    if len(text) <= 4:
        return text
    return f"****{text[-4:]}"
