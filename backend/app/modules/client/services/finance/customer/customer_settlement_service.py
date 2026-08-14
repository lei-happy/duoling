"""客户结算单 Service（文档 02 §四）

对账单确认「事项」，结算单确认「要收多少钱」——它才是应收账龄的原子单位，也是
唯一会锁运单的应收单据。

三个容易混的金额（这里钉死，全模块统一）：

- ``planned_amount``：应收金额 = Σ 桥接行 ``applied_amount``，行变动即重算；
- ``received_amount_total``：已收累计 = Σ 有效收款核销明细，未满额时单据仍停在
  已审批；账龄按 ``planned_amount - received_amount_total`` 取未收余额；
- ``actual_amount``：正式收妥金额，只在满额置「已收款」时写一次。

收款两条路径（§4.6）互斥：单据直登与收款单核销都要求 ``status=2``，且本 service
在直登时额外拒绝「已有核销记录」的单据——否则同一笔钱会被记两次。
"""

from datetime import date as ddate, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.customer_recon import (
    CustomerRecon,
    CustomerReconWaybillLink,
)
from app.modules.client.models.finance.customer_settlement import (
    CUSTOMER_SETTLE_DOC_KIND,
    CustomerSettleReconLink,
    CustomerSettlement,
)
from app.modules.client.models.finance.receipt_voucher import ReceiptSettleLink
from app.modules.client.models.partner.customer import Customer
from app.modules.client.services.finance.base.constants import FinanceDirection
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
from app.modules.client.services.finance.customer.customer_recon_service import (
    AMOUNT_TOLERANCE,
    CustomerReconService,
)
from app.modules.client.services.finance.linkage.lock_orchestrator import (
    LockOrchestrator,
)


