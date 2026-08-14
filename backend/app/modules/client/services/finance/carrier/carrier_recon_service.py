"""承运商对账单 Service（文档 03 §三）

与客户对账单同构：把周期内某承运商的任务列成行，核对台数与金额，确认后交结算单
付钱。应付侧多两件事，也正是本文件与客户侧的全部差异：

1. **预付扣减**：任务在途时可能已通过任务级预付 / 补款付过钱，建行时按当前已支付
   合计写 ``prepaid_offset_amount`` 快照，行净额 = 毛额 - 扣减。主表
   ``planned_amount`` 存净额合计——结算单按它付款，毛额只用于对账页展示。
2. **路径互斥**：一张任务的钱只能走一条路。任务级最终结算单已付过款的任务不能再
   进对账，判定统一走 ``ConsistencyChecker.assert_task_settle_exclusive``。

置脏、差异检出、确认拦截、强制确认全部复用核对器的通用实现，本模块只在导入时注册
承运商侧的表结构与两个检测器。
"""

from datetime import date as ddate, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.carrier_recon import (
    CARRIER_RECON_DOC_KIND,
    CarrierRecon,
    CarrierReconTaskLink,
)
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.models.partner.carrier_settlement import CarrierSettlement
from app.modules.client.models.task.constants import CarrierType
from app.modules.client.models.task.task import Task
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
)
from app.modules.client.services.finance.linkage.task_to_finance import (
    TASK_SETTLEABLE_STATUS,
    TaskToFinance,
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

# 行调整额触发业务主管审批的阈值（承运商侧 ¥3000，文档 03 §3.5）
ADJUST_APPROVAL_THRESHOLD = Decimal("3000")
# 金额比对容差：低于一分不算差异
AMOUNT_TOLERANCE = Decimal("0.01")
_CENT = Decimal("0.01")


class CarrierReconService(FinanceDocService):
    """承运商对账单"""

    model = CarrierRecon
    doc_kind = CARRIER_RECON_DOC_KIND
    doc_label = "承运商对账单"
    doc_no_prefix = "PR"
    direction = FinanceDirection.PAY
    editable_statuses = (FIN_DRAFT,)

    # ------------------------------------------------------------------
    # 候选池
    # ------------------------------------------------------------------
    @classmethod
    async def list_candidates(
        cls,
        db: AsyncSession,
        *,
        carrier_id: int,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        keyword: Optional[str] = None,
        recon_id: Optional[int] = None,
        limit: int = 500,
    ) -> List[dict]:
        """可加入对账单的任务候选，带上建行要用的业务事实与预付扣减预览。

        预付扣减在候选阶段就算出来给用户看：对账岗最关心的正是「这单是不是已经付过
        一部分了」，等挂进去才显示等于让人反复删行。
        """
        tasks = await TaskToFinance.list_carrier_recon_candidates(
            db,
            carrier_id=carrier_id,
            period_start=period_start,
            period_end=period_end,
            keyword=keyword,
            exclude_recon_id=recon_id,
            limit=limit,
        )
        if not tasks:
            return []
        out: List[dict] = []
        for t in tasks:
            offset = await TaskToFinance.paid_prepay_amount(db, int(t.id))
            gross = Decimal(str(t.carrier_cost_amount or 0))
            out.append({
                "taskId": int(t.id),
                "taskNo": t.task_no,
                "plateNumber": t.plate_number,
                "mainDriverName": t.main_driver_name,
                "origin": t.origin,
                "destination": t.destination,
                "signedQuantity": int(t.total_quantity or 0),
                "signedAt": t.actual_arrive_time,
                "carrierCostAmount": _f(gross),
                "prepaidOffsetAmount": _f(offset),
                "netAmount": _f(gross - offset),
                "status": int(t.status or 0),
            })
        return out

    # ------------------------------------------------------------------
    # 创建与行维护
    # ------------------------------------------------------------------
    @classmethod
    async def create_from_candidates(
        cls,
        db: AsyncSession,
        *,
        carrier_id: int,
        period_start: datetime,
        period_end: datetime,
        task_ids: Sequence[int],
        billing_base: int = BillingBase.BY_VEHICLE,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> CarrierRecon:
        """按选中候选生成草稿态对账单（并冻结推荐结算账户）。"""
        carrier = await cls._get_carrier_or_404(db, carrier_id)
        if period_start is None or period_end is None:
            raise BizException("请选择对账周期的起止日期")
        await cls._assert_period_unique(db, carrier_id, period_start, period_end)

        account = await cls.default_account(db, carrier_id)
        recon = CarrierRecon(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.PAY,
            status=FIN_DRAFT,
            carrier_id=carrier_id,
            carrier_name=carrier.carrier_name,
            carrier_short_name=carrier.short_name,
            enterprise_id=carrier.enterprise_id,
            carrier_contact_name=carrier.contact_person,
            carrier_contact_phone=carrier.contact_phone,
            settlement_account_id=(int(account.id) if account else None),
            settlement_account_label=(account.account_label if account else None),
            settlement_type_snapshot=(
                int(account.settlement_type) if account else None
            ),
            period_start=period_start,
            period_end=period_end,
            planned_amount=Decimal("0"),
            created_by=operator_id,
            remark=remark,
            dedup_key=CarrierRecon.build_dedup_key(
                carrier_id, period_start, period_end,
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
            direction=FinanceDirection.PAY,
            operator_id=operator_id,
            payload_snapshot={
                "carrierId": carrier_id,
                "periodStart": period_start.strftime("%Y-%m-%d"),
                "periodEnd": period_end.strftime("%Y-%m-%d"),
            },
        )
        if task_ids:
            await cls.add_tasks(
                db, recon.id, task_ids,
                billing_base=billing_base, operator_id=operator_id,
            )
        return recon

    @classmethod
    async def add_tasks(
        cls,
        db: AsyncSession,
        recon_id: int,
        task_ids: Sequence[int],
        *,
        billing_base: int = BillingBase.BY_VEHICLE,
        operator_id: Optional[int] = None,
    ) -> List[CarrierReconTaskLink]:
        """批量挂入任务并冻结业务事实与预付扣减快照。"""
        recon = await cls.get_or_404(db, recon_id)
        cls.assert_editable(recon)
        ids = _unique_ints(task_ids)
        if not ids:
            raise BizException("请先选择要加入对账的任务")

        existing = await cls._active_link_task_ids(db, recon_id)
        ids = [i for i in ids if i not in existing]
        if not ids:
            raise BizException("所选任务都已在本对账单中，无需重复添加")

        tasks = await cls._load_tasks(db, ids)
        now = datetime.now()
        rows: List[CarrierReconTaskLink] = []
        for t in tasks:
            cls._assert_reconcilable(t, int(recon.carrier_id))
            await ConsistencyChecker.assert_task_settle_exclusive(
                db, int(t.id), intent="carrier_recon",
            )
            if await ConsistencyChecker.is_biz_doc_bound(
                db, ReconKind.CARRIER, int(t.id), exclude_recon_id=recon_id,
            ):
                raise BizException(
                    f"任务 {t.task_no} 已在其他承运商对账单中，"
                    "请先从那张对账单移除再加入本单"
                )
            offset = await TaskToFinance.paid_prepay_amount(db, int(t.id))
            qty, price, gross = cls._derive_line_amount(billing_base, t)
            row = CarrierReconTaskLink(
                recon_id=recon_id,
                task_id=int(t.id),
                task_no=t.task_no,
                plate_number=t.plate_number,
                billing_base=billing_base,
                quantity=qty,
                unit_price=price,
                gross_amount=gross,
                adjust_amount=Decimal("0"),
                prepaid_offset_amount=offset,
                net_amount=_money(gross - offset),
                carrier_cost_snapshot=(
                    Decimal(str(t.carrier_cost_amount))
                    if t.carrier_cost_amount is not None else None
                ),
                signed_quantity_snapshot=int(t.total_quantity or 0),
                signed_at_snapshot=t.actual_arrive_time,
                locked_snapshot_at=now,
                dedup_key=CarrierReconTaskLink.build_dedup_key(
                    recon_id, int(t.id),
                ),
            )
            db.add(row)
            rows.append(row)
        await db.flush()

        await cls._mark_tasks_bound(db, [int(t.id) for t in tasks], True)
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
        """移除一行（软删并释放去重键，任务回到候选池）。"""
        recon = await cls.get_or_404(db, recon_id)
        cls.assert_editable(recon)
        line = await cls._get_line_or_404(db, recon_id, link_id)
        line.is_deleted = 1
        line.dedup_key = None
        await db.flush()
        await cls._unbind_task_if_free(db, int(line.task_id))
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
    ) -> CarrierReconTaskLink:
        """调整行的数量 / 单价 / 调整额，重算毛额与净额。

        **只有显式改了数量或单价才按乘积重算基数**；只改调整额时沿用建行时的任务成本
        基数。单价是 `成本 / 台数` 取两位小数的派生值，按台常除不尽（1000 元 3 台
        → 333.33），若每次调整都回落到乘积，账面会凭空少掉分位残差（文档 03 §3.5）。

        扣减额不在这里改：那是「已经付过多少钱」的客观事实，要改只能通过调整额补回，
        这样账上留得住痕迹。
        """
        recon = await cls.get_or_404(db, recon_id)
        cls.assert_editable(recon)
        line = await cls._get_line_or_404(db, recon_id, link_id)

        old_adjust = Decimal(str(line.adjust_amount or 0))
        base = Decimal(str(line.gross_amount or 0)) - old_adjust
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
        line.gross_amount = _money(base + Decimal(str(line.adjust_amount or 0)))
        line.net_amount = _money(
            Decimal(str(line.gross_amount))
            - Decimal(str(line.prepaid_offset_amount or 0))
        )
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
                direction=FinanceDirection.PAY,
                occurred_amount=new_adjust - old_adjust,
                operator_id=operator_id,
                reason=line.adjust_reason,
                payload_snapshot={
                    "linkId": int(line.id),
                    "taskNo": line.task_no,
                    "oldAdjust": float(old_adjust),
                    "newAdjust": float(new_adjust),
                    "netAmount": float(line.net_amount or 0),
                },
            )
            await db.flush()
        return line

    @classmethod
    async def refresh_totals(cls, db: AsyncSession, recon_id: int) -> None:
        """重算主表合计。``planned_amount`` 取净额合计（结算单按它付钱）。"""
        r = await db.execute(
            select(
                func.count(CarrierReconTaskLink.id),
                func.coalesce(func.sum(CarrierReconTaskLink.quantity), 0),
                func.coalesce(func.sum(CarrierReconTaskLink.gross_amount), 0),
                func.coalesce(
                    func.sum(CarrierReconTaskLink.prepaid_offset_amount), 0
                ),
                func.coalesce(func.sum(CarrierReconTaskLink.net_amount), 0),
                func.coalesce(func.sum(CarrierReconTaskLink.adjust_amount), 0),
            ).where(
                CarrierReconTaskLink.recon_id == recon_id,
                CarrierReconTaskLink.is_deleted == 0,
            )
        )
        count, qty, gross, offset, net, adjust = r.one()
        await db.execute(
            update(CarrierRecon)
            .where(CarrierRecon.id == recon_id)
            .values(
                task_count=int(count or 0),
                total_quantity=Decimal(str(qty or 0)),
                gross_amount_total=Decimal(str(gross or 0)),
                prepaid_offset_total=Decimal(str(offset or 0)),
                planned_amount=Decimal(str(net or 0)),
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
    ) -> CarrierRecon:
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
            direction=FinanceDirection.PAY,
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
    ) -> CarrierRecon:
        """草稿 → 已确认。

        净额允许为 0（预付已把钱付完的纯抵账单），但不允许为负——那说明预付比对账
        总额还多，属于数据错误，得先查清楚。
        """
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) != FIN_DRAFT:
            raise BizException(
                f"只有草稿状态的对账单可以确认（当前：{cls.status_text(recon)}）"
            )
        if int(recon.task_count or 0) <= 0:
            raise BizException("对账单里还没有任务，请先添加对账明细")
        if Decimal(str(recon.planned_amount or 0)) < 0:
            raise BizException(
                "净应付金额为负数，说明预付金额已超过对账总额；"
                "请核对预付单与各行金额后再确认"
            )
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
                "taskCount": int(recon.task_count or 0),
                "forced": bool(force_reason),
            },
        )
        return recon

    @classmethod
    async def record_carrier_sign(
        cls,
        db: AsyncSession,
        recon_id: int,
        *,
        signer_name: str,
        voucher_url: Optional[str] = None,
        signed_at: Optional[datetime] = None,
        operator_id: Optional[int] = None,
    ) -> CarrierRecon:
        """登记承运商回签（不改状态，只补事实与凭证）。"""
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) not in (FIN_REVIEWED, FIN_PAID):
            raise BizException("请先确认对账单，再登记承运商回签")
        if not (signer_name or "").strip():
            raise BizException("请填写承运商确认人姓名")
        recon.confirmed_by_carrier_name = signer_name.strip()
        recon.confirmed_by_carrier_at = signed_at or datetime.now()
        if voucher_url:
            recon.confirm_voucher_url = voucher_url
        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=recon_id,
            event_type=FinanceEventType.LOCK,
            direction=FinanceDirection.PAY,
            operator_id=operator_id,
            reason=f"承运商 {recon.confirmed_by_carrier_name} 已回签",
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
    ) -> CarrierRecon:
        """已确认 → 草稿（退回修改）。已被结算单关联时拒绝。"""
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) != FIN_REVIEWED:
            raise BizException(
                f"只有已确认的对账单可以退回草稿（当前：{cls.status_text(recon)}）"
            )
        if int(recon.settle_count or 0) > 0:
            raise BizException(
                "本对账单已被结算单关联，不能退回草稿；请先撤销相关结算单再退回"
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
    ) -> CarrierRecon:
        """撤销对账单：释放任务挂接、失效未决差异、释放同期唯一键。"""
        recon = await cls.get_or_404(db, recon_id)
        if int(recon.status) == FIN_CANCELLED:
            raise BizException("该对账单已撤销，无需重复操作")
        if int(recon.settle_count or 0) > 0:
            raise BizException(
                "本对账单已被结算单关联，不能撤销；请先撤销相关结算单"
            )
        text = cls.assert_reason(reason)
        task_ids = await cls._active_link_task_ids(db, recon_id)

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
        for tid in task_ids:
            await cls._unbind_task_if_free(db, tid)
        return recon

    @classmethod
    async def unlock_settled(
        cls,
        db: AsyncSession,
        recon_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> CarrierRecon:
        """已结清 → 已确认（承运商事后追加差异，高权限）。"""
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
    ) -> CarrierRecon:
        """按关联结算单重算结清进度，全部付妥则自动转「已结清」。

        与客户侧一致，转换是双向的：结算单撤销付款后钱退回来了，对账单必须退出
        「已结清」，否则应付看板上这笔钱会凭空消失。
        """
        from app.modules.client.models.finance.carrier_settlement_doc import (
            CarrierSettleReconLink,
            CarrierSettlementDoc,
        )

        recon = await cls.get_or_404(db, recon_id)
        r = await db.execute(
            select(
                func.count(CarrierSettleReconLink.id),
                func.coalesce(
                    func.sum(CarrierSettleReconLink.applied_amount), 0
                ),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                CarrierSettlementDoc.status == FIN_PAID,
                                CarrierSettleReconLink.applied_amount,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ),
            )
            .join(
                CarrierSettlementDoc,
                CarrierSettlementDoc.id == CarrierSettleReconLink.settle_id,
            )
            .where(
                CarrierSettleReconLink.recon_id == recon_id,
                CarrierSettleReconLink.is_deleted == 0,
                CarrierSettlementDoc.is_deleted == 0,
                CarrierSettlementDoc.status != FIN_CANCELLED,
            )
        )
        count, applied, paid = r.one()
        recon.settle_count = int(count or 0)
        recon.applied_amount_total = Decimal(str(applied or 0))
        recon.paid_amount_total = Decimal(str(paid or 0))
        await db.flush()

        planned = Decimal(str(recon.planned_amount or 0))
        covered = (
            planned > 0
            and Decimal(str(recon.paid_amount_total)) + AMOUNT_TOLERANCE >= planned
        )
        if covered and int(recon.status) == FIN_REVIEWED:
            await cls.change_status(
                db, recon, FIN_PAID,
                event_type=FinanceEventType.SETTLE,
                operator_id=operator_id,
                occurred_amount=recon.paid_amount_total,
            )
        elif not covered and int(recon.status) == FIN_PAID:
            await cls.change_status(
                db, recon, FIN_REVIEWED,
                event_type=FinanceEventType.UNLOCK,
                operator_id=operator_id,
                reason="关联结算单付款已撤销，对账单退回已确认",
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

        扣减额也一起刷新：预付单在对账期间被撤销或补付都会让扣减额变化，回灌的语义
        就是「认可业务侧现值」，此时把扣减额一并拉正才是一致的。手工调整额保留。
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

        ids = [int(ln.task_id) for ln in targets]
        tasks = {int(t.id): t for t in await cls._load_tasks(db, ids)}
        now = datetime.now()
        for ln in targets:
            t = tasks.get(int(ln.task_id))
            if t is None:
                continue
            qty, price, gross = cls._derive_line_amount(
                int(ln.billing_base or BillingBase.BY_VEHICLE), t,
            )
            offset = await TaskToFinance.paid_prepay_amount(db, int(t.id))
            ln.quantity = qty
            ln.unit_price = price
            ln.gross_amount = _money(gross + Decimal(str(ln.adjust_amount or 0)))
            ln.prepaid_offset_amount = offset
            ln.net_amount = _money(Decimal(str(ln.gross_amount)) - offset)
            ln.carrier_cost_snapshot = (
                Decimal(str(t.carrier_cost_amount))
                if t.carrier_cost_amount is not None else None
            )
            ln.signed_quantity_snapshot = int(t.total_quantity or 0)
            ln.signed_at_snapshot = t.actual_arrive_time
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
            direction=FinanceDirection.PAY,
            operator_id=operator_id,
            reason=f"已按业务侧当前数据重算 {len(targets)} 行",
            payload_snapshot={"refreshedLines": len(targets)},
        )
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
        carrier_id: Optional[int] = None,
        enterprise_id: Optional[int] = None,
        status: Optional[int] = None,
        period_start: Optional[ddate] = None,
        period_end: Optional[ddate] = None,
        only_dirty: bool = False,
        only_diff: bool = False,
        only_unsigned: bool = False,
    ) -> Tuple[List[CarrierRecon], int]:
        stmt = select(CarrierRecon).where(CarrierRecon.is_deleted == 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                CarrierRecon.doc_no.like(kw)
                | CarrierRecon.carrier_name.like(kw)
            )
        if carrier_id:
            stmt = stmt.where(CarrierRecon.carrier_id == carrier_id)
        if enterprise_id:
            stmt = stmt.where(CarrierRecon.enterprise_id == enterprise_id)
        if status is not None:
            stmt = stmt.where(CarrierRecon.status == status)
        if period_start:
            stmt = stmt.where(CarrierRecon.period_end >= period_start)
        if period_end:
            stmt = stmt.where(CarrierRecon.period_start <= period_end)
        if only_dirty:
            stmt = stmt.where(CarrierRecon.dirty_line_count > 0)
        if only_diff:
            stmt = stmt.where(CarrierRecon.diff_open_count > 0)
        if only_unsigned:
            stmt = stmt.where(
                CarrierRecon.status == FIN_REVIEWED,
                CarrierRecon.confirmed_by_carrier_at.is_(None),
            )

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(CarrierRecon.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_lines(
        cls, db: AsyncSession, recon_id: int,
    ) -> List[CarrierReconTaskLink]:
        return await cls._load_lines(db, recon_id)

    @classmethod
    async def doc_no_map(
        cls, db: AsyncSession, recon_ids: Iterable[int],
    ) -> Dict[int, str]:
        ids = [int(x) for x in recon_ids if x]
        if not ids:
            return {}
        r = await db.execute(
            select(CarrierRecon.id, CarrierRecon.doc_no)
            .where(CarrierRecon.id.in_(ids))
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
        """对账类按钮位：没有提交/审批，有确认与回签（与客户侧同构）。"""
        status = int(doc.status)
        settled_or_cancelled = status in (FIN_PAID, FIN_CANCELLED)
        return {
            "canEdit": status == FIN_DRAFT,
            "canDelete": status in (FIN_DRAFT, FIN_CANCELLED),
            "canConfirm": status == FIN_DRAFT,
            "canForceConfirm": (
                status == FIN_DRAFT and int(doc.diff_open_count or 0) > 0
            ),
            "canCarrierSign": status in (FIN_REVIEWED, FIN_PAID),
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
    # 核对器绑定：承运商侧的行级检测
    # ------------------------------------------------------------------
    @classmethod
    async def detect_line_diffs(
        cls,
        db: AsyncSession,
        recon: Any,
        lines: Sequence[Any],
    ) -> List[DiffCandidate]:
        """比对每行快照与任务侧当前事实（台数 / 成本 / 扣减 / 状态回退）。

        扣减不符（``DiffType.OFFSET``）是应付侧特有且最危险的一类：预付单事后被撤销
        却没人改对账行，就会照着旧扣减少付钱，承运商一定会来吵。
        """
        if not lines:
            return []
        ids = [int(ln.task_id) for ln in lines]
        tasks = {int(t.id): t for t in await cls._load_tasks(db, ids)}

        out: List[DiffCandidate] = []
        for ln in lines:
            tid = int(ln.task_id)
            t = tasks.get(tid)
            if t is None:
                out.append(DiffCandidate(
                    biz_doc_id=tid,
                    biz_doc_no=ln.task_no,
                    link_id=int(ln.id),
                    diff_type=DiffType.INELIGIBLE,
                    expected_value="任务存在",
                    actual_value="任务已删除",
                ))
                continue

            if int(t.status or 0) < TASK_SETTLEABLE_STATUS:
                out.append(DiffCandidate(
                    biz_doc_id=tid,
                    biz_doc_no=ln.task_no,
                    link_id=int(ln.id),
                    diff_type=DiffType.STATUS_REVERTED,
                    expected_value="已交车",
                    actual_value="尚未交车",
                ))

            snap_qty = ln.signed_quantity_snapshot
            cur_qty = int(t.total_quantity or 0)
            if snap_qty is not None and int(snap_qty) != cur_qty:
                out.append(DiffCandidate(
                    biz_doc_id=tid,
                    biz_doc_no=ln.task_no,
                    link_id=int(ln.id),
                    diff_type=DiffType.QUANTITY,
                    expected_value=f"{int(snap_qty)} 台",
                    actual_value=f"{cur_qty} 台",
                ))

            snap_cost = ln.carrier_cost_snapshot
            cur_cost = t.carrier_cost_amount
            if snap_cost is not None and cur_cost is not None:
                delta = Decimal(str(cur_cost)) - Decimal(str(snap_cost))
                if abs(delta) >= AMOUNT_TOLERANCE:
                    out.append(DiffCandidate(
                        biz_doc_id=tid,
                        biz_doc_no=ln.task_no,
                        link_id=int(ln.id),
                        diff_type=DiffType.AMOUNT,
                        expected_value=f"{Decimal(str(snap_cost)):.2f} 元",
                        actual_value=f"{Decimal(str(cur_cost)):.2f} 元",
                        diff_amount=delta,
                    ))

            snap_offset = Decimal(str(ln.prepaid_offset_amount or 0))
            cur_offset = await TaskToFinance.paid_prepay_amount(db, tid)
            if abs(cur_offset - snap_offset) >= AMOUNT_TOLERANCE:
                out.append(DiffCandidate(
                    biz_doc_id=tid,
                    biz_doc_no=ln.task_no,
                    link_id=int(ln.id),
                    diff_type=DiffType.OFFSET,
                    expected_value=f"扣减 {snap_offset:.2f} 元",
                    actual_value=f"实际已付预付补款 {cur_offset:.2f} 元",
                    diff_amount=cur_offset - snap_offset,
                ))
        return out

    @classmethod
    async def detect_orphans(
        cls, db: AsyncSession, filters: dict,
    ) -> List[DiffCandidate]:
        """漏挂检测：周期内已交车、未挂任何对账单的任务。"""
        carrier_id = filters.get("carrier_id")
        if not carrier_id:
            return []
        candidates = await TaskToFinance.list_carrier_recon_candidates(
            db,
            carrier_id=int(carrier_id),
            period_start=filters.get("period_start"),
            period_end=filters.get("period_end"),
            limit=int(filters.get("limit") or 200),
        )
        return [
            DiffCandidate(
                biz_doc_id=int(t.id),
                biz_doc_no=t.task_no,
                diff_type=DiffType.MISSING,
                expected_value="已挂入对账单",
                actual_value="未挂入任何对账单",
                diff_amount=(
                    Decimal(str(t.carrier_cost_amount))
                    if t.carrier_cost_amount is not None else None
                ),
            )
            for t in candidates
        ]

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @staticmethod
    def _derive_line_amount(
        billing_base: int, task: Task,
    ) -> Tuple[Decimal, Decimal, Decimal]:
        """由计费基础与任务事实推导 (数量, 单价, 毛额)。

        与客户侧同理：毛额以任务承运成本为准，不按乘积——按台单价常除不尽，
        乘积落账会少付几分钱。手工改数量或单价后才按乘积重算。
        """
        cost = (
            Decimal(str(task.carrier_cost_amount))
            if task.carrier_cost_amount is not None else Decimal("0")
        )
        if billing_base == BillingBase.BY_VEHICLE:
            qty = Decimal(int(task.total_quantity or 0))
        elif billing_base in (BillingBase.BY_TRIP, BillingBase.FIXED):
            qty = Decimal("1")
        else:
            qty = Decimal("0")
        price = _money(cost / qty) if qty > 0 else Decimal("0")
        return _money(qty), price, _money(cost)

    @staticmethod
    def _assert_reconcilable(task: Task, carrier_id: int) -> None:
        if int(task.carrier_id or 0) != int(carrier_id):
            raise BizException(
                f"任务 {task.task_no} 不属于本对账单的承运商，不能加入"
            )
        if int(task.carrier_type or 0) != CarrierType.CARRIER:
            raise BizException(
                f"任务 {task.task_no} 不是承运商承运（自有车走司机工资单、"
                "社会运力走任务级尾款），不能加入承运商对账"
            )
        if int(task.status or 0) < TASK_SETTLEABLE_STATUS:
            raise BizException(
                f"任务 {task.task_no} 还没有交车完成，暂时不能对账"
            )
        if int(task.is_locked or 0) == 1:
            raise BizException(
                f"任务 {task.task_no} 的费用已结清并锁定，不能重复对账"
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
    async def default_account(
        db: AsyncSession, carrier_id: int,
    ) -> Optional[CarrierSettlement]:
        """取承运商的默认结算账户（启用中、is_default 优先）。结算单侧建单也用它。"""
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
            .limit(1)
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def get_account_or_404(
        db: AsyncSession, carrier_id: int, account_id: int,
    ) -> CarrierSettlement:
        """按 ID 取结算账户，并校验归属与启用状态。

        付错账户等于把钱付给别人，故归属校验放在最底层，任何写入路径都绕不过。
        """
        r = await db.execute(
            select(CarrierSettlement).where(
                CarrierSettlement.id == account_id,
                CarrierSettlement.is_deleted == 0,
            )
        )
        account = r.scalar_one_or_none()
        if account is None:
            raise BizException("结算账户不存在，请重新选择")
        if int(account.carrier_id or 0) != int(carrier_id):
            raise BizException("该账户不属于本承运商，请重新选择，以免付错款")
        if int(account.status or 0) != 1:
            raise BizException(
                f"账户「{account.account_label}」已停用，请换一个启用中的账户"
            )
        return account

    @classmethod
    async def _assert_period_unique(
        cls,
        db: AsyncSession,
        carrier_id: int,
        period_start: datetime,
        period_end: datetime,
    ) -> None:
        r = await db.execute(
            select(CarrierRecon.doc_no).where(
                CarrierRecon.carrier_id == carrier_id,
                CarrierRecon.is_deleted == 0,
                CarrierRecon.status != FIN_CANCELLED,
                CarrierRecon.period_start == period_start,
                CarrierRecon.period_end == period_end,
            ).limit(1)
        )
        doc_no = r.scalar_one_or_none()
        if doc_no:
            raise BizException(
                f"该承运商在这个周期已有对账单 {doc_no}，"
                "请直接在那张单上补充任务，或换一个对账周期"
            )

    @staticmethod
    async def _load_tasks(
        db: AsyncSession, task_ids: Sequence[int],
    ) -> List[Task]:
        if not task_ids:
            return []
        r = await db.execute(
            select(Task).where(
                Task.id.in_(list(task_ids)), Task.is_deleted == 0,
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_lines(
        db: AsyncSession, recon_id: int,
    ) -> List[CarrierReconTaskLink]:
        r = await db.execute(
            select(CarrierReconTaskLink)
            .where(
                CarrierReconTaskLink.recon_id == recon_id,
                CarrierReconTaskLink.is_deleted == 0,
            )
            .order_by(CarrierReconTaskLink.id.asc())
        )
        return list(r.scalars().all())

    @staticmethod
    async def _get_line_or_404(
        db: AsyncSession, recon_id: int, link_id: int,
    ) -> CarrierReconTaskLink:
        r = await db.execute(
            select(CarrierReconTaskLink).where(
                CarrierReconTaskLink.id == link_id,
                CarrierReconTaskLink.recon_id == recon_id,
                CarrierReconTaskLink.is_deleted == 0,
            )
        )
        line = r.scalar_one_or_none()
        if line is None:
            raise BizException("对账明细不存在或已被移除")
        return line

    @staticmethod
    async def _active_link_task_ids(
        db: AsyncSession, recon_id: int,
    ) -> List[int]:
        r = await db.execute(
            select(CarrierReconTaskLink.task_id).where(
                CarrierReconTaskLink.recon_id == recon_id,
                CarrierReconTaskLink.is_deleted == 0,
            )
        )
        return [int(x) for x in r.scalars().all()]

    @staticmethod
    async def _mark_tasks_bound(
        db: AsyncSession, task_ids: Sequence[int], bound: bool,
    ) -> None:
        """维护任务的 ``is_recon_bound`` 软标记。

        它同时是「任务级最终结算单不许再开」的判据（见
        ``assert_task_settle_exclusive`` 的 ``final_settle`` 分支），因此必须与桥接
        行同事务维护，不能只当徽章。
        """
        if not task_ids:
            return
        await db.execute(
            update(Task)
            .where(Task.id.in_(list(task_ids)))
            .values(is_recon_bound=1 if bound else 0)
        )
        await db.flush()

    @classmethod
    async def _unbind_task_if_free(cls, db: AsyncSession, task_id: int) -> None:
        still_bound = await ConsistencyChecker.is_biz_doc_bound(
            db, ReconKind.CARRIER, task_id,
        )
        if not still_bound:
            await cls._mark_tasks_bound(db, [task_id], False)


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


# 承运商侧对账的表结构与检测器注册进核对器
ConsistencyChecker.register_binding(ReconBinding(
    recon_kind=ReconKind.CARRIER,
    biz_doc_type=BizDocType.TASK,
    recon_model=CarrierRecon,
    link_model=CarrierReconTaskLink,
    link_recon_fk="recon_id",
    link_biz_fk="task_id",
    line_detector=CarrierReconService.detect_line_diffs,
    orphan_detector=CarrierReconService.detect_orphans,
))
