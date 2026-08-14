"""自有司机工资单 Service（文档 04 §三 ~ §五）

工资单与承运商对账最大的不同：**没有对账对手**。司机不会跟公司逐台核对，所以这里
不接一致性核对器，也没有「回签」与「差异台账」；任务事实变动靠
``task.is_payroll_bound`` 软锁直接拦在业务侧。

金额口径钉死在三处（模型注释、本 Service 的 ``refresh_totals``、工资条渲染），任何
一处改了必须同步另外两处：

    应发 = 底薪与补贴合计 + 任务提成合计
    实发 = 应发 - 扣减项合计 - 抵账项合计 - 任务级预付抵扣

两个刻意的设计选择：

1. **提成汇总项不可手工改**：``commission_total`` 这一行的金额恒等于任务提成行合计，
   由系统回填。允许手改就会出现「工资条加总对不上」，而司机对工资条的信任一次就
   崩完。
2. **预付抵扣按本单已挂任务汇总**，不是按周期扫全部预付单。按周期扫会在同司机跨
   周期补挂任务时重复扣钱；按已挂任务汇总天然与工资单口径一致。
"""

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.models.capacity.self_capacity.driver.driver_account import (
    DriverAccount,
)
from app.modules.client.models.finance.driver_payroll import (
    DRIVER_PAYROLL_DOC_KIND,
    DriverPayroll,
    DriverPayrollItem,
    DriverPayrollTaskLink,
)
from app.modules.client.models.task.constants import CarrierType
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
from app.modules.client.services.finance.base.constants import (
    COMMISSION_ITEM_TYPE,
    PAYROLL_ITEM_TYPES,
    BillingBase,
    DocType,
    FinanceDirection,
    PayrollItemCategory,
    PayrollModel,
    PayrollPeriodType,
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
from app.modules.client.services.finance.linkage.lock_orchestrator import (
    LockOrchestrator,
)
from app.modules.client.services.finance.linkage.task_to_finance import (
    TASK_SETTLEABLE_STATUS,
    TaskToFinance,
)

_CENT = Decimal("0.01")
AMOUNT_TOLERANCE = Decimal("0.01")
# 司机侧提成调整超过此额需主管审批（文档 04 §3.6 未定额，取承运商侧一半）
ADJUST_APPROVAL_THRESHOLD = Decimal("1500")


class DriverPayrollService(FinanceDocService):
    """自有司机工资单"""

    model = DriverPayroll
    doc_kind = DRIVER_PAYROLL_DOC_KIND
    doc_label = "司机工资单"
    doc_no_prefix = "DP"
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
        driver_id: int,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        limit: int = 500,
    ) -> List[dict]:
        """该司机本周期可计提成的任务（自有车、已交车、未挂其他工资单）。

        任务上冷冻的是运力而非司机，所以先把该司机名下所有运力（含已解绑的历史运力）
        取出来再按运力筛任务——只看当前绑定会漏掉换车前跑的任务。
        """
        capacity_ids = await cls._capacity_ids_of(db, driver_id)
        if not capacity_ids:
            return []
        out: List[dict] = []
        for cid in capacity_ids:
            tasks = await TaskToFinance.list_payroll_candidates(
                db,
                capacity_id=cid,
                period_start=period_start,
                period_end=period_end,
                limit=limit,
            )
            for t in tasks:
                out.append({
                    "taskId": int(t.id),
                    "taskNo": t.task_no,
                    "plateNumber": t.plate_number,
                    "origin": t.origin,
                    "destination": t.destination,
                    "signedQuantity": int(t.total_quantity or 0),
                    "signedAt": t.actual_arrive_time,
                    "prepaidPaidAmount": _f(
                        await cls._task_driver_prepaid(db, int(t.id), driver_id)
                    ),
                    "status": int(t.status or 0),
                })
            if len(out) >= limit:
                break
        return out[:limit]

    @classmethod
    async def list_accounts(cls, db: AsyncSession, driver_id: int) -> List[dict]:
        """该司机的可用账户（发薪账户下拉）。"""
        r = await db.execute(
            select(DriverAccount)
            .where(
                DriverAccount.driver_id == driver_id,
                DriverAccount.is_deleted == 0,
                DriverAccount.status == 1,
            )
            .order_by(DriverAccount.account_type.asc(), DriverAccount.id.asc())
        )
        return [
            {
                "accountId": int(a.id),
                "accountType": int(a.account_type or 0),
                "accountName": a.account_name,
                "accountNoMasked": _mask(a.account_no),
                "balance": _f(a.balance),
            }
            for a in r.scalars().all()
        ]

    # ------------------------------------------------------------------
    # 创建与任务提成行
    # ------------------------------------------------------------------
    @classmethod
    async def create_from_candidates(
        cls,
        db: AsyncSession,
        *,
        driver_id: int,
        period_start: datetime,
        period_end: datetime,
        task_ids: Sequence[int] = (),
        payroll_model: int = PayrollModel.MIXED,
        period_type: int = PayrollPeriodType.MONTHLY,
        unit_price: Optional[Decimal] = None,
        billing_base: int = BillingBase.BY_VEHICLE,
        account_id: Optional[int] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> DriverPayroll:
        """生成草稿工资单。

        ``unit_price`` 是本单任务提成的统一计件单价：系统没有司机提成费率表，单价由
        制单人按当期约定填一次，个别任务再单独调整。留空则建 0 元行，等着后面调整。
        """
        driver = await cls._get_driver_or_404(db, driver_id)
        if period_start is None or period_end is None:
            raise BizException("请选择工资周期的起止日期")
        if period_start > period_end:
            raise BizException("工资周期的开始日期不能晚于结束日期")
        if int(payroll_model) not in PayrollModel.ALL:
            raise BizException("薪资模型不正确，请选择月薪固定、计件提成或底薪加提成")
        await cls._assert_period_unique(db, driver_id, period_start, period_end)

        account = None
        if account_id:
            account = await cls.get_account_or_404(db, driver_id, int(account_id))
        else:
            account = await cls._default_account(db, driver_id)

        payroll = DriverPayroll(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.PAY,
            status=FIN_DRAFT,
            driver_id=driver_id,
            driver_name=driver.name,
            driver_phone=driver.phone,
            enterprise_id=driver.enterprise_id,
            payroll_model=int(payroll_model),
            period_type=int(period_type),
            period_start=period_start,
            period_end=period_end,
            planned_amount=Decimal("0"),
            account_id=(int(account.id) if account else None),
            account_type=(int(account.account_type) if account else None),
            account_name_snapshot=(account.account_name if account else None),
            account_no_masked=(_mask(account.account_no) if account else None),
            created_by=operator_id,
            remark=remark,
            dedup_key=DriverPayroll.build_dedup_key(
                driver_id, period_start, period_end,
            ),
        )
        db.add(payroll)
        await db.flush()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=payroll.id,
            event_type=FinanceEventType.CREATE,
            to_status=FIN_DRAFT,
            direction=FinanceDirection.PAY,
            operator_id=operator_id,
            payload_snapshot={
                "driverId": driver_id,
                "periodStart": period_start.strftime("%Y-%m-%d"),
                "periodEnd": period_end.strftime("%Y-%m-%d"),
                "payrollModel": int(payroll_model),
            },
        )
        if task_ids:
            await cls.add_tasks(
                db, payroll.id, task_ids,
                unit_price=unit_price,
                billing_base=billing_base,
                operator_id=operator_id,
            )
        else:
            await cls.refresh_totals(db, payroll.id)
        return payroll

    @classmethod
    async def add_tasks(
        cls,
        db: AsyncSession,
        payroll_id: int,
        task_ids: Sequence[int],
        *,
        unit_price: Optional[Decimal] = None,
        billing_base: int = BillingBase.BY_VEHICLE,
        operator_id: Optional[int] = None,
    ) -> List[DriverPayrollTaskLink]:
        """批量挂入任务提成行，并给任务打上工资单软锁。"""
        payroll = await cls.get_or_404(db, payroll_id)
        cls.assert_editable(payroll)
        ids = _unique_ints(task_ids)
        if not ids:
            raise BizException("请先选择要计入工资的任务")

        existing = await cls._active_task_ids(db, payroll_id)
        ids = [i for i in ids if i not in existing]
        if not ids:
            raise BizException("所选任务都已在本工资单中，无需重复添加")

        capacity_ids = set(await cls._capacity_ids_of(db, int(payroll.driver_id)))
        price = Decimal(str(unit_price or 0)).quantize(_CENT, ROUND_HALF_UP)
        if price < 0:
            raise BizException("计件单价不能为负数")

        tasks = await cls._load_tasks(db, ids)
        now = datetime.now()
        rows: List[DriverPayrollTaskLink] = []
        for t in tasks:
            cls._assert_payable(t, capacity_ids)
            qty = cls._derive_quantity(billing_base, t)
            row = DriverPayrollTaskLink(
                payroll_id=payroll_id,
                task_id=int(t.id),
                task_no=t.task_no,
                plate_number=t.plate_number,
                signed_at=t.actual_arrive_time,
                billing_base=int(billing_base),
                quantity=qty,
                unit_price=price,
                commission_amount=_money(qty * price),
                adjust_amount=Decimal("0"),
                signed_quantity_snapshot=int(t.total_quantity or 0),
                locked_snapshot_at=now,
                dedup_key=DriverPayrollTaskLink.build_dedup_key(
                    payroll_id, int(t.id),
                ),
            )
            db.add(row)
            rows.append(row)
        await db.flush()

        await LockOrchestrator.mark_tasks_payroll_bound(
            db, [int(t.id) for t in tasks], bound=True,
        )
        await cls.refresh_totals(db, payroll_id)
        return rows

    @classmethod
    async def remove_task(
        cls,
        db: AsyncSession,
        payroll_id: int,
        link_id: int,
        *,
        operator_id: Optional[int] = None,
    ) -> None:
        """移除任务提成行（软删并解除软锁，任务回到候选池）。"""
        payroll = await cls.get_or_404(db, payroll_id)
        cls.assert_editable(payroll)
        row = await cls._get_task_link_or_404(db, payroll_id, link_id)
        row.is_deleted = 1
        row.dedup_key = None
        await db.flush()
        await LockOrchestrator.mark_tasks_payroll_bound(
            db, [int(row.task_id)], bound=False,
        )
        await cls.refresh_totals(db, payroll_id)

    @classmethod
    async def adjust_task(
        cls,
        db: AsyncSession,
        payroll_id: int,
        link_id: int,
        *,
        quantity: Optional[Decimal] = None,
        unit_price: Optional[Decimal] = None,
        adjust_amount: Optional[Decimal] = None,
        adjust_reason: Optional[str] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> DriverPayrollTaskLink:
        """调整单条任务的提成（数量 / 单价 / 调整额）。"""
        payroll = await cls.get_or_404(db, payroll_id)
        cls.assert_editable(payroll)
        row = await cls._get_task_link_or_404(db, payroll_id, link_id)

        old = Decimal(str(row.commission_amount or 0))
        if quantity is not None:
            if Decimal(str(quantity)) < 0:
                raise BizException("计件数量不能为负数")
            row.quantity = Decimal(str(quantity))
        if unit_price is not None:
            if Decimal(str(unit_price)) < 0:
                raise BizException("计件单价不能为负数")
            row.unit_price = Decimal(str(unit_price))
        if adjust_amount is not None:
            value = Decimal(str(adjust_amount))
            if value != 0 and not (adjust_reason or row.adjust_reason):
                raise BizException("有调整金额时必须填写调整原因，便于向司机解释")
            row.adjust_amount = value
        if adjust_reason is not None:
            row.adjust_reason = adjust_reason.strip() or None
        if remark is not None:
            row.remark = remark

        row.commission_amount = _money(
            Decimal(str(row.quantity or 0)) * Decimal(str(row.unit_price or 0))
            + Decimal(str(row.adjust_amount or 0))
        )
        await db.flush()
        await cls.refresh_totals(db, payroll_id)

        new = Decimal(str(row.commission_amount or 0))
        if new != old:
            payroll.adjust_approved_by = None
            payroll.adjust_approved_at = None
            await FinanceDocEventWriter.write(
                db,
                doc_kind=cls.doc_kind,
                doc_id=payroll_id,
                event_type=FinanceEventType.ADJUST,
                direction=FinanceDirection.PAY,
                occurred_amount=new - old,
                operator_id=operator_id,
                reason=row.adjust_reason,
                payload_snapshot={
                    "linkId": int(row.id),
                    "taskNo": row.task_no,
                    "oldCommission": float(old),
                    "newCommission": float(new),
                },
            )
            await db.flush()
        return row

    # ------------------------------------------------------------------
    # 工资项
    # ------------------------------------------------------------------
    @classmethod
    async def add_item(
        cls,
        db: AsyncSession,
        payroll_id: int,
        *,
        item_type: str,
        amount: Decimal,
        item_name: Optional[str] = None,
        category: Optional[int] = None,
        formula: Optional[str] = None,
        sort_order: int = 0,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> DriverPayrollItem:
        """新增一个工资项。提成汇总项由系统维护，不接受手工新增。"""
        payroll = await cls.get_or_404(db, payroll_id)
        cls.assert_editable(payroll)
        code = (item_type or "").strip()
        if code == COMMISSION_ITEM_TYPE:
            raise BizException(
                "任务提成由任务明细自动汇总，请到任务提成里调整，不要手工添加"
            )
        default = PAYROLL_ITEM_TYPES.get(code)
        if default is None and category is None:
            raise BizException("工资项类型不正确，请从下拉里选择")
        value = Decimal(str(amount or 0)).quantize(_CENT, ROUND_HALF_UP)
        if value <= 0:
            raise BizException("工资项金额要填正数，是加还是减由项目类型决定")

        row = DriverPayrollItem(
            payroll_id=payroll_id,
            item_type=code,
            item_name=(item_name or (default[0] if default else code)),
            category=int(category if category is not None else default[1]),
            amount=value,
            formula=formula,
            sort_order=int(sort_order or 0),
            remark=remark,
        )
        db.add(row)
        await db.flush()
        await cls.refresh_totals(db, payroll_id)
        return row

    @classmethod
    async def update_item(
        cls,
        db: AsyncSession,
        payroll_id: int,
        item_id: int,
        *,
        amount: Optional[Decimal] = None,
        item_name: Optional[str] = None,
        formula: Optional[str] = None,
        sort_order: Optional[int] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> DriverPayrollItem:
        payroll = await cls.get_or_404(db, payroll_id)
        cls.assert_editable(payroll)
        row = await cls._get_item_or_404(db, payroll_id, item_id)
        if row.item_type == COMMISSION_ITEM_TYPE and amount is not None:
            raise BizException(
                "任务提成金额由任务明细汇总得出，请到任务提成里调整"
            )
        if amount is not None:
            value = Decimal(str(amount)).quantize(_CENT, ROUND_HALF_UP)
            if value <= 0:
                raise BizException("工资项金额要填正数")
            row.amount = value
        if item_name is not None:
            row.item_name = item_name
        if formula is not None:
            row.formula = formula
        if sort_order is not None:
            row.sort_order = int(sort_order)
        if remark is not None:
            row.remark = remark
        await db.flush()
        await cls.refresh_totals(db, payroll_id)
        return row

    @classmethod
    async def remove_item(
        cls, db: AsyncSession, payroll_id: int, item_id: int,
    ) -> None:
        payroll = await cls.get_or_404(db, payroll_id)
        cls.assert_editable(payroll)
        row = await cls._get_item_or_404(db, payroll_id, item_id)
        if row.item_type == COMMISSION_ITEM_TYPE:
            raise BizException("任务提成汇总项不能删除，移除任务后会自动消失")
        row.is_deleted = 1
        await db.flush()
        await cls.refresh_totals(db, payroll_id)

    # ------------------------------------------------------------------
    # 合计重算
    # ------------------------------------------------------------------
    @classmethod
    async def refresh_totals(cls, db: AsyncSession, payroll_id: int) -> None:
        """重算五个金额合计，并同步提成汇总项与预付抵扣。

        顺序有讲究：先算任务提成 → 回填 ``commission_total`` 工资项 → 再按工资项分类
        汇总。反过来会把上一轮的提成金额算进去。
        """
        payroll = await cls.get_or_404(db, payroll_id)
        r = await db.execute(
            select(
                func.count(DriverPayrollTaskLink.id),
                func.coalesce(
                    func.sum(DriverPayrollTaskLink.signed_quantity_snapshot), 0
                ),
                func.coalesce(
                    func.sum(DriverPayrollTaskLink.commission_amount), 0
                ),
            ).where(
                DriverPayrollTaskLink.payroll_id == payroll_id,
                DriverPayrollTaskLink.is_deleted == 0,
            )
        )
        task_count, signed_qty, commission = r.one()
        commission = Decimal(str(commission or 0))
        await cls._sync_commission_item(db, payroll_id, commission)

        prepaid = await cls._prepaid_offset_total(
            db, payroll_id, int(payroll.driver_id),
        )
        items = await cls.list_items(db, payroll_id)
        base = Decimal("0")
        deduction = Decimal("0")
        for it in items:
            amount = Decimal(str(it.amount or 0))
            category = int(it.category or 0)
            if it.item_type == COMMISSION_ITEM_TYPE:
                continue
            if category == PayrollItemCategory.ADDITION:
                base += amount
            else:
                deduction += amount

        gross = _money(base + commission)
        net = _money(gross - deduction - prepaid)
        await db.execute(
            update(DriverPayroll)
            .where(DriverPayroll.id == payroll_id)
            .values(
                task_count=int(task_count or 0),
                total_signed_quantity=int(signed_qty or 0),
                total_commission_amount=commission,
                total_base_amount=_money(base),
                total_deduction_amount=_money(deduction),
                total_prepaid_offset_amount=prepaid,
                gross_amount=gross,
                net_amount=net,
                planned_amount=net,
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
        payroll_id: int,
        *,
        operator_id: Optional[int] = None,
        remark: Optional[str] = None,
    ) -> DriverPayroll:
        """主管审批大额提成调整（不改状态，只解开提交门槛）。"""
        payroll = await cls.get_or_404(db, payroll_id)
        total = await cls._adjust_total(db, payroll_id)
        if abs(total) <= ADJUST_APPROVAL_THRESHOLD:
            raise BizException(
                f"本单提成调整未超过 {ADJUST_APPROVAL_THRESHOLD:.0f} 元，"
                "不需要审批，可直接提交"
            )
        payroll.adjust_approved_by = operator_id
        payroll.adjust_approved_at = datetime.now()
        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=payroll_id,
            event_type=FinanceEventType.APPROVE,
            direction=FinanceDirection.PAY,
            occurred_amount=total,
            operator_id=operator_id,
            reason=remark or "大额提成调整审批通过",
            payload_snapshot={"scope": "adjust", "adjustTotal": float(total)},
        )
        await db.flush()
        return payroll

    @classmethod
    async def submit(
        cls, db: AsyncSession, doc_id: int, operator_id: Optional[int] = None,
    ) -> DriverPayroll:
        """草稿 → 待审批。

        实发为负是允许的（本月扣款大于应发，下月结转），只提示不拦——真正该拦的是
        「一张什么都没有的空单」和「薪资模型与内容不匹配」。
        """
        payroll = await cls.get_or_404(db, doc_id)
        items = await cls.list_items(db, doc_id)
        has_task = int(payroll.task_count or 0) > 0
        has_item = any(
            x.item_type != COMMISSION_ITEM_TYPE for x in items
        )
        if not has_task and not has_item:
            raise BizException("工资单还是空的，请先添加任务提成或工资项")

        model = int(payroll.payroll_model or 0)
        codes = {x.item_type for x in items}
        if model in (PayrollModel.FIXED, PayrollModel.MIXED) and (
            "base_salary" not in codes
        ):
            raise BizException(
                "月薪与底薪加提成模式必须有「底薪」工资项，请先补上"
            )
        if model in (PayrollModel.PIECE, PayrollModel.MIXED) and not has_task:
            raise BizException(
                "计件与底薪加提成模式必须有至少一条任务提成，请先添加任务"
            )
        await cls._assert_adjust_approved(db, payroll)

        await cls.change_status(
            db, payroll, FIN_PENDING_REVIEW,
            event_type=FinanceEventType.SUBMIT,
            operator_id=operator_id,
            occurred_amount=payroll.net_amount,
            payload_snapshot={
                "grossAmount": float(payroll.gross_amount or 0),
                "netAmount": float(payroll.net_amount or 0),
            },
        )
        return payroll

    @classmethod
    async def pay(
        cls,
        db: AsyncSession,
        payroll_id: int,
        *,
        actual_amount: Optional[Decimal] = None,
        paid_at: Optional[datetime] = None,
        pay_method: Optional[int] = None,
        account_id: Optional[int] = None,
        pay_voucher_url: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> DriverPayroll:
        """已审批 → 已发放，并把任务标记为已发薪。

        实发为 0 或负数的单也允许「发放」：它是账面闭环动作（本月不打钱，扣款结转），
        此时不校验金额与凭证，与承运商侧的纯抵账单同理。
        """
        payroll = await cls.get_or_404(db, payroll_id)
        if int(payroll.status) != FIN_REVIEWED:
            raise BizException(
                f"只有已审批的工资单可以发放（当前：{cls.status_text(payroll)}）"
            )
        if account_id:
            await cls.update_account(
                db, payroll_id, account_id=int(account_id),
                operator_id=operator_id,
            )
        net = Decimal(str(payroll.net_amount or 0))
        when = paid_at or datetime.now()
        amount = Decimal(str(actual_amount if actual_amount is not None else net))

        if net > 0:
            if not payroll.account_id:
                raise BizException("请先选择发薪账户，再登记发放")
            await cls.get_account_or_404(
                db, int(payroll.driver_id), int(payroll.account_id),
            )
            FinanceStateMachine.assert_payable(
                actual_amount=amount, paid_at=when, pay_method=pay_method,
            )
            if abs(amount - net) > AMOUNT_TOLERANCE:
                raise BizException(
                    f"发放金额需与实发合计 {net:.2f} 元一致；"
                    "确需变动请先调整工资项，保留痕迹"
                )

        payroll.actual_amount = amount
        payroll.paid_at = when
        payroll.pay_method = pay_method
        payroll.paid_amount_total = amount
        if pay_voucher_url:
            payroll.pay_voucher_url = pay_voucher_url

        await cls.change_status(
            db, payroll, FIN_PAID,
            event_type=FinanceEventType.PAY,
            operator_id=operator_id,
            occurred_amount=amount,
            payload_snapshot={
                "accountId": payroll.account_id,
                "accountType": payroll.account_type,
                "netAmount": float(net),
            },
        )
        task_ids = await cls._active_task_ids(db, payroll_id)
        if task_ids:
            await LockOrchestrator.mark_tasks_payroll_settled(
                db, list(task_ids), settled=True,
            )
        return payroll

    @classmethod
    async def cancel_payment(
        cls,
        db: AsyncSession,
        payroll_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> DriverPayroll:
        """撤销发放（3→2，高权限）：清空发放字段并撤回任务发薪标记。"""
        payroll = await cls.get_or_404(db, payroll_id)
        if int(payroll.status) != FIN_PAID:
            raise BizException(
                f"只有已发放的工资单可以撤销发放"
                f"（当前：{cls.status_text(payroll)}）"
            )
        if payroll.batch_id:
            raise BizException(
                "本单已进入打款批次，请先在出纳台把它从批次中移出再撤销发放"
            )
        text = cls.assert_reason(reason, action="撤销发放")
        amount = payroll.actual_amount

        await cls.change_status(
            db, payroll, FIN_REVIEWED,
            event_type=FinanceEventType.CANCEL_PAY,
            operator_id=operator_id,
            reason=text,
            occurred_amount=(-amount if amount is not None else None),
            skip_lock_check=True,
        )
        payroll.actual_amount = None
        payroll.paid_at = None
        payroll.pay_method = None
        payroll.pay_voucher_url = None
        payroll.paid_amount_total = Decimal("0")
        await db.flush()

        task_ids = await cls._active_task_ids(db, payroll_id)
        if task_ids:
            await LockOrchestrator.mark_tasks_payroll_settled(
                db, list(task_ids), settled=False,
            )
        return payroll

    @classmethod
    async def cancel_payroll(
        cls,
        db: AsyncSession,
        payroll_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> DriverPayroll:
        """撤销工资单：解除任务软锁与同期唯一键。"""
        payroll = await cls.get_or_404(db, payroll_id)
        if int(payroll.status) == FIN_CANCELLED:
            raise BizException("该工资单已撤销，无需重复操作")
        if int(payroll.status) == FIN_PAID:
            raise BizException("已发放的工资单请先撤销发放，再撤销单据")
        text = cls.assert_reason(reason)
        task_ids = await cls._active_task_ids(db, payroll_id)

        await cls.change_status(
            db, payroll, FIN_CANCELLED,
            event_type=FinanceEventType.CANCEL,
            operator_id=operator_id,
            reason=text,
            skip_lock_check=True,
        )
        payroll.dedup_key = None
        await db.flush()
        if task_ids:
            await LockOrchestrator.mark_tasks_payroll_bound(
                db, list(task_ids), bound=False,
            )
        return payroll

    @classmethod
    async def update_account(
        cls,
        db: AsyncSession,
        payroll_id: int,
        *,
        account_id: int,
        operator_id: Optional[int] = None,
    ) -> DriverPayroll:
        """改发薪账户（草稿到已审批都允许，发放前换卡是常态）。"""
        payroll = await cls.get_or_404(db, payroll_id)
        if int(payroll.status) not in (FIN_DRAFT, FIN_PENDING_REVIEW, FIN_REVIEWED):
            raise BizException(
                f"工资单当前是「{cls.status_text(payroll)}」，不能再改发薪账户"
            )
        account = await cls.get_account_or_404(
            db, int(payroll.driver_id), int(account_id),
        )
        payroll.account_id = int(account.id)
        payroll.account_type = int(account.account_type or 0)
        payroll.account_name_snapshot = account.account_name
        payroll.account_no_masked = _mask(account.account_no)
        await db.flush()
        return payroll

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
        driver_id: Optional[int] = None,
        enterprise_id: Optional[int] = None,
        status: Optional[int] = None,
        payroll_model: Optional[int] = None,
        period_start: Optional[object] = None,
        period_end: Optional[object] = None,
    ) -> Tuple[List[DriverPayroll], int]:
        stmt = select(DriverPayroll).where(DriverPayroll.is_deleted == 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                DriverPayroll.doc_no.like(kw)
                | DriverPayroll.driver_name.like(kw)
                | DriverPayroll.driver_phone.like(kw)
            )
        if driver_id:
            stmt = stmt.where(DriverPayroll.driver_id == driver_id)
        if enterprise_id:
            stmt = stmt.where(DriverPayroll.enterprise_id == enterprise_id)
        if status is not None:
            stmt = stmt.where(DriverPayroll.status == status)
        if payroll_model is not None:
            stmt = stmt.where(DriverPayroll.payroll_model == payroll_model)
        if period_start is not None:
            stmt = stmt.where(DriverPayroll.period_end >= period_start)
        if period_end is not None:
            stmt = stmt.where(DriverPayroll.period_start <= period_end)

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(DriverPayroll.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_task_links(
        cls, db: AsyncSession, payroll_id: int,
    ) -> List[DriverPayrollTaskLink]:
        r = await db.execute(
            select(DriverPayrollTaskLink)
            .where(
                DriverPayrollTaskLink.payroll_id == payroll_id,
                DriverPayrollTaskLink.is_deleted == 0,
            )
            .order_by(
                DriverPayrollTaskLink.signed_at.asc(),
                DriverPayrollTaskLink.id.asc(),
            )
        )
        return list(r.scalars().all())

    @classmethod
    async def list_items(
        cls, db: AsyncSession, payroll_id: int,
    ) -> List[DriverPayrollItem]:
        r = await db.execute(
            select(DriverPayrollItem)
            .where(
                DriverPayrollItem.payroll_id == payroll_id,
                DriverPayrollItem.is_deleted == 0,
            )
            .order_by(
                DriverPayrollItem.category.asc(),
                DriverPayrollItem.sort_order.asc(),
                DriverPayrollItem.id.asc(),
            )
        )
        return list(r.scalars().all())

    @classmethod
    async def payslip(cls, db: AsyncSession, payroll_id: int) -> dict:
        """工资条数据（文档 04 §7.4 的结构，前端直接渲染）。"""
        payroll = await cls.get_or_404(db, payroll_id)
        items = await cls.list_items(db, payroll_id)
        grouped: Dict[int, List[dict]] = {1: [], 2: [], 3: []}
        for it in items:
            grouped.setdefault(int(it.category or 1), []).append({
                "itemType": it.item_type,
                "itemName": it.item_name,
                "amount": _f(it.amount),
                "formula": it.formula,
            })
        prepaid = Decimal(str(payroll.total_prepaid_offset_amount or 0))
        if prepaid > 0:
            grouped[PayrollItemCategory.OFFSET].append({
                "itemType": "task_prepaid_offset",
                "itemName": "任务级预付抵扣",
                "amount": _f(prepaid),
                "formula": "本单任务已发放的预付与补款合计",
            })
        return {
            "docNo": payroll.doc_no,
            "driverName": payroll.driver_name,
            "periodStart": payroll.period_start,
            "periodEnd": payroll.period_end,
            "taskCount": int(payroll.task_count or 0),
            "totalSignedQuantity": int(payroll.total_signed_quantity or 0),
            "additions": grouped.get(PayrollItemCategory.ADDITION, []),
            "deductions": grouped.get(PayrollItemCategory.DEDUCTION, []),
            "offsets": grouped.get(PayrollItemCategory.OFFSET, []),
            "grossAmount": _f(payroll.gross_amount),
            "netAmount": _f(payroll.net_amount),
            "accountType": payroll.account_type,
            "accountNoMasked": payroll.account_no_masked,
            "paidAt": payroll.paid_at,
        }

    @classmethod
    def status_text(cls, payroll: Any) -> str:
        return status_label(int(payroll.status or 0), cls.doc_kind)

    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        flags = super().action_flags(doc)
        status = int(doc.status)
        flags.update({
            "canEditLines": status == FIN_DRAFT,
            "canChangeAccount": status in (
                FIN_DRAFT, FIN_PENDING_REVIEW, FIN_REVIEWED,
            ),
            "canPay": status == FIN_REVIEWED,
            "canCancelPay": status == FIN_PAID and not doc.batch_id,
            "canPayslip": status in (FIN_REVIEWED, FIN_PAID),
            "netIsNegative": Decimal(str(doc.net_amount or 0)) < 0,
        })
        return flags

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @staticmethod
    async def get_account_or_404(
        db: AsyncSession, driver_id: int, account_id: int,
    ) -> DriverAccount:
        r = await db.execute(
            select(DriverAccount).where(
                DriverAccount.id == account_id,
                DriverAccount.is_deleted == 0,
            )
        )
        account = r.scalar_one_or_none()
        if account is None:
            raise BizException("发薪账户不存在，请重新选择")
        if int(account.driver_id or 0) != int(driver_id):
            raise BizException("该账户不属于本司机，请重新选择，以免发错人")
        if int(account.status or 0) != 1:
            raise BizException(
                f"账户「{account.account_name}」已停用，请换一个可用账户"
            )
        return account

    @staticmethod
    async def _default_account(
        db: AsyncSession, driver_id: int,
    ) -> Optional[DriverAccount]:
        """默认发薪账户：优先银行卡（account_type=1）。"""
        r = await db.execute(
            select(DriverAccount)
            .where(
                DriverAccount.driver_id == driver_id,
                DriverAccount.is_deleted == 0,
                DriverAccount.status == 1,
            )
            .order_by(DriverAccount.account_type.asc(), DriverAccount.id.asc())
            .limit(1)
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _get_driver_or_404(db: AsyncSession, driver_id: int) -> Driver:
        r = await db.execute(
            select(Driver).where(
                Driver.id == driver_id, Driver.is_deleted == 0,
            )
        )
        driver = r.scalar_one_or_none()
        if driver is None:
            raise BizException("司机不存在或已删除，请重新选择")
        if int(driver.status or 0) == 2:
            raise BizException(
                f"司机 {driver.name} 已离职；如需补发工资请先由人事恢复在职状态"
            )
        return driver

    @staticmethod
    async def _capacity_ids_of(db: AsyncSession, driver_id: int) -> List[int]:
        r = await db.execute(
            select(Capacity.id).where(
                Capacity.driver_id == driver_id,
                Capacity.is_deleted == 0,
            )
        )
        return [int(x) for x in r.scalars().all()]

    @classmethod
    async def _assert_period_unique(
        cls,
        db: AsyncSession,
        driver_id: int,
        period_start: datetime,
        period_end: datetime,
    ) -> None:
        r = await db.execute(
            select(DriverPayroll.doc_no).where(
                DriverPayroll.driver_id == driver_id,
                DriverPayroll.is_deleted == 0,
                DriverPayroll.status != FIN_CANCELLED,
                DriverPayroll.period_start == period_start,
                DriverPayroll.period_end == period_end,
            ).limit(1)
        )
        doc_no = r.scalar_one_or_none()
        if doc_no:
            raise BizException(
                f"该司机在这个周期已有工资单 {doc_no}，"
                "请直接在那张单上补充，或换一个发放周期"
            )

    @staticmethod
    def _assert_payable(task: Task, capacity_ids: Iterable[int]) -> None:
        if int(task.carrier_type or 0) != CarrierType.SELF:
            raise BizException(
                f"任务 {task.task_no} 不是自有车任务，不能计入司机工资；"
                "承运商任务请走承运商对账"
            )
        if int(task.status or 0) != TASK_SETTLEABLE_STATUS:
            raise BizException(
                f"任务 {task.task_no} 还没交车，请等交车完成后再计入工资"
            )
        if task.capacity_id is not None and int(task.capacity_id) not in set(
            int(x) for x in capacity_ids
        ):
            raise BizException(
                f"任务 {task.task_no} 不是这位司机跑的，请核对后重新选择"
            )
        if int(getattr(task, "payroll_settled", 0) or 0) == 1:
            raise BizException(
                f"任务 {task.task_no} 的工资已发放过，不能重复计入"
            )

    @staticmethod
    def _derive_quantity(billing_base: int, task: Task) -> Decimal:
        """计件数量：按台取已交车台数，按趟恒为 1，按吨暂无吨位事实取台数兜底。"""
        if int(billing_base) == BillingBase.BY_TRIP:
            return Decimal("1")
        return Decimal(str(int(task.total_quantity or 0)))

    @classmethod
    async def _sync_commission_item(
        cls, db: AsyncSession, payroll_id: int, commission: Decimal,
    ) -> None:
        """维护 ``commission_total`` 工资项：有提成则建/更新，无提成则软删。"""
        r = await db.execute(
            select(DriverPayrollItem).where(
                DriverPayrollItem.payroll_id == payroll_id,
                DriverPayrollItem.item_type == COMMISSION_ITEM_TYPE,
                DriverPayrollItem.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if commission == 0:
            if row is not None:
                row.is_deleted = 1
                await db.flush()
            return
        name, category = PAYROLL_ITEM_TYPES[COMMISSION_ITEM_TYPE]
        if row is None:
            db.add(DriverPayrollItem(
                payroll_id=payroll_id,
                item_type=COMMISSION_ITEM_TYPE,
                item_name=name,
                category=category,
                amount=commission,
                formula="按任务提成明细汇总",
                sort_order=50,
            ))
        else:
            row.amount = commission
        await db.flush()

    @classmethod
    async def _prepaid_offset_total(
        cls, db: AsyncSession, payroll_id: int, driver_id: int,
    ) -> Decimal:
        """本单任务里已付给该司机的预付 / 补款合计（实发的扣减项）。"""
        task_ids = await cls._active_task_ids(db, payroll_id)
        if not task_ids:
            return Decimal("0")
        r = await db.execute(
            select(func.coalesce(func.sum(TaskFinanceDoc.actual_amount), 0))
            .where(
                TaskFinanceDoc.task_id.in_(list(task_ids)),
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.payee_type == 1,
                TaskFinanceDoc.payee_id == driver_id,
                TaskFinanceDoc.doc_type.in_(
                    (DocType.PREPAY, DocType.SUPPLEMENT)
                ),
                TaskFinanceDoc.status == FIN_PAID,
            )
        )
        return _money(Decimal(str(r.scalar() or 0)))

    @staticmethod
    async def _task_driver_prepaid(
        db: AsyncSession, task_id: int, driver_id: int,
    ) -> Decimal:
        r = await db.execute(
            select(func.coalesce(func.sum(TaskFinanceDoc.actual_amount), 0))
            .where(
                TaskFinanceDoc.task_id == task_id,
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.payee_type == 1,
                TaskFinanceDoc.payee_id == driver_id,
                TaskFinanceDoc.doc_type.in_(
                    (DocType.PREPAY, DocType.SUPPLEMENT)
                ),
                TaskFinanceDoc.status == FIN_PAID,
            )
        )
        return Decimal(str(r.scalar() or 0))

    @classmethod
    async def _adjust_total(cls, db: AsyncSession, payroll_id: int) -> Decimal:
        r = await db.execute(
            select(
                func.coalesce(func.sum(DriverPayrollTaskLink.adjust_amount), 0)
            ).where(
                DriverPayrollTaskLink.payroll_id == payroll_id,
                DriverPayrollTaskLink.is_deleted == 0,
            )
        )
        return Decimal(str(r.scalar() or 0))

    @classmethod
    async def _assert_adjust_approved(
        cls, db: AsyncSession, payroll: DriverPayroll,
    ) -> None:
        total = abs(await cls._adjust_total(db, int(payroll.id)))
        if total <= ADJUST_APPROVAL_THRESHOLD:
            return
        if payroll.adjust_approved_at is None:
            raise BizException(
                f"本单提成调整合计 {total:.2f} 元，超过 "
                f"{ADJUST_APPROVAL_THRESHOLD:.0f} 元需主管审批后才能提交"
            )

    @classmethod
    async def _active_task_ids(
        cls, db: AsyncSession, payroll_id: int,
    ) -> List[int]:
        r = await db.execute(
            select(DriverPayrollTaskLink.task_id).where(
                DriverPayrollTaskLink.payroll_id == payroll_id,
                DriverPayrollTaskLink.is_deleted == 0,
            )
        )
        return [int(x) for x in r.scalars().all()]

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
        tasks = list(r.scalars().all())
        found = {int(t.id) for t in tasks}
        missing = [i for i in task_ids if i not in found]
        if missing:
            raise BizException("部分任务已删除，请刷新后重新选择")
        return tasks

    @staticmethod
    async def _get_task_link_or_404(
        db: AsyncSession, payroll_id: int, link_id: int,
    ) -> DriverPayrollTaskLink:
        r = await db.execute(
            select(DriverPayrollTaskLink).where(
                DriverPayrollTaskLink.id == link_id,
                DriverPayrollTaskLink.payroll_id == payroll_id,
                DriverPayrollTaskLink.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("这条任务提成不存在或已移除，请刷新后重试")
        return row

    @staticmethod
    async def _get_item_or_404(
        db: AsyncSession, payroll_id: int, item_id: int,
    ) -> DriverPayrollItem:
        r = await db.execute(
            select(DriverPayrollItem).where(
                DriverPayrollItem.id == item_id,
                DriverPayrollItem.payroll_id == payroll_id,
                DriverPayrollItem.is_deleted == 0,
            )
        )
        row = r.scalar_one_or_none()
        if row is None:
            raise BizException("这个工资项不存在或已删除，请刷新后重试")
        return row


def _money(v: Decimal) -> Decimal:
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)


def _unique_ints(values: Iterable[Any]) -> List[int]:
    out: List[int] = []
    seen = set()
    for v in values or []:
        i = int(v)
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def _mask(account_no: Optional[str]) -> Optional[str]:
    if not account_no:
        return None
    text = str(account_no).strip()
    return text if len(text) <= 4 else f"****{text[-4:]}"


def _f(v: Any) -> Optional[float]:
    return float(v) if v is not None else None