class CustomerSettlementService(FinanceDocService):
    """客户结算单"""

    model = CustomerSettlement
    doc_kind = CUSTOMER_SETTLE_DOC_KIND
    doc_label = "客户结算单"
    doc_no_prefix = "CS"
    direction = FinanceDirection.RECEIVE

    # ------------------------------------------------------------------
    # 候选：可并入结算的已确认对账单
    # ------------------------------------------------------------------
    @classmethod
    async def list_recon_candidates(
        cls,
        db: AsyncSession,
        *,
        customer_id: int,
        settle_id: Optional[int] = None,
        keyword: Optional[str] = None,
        limit: int = 200,
    ) -> List[dict]:
        """该客户还有未结金额的「已确认」对账单。

        ``settle_id`` 用于编辑既有结算单：本单已认领的金额要还回可用额度，
        否则改一次金额就再也加不回来。
        """
        stmt = select(CustomerRecon).where(
            CustomerRecon.customer_id == customer_id,
            CustomerRecon.is_deleted == 0,
            CustomerRecon.status == FIN_REVIEWED,
        )
        if keyword:
            stmt = stmt.where(CustomerRecon.doc_no.like(f"%{keyword.strip()}%"))
        r = await db.execute(
            stmt.order_by(CustomerRecon.id.desc()).limit(max(1, int(limit)))
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
                "waybillCount": int(m.waybill_count or 0),
                "plannedAmount": float(m.planned_amount or 0),
                "appliedAmountTotal": float(m.applied_amount_total or 0),
                "availableAmount": float(available),
                "confirmedByCustomerAt": m.confirmed_by_customer_at,
                "diffForcedCount": int(m.diff_forced_count or 0),
            })
        return out

    # ------------------------------------------------------------------
    # 创建与关联维护
    # ------------------------------------------------------------------
    @classmethod
    async def create_from_recons(
        cls,
        db: AsyncSession,
        *,
        customer_id: int,
        recons: Sequence[dict],
        due_date: Optional[ddate] = None,
        invoice_required: int = 0,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerSettlement:
        """按选中对账单生成草稿结算单。

        ``recons`` 每项 ``{"reconId": int, "appliedAmount": Decimal | None}``，
        金额留空表示「认领该对账单的全部未结金额」。
        """
        customer = await cls._get_customer_or_404(db, customer_id)
        if not recons:
            raise BizException("请至少选择一张已确认的对账单")

        settle = CustomerSettlement(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.RECEIVE,
            status=FIN_DRAFT,
            customer_id=customer_id,
            customer_name=customer.customer_name,
            enterprise_id=customer.enterprise_id,
            planned_amount=Decimal("0"),
            due_date=due_date,
            invoice_required=1 if invoice_required else 0,
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
            direction=FinanceDirection.RECEIVE,
            operator_id=operator_id,
            payload_snapshot={"customerId": customer_id},
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
    ) -> List[CustomerSettleReconLink]:
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

        rows: List[CustomerSettleReconLink] = []
        for item in recons:
            rid = int(item.get("reconId"))
            recon = models.get(rid)
            if recon is None:
                raise BizException("对账单不存在或已删除，请刷新后重试")
            cls._assert_linkable(recon, int(settle.customer_id))

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
                row = CustomerSettleReconLink(
                    settle_id=settle_id,
                    recon_id=rid,
                    recon_doc_no=recon.doc_no,
                    applied_amount=amount,
                    dedup_key=CustomerSettleReconLink.build_dedup_key(
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
            await CustomerReconService.refresh_settle_progress(
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
            select(CustomerSettleReconLink).where(
                CustomerSettleReconLink.id == link_id,
                CustomerSettleReconLink.settle_id == settle_id,
                CustomerSettleReconLink.is_deleted == 0,
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
        await CustomerReconService.refresh_settle_progress(
            db, recon_id, operator_id=operator_id,
        )

    @classmethod
    async def refresh_totals(cls, db: AsyncSession, settle_id: int) -> None:
        """重算应收金额与关联数（桥接行变动后调用）。"""
        r = await db.execute(
            select(
                func.count(CustomerSettleReconLink.id),
                func.coalesce(
                    func.sum(CustomerSettleReconLink.applied_amount), 0
                ),
            ).where(
                CustomerSettleReconLink.settle_id == settle_id,
                CustomerSettleReconLink.is_deleted == 0,
            )
        )
        count, amount = r.one()
        settle = await cls.get_or_404(db, settle_id)
        settle.recon_count = int(count or 0)
        settle.planned_amount = Decimal(str(amount or 0))
        await db.flush()

    # ------------------------------------------------------------------
    # 状态流转
    # ------------------------------------------------------------------
    @classmethod
    async def submit(
        cls, db: AsyncSession, doc_id: int, operator_id: Optional[int] = None,
    ) -> CustomerSettlement:
        """草稿 → 待审批（至少 1 张对账单、金额为正）。"""
        settle = await cls.get_or_404(db, doc_id)
        if int(settle.recon_count or 0) <= 0:
            raise BizException("请先关联至少一张已确认的对账单再提交")
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
    async def receive(
        cls,
        db: AsyncSession,
        settle_id: int,
        *,
        actual_amount: Decimal,
        received_at: datetime,
        receive_method: Optional[int],
        received_account_id: Optional[int] = None,
        received_account_label: Optional[str] = None,
        voucher_url: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerSettlement:
        """单据直登收款（2→3），并锁定关联运单。

        已有核销记录的单据不允许直登：那笔钱应该继续走收款单核销，否则同一笔到账
        会在两条路径上各记一次。
        """
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) != FIN_REVIEWED:
            raise BizException(
                f"只有已审批的结算单可以登记收款"
                f"（当前：{cls.status_text(settle)}）"
            )
        if Decimal(str(settle.received_amount_total or 0)) > 0:
            raise BizException(
                "本单已有到账核销记录，请到出纳台用收款单继续核销，"
                "不要重复登记收款"
            )
        FinanceStateMachine.assert_payable(
            actual_amount=actual_amount,
            paid_at=received_at,
            pay_method=receive_method,
        )
        amount = Decimal(str(actual_amount))
        planned = Decimal(str(settle.planned_amount or 0))
        if amount > planned + AMOUNT_TOLERANCE:
            raise BizException(
                f"收款金额不能超过应收金额 {planned:.2f} 元；"
                "多收的部分请用收款单登记，留在未核销余额里"
            )
        if amount + AMOUNT_TOLERANCE < planned:
            raise BizException(
                f"本次收款 {amount:.2f} 元少于应收 {planned:.2f} 元，"
                "分次到账请到出纳台用收款单核销"
            )

        cls._apply_receive_fields(
            settle,
            amount=amount,
            received_at=received_at,
            receive_method=receive_method,
            account_id=received_account_id,
            account_label=received_account_label,
            voucher_url=voucher_url,
        )
        settle.received_amount_total = amount
        await cls._to_received(db, settle, operator_id=operator_id)
        return settle

    @classmethod
    async def apply_receipt(
        cls,
        db: AsyncSession,
        settle_id: int,
        *,
        amount: Decimal,
        received_at: Optional[datetime] = None,
        receive_method: Optional[int] = None,
        account_id: Optional[int] = None,
        account_label: Optional[str] = None,
        voucher_url: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerSettlement:
        """收款单核销驱动：累加已收，满额自动置「已收款」并锁运单。

        由 ``ReceiptVoucherService`` 调用；``amount`` 是本单核销后的**累计**已收额，
        由收款单侧按有效核销明细汇总后传入，避免两处各自增减导致漂移。
        """
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) not in (FIN_REVIEWED, FIN_PAID):
            raise BizException(
                f"结算单 {settle.doc_no} 当前是「{cls.status_text(settle)}」，"
                "不能核销到账；只有已审批的结算单可以核销"
            )
        total = Decimal(str(amount))
        planned = Decimal(str(settle.planned_amount or 0))
        if total > planned + AMOUNT_TOLERANCE:
            raise BizException(
                f"结算单 {settle.doc_no} 应收 {planned:.2f} 元，"
                f"核销累计 {total:.2f} 元已超额，请调整核销金额"
            )
        settle.received_amount_total = total
        covered = planned > 0 and total + AMOUNT_TOLERANCE >= planned

        if covered and int(settle.status) == FIN_REVIEWED:
            cls._apply_receive_fields(
                settle,
                amount=total,
                received_at=received_at or datetime.now(),
                receive_method=receive_method,
                account_id=account_id,
                account_label=account_label,
                voucher_url=voucher_url,
            )
            await cls._to_received(db, settle, operator_id=operator_id)
        else:
            await db.flush()
            await cls._refresh_recon_progress(db, settle.id, operator_id)
        return settle

    @classmethod
    async def assert_receipt_reversible(
        cls, db: AsyncSession, settle_id: int,
    ) -> None:
        """撤销核销的前置校验。

        单独成方法是为了让收款单侧**在删明细之前**就能拦下来：已收妥的单据必须
        先撤销收款（高权限、会解锁运单），否则钱退回去了运单还锁着、账龄也还是 0。
        """
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) == FIN_PAID:
            raise BizException(
                f"结算单 {settle.doc_no} 已收妥，需先在结算单上撤销收款，"
                "再撤销这笔核销"
            )

    @classmethod
    async def unapply_receipt(
        cls,
        db: AsyncSession,
        settle_id: int,
        *,
        amount: Decimal,
        operator_id: Optional[int] = None,
    ) -> CustomerSettlement:
        """撤销核销后回写已收累计（``amount`` 为撤销后的累计值）。"""
        await cls.assert_receipt_reversible(db, settle_id)
        settle = await cls.get_or_404(db, settle_id)
        settle.received_amount_total = Decimal(str(amount))
        await db.flush()
        await cls._refresh_recon_progress(db, settle.id, operator_id)
        return settle

    @classmethod
    async def cancel_receive(
        cls,
        db: AsyncSession,
        settle_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CustomerSettlement:
        """撤销收款（3→2，高权限）：解锁运单、按有效核销重算已收累计。"""
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) != FIN_PAID:
            raise BizException(
                f"只有已收款的结算单可以撤销收款"
                f"（当前：{cls.status_text(settle)}）"
            )
        if int(settle.invoice_count or 0) > 0:
            raise BizException(
                "本单已开发票，不能撤销收款；请先作废或红冲发票"
            )
        text = cls.assert_reason(reason, action="撤销收款")
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
        settle.received_at = None
        settle.received_voucher_url = None
        settle.received_account_id = None
        settle.received_account_label = None
        # 已收累计回到「有效核销明细之和」：直登的没有明细即归零，
        # 核销驱动的保留已认领部分，单据退回已审批继续等后续到账
        settle.received_amount_total = await cls.settled_amount_of(db, settle_id)
        await db.flush()

        await LockOrchestrator.unlock_waybills(db, by_doc_id=settle_id)
        await cls._refresh_recon_progress(db, settle_id, operator_id)
        return settle

    @classmethod
    async def cancel_settlement(
        cls,
        db: AsyncSession,
        settle_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CustomerSettlement:
        """撤销结算单：释放对账单认领额度、解除去重键。"""
        settle = await cls.get_or_404(db, settle_id)
        if int(settle.status) == FIN_CANCELLED:
            raise BizException("该结算单已撤销，无需重复操作")
        if int(settle.status) == FIN_PAID:
            raise BizException(
                "已收款的结算单请先撤销收款，再撤销单据"
            )
        if await cls.settled_amount_of(db, settle_id) > 0:
            raise BizException(
                "本单已有到账核销记录，请先在出纳台撤销核销再撤销单据"
            )
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
            await CustomerReconService.refresh_settle_progress(
                db, rid, operator_id=operator_id,
            )
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
        customer_id: Optional[int] = None,
        enterprise_id: Optional[int] = None,
        status: Optional[int] = None,
        due_before: Optional[ddate] = None,
        only_unreceived: bool = False,
        invoice_required: Optional[int] = None,
    ) -> Tuple[List[CustomerSettlement], int]:
        stmt = select(CustomerSettlement).where(
            CustomerSettlement.is_deleted == 0
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                CustomerSettlement.doc_no.like(kw)
                | CustomerSettlement.customer_name.like(kw)
            )
        if customer_id:
            stmt = stmt.where(CustomerSettlement.customer_id == customer_id)
        if enterprise_id:
            stmt = stmt.where(CustomerSettlement.enterprise_id == enterprise_id)
        if status is not None:
            stmt = stmt.where(CustomerSettlement.status == status)
        if due_before:
            stmt = stmt.where(CustomerSettlement.due_date <= due_before)
        if invoice_required is not None:
            stmt = stmt.where(
                CustomerSettlement.invoice_required == invoice_required
            )
        if only_unreceived:
            stmt = stmt.where(
                CustomerSettlement.status.in_([FIN_REVIEWED, FIN_PAID]),
                CustomerSettlement.planned_amount
                > CustomerSettlement.received_amount_total,
            )

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(CustomerSettlement.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_links(
        cls, db: AsyncSession, settle_id: int,
    ) -> List[CustomerSettleReconLink]:
        return await cls._load_links(db, settle_id)

    @classmethod
    async def list_receipt_links(
        cls, db: AsyncSession, settle_id: int,
    ) -> List[ReceiptSettleLink]:
        """本单的到账构成（出纳台反查用）。"""
        r = await db.execute(
            select(ReceiptSettleLink)
            .where(
                ReceiptSettleLink.settle_id == settle_id,
                ReceiptSettleLink.is_deleted == 0,
            )
            .order_by(ReceiptSettleLink.id.asc())
        )
        return list(r.scalars().all())

    @classmethod
    async def settled_amount_of(cls, db: AsyncSession, settle_id: int) -> Decimal:
        """本单有效核销明细之和（已收累计的唯一事实来源）。"""
        r = await db.execute(
            select(func.coalesce(func.sum(ReceiptSettleLink.applied_amount), 0))
            .where(
                ReceiptSettleLink.settle_id == settle_id,
                ReceiptSettleLink.is_deleted == 0,
            )
        )
        return Decimal(str(r.scalar() or 0))

    @classmethod
    def status_text(cls, settle: Any) -> str:
        return status_label(int(settle.status or 0), cls.doc_kind)

    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        flags = super().action_flags(doc)
        status = int(doc.status)
        planned = Decimal(str(doc.planned_amount or 0))
        received = Decimal(str(doc.received_amount_total or 0))
        flags.update({
            "canLinkRecon": status == FIN_DRAFT,
            "canReceive": status == FIN_REVIEWED and received <= 0,
            "canClaimReceipt": (
                status == FIN_REVIEWED and planned > received
            ),
            "canCancelReceive": status == FIN_PAID,
            "canInvoice": status == FIN_PAID and int(doc.invoice_required or 0) == 1,
            "unreceivedAmount": float(max(planned - received, Decimal("0"))),
        })
        # 直登与核销互斥：有核销记录就不再给「登记收款」入口
        flags["canPay"] = flags["canReceive"]
        return flags

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @staticmethod
    def _apply_receive_fields(
        settle: CustomerSettlement,
        *,
        amount: Decimal,
        received_at: datetime,
        receive_method: Optional[int],
        account_id: Optional[int],
        account_label: Optional[str],
        voucher_url: Optional[str],
    ) -> None:
        settle.actual_amount = amount
        settle.paid_at = received_at
        settle.received_at = received_at
        settle.pay_method = receive_method
        if account_id is not None:
            settle.received_account_id = account_id
        if account_label:
            settle.received_account_label = account_label
        if voucher_url:
            settle.received_voucher_url = voucher_url

    @classmethod
    async def _to_received(
        cls,
        db: AsyncSession,
        settle: CustomerSettlement,
        *,
        operator_id: Optional[int],
    ) -> None:
        """置「已收款」并做硬联动：锁运单 + 推进对账单结清进度。"""
        await cls.change_status(
            db, settle, FIN_PAID,
            event_type=FinanceEventType.PAY,
            operator_id=operator_id,
            occurred_amount=settle.actual_amount,
        )
        waybill_ids = await cls.waybill_ids_of(db, int(settle.id))
        locked = await LockOrchestrator.lock_waybills(
            db, waybill_ids, by_doc_id=int(settle.id),
        )
        if locked:
            await FinanceDocEventWriter.write(
                db,
                doc_kind=cls.doc_kind,
                doc_id=int(settle.id),
                event_type=FinanceEventType.LOCK,
                direction=FinanceDirection.RECEIVE,
                operator_id=operator_id,
                reason=f"收款完成，已锁定 {locked} 张运单",
            )
            await db.flush()
        await cls._refresh_recon_progress(db, int(settle.id), operator_id)

    @classmethod
    async def waybill_ids_of(cls, db: AsyncSession, settle_id: int) -> List[int]:
        """本结算单覆盖的运单（经对账单桥接两跳取得）。"""
        r = await db.execute(
            select(CustomerReconWaybillLink.waybill_id)
            .join(
                CustomerSettleReconLink,
                CustomerSettleReconLink.recon_id
                == CustomerReconWaybillLink.recon_id,
            )
            .where(
                CustomerSettleReconLink.settle_id == settle_id,
                CustomerSettleReconLink.is_deleted == 0,
                CustomerReconWaybillLink.is_deleted == 0,
            )
        )
        return [int(x) for x in r.scalars().all()]

    @classmethod
    async def _refresh_recon_progress(
        cls, db: AsyncSession, settle_id: int, operator_id: Optional[int],
    ) -> None:
        for row in await cls._load_links(db, settle_id):
            await CustomerReconService.refresh_settle_progress(
                db, int(row.recon_id), operator_id=operator_id,
            )

    @staticmethod
    def _available_amount(
        recon: CustomerRecon, mine: Optional[Decimal],
    ) -> Decimal:
        """该对账单还能被认领的金额（本单已认领的部分算可用）。"""
        planned = Decimal(str(recon.planned_amount or 0))
        applied = Decimal(str(recon.applied_amount_total or 0))
        return planned - applied + Decimal(str(mine or 0))

    @staticmethod
    def _assert_linkable(recon: CustomerRecon, customer_id: int) -> None:
        if int(recon.customer_id or 0) != int(customer_id):
            raise BizException(
                f"对账单 {recon.doc_no} 属于其他客户，不能并入本结算单"
            )
        if int(recon.status) not in (FIN_REVIEWED, FIN_PAID):
            raise BizException(
                f"对账单 {recon.doc_no} 还未确认，请先确认对账单再结算"
            )

    @staticmethod
    async def _get_customer_or_404(db: AsyncSession, customer_id: int) -> Customer:
        r = await db.execute(
            select(Customer).where(
                Customer.id == customer_id, Customer.is_deleted == 0,
            )
        )
        c = r.scalar_one_or_none()
        if c is None:
            raise BizException("客户不存在或已停用，请重新选择")
        return c

    @staticmethod
    async def _load_links(
        db: AsyncSession, settle_id: int,
    ) -> List[CustomerSettleReconLink]:
        r = await db.execute(
            select(CustomerSettleReconLink)
            .where(
                CustomerSettleReconLink.settle_id == settle_id,
                CustomerSettleReconLink.is_deleted == 0,
            )
            .order_by(CustomerSettleReconLink.id.asc())
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_recons(
        db: AsyncSession, recon_ids: Sequence[int],
    ) -> Dict[int, CustomerRecon]:
        if not recon_ids:
            return {}
        r = await db.execute(
            select(CustomerRecon).where(
                CustomerRecon.id.in_(list(recon_ids)),
                CustomerRecon.is_deleted == 0,
            )
        )
        return {int(x.id): x for x in r.scalars().all()}

    @staticmethod
    async def _applied_by_settle(
        db: AsyncSession,
        settle_id: Optional[int],
        recon_ids: Sequence[int],
    ) -> Dict[int, Decimal]:
        """本结算单已认领各对账单的金额。"""
        if settle_id is None or not recon_ids:
            return {}
        r = await db.execute(
            select(
                CustomerSettleReconLink.recon_id,
                CustomerSettleReconLink.applied_amount,
            ).where(
                CustomerSettleReconLink.settle_id == settle_id,
                CustomerSettleReconLink.recon_id.in_(list(recon_ids)),
                CustomerSettleReconLink.is_deleted == 0,
            )
        )
        return {int(rid): Decimal(str(amt or 0)) for rid, amt in r.all()}
