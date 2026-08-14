"""客户对账单 Service（文档 02 §三）

对账单是「事项确认书」：把一段周期内某客户的运单按计费基础列成行，与客户核对
台数与金额，确认后才由结算单去收钱。因此本 service 的重点不是审批流（对账类没有
待审批状态），而是**行的维护与快照的可信**：

- 建行时把运费与已交车台数**冻结成快照**，业务侧后续变更只置脏留差异，不回灌改钱；
- 行的增删改都会重算主表合计，列表页不做子查询；
- 确认（0→2）前过三道闸：至少一行且金额为正、无阻塞级未处置差异、大额调整已获
  业务主管审批。

与核对器的关系：本模块在导入时把客户侧的表结构与两个检测器注册进
``ConsistencyChecker``，之后置脏、差异检出、确认拦截、强制确认全部走核对器的
通用实现，客户侧不再自己写一套。
"""

from datetime import date as ddate, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.customer_recon import (
    CUSTOMER_RECON_DOC_KIND,
    CustomerRecon,
    CustomerReconWaybillLink,
)
from app.modules.client.models.partner.customer import Customer
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.services.finance.base.constants import (
    BillingBase,
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
    FIN_REVIEWED,
    FinanceStateMachine,
)
from app.modules.client.services.finance.linkage.waybill_to_finance import (
    WAYBILL_RECONCILABLE_STATUSES,
    WaybillToFinance,
)
from app.modules.client.services.finance.recon.consistency_checker import (
    ConsistencyChecker,
    DiffCandidate,
    ReconBinding,
)
from app.modules.client.services.finance.recon.diff_constants import (
    BizDocType,
    DiffType,
    ReconKind,
)

# 行调整额触发业务主管审批的阈值（客户侧 ¥5000，承运商侧 ¥3000，文档 02 §3.6）
ADJUST_APPROVAL_THRESHOLD = Decimal("5000")
# 金额比对容差：低于一分不算差异，避免除不尽的分位噪音刷出一堆假差异
AMOUNT_TOLERANCE = Decimal("0.01")
_CENT = Decimal("0.01")


