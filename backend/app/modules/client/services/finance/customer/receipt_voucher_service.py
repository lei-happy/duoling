"""收款单 Service（文档 10 §四）

收款单记的是**银行到账这个事实**，不是应收义务——所以它没有审批环节，只有
「录入 → 认领核销 → 核销完」。一笔到账可核销到多张结算单，一张结算单也可由多笔
到账付清。

核销金额的事实来源只有一处：``biz_receipt_settle_link`` 的有效明细。收款单的
``settled_amount`` 与结算单的 ``received_amount_total`` 都是按明细汇总回写的冗余，
任何一侧都不做「加减法累积」——加减法一旦漏一次撤销就永久对不上。
"""

from datetime import date as ddate, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.customer_settlement import CustomerSettlement
from app.modules.client.models.finance.receipt_voucher import (
    RECEIPT_VOUCHER_DOC_KIND,
    ReceiptSettleLink,
    ReceiptVoucher,
)
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
    FIN_REVIEWED,
    FIN_SETTLED,
    label as status_label,
)
from app.modules.client.services.finance.customer.customer_recon_service import (
    AMOUNT_TOLERANCE,
)
from app.modules.client.services.finance.customer.customer_settlement_service import (
    CustomerSettlementService,
)

_CENT = Decimal("0.01")