class CustomerReconService(FinanceDocService):
    """客户对账单"""

    model = CustomerRecon
    doc_kind = CUSTOMER_RECON_DOC_KIND
    doc_label = "客户对账单"
    doc_no_prefix = "CR"
    direction = FinanceDirection.RECEIVE
    # 对账类没有待审批态：草稿可改，已确认要先退回草稿
    editable_statuses = (FIN_DRAFT,)

    # ------------------------------------------------------------------
    # 候选池
    # ------------------------------------------------------------------
    @classmethod
    async def list_candidates(
        cls,
        db: AsyncSession,
        *,
        customer_id: int,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        keyword: Optional[str] = None,
        recon_id: Optional[int] = None,
        limit: int = 500,
    ) -> List[dict]:
        """可加入对账单的运单候选，带上建行要用的业务事实。

        ``recon_id`` 用于「给已存在的对账单补挂运单」：本单已挂的行不算冲突。
        """
        waybills = await WaybillToFinance.list_candidates(
            db,
            customer_id=customer_id,
            period_start=period_start,
            period_end=period_end,
            keyword=keyword,
            exclude_recon_id=recon_id,
            limit=limit,
        )
        if not waybills:
            return []
        ids = [int(w.id) for w in waybills]
        qty_map = await WaybillToFinance.signed_quantity_map(db, ids)
        at_map = await WaybillToFinance.signed_at_map(db, ids)
        return [
            {
                "waybillId": int(w.id),
                "waybillNo": w.waybill_no,
                "customerId": w.customer_id,
                "origin": w.origin,
                "destination": w.destination,
                "dealerName": w.dealer_name,
                "quantity": int(w.quantity or 0),
                "signedQuantity": qty_map.get(int(w.id), 0),
                "signedAt": at_map.get(int(w.id)),
                "freightAmount": _f(w.freight_amount),
                "status": int(w.status or 0),
            }
            for w in waybills
        ]

    # ------------------------------------------------------------------
    # 创建与行维护
    # ------------------------------------------------------------------
    @classmethod
    async def create_from_candidates(
        cls,
        db: AsyncSession,
        *,
        customer_id: int,
        period_start: datetime,
        period_end: datetime,
        waybill_ids: Sequence[int],
        billing_base: int = BillingBase.BY_VEHICLE,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerRecon:
        """按选中候选生成草稿态对账单。"""
        customer = await cls._get_customer_or_404(db, customer_id)
        if period_start is None or period_end is None:
            raise BizException("请选择对账周期的起止日期")
        await cls._assert_period_unique(db, customer_id, period_start, period_end)

        recon = CustomerRecon(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.RECEIVE,
            status=FIN_DRAFT,
            customer_id=customer_id,
            customer_name=customer.customer_name,
            enterprise_id=customer.enterprise_id,
            settlement_type=customer.settlement_type,
            customer_contact_name=customer.contact_person,
            customer_contact_phone=customer.contact_phone,
            period_start=period_start,
            period_end=period_end,
            planned_amount=Decimal("0"),
            created_by=operator_id,
            remark=remark,
            dedup_key=CustomerRecon.build_dedup_key(
                customer_id, period_start, period_end,
            ),
        )
        db.add(recon)
        await db.flush()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=recon.id,
            event_type=FinanceEventType.CREATE,
            to_status=FIN_DRAFT,
            direction=FinanceDirection.RECEIVE,
            operator_id=operator_id,
            payload_snapshot={
                "customerId": customer_id,
                "periodStart": period_start.strftime("%Y-%m-%d"),
                "periodEnd": period_end.strftime("%Y-%m-%d"),
            },
        )
        if waybill_ids:
            await cls.add_waybills(
                db, recon.id, waybill_ids,
                billing_base=billing_base, operator_id=operator_id,
            )
        return recon

    @classmethod
    async def add_waybills(
        cls,
        db: AsyncSession,
        recon_id: int,
        waybill_ids: Sequence[int],
        *,
        billing_base: int = BillingBase.BY_VEHICLE,
        operator_id: Optional[int] = None,
    ) -> List[CustomerReconWaybillLink]:
        """批量挂入运单并冻结业务事实快照。"""
        recon = await cls.get_or_404(db, recon_id)
        cls.assert_editable(recon)
        ids = _unique_ints(waybill_ids)
        if not ids:
            raise BizException("请先选择要加入对账的运单")

        existing = await cls._active_link_waybill_ids(db, recon_id)
        ids = [i for i in ids if i not in existing]
        if not ids:
            raise BizException("所选运单都已在本对账单中，无需重复添加")

        waybills = await cls._load_waybills(db, ids)
        qty_map = await WaybillToFinance.signed_quantity_map(db, ids)
        now = datetime.now()
        rows: List[CustomerReconWaybillLink] = []
        for wb in waybills:
            cls._assert_reconcilable(wb, int(recon.customer_id))
            if await ConsistencyChecker.is_biz_doc_bound(
                db, ReconKind.CUSTOMER, int(wb.id), exclude_recon_id=recon_id,
            ):
                raise BizException(
                    f"运单 {wb.waybill_no} 已在其他客户对账单中，"
                    "请先从那张对账单移除再加入本单"
                )
            signed_qty = int(qty_map.get(int(wb.id), 0))
            qty, price, amount = cls._derive_line_amount(
                billing_base, wb, signed_qty,
            )
            row = CustomerReconWaybillLink(
                recon_id=recon_id,
                waybill_id=int(wb.id),
                waybill_no=wb.waybill_no,
                billing_base=billing_base,
                quantity=qty,
                unit_price=price,
                amount=amount,
                adjust_amount=Decimal("0"),
                freight_amount_snapshot=(
                    Decimal(str(wb.freight_amount))
                    if wb.freight_amount is not None else None
                ),
                signed_quantity_snapshot=signed_qty,
                locked_snapshot_at=now,
                dedup_key=CustomerReconWaybillLink.build_dedup_key(
                    recon_id, int(wb.id),
                ),
            )
            db.add(row)
            rows.append(row)
        await db.flush()

        await cls._mark_waybills_bound(db, [int(w.id) for w in waybills], True)
        await cls.refresh_totals(db, recon_id)
        return rows

    @classmethod
    async def remove_line(
        cls,
        db: AsyncSession,
        recon_id: int,
        link_id: int,
        *,
        operator_id: Optional[int] = None,
    ) -> None:
        """移除一行（软删并释放去重键，运单回到候选池）。"""
        recon = await cls.get_or_404(db, recon_id)
        cls.assert_editable(recon)
        line = await cls._get_line_or_404(db, recon_id, link_id)
        line.is_deleted = 1
        line.dedup_key = None
        await db.flush()
        await cls._unbind_waybill_if_free(db, int(line.waybill_id))
        await cls.refresh_totals(db, recon_id)

    @classmethod
    async def adjust_line(
        cls,
        db: AsyncSession,
        recon_id: int,
        link_id: int,
        *,
        quantity: Optional[Decimal] = None,
        unit_price: Optional[Decimal] = None,
        adjust_amount: Optional[Decimal] = None,
        adjust_reason: Optional[str] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerReconWaybillLink:
        """调整行的数量 / 单价 / 调整额，重算行金额。

        **只有显式改了数量或单价才按乘积重算基数**；只改调整额时沿用建行时的运单运费
        基数。单价是 `运费 / 台数` 取两位小数的派生值，按台常除不尽（1000 元 3 台
        → 333.33），若每次调整都回落到乘积，账面会凭空少掉分位残差（文档 02 §3.5）。

        调整额变动会写事件 16 并清空既有的大额调整审批——否则先批小额、再改成
        大额就能绕过门槛。
        """
        recon = await cls.get_or_404(db, recon_id)
        cls.assert_editable(recon)
        line = await cls._get_line_or_404(db, recon_id, link_id)

        old_adjust = Decimal(str(line.adjust_amount or 0))
        base = Decimal(str(line.amount or 0)) - old_adjust
        if quantity is not None:
            if Decimal(str(quantity)) < 0:
                raise BizException("计费数量不能为负数")
            line.quantity = Decimal(str(quantity))
        if unit_price is not None:
            if Decimal(str(unit_price)) < 0:
                raise BizException("单价不能为负数")
            line.unit_price = Decimal(str(unit_price))
        if adjust_amount is not None:
            new_adjust = Decimal(str(adjust_amount))
            if new_adjust != 0 and not (adjust_reason or line.adjust_reason):
                raise BizException("有调整金额时必须填写调整原因，便于事后核对")
            line.adjust_amount = new_adjust
        if adjust_reason is not None:
            line.adjust_reason = adjust_reason.strip() or None
        if remark is not None:
            line.remark = remark

        if quantity is not None or unit_price is not None:
            base = Decimal(str(line.quantity or 0)) * Decimal(str(line.unit_price or 0))
        line.amount = _money(base + Decimal(str(line.adjust_amount or 0)))
        await db.flush()
        await cls.refresh_totals(db, recon_id)

        new_adjust = Decimal(str(line.adjust_amount or 0))
        if new_adjust != old_adjust:
            recon.adjust_approved_by = None
            recon.adjust_approved_at = None
            await FinanceDocEventWriter.write(
                db,
                doc_kind=cls.doc_kind,
                doc_id=recon_id,
                event_type=FinanceEventType.ADJUST,
                direction=FinanceDirection.RECEIVE,
                occurred_amount=new_adjust - old_adjust,
                operator_id=operator_id,
                reason=line.adjust_reason,
                payload_snapshot={
                    "linkId": int(line.id),
                    "waybillNo": line.waybill_no,
                    "oldAdjust": float(old_adjust),
                    "newAdjust": float(new_adjust),
                    "lineAmount": float(line.amount or 0),
                },
            )
            await db.flush()
        return line

    @classmethod
    async def refresh_totals(cls, db: AsyncSession, recon_id: int) -> None:
        """重算主表合计（行增删改后调用；列表页据此免子查询）。"""
        r = await db.execute(
            select(
                func.count(CustomerReconWaybillLink.id),
                func.coalesce(func.sum(CustomerReconWaybillLink.quantity), 0),
                func.coalesce(func.sum(CustomerReconWaybillLink.amount), 0),
                func.coalesce(
                    func.sum(CustomerReconWaybillLink.adjust_amount), 0
                ),
            ).where(
                CustomerReconWaybillLink.recon_id == recon_id,
                CustomerReconWaybillLink.is_deleted == 0,
            )
        )
        count, qty, amount, adjust = r.one()
        await db.execute(
            update(CustomerRecon)
            .where(CustomerRecon.id == recon_id)
            .values(
                waybill_count=int(count or 0),
                total_quantity=Decimal(str(qty or 0)),
                planned_amount=Decimal(str(amount or 0)),
                adjust_amount_total=Decimal(str(adjust or 0)),
            )
        )
        await db.flush()

    # ------------------------------------------------------------------
    # 状态流转
    # ------------------------------------------------------------------
    @classmethod
    async def approve_adjust(
        cls,
        db: AsyncSession,
        recon_id: int,
        *,
        operator_id: Optional[int] = None,
        remark: Optional[str] = None,
    ) -> CustomerRecon:
        """业务主管审批大额调整（不改单据状态，只解开确认门槛）。"""
        recon = await cls.get_or_404(db, recon_id)
        total = abs(Decimal(str(recon.adjust_amount_total or 0)))
        if total <= ADJUST_APPROVAL_THRESHOLD:
            raise BizException(
                f"本单调整金额未超过 {ADJUST_APPROVAL_THRESHOLD:.0f} 元，"
                "不需要审批，可直接确认"
            )
        recon.adjust_approved_by = operator_id
        recon.adjust_approved_at = datetime.now()
        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=recon_id,
            event_type=FinanceEventType.APPROVE,
            direction=FinanceDirection.RECEIVE,
            occurred_amount=Decimal(str(recon.adjust_amount_total or 0)),
            operator_id=operator_id,
            reason=remark or "大额调整审批通过",
            payload_snapshot={"scope": "adjust", "adjustTotal": float(total)},
        )
        await db.flush()
        return recon

    @classmethod
    async def confirm(
        cls,
        db: AsyncSession,
        recon_id: int,
        *,
        operator_id: Optional[int] = None,
        force_reason: Optional[str] = None,
    ) -> CustomerRecon:
        """草稿 → 已确认。

        ``force_reason`` 非空时走「带差异强制确认」：先放行阻塞级差异并留痕，
        再确认。这是财务主管的高权限动作，不是常规路径。
        """
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) != FIN_DRAFT:
            raise BizException(
                f"只有草稿状态的对账单可以确认（当前：{cls.status_text(recon)}）"
            )
        if int(recon.waybill_count or 0) <= 0:
            raise BizException("对账单里还没有运单，请先添加对账明细")
        if Decimal(str(recon.planned_amount or 0)) <= 0:
            raise BizException("对账金额必须大于 0，请检查各行的数量与单价")
        cls._assert_adjust_approved(recon)

        if force_reason:
            await ConsistencyChecker.force_confirm(
                db,
                recon_kind=cls.doc_kind,
                recon_id=recon_id,
                reason=force_reason,
                operator_id=operator_id,
            )
        else:
            await ConsistencyChecker.assert_confirmable(
                db, recon_kind=cls.doc_kind, recon_id=recon_id,
            )

        await cls.change_status(
            db, recon, FIN_REVIEWED,
            event_type=FinanceEventType.APPROVE,
            operator_id=operator_id,
            occurred_amount=recon.planned_amount,
            payload_snapshot={
                "waybillCount": int(recon.waybill_count or 0),
                "forced": bool(force_reason),
            },
        )
        return recon

    @classmethod
    async def record_customer_sign(
        cls,
        db: AsyncSession,
        recon_id: int,
        *,
        signer_name: str,
        voucher_url: Optional[str] = None,
        signed_at: Optional[datetime] = None,
        operator_id: Optional[int] = None,
    ) -> CustomerRecon:
        """登记客户回签（不改状态，只补事实与凭证）。"""
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) not in (FIN_REVIEWED, FIN_PAID):
            raise BizException("请先确认对账单，再登记客户回签")
        if not (signer_name or "").strip():
            raise BizException("请填写客户方确认人姓名")
        recon.confirmed_by_customer_name = signer_name.strip()
        recon.confirmed_by_customer_at = signed_at or datetime.now()
        if voucher_url:
            recon.confirm_voucher_url = voucher_url
        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=recon_id,
            event_type=FinanceEventType.LOCK,
            direction=FinanceDirection.RECEIVE,
            operator_id=operator_id,
            reason=f"客户方 {recon.confirmed_by_customer_name} 已回签",
            payload_snapshot={"voucherUrl": recon.confirm_voucher_url},
        )
        await db.flush()
        return recon

    @classmethod
    async def withdraw(
        cls,
        db: AsyncSession,
        recon_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CustomerRecon:
        """已确认 → 草稿（退回修改）。已被结算单关联时拒绝。"""
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) != FIN_REVIEWED:
            raise BizException(
                f"只有已确认的对账单可以退回草稿（当前：{cls.status_text(recon)}）"
            )
        if int(recon.settle_count or 0) > 0:
            raise BizException(
                "本对账单已被结算单关联，不能退回草稿；"
                "请先撤销相关结算单再退回"
            )
        text = cls.assert_reason(reason, action="退回")
        await cls.change_status(
            db, recon, FIN_DRAFT,
            event_type=FinanceEventType.WITHDRAW,
            operator_id=operator_id,
            reason=text,
        )
        return recon

    @classmethod
    async def cancel_recon(
        cls,
        db: AsyncSession,
        recon_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CustomerRecon:
        """撤销对账单：释放运单挂接、失效未决差异、释放同期唯一键。"""
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) in (FIN_CANCELLED,):
            raise BizException("该对账单已撤销，无需重复操作")
        if int(recon.settle_count or 0) > 0:
            raise BizException(
                "本对账单已被结算单关联，不能撤销；请先撤销相关结算单"
            )
        text = cls.assert_reason(reason)
        waybill_ids = await cls._active_link_waybill_ids(db, recon_id)

        await cls.change_status(
            db, recon, FIN_CANCELLED,
            event_type=FinanceEventType.CANCEL,
            operator_id=operator_id,
            reason=text,
            skip_lock_check=True,
        )
        recon.dedup_key = None
        await ConsistencyChecker.invalidate_by_recon(
            db, recon_kind=cls.doc_kind, recon_id=recon_id,
        )
        await db.flush()
        for wid in waybill_ids:
            await cls._unbind_waybill_if_free(db, wid)
        return recon

    @classmethod
    async def unlock_settled(
        cls,
        db: AsyncSession,
        recon_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CustomerRecon:
        """已结清 → 已确认（客户事后追加差异，高权限）。"""
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) != FIN_PAID:
            raise BizException(
                f"只有已结清的对账单需要解锁（当前：{cls.status_text(recon)}）"
            )
        text = cls.assert_reason(reason, action="解锁结清")
        await cls.change_status(
            db, recon, FIN_REVIEWED,
            event_type=FinanceEventType.UNLOCK,
            operator_id=operator_id,
            reason=text,
            skip_lock_check=True,
        )
        return recon

    @classmethod
    async def refresh_settle_progress(
        cls, db: AsyncSession, recon_id: int, *, operator_id: Optional[int] = None,
    ) -> CustomerRecon:
        """按关联结算单重算结清进度，全部收妥则自动转「已结清」。

        由结算单侧在关联 / 收款 / 撤销后调用；对账单自己不感知结算单的状态变化。
        """
        from app.modules.client.models.finance.customer_settlement import (
            CustomerSettleReconLink,
            CustomerSettlement,
        )

        recon = await cls.get_or_404(db, recon_id)
        r = await db.execute(
            select(
                func.count(CustomerSettleReconLink.id),
                func.coalesce(
                    func.sum(CustomerSettleReconLink.applied_amount), 0
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                CustomerSettlement.status == FIN_PAID,
                                CustomerSettleReconLink.applied_amount,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),
            )
            .join(
                CustomerSettlement,
                CustomerSettlement.id == CustomerSettleReconLink.settle_id,
            )
            .where(
                CustomerSettleReconLink.recon_id == recon_id,
                CustomerSettleReconLink.is_deleted == 0,
                CustomerSettlement.is_deleted == 0,
                CustomerSettlement.status != FIN_CANCELLED,
            )
        )
        count, applied, received = r.one()
        recon.settle_count = int(count or 0)
        recon.applied_amount_total = Decimal(str(applied or 0))
        recon.received_amount_total = Decimal(str(received or 0))
        await db.flush()

        planned = Decimal(str(recon.planned_amount or 0))
        covered = (
            planned > 0
            and Decimal(str(recon.received_amount_total)) + AMOUNT_TOLERANCE
            >= planned
        )
        if covered and int(recon.status) == FIN_REVIEWED:
            await cls.change_status(
                db, recon, FIN_PAID,
                event_type=FinanceEventType.SETTLE,
                operator_id=operator_id,
                occurred_amount=recon.received_amount_total,
            )
        elif not covered and int(recon.status) == FIN_PAID:
            # 结算单撤销收款后钱已退回，对账单必须跟着退出「已结清」，
            # 否则应收看板上这笔钱凭空消失
            await cls.change_status(
                db, recon, FIN_REVIEWED,
                event_type=FinanceEventType.UNLOCK,
                operator_id=operator_id,
                reason="关联结算单收款已撤销，对账单退回已确认",
                skip_lock_check=True,
            )
        return recon

    # ------------------------------------------------------------------
    # 回灌重算
    # ------------------------------------------------------------------
    @classmethod
    async def recalc_from_business(
        cls,
        db: AsyncSession,
        recon_id: int,
        *,
        only_dirty: bool = True,
        operator_id: Optional[int] = None,
    ) -> int:
        """用业务侧当前事实刷新对账行快照与金额，返回刷新行数。

        这是文档 09 §5.3 的「回灌重算」处置路径：确认计费引擎的新结果正确后，
        把对账行拉回与业务一致，脏标记随之清除。行的手工调整额保留——那是人为
        商务决定，不该被重算抹掉。
        """
        recon = await cls.get_or_404(db, recon_id)
        cls.assert_editable(recon)
        lines = await cls._load_lines(db, recon_id)
        targets = [
            ln for ln in lines
            if not only_dirty or int(getattr(ln, "recon_dirty", 0) or 0) == 1
        ]
        if not targets:
            raise BizException("当前没有需要重算的对账行")

        ids = [int(ln.waybill_id) for ln in targets]
        waybills = {int(w.id): w for w in await cls._load_waybills(db, ids)}
        qty_map = await WaybillToFinance.signed_quantity_map(db, ids)
        now = datetime.now()
        for ln in targets:
            wb = waybills.get(int(ln.waybill_id))
            if wb is None:
                continue
            signed_qty = int(qty_map.get(int(ln.waybill_id), 0))
            qty, price, amount = cls._derive_line_amount(
                int(ln.billing_base or BillingBase.BY_VEHICLE), wb, signed_qty,
            )
            ln.quantity = qty
            ln.unit_price = price
            ln.amount = _money(amount + Decimal(str(ln.adjust_amount or 0)))
            ln.freight_amount_snapshot = (
                Decimal(str(wb.freight_amount))
                if wb.freight_amount is not None else None
            )
            ln.signed_quantity_snapshot = signed_qty
            ln.locked_snapshot_at = now
            ln.recon_dirty = 0
            ln.dirty_reason = None
            ln.dirty_at = None
        await db.flush()
        await cls.refresh_totals(db, recon_id)

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=recon_id,
            event_type=FinanceEventType.RECALC_REFRESH,
            direction=FinanceDirection.RECEIVE,
            operator_id=operator_id,
            reason=f"已按业务侧当前数据重算 {len(targets)} 行",
            payload_snapshot={"refreshedLines": len(targets)},
        )
        # 重算后重跑核对：已消解的差异自动失效，计数列同步刷新
        await ConsistencyChecker.check_recon(
            db, recon_kind=cls.doc_kind, recon_id=recon_id,
            operator_id=operator_id,
        )
        return len(targets)

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
        period_start: Optional[ddate] = None,
        period_end: Optional[ddate] = None,
        only_dirty: bool = False,
        only_diff: bool = False,
        only_unsigned: bool = False,
    ) -> Tuple[List[CustomerRecon], int]:
        stmt = select(CustomerRecon).where(CustomerRecon.is_deleted == 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                CustomerRecon.doc_no.like(kw)
                | CustomerRecon.customer_name.like(kw)
            )
        if customer_id:
            stmt = stmt.where(CustomerRecon.customer_id == customer_id)
        if enterprise_id:
            stmt = stmt.where(CustomerRecon.enterprise_id == enterprise_id)
        if status is not None:
            stmt = stmt.where(CustomerRecon.status == status)
        if period_start:
            stmt = stmt.where(CustomerRecon.period_end >= period_start)
        if period_end:
            stmt = stmt.where(CustomerRecon.period_start <= period_end)
        if only_dirty:
            stmt = stmt.where(CustomerRecon.dirty_line_count > 0)
        if only_diff:
            stmt = stmt.where(CustomerRecon.diff_open_count > 0)
        if only_unsigned:
            # 待客户回签：已确认但还没收到客户签字的单
            stmt = stmt.where(
                CustomerRecon.status == FIN_REVIEWED,
                CustomerRecon.confirmed_by_customer_at.is_(None),
            )

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(CustomerRecon.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_lines(
        cls, db: AsyncSession, recon_id: int,
    ) -> List[CustomerReconWaybillLink]:
        return await cls._load_lines(db, recon_id)

    @classmethod
    async def doc_no_map(
        cls, db: AsyncSession, recon_ids: Iterable[int],
    ) -> Dict[int, str]:
        """批量取对账单编号（差异待办列表要显示所属单号，避免逐行查询）。"""
        ids = [int(x) for x in recon_ids if x]
        if not ids:
            return {}
        r = await db.execute(
            select(CustomerRecon.id, CustomerRecon.doc_no)
            .where(CustomerRecon.id.in_(ids))
        )
        return {int(i): no for i, no in r.all()}

    @classmethod
    def status_text(cls, recon: Any) -> str:
        from app.modules.client.services.finance.base.finance_state_machine import (
            label,
        )
        return label(int(recon.status or 0), cls.doc_kind)

    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        """对账类的按钮位与通用模板不同：没有提交/审批，有确认与回签。"""
        status = int(doc.status)
        settled_or_cancelled = status in (FIN_PAID, FIN_CANCELLED)
        return {
            "canEdit": status == FIN_DRAFT,
            "canDelete": status in (FIN_DRAFT, FIN_CANCELLED),
            "canConfirm": status == FIN_DRAFT,
            "canForceConfirm": (
                status == FIN_DRAFT and int(doc.diff_open_count or 0) > 0
            ),
            "canCustomerSign": status in (FIN_REVIEWED, FIN_PAID),
            "canWithdraw": (
                status == FIN_REVIEWED and int(doc.settle_count or 0) == 0
            ),
            "canCancel": (
                not settled_or_cancelled and int(doc.settle_count or 0) == 0
            ),
            "canUnlockSettled": status == FIN_PAID,
            "canCheck": status in (FIN_DRAFT, FIN_REVIEWED),
            "canRecalc": status == FIN_DRAFT,
            "needAdjustApproval": cls._need_adjust_approval(doc),
        }

    # ------------------------------------------------------------------
    # 核对器绑定：客户侧的行级检测
    # ------------------------------------------------------------------
    @classmethod
    async def detect_line_diffs(
        cls,
        db: AsyncSession,
        recon: Any,
        lines: Sequence[Any],
    ) -> List[DiffCandidate]:
        """比对每行快照与业务侧当前事实（台数 / 金额 / 状态回退）。

        只比对**当前事实与快照**，不重算价格：价格是商务约定，快照就是约定本身；
        真正会漂移的是台数与计费引擎结果。
        """
        if not lines:
            return []
        ids = [int(ln.waybill_id) for ln in lines]
        waybills = {int(w.id): w for w in await cls._load_waybills(db, ids)}
        qty_map = await WaybillToFinance.signed_quantity_map(db, ids)

        out: List[DiffCandidate] = []
        for ln in lines:
            wid = int(ln.waybill_id)
            wb = waybills.get(wid)
            if wb is None:
                out.append(DiffCandidate(
                    biz_doc_id=wid,
                    biz_doc_no=ln.waybill_no,
                    link_id=int(ln.id),
                    diff_type=DiffType.INELIGIBLE,
                    expected_value="运单存在",
                    actual_value="运单已删除",
                ))
                continue

            if int(wb.status or 0) not in WAYBILL_RECONCILABLE_STATUSES:
                out.append(DiffCandidate(
                    biz_doc_id=wid,
                    biz_doc_no=ln.waybill_no,
                    link_id=int(ln.id),
                    diff_type=DiffType.STATUS_REVERTED,
                    expected_value="已交车",
                    actual_value="尚未交车",
                ))

            snap_qty = ln.signed_quantity_snapshot
            cur_qty = int(qty_map.get(wid, 0))
            if snap_qty is not None and int(snap_qty) != cur_qty:
                out.append(DiffCandidate(
                    biz_doc_id=wid,
                    biz_doc_no=ln.waybill_no,
                    link_id=int(ln.id),
                    diff_type=DiffType.QUANTITY,
                    expected_value=f"{int(snap_qty)} 台",
                    actual_value=f"{cur_qty} 台",
                ))

            snap_amt = ln.freight_amount_snapshot
            cur_amt = wb.freight_amount
            if snap_amt is not None and cur_amt is not None:
                delta = Decimal(str(cur_amt)) - Decimal(str(snap_amt))
                if abs(delta) >= AMOUNT_TOLERANCE:
                    out.append(DiffCandidate(
                        biz_doc_id=wid,
                        biz_doc_no=ln.waybill_no,
                        link_id=int(ln.id),
                        diff_type=DiffType.AMOUNT,
                        expected_value=f"{Decimal(str(snap_amt)):.2f} 元",
                        actual_value=f"{Decimal(str(cur_amt)):.2f} 元",
                        diff_amount=delta,
                    ))
        return out

    @classmethod
    async def detect_orphans(
        cls, db: AsyncSession, filters: dict,
    ) -> List[DiffCandidate]:
        """漏挂检测：周期内已交车、未挂任何对账单的运单。

        由对账工作台按客户 + 周期主动触发，故 ``customer_id`` 必填；不传则返回空，
        避免全表扫描把整个租户的历史运单都报成漏挂。
        """
        customer_id = filters.get("customer_id")
        if not customer_id:
            return []
        candidates = await WaybillToFinance.list_candidates(
            db,
            customer_id=int(customer_id),
            period_start=filters.get("period_start"),
            period_end=filters.get("period_end"),
            limit=int(filters.get("limit") or 200),
        )
        return [
            DiffCandidate(
                biz_doc_id=int(w.id),
                biz_doc_no=w.waybill_no,
                diff_type=DiffType.MISSING,
                expected_value="已挂入对账单",
                actual_value="未挂入任何对账单",
                diff_amount=(
                    Decimal(str(w.freight_amount))
                    if w.freight_amount is not None else None
                ),
            )
            for w in candidates
        ]

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @staticmethod
    def _derive_line_amount(
        billing_base: int, waybill: Waybill, signed_qty: int,
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """由计费基础与运单事实推导 (数量, 单价, 行金额)。

        行金额以运费金额为准而非乘积：按台单价常有除不尽（3 台 1000 元），先以
        运费落账不会因分位取整少收几分钱。之后手工改数量或单价，则按乘积重算。
        """
        freight = (
            Decimal(str(waybill.freight_amount))
            if waybill.freight_amount is not None else Decimal("0")
        )
        if billing_base == BillingBase.BY_VEHICLE:
            qty = Decimal(signed_qty or waybill.quantity or 0)
        elif billing_base in (BillingBase.BY_TRIP, BillingBase.FIXED):
            qty = Decimal("1")
        else:
            # 按吨：吨数不在运单上，留 0 由对账岗手工填
            qty = Decimal("0")
        price = _money(freight / qty) if qty > 0 else Decimal("0")
        return _money(qty), price, _money(freight)

    @staticmethod
    def _assert_reconcilable(waybill: Waybill, customer_id: int) -> None:
        if int(waybill.customer_id or 0) != int(customer_id):
            raise BizException(
                f"运单 {waybill.waybill_no} 不属于本对账单的客户，不能加入"
            )
        if int(waybill.status or 0) not in WAYBILL_RECONCILABLE_STATUSES:
            raise BizException(
                f"运单 {waybill.waybill_no} 还没有交车完成，暂时不能对账"
            )
        if int(waybill.is_locked or 0) == 1:
            raise BizException(
                f"运单 {waybill.waybill_no} 的费用已结清并锁定，不能重复对账"
            )

    @classmethod
    def _need_adjust_approval(cls, recon: Any) -> bool:
        total = abs(Decimal(str(recon.adjust_amount_total or 0)))
        return (
            total > ADJUST_APPROVAL_THRESHOLD
            and recon.adjust_approved_at is None
        )

    @classmethod
    def _assert_adjust_approved(cls, recon: Any) -> None:
        if cls._need_adjust_approval(recon):
            total = abs(Decimal(str(recon.adjust_amount_total or 0)))
            raise BizException(
                f"本单调整金额合计 {total:.2f} 元，超过 "
                f"{ADJUST_APPROVAL_THRESHOLD:.0f} 元需业务主管审批后才能确认"
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

    @classmethod
    async def _assert_period_unique(
        cls,
        db: AsyncSession,
        customer_id: int,
        period_start: datetime,
        period_end: datetime,
    ) -> None:
        r = await db.execute(
            select(CustomerRecon.doc_no).where(
                CustomerRecon.customer_id == customer_id,
                CustomerRecon.is_deleted == 0,
                CustomerRecon.status != FIN_CANCELLED,
                CustomerRecon.period_start == period_start,
                CustomerRecon.period_end == period_end,
            ).limit(1)
        )
        doc_no = r.scalar_one_or_none()
        if doc_no:
            raise BizException(
                f"该客户在这个周期已有对账单 {doc_no}，"
                "请直接在那张单上补充运单，或换一个对账周期"
            )

    @staticmethod
    async def _load_waybills(
        db: AsyncSession, waybill_ids: Sequence[int],
    ) -> List[Waybill]:
        if not waybill_ids:
            return []
        r = await db.execute(
            select(Waybill).where(
                Waybill.id.in_(list(waybill_ids)), Waybill.is_deleted == 0,
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_lines(
        db: AsyncSession, recon_id: int,
    ) -> List[CustomerReconWaybillLink]:
        r = await db.execute(
            select(CustomerReconWaybillLink)
            .where(
                CustomerReconWaybillLink.recon_id == recon_id,
                CustomerReconWaybillLink.is_deleted == 0,
            )
            .order_by(CustomerReconWaybillLink.id.asc())
        )
        return list(r.scalars().all())

    @staticmethod
    async def _get_line_or_404(
        db: AsyncSession, recon_id: int, link_id: int,
    ) -> CustomerReconWaybillLink:
        r = await db.execute(
            select(CustomerReconWaybillLink).where(
                CustomerReconWaybillLink.id == link_id,
                CustomerReconWaybillLink.recon_id == recon_id,
                CustomerReconWaybillLink.is_deleted == 0,
            )
        )
        line = r.scalar_one_or_none()
        if line is None:
            raise BizException("对账明细不存在或已被移除")
        return line

    @staticmethod
    async def _active_link_waybill_ids(
        db: AsyncSession, recon_id: int,
    ) -> List[int]:
        r = await db.execute(
            select(CustomerReconWaybillLink.waybill_id).where(
                CustomerReconWaybillLink.recon_id == recon_id,
                CustomerReconWaybillLink.is_deleted == 0,
            )
        )
        return [int(x) for x in r.scalars().all()]

    @staticmethod
    async def _mark_waybills_bound(
        db: AsyncSession, waybill_ids: Sequence[int], bound: bool,
    ) -> None:
        """维护运单的 ``is_recon_bound`` 软标记（仅供列表徽章，非拦截判据）。"""
        if not waybill_ids:
            return
        await db.execute(
            update(Waybill)
            .where(Waybill.id.in_(list(waybill_ids)))
            .values(is_recon_bound=1 if bound else 0)
        )
        await db.flush()

    @classmethod
    async def _unbind_waybill_if_free(
        cls, db: AsyncSession, waybill_id: int,
    ) -> None:
        """该运单不再挂在任何非撤销对账单上时，清掉软标记。"""
        still_bound = await ConsistencyChecker.is_biz_doc_bound(
            db, ReconKind.CUSTOMER, waybill_id,
        )
        if not still_bound:
            await cls._mark_waybills_bound(db, [waybill_id], False)


def _money(v: Decimal) -> Decimal:
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None


def _unique_ints(values: Sequence[Any]) -> List[int]:
    seen: Dict[int, None] = {}
    for v in values or []:
        if v:
            seen.setdefault(int(v), None)
    return list(seen.keys())


# 客户侧对账的表结构与检测器注册进核对器：置脏、差异检出、确认拦截、强制确认
# 之后全部走核对器的通用实现，不在本文件重复。
ConsistencyChecker.register_binding(ReconBinding(
    recon_kind=ReconKind.CUSTOMER,
    biz_doc_type=BizDocType.WAYBILL,
    recon_model=CustomerRecon,
    link_model=CustomerReconWaybillLink,
    link_recon_fk="recon_id",
    link_biz_fk="waybill_id",
    line_detector=CustomerReconService.detect_line_diffs,
    orphan_detector=CustomerReconService.detect_orphans,
))