class ReceiptVoucherService(FinanceDocService):
    """收款单（到账事实与核销）"""

    model = ReceiptVoucher
    doc_kind = RECEIPT_VOUCHER_DOC_KIND
    doc_label = "收款单"
    doc_no_prefix = "SK"
    direction = FinanceDirection.RECEIVE
    # 到账信息在未核销前都可改；一旦有核销明细，靠 assert_no_settled 单独拦
    editable_statuses = (FIN_DRAFT,)
    deletable_statuses = (FIN_DRAFT, FIN_CANCELLED)

    @classmethod
    def assert_editable(cls, receipt: Any) -> None:
        """覆盖通用提示：收款单没有「退回草稿」，解锁编辑靠撤销核销。"""
        if int(receipt.status) not in tuple(cls.editable_statuses):
            raise BizException(
                f"这笔到账当前是「{cls.status_text(receipt)}」，不能修改；"
                "请先撤销核销记录"
            )

    # ------------------------------------------------------------------
    # 录入与维护
    # ------------------------------------------------------------------
    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        *,
        amount: Decimal,
        received_at: datetime,
        receive_method: Optional[int] = None,
        customer_id: Optional[int] = None,
        payer_name: Optional[str] = None,
        bank_account_id: Optional[int] = None,
        bank_account_label: Optional[str] = None,
        bank_serial_no: Optional[str] = None,
        voucher_url: Optional[str] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> ReceiptVoucher:
        """登记一笔到账。"""
        total = Decimal(str(amount or 0))
        if total <= 0:
            raise BizException("到账金额必须大于 0")
        if received_at is None:
            raise BizException("请填写到账时间")
        await cls._assert_serial_unique(db, bank_serial_no)

        customer = None
        if customer_id:
            customer = await cls._get_customer_or_404(db, customer_id)

        receipt = ReceiptVoucher(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.RECEIVE,
            status=FIN_DRAFT,
            customer_id=customer_id,
            customer_name=customer.customer_name if customer else None,
            payer_name=(payer_name or "").strip() or None,
            bank_account_id=bank_account_id,
            bank_account_label=bank_account_label,
            received_at=received_at,
            receive_method=receive_method,
            bank_serial_no=(bank_serial_no or "").strip() or None,
            voucher_url=voucher_url,
            planned_amount=total,
            actual_amount=total,
            paid_at=received_at,
            pay_method=receive_method,
            settled_amount=Decimal("0"),
            unsettled_amount=total,
            created_by=operator_id,
            remark=remark,
        )
        db.add(receipt)
        await db.flush()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=receipt.id,
            event_type=FinanceEventType.CREATE,
            to_status=FIN_DRAFT,
            direction=FinanceDirection.RECEIVE,
            occurred_amount=total,
            operator_id=operator_id,
            payload_snapshot={
                "payerName": receipt.payer_name,
                "bankSerialNo": receipt.bank_serial_no,
            },
        )
        await db.flush()
        # 钱已经进账户了，账面余额随登记动作走，不等认领核销（文档 10 §3.3）
        await cls._apply_account_delta(
            db, receipt, total, operator_id=operator_id,
        )
        return receipt

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        receipt_id: int,
        *,
        amount: Optional[Decimal] = None,
        received_at: Optional[datetime] = None,
        receive_method: Optional[int] = None,
        customer_id: Optional[int] = None,
        payer_name: Optional[str] = None,
        bank_account_id: Optional[int] = None,
        bank_account_label: Optional[str] = None,
        bank_serial_no: Optional[str] = None,
        voucher_url: Optional[str] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> ReceiptVoucher:
        """修改到账信息（仅未核销时可改）。"""
        receipt = await cls.get_or_404(db, receipt_id)
        cls.assert_editable(receipt)
        await cls.assert_no_settled(db, receipt_id, action="修改")
        # 改金额或改账户都会让账面余额失真，先记住原值，改完按差额回补
        old_account_id = receipt.bank_account_id
        old_amount = Decimal(str(receipt.planned_amount or 0))

        if amount is not None:
            total = Decimal(str(amount))
            if total <= 0:
                raise BizException("到账金额必须大于 0")
            receipt.planned_amount = total
            receipt.actual_amount = total
            receipt.unsettled_amount = total
        if received_at is not None:
            receipt.received_at = received_at
            receipt.paid_at = received_at
        if receive_method is not None:
            receipt.receive_method = receive_method
            receipt.pay_method = receive_method
        if customer_id is not None:
            customer = await cls._get_customer_or_404(db, customer_id)
            receipt.customer_id = customer_id
            receipt.customer_name = customer.customer_name
        if payer_name is not None:
            receipt.payer_name = payer_name.strip() or None
        if bank_account_id is not None:
            receipt.bank_account_id = bank_account_id
        if bank_account_label is not None:
            receipt.bank_account_label = bank_account_label
        if bank_serial_no is not None:
            serial = bank_serial_no.strip() or None
            if serial != receipt.bank_serial_no:
                await cls._assert_serial_unique(db, serial, exclude_id=receipt_id)
            receipt.bank_serial_no = serial
        if voucher_url is not None:
            receipt.voucher_url = voucher_url
        if remark is not None:
            receipt.remark = remark
        await db.flush()

        new_amount = Decimal(str(receipt.planned_amount or 0))
        if old_account_id != receipt.bank_account_id:
            await cls._apply_account_delta_for(
                db, old_account_id, -old_amount,
                reason=f"收款单 {receipt.doc_no} 换账户", operator_id=operator_id,
            )
            await cls._apply_account_delta(
                db, receipt, new_amount, operator_id=operator_id,
            )
        elif new_amount != old_amount:
            await cls._apply_account_delta(
                db, receipt, new_amount - old_amount, operator_id=operator_id,
            )
        return receipt

    @classmethod
    async def cancel_receipt(
        cls,
        db: AsyncSession,
        receipt_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> ReceiptVoucher:
        """撤销收款单（录错）。有核销明细时要求先撤销核销。"""
        receipt = await cls.get_or_404(db, receipt_id)
        if int(receipt.status) == FIN_CANCELLED:
            raise BizException("该收款单已撤销，无需重复操作")
        await cls.assert_no_settled(db, receipt_id, action="撤销")
        text = cls.assert_reason(reason)
        await cls.change_status(
            db, receipt, FIN_CANCELLED,
            event_type=FinanceEventType.CANCEL,
            operator_id=operator_id,
            reason=text,
        )
        await cls._apply_account_delta(
            db, receipt, -Decimal(str(receipt.planned_amount or 0)),
            operator_id=operator_id,
        )
        return receipt

    @classmethod
    async def _apply_account_delta(
        cls,
        db: AsyncSession,
        receipt: ReceiptVoucher,
        delta: Decimal,
        *,
        operator_id: Optional[int] = None,
    ) -> None:
        """同步企业银行账户账面余额（未指定账户时自动跳过）。"""
        await cls._apply_account_delta_for(
            db, receipt.bank_account_id, delta,
            reason=f"收款单 {receipt.doc_no}", operator_id=operator_id,
        )

    @classmethod
    async def _apply_account_delta_for(
        cls,
        db: AsyncSession,
        account_id: Optional[int],
        delta: Decimal,
        *,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> None:
        if not account_id:
            return
        from app.modules.client.services.finance.cashier.bank_account_service import (
            BankAccountService,
        )

        await BankAccountService.apply_delta(
            db, int(account_id), delta, reason=reason, operator_id=operator_id,
        )

    # ------------------------------------------------------------------
    # 认领核销
    # ------------------------------------------------------------------
    @classmethod
    async def list_claim_candidates(
        cls,
        db: AsyncSession,
        receipt_id: int,
        *,
        keyword: Optional[str] = None,
        limit: int = 50,
    ) -> List[dict]:
        """可核销的结算单候选，按「金额接近本次未核销余额」排序。

        只做排序推荐，不自动核销——自动匹配是明确不做的范围（``00`` §1.3）。
        """
        receipt = await cls.get_or_404(db, receipt_id)
        stmt = select(CustomerSettlement).where(
            CustomerSettlement.is_deleted == 0,
            CustomerSettlement.status == FIN_REVIEWED,
            CustomerSettlement.planned_amount
            > CustomerSettlement.received_amount_total,
        )
        if receipt.customer_id:
            stmt = stmt.where(
                CustomerSettlement.customer_id == receipt.customer_id
            )
        elif receipt.payer_name:
            stmt = stmt.where(
                CustomerSettlement.customer_name.like(f"%{receipt.payer_name}%")
            )
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                CustomerSettlement.doc_no.like(kw)
                | CustomerSettlement.customer_name.like(kw)
            )
        r = await db.execute(stmt.limit(500))
        rows = list(r.scalars().all())
        if not rows:
            return []

        mine = await cls._applied_by_receipt(
            db, receipt_id, [int(x.id) for x in rows],
        )
        unsettled = Decimal(str(receipt.unsettled_amount or 0))
        out = []
        for m in rows:
            unreceived = (
                Decimal(str(m.planned_amount or 0))
                - Decimal(str(m.received_amount_total or 0))
                + Decimal(str(mine.get(int(m.id)) or 0))
            )
            if unreceived <= 0:
                continue
            out.append({
                "settleId": int(m.id),
                "docNo": m.doc_no,
                "customerId": m.customer_id,
                "customerName": m.customer_name,
                "plannedAmount": float(m.planned_amount or 0),
                "receivedAmountTotal": float(m.received_amount_total or 0),
                "unreceivedAmount": float(unreceived),
                "appliedByThisReceipt": float(mine.get(int(m.id)) or 0),
                "dueDate": m.due_date,
                "_gap": abs(unreceived - unsettled),
            })
        out.sort(key=lambda x: (x["_gap"], -x["unreceivedAmount"]))
        for item in out:
            item.pop("_gap", None)
        return out[:max(1, int(limit))]

    @classmethod
    async def suggest_allocation(
        cls, db: AsyncSession, receipt_id: int,
    ) -> List[dict]:
        """一键按顺序填满：按到期日先后把未核销余额分配给候选结算单。"""
        receipt = await cls.get_or_404(db, receipt_id)
        remain = Decimal(str(receipt.unsettled_amount or 0))
        if remain <= 0:
            return []
        candidates = await cls.list_claim_candidates(db, receipt_id, limit=200)
        candidates.sort(key=lambda x: (x["dueDate"] or ddate.max, x["settleId"]))
        out = []
        for c in candidates:
            if remain <= 0:
                break
            take = min(remain, Decimal(str(c["unreceivedAmount"])))
            if take <= 0:
                continue
            out.append({
                "settleId": c["settleId"],
                "docNo": c["docNo"],
                "amount": float(take),
            })
            remain -= take
        return out

    @classmethod
    async def claim(
        cls,
        db: AsyncSession,
        receipt_id: int,
        allocations: Sequence[dict],
        *,
        operator_id: Optional[int] = None,
    ) -> ReceiptVoucher:
        """把到账金额核销到结算单。

        ``allocations`` 每项 ``{"settleId": int, "amount": Decimal, "remark": str}``，
        ``amount`` 是该 (收款单, 结算单) 关系的**目标金额**而非增量——同一对关系
        只有一条明细，重复提交是覆盖，不会翻倍。
        """
        receipt = await cls.get_or_404(db, receipt_id)
        if int(receipt.status) == FIN_CANCELLED:
            raise BizException("已撤销的收款单不能再核销")
        if not allocations:
            raise BizException("请选择要核销的结算单并填写金额")

        settle_ids = [
            int(a.get("settleId")) for a in allocations if a.get("settleId")
        ]
        settlements = await cls._load_settlements(db, settle_ids)
        existing = {
            int(x.settle_id): x
            for x in await cls.list_links(db, receipt_id)
        }
        now = datetime.now()
        total_receipt = Decimal(str(receipt.planned_amount or 0))

        for item in allocations:
            sid = int(item.get("settleId"))
            settle = settlements.get(sid)
            if settle is None:
                raise BizException("结算单不存在或已删除，请刷新后重试")
            cls._assert_claimable(receipt, settle)

            amount = Decimal(str(item.get("amount") or 0)).quantize(_CENT)
            if amount <= 0:
                raise BizException(
                    f"结算单 {settle.doc_no} 的核销金额必须大于 0"
                )
            row = existing.get(sid)
            if row is None:
                row = ReceiptSettleLink(
                    receipt_id=receipt_id,
                    settle_id=sid,
                    settle_doc_no=settle.doc_no,
                    applied_amount=amount,
                    settled_at=now,
                    settled_by=operator_id,
                    dedup_key=ReceiptSettleLink.build_dedup_key(receipt_id, sid),
                )
                db.add(row)
                existing[sid] = row
            else:
                row.applied_amount = amount
                row.settled_at = now
                row.settled_by = operator_id
            if item.get("remark") is not None:
                row.remark = item.get("remark")
        await db.flush()

        settled = await cls.settled_amount_of(db, receipt_id)
        if settled > total_receipt + AMOUNT_TOLERANCE:
            raise BizException(
                f"核销金额合计 {settled:.2f} 元超过到账金额 "
                f"{total_receipt:.2f} 元，请调整分配金额"
            )

        # 结算单侧按「该结算单的全部有效核销明细」回写，满额自动收款并锁运单
        for sid in {int(a.get("settleId")) for a in allocations if a.get("settleId")}:
            cumulative = await CustomerSettlementService.settled_amount_of(db, sid)
            await CustomerSettlementService.apply_receipt(
                db, sid,
                amount=cumulative,
                received_at=receipt.received_at,
                receive_method=receipt.receive_method,
                account_id=receipt.bank_account_id,
                account_label=receipt.bank_account_label,
                voucher_url=receipt.voucher_url,
                operator_id=operator_id,
            )

        await cls._refresh_progress(
            db, receipt,
            event_type=FinanceEventType.RECEIPT_CLAIM,
            operator_id=operator_id,
            reason=f"已核销 {settled:.2f} 元到 {len(existing)} 张结算单",
        )
        return receipt

    @classmethod
    async def unclaim(
        cls,
        db: AsyncSession,
        receipt_id: int,
        settle_id: int,
        *,
        reason: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> ReceiptVoucher:
        """撤销一条核销明细。"""
        receipt = await cls.get_or_404(db, receipt_id)
        r = await db.execute(
            select(ReceiptSettleLink).where(
                ReceiptSettleLink.receipt_id == receipt_id,
                ReceiptSettleLink.settle_id == settle_id,
                ReceiptSettleLink.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("这条核销记录不存在或已撤销")
        # 先校验再删明细：拦不住的话明细已经没了，已收累计就成了 0
        await CustomerSettlementService.assert_receipt_reversible(db, settle_id)

        amount = Decimal(str(row.applied_amount or 0))
        row.is_deleted = 1
        row.dedup_key = None
        await db.flush()

        cumulative = await CustomerSettlementService.settled_amount_of(db, settle_id)
        await CustomerSettlementService.unapply_receipt(
            db, settle_id, amount=cumulative, operator_id=operator_id,
        )
        await cls._refresh_progress(
            db, receipt,
            event_type=FinanceEventType.UNSETTLE,
            operator_id=operator_id,
            occurred_amount=-amount,
            reason=reason or f"撤销核销 {amount:.2f} 元（{row.settle_doc_no}）",
        )
        return receipt

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
        status: Optional[int] = None,
        received_start: Optional[ddate] = None,
        received_end: Optional[ddate] = None,
        only_unsettled: bool = False,
    ) -> Tuple[List[ReceiptVoucher], int]:
        stmt = select(ReceiptVoucher).where(ReceiptVoucher.is_deleted == 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                ReceiptVoucher.doc_no.like(kw)
                | ReceiptVoucher.payer_name.like(kw)
                | ReceiptVoucher.customer_name.like(kw)
                | ReceiptVoucher.bank_serial_no.like(kw)
            )
        if customer_id:
            stmt = stmt.where(ReceiptVoucher.customer_id == customer_id)
        if status is not None:
            stmt = stmt.where(ReceiptVoucher.status == status)
        if received_start:
            stmt = stmt.where(
                ReceiptVoucher.received_at
                >= datetime.combine(received_start, datetime.min.time())
            )
        if received_end:
            stmt = stmt.where(
                ReceiptVoucher.received_at
                <= datetime.combine(received_end, datetime.max.time())
            )
        if only_unsettled:
            stmt = stmt.where(
                ReceiptVoucher.status != FIN_CANCELLED,
                ReceiptVoucher.unsettled_amount > 0,
            )

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(ReceiptVoucher.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_links(
        cls, db: AsyncSession, receipt_id: int,
    ) -> List[ReceiptSettleLink]:
        r = await db.execute(
            select(ReceiptSettleLink)
            .where(
                ReceiptSettleLink.receipt_id == receipt_id,
                ReceiptSettleLink.is_deleted == 0,
            )
            .order_by(ReceiptSettleLink.id.asc())
        )
        return list(r.scalars().all())

    @classmethod
    async def settled_amount_of(
        cls, db: AsyncSession, receipt_id: int,
    ) -> Decimal:
        r = await db.execute(
            select(func.coalesce(func.sum(ReceiptSettleLink.applied_amount), 0))
            .where(
                ReceiptSettleLink.receipt_id == receipt_id,
                ReceiptSettleLink.is_deleted == 0,
            )
        )
        return Decimal(str(r.scalar() or 0))

    @classmethod
    async def cashier_stats(cls, db: AsyncSession) -> dict:
        """出纳台 KPI：待认领笔数与金额、今日到账金额。"""
        r = await db.execute(
            select(
                func.count(ReceiptVoucher.id),
                func.coalesce(func.sum(ReceiptVoucher.unsettled_amount), 0),
            ).where(
                ReceiptVoucher.is_deleted == 0,
                ReceiptVoucher.status != FIN_CANCELLED,
                ReceiptVoucher.unsettled_amount > 0,
            )
        )
        pending_count, pending_amount = r.one()
        today = ddate.today()
        r2 = await db.execute(
            select(func.coalesce(func.sum(ReceiptVoucher.planned_amount), 0)).where(
                ReceiptVoucher.is_deleted == 0,
                ReceiptVoucher.status != FIN_CANCELLED,
                ReceiptVoucher.received_at
                >= datetime.combine(today, datetime.min.time()),
                ReceiptVoucher.received_at
                <= datetime.combine(today, datetime.max.time()),
            )
        )
        return {
            "pendingClaimCount": int(pending_count or 0),
            "pendingClaimAmount": float(pending_amount or 0),
            "todayReceivedAmount": float(r2.scalar() or 0),
        }

    @classmethod
    def status_text(cls, receipt: Any) -> str:
        return status_label(int(receipt.status or 0), cls.doc_kind)

    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        status = int(doc.status)
        settled = Decimal(str(doc.settled_amount or 0))
        unsettled = Decimal(str(doc.unsettled_amount or 0))
        return {
            "canEdit": status == FIN_DRAFT and settled <= 0,
            "canDelete": status in (FIN_DRAFT, FIN_CANCELLED) and settled <= 0,
            "canClaim": status != FIN_CANCELLED and unsettled > 0,
            "canUnclaim": settled > 0,
            "canCancel": status != FIN_CANCELLED and settled <= 0,
        }

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @classmethod
    async def assert_no_settled(
        cls, db: AsyncSession, receipt_id: int, *, action: str = "修改",
    ) -> None:
        if await cls.settled_amount_of(db, receipt_id) > 0:
            raise BizException(
                f"本笔到账已核销到结算单，不能{action}；"
                "请先撤销核销记录"
            )

    @classmethod
    async def _refresh_progress(
        cls,
        db: AsyncSession,
        receipt: ReceiptVoucher,
        *,
        event_type: int,
        operator_id: Optional[int],
        reason: Optional[str] = None,
        occurred_amount: Optional[Decimal] = None,
    ) -> None:
        """按有效核销明细回写核销进度并推进状态。"""
        total = Decimal(str(receipt.planned_amount or 0))
        settled = await cls.settled_amount_of(db, int(receipt.id))
        receipt.settled_amount = settled
        receipt.unsettled_amount = total - settled

        old = int(receipt.status)
        if settled <= 0:
            new = FIN_DRAFT
        elif settled + AMOUNT_TOLERANCE >= total:
            new = FIN_SETTLED
        else:
            new = FIN_PAID
        if new != old:
            await cls.change_status(
                db, receipt, new,
                event_type=event_type,
                operator_id=operator_id,
                occurred_amount=occurred_amount if occurred_amount else settled,
                reason=reason,
                skip_lock_check=True,
            )
        else:
            await FinanceDocEventWriter.write(
                db,
                doc_kind=cls.doc_kind,
                doc_id=int(receipt.id),
                event_type=event_type,
                direction=FinanceDirection.RECEIVE,
                occurred_amount=occurred_amount if occurred_amount else settled,
                operator_id=operator_id,
                reason=reason,
            )
            await db.flush()

    @staticmethod
    def _assert_claimable(
        receipt: ReceiptVoucher, settle: CustomerSettlement,
    ) -> None:
        if int(settle.status) != FIN_REVIEWED:
            raise BizException(
                f"结算单 {settle.doc_no} 当前不可核销，"
                "只有已审批未收款的结算单可以认领到账"
            )
        if receipt.customer_id and int(settle.customer_id or 0) != int(
            receipt.customer_id
        ):
            raise BizException(
                f"结算单 {settle.doc_no} 属于其他客户，"
                "不能用这笔到账核销；请确认付款方"
            )

    @staticmethod
    async def _assert_serial_unique(
        db: AsyncSession,
        bank_serial_no: Optional[str],
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        """同一银行流水号只允许登记一次（防出纳重复录同一笔到账）。"""
        serial = (bank_serial_no or "").strip()
        if not serial:
            return
        stmt = select(ReceiptVoucher.doc_no).where(
            ReceiptVoucher.bank_serial_no == serial,
            ReceiptVoucher.is_deleted == 0,
            ReceiptVoucher.status != FIN_CANCELLED,
        )
        if exclude_id is not None:
            stmt = stmt.where(ReceiptVoucher.id != exclude_id)
        doc_no = (await db.execute(stmt.limit(1))).scalar_one_or_none()
        if doc_no:
            raise BizException(
                f"这笔流水已登记为收款单 {doc_no}，不要重复录入"
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
    async def _load_settlements(
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
    async def _applied_by_receipt(
        db: AsyncSession, receipt_id: int, settle_ids: Sequence[int],
    ) -> Dict[int, Decimal]:
        if not settle_ids:
            return {}
        r = await db.execute(
            select(
                ReceiptSettleLink.settle_id, ReceiptSettleLink.applied_amount,
            ).where(
                ReceiptSettleLink.receipt_id == receipt_id,
                ReceiptSettleLink.settle_id.in_(list(settle_ids)),
                ReceiptSettleLink.is_deleted == 0,
            )
        )
        return {int(sid): Decimal(str(amt or 0)) for sid, amt in r.all()}
