"""任务单 → 承运商对账 / 司机工资 联动闸口

业务模块（06 任务单 / 计费引擎 / 任务级费用单）与应付侧对账之间的中转层，
职责与 ``waybill_to_finance`` 对称：候选池、业务事实口径、闸口（拦截与置脏）。

应付侧比应收侧多一条硬约束：**同一个任务的钱只能走一条路**。

| 承运类型 | 结算路径 |
|---------|---------|
| 1 自有车 | 司机工资单（``biz_driver_payroll``） |
| 2 承运商 | 承运商对账 → 结算单，或任务级最终结算单（二者互斥） |
| 3 社会运力 | 任务级预付 + 尾款（不进对账） |

互斥判定统一由 ``ConsistencyChecker.assert_task_settle_exclusive`` 收口，本模块
只负责在候选池里提前把不该出现的任务过滤掉，避免用户挂上去才被拦。
"""

from decimal import Decimal
from typing import List, Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.constants import CarrierType
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
from app.modules.client.services.finance.base.constants import DocType
from app.modules.client.services.finance.base.finance_state_machine import (
    FIN_PAID,
)
from app.modules.client.services.finance.recon.consistency_checker import (
    ConsistencyChecker,
)
from app.modules.client.services.finance.recon.diff_constants import ReconKind

# 任务可纳入应付对账 / 工资单的状态：5 已交车
TASK_SETTLEABLE_STATUS = 5

_ACTION_LABELS = {
    "update": "修改",
    "delete": "删除",
    "recalc": "重新核算",
}


class TaskToFinance:
    """任务单侧联动闸口"""

    # ------------------------------------------------------------------
    # 候选池
    # ------------------------------------------------------------------
    @staticmethod
    async def list_carrier_recon_candidates(
        db: AsyncSession,
        *,
        carrier_id: int,
        period_start: Optional[object] = None,
        period_end: Optional[object] = None,
        keyword: Optional[str] = None,
        exclude_recon_id: Optional[int] = None,
        limit: int = 500,
    ) -> List[Task]:
        """返回可加入承运商对账单的任务候选（文档 03 §3.4）。

        过滤：指定承运商、承运类型为承运商、已交车、未被结算锁定、未挂在任何
        非撤销对账单、且不存在已支付的任务级最终结算单（互斥）。
        """
        settled_final = (
            select(TaskFinanceDoc.task_id).where(
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.doc_type == DocType.SETTLE,
                TaskFinanceDoc.is_final == 1,
                TaskFinanceDoc.status == FIN_PAID,
            )
        )
        stmt = select(Task).where(
            Task.carrier_id == carrier_id,
            Task.carrier_type == CarrierType.CARRIER,
            Task.is_deleted == 0,
            Task.status == TASK_SETTLEABLE_STATUS,
            Task.is_locked == 0,
            Task.id.notin_(settled_final),
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(
                Task.task_no.like(kw),
                Task.plate_number.like(kw),
            ))
        if period_start is not None:
            stmt = stmt.where(Task.actual_arrive_time >= period_start)
        if period_end is not None:
            stmt = stmt.where(Task.actual_arrive_time <= period_end)

        bound = ConsistencyChecker.bound_biz_ids(
            ReconKind.CARRIER, exclude_recon_id=exclude_recon_id,
        )
        if bound is not None:
            stmt = stmt.where(Task.id.notin_(bound))

        r = await db.execute(
            stmt.order_by(Task.id.asc()).limit(max(1, int(limit)))
        )
        return list(r.scalars().all())

    @staticmethod
    async def list_payroll_candidates(
        db: AsyncSession,
        *,
        capacity_id: Optional[int] = None,
        period_start: Optional[object] = None,
        period_end: Optional[object] = None,
        limit: int = 500,
    ) -> List[Task]:
        """返回可纳入司机工资单的任务候选（文档 04）。

        过滤：自有车、已交车、未挂工资单、未发放。自有车不进承运商对账，
        因此不需要对账挂接排除。

        按 ``capacity_id``（自有运力）而非司机 id 过滤：任务上冷冻的是运力，
        司机是运力的当期配置，按运力筛才是任务侧的事实口径。
        """
        stmt = select(Task).where(
            Task.carrier_type == CarrierType.SELF,
            Task.is_deleted == 0,
            Task.status == TASK_SETTLEABLE_STATUS,
            Task.is_payroll_bound == 0,
            Task.payroll_settled == 0,
        )
        if capacity_id is not None:
            stmt = stmt.where(Task.capacity_id == capacity_id)
        if period_start is not None:
            stmt = stmt.where(Task.actual_arrive_time >= period_start)
        if period_end is not None:
            stmt = stmt.where(Task.actual_arrive_time <= period_end)
        r = await db.execute(
            stmt.order_by(Task.id.asc()).limit(max(1, int(limit)))
        )
        return list(r.scalars().all())

    # ------------------------------------------------------------------
    # 业务事实聚合
    # ------------------------------------------------------------------
    @staticmethod
    async def paid_prepay_amount(db: AsyncSession, task_id: int) -> Decimal:
        """该任务已支付的预付 + 补款合计（承运商对账行的扣减额口径）。

        对账行写 ``prepaid_offset_amount`` 快照与核对器比对现值都用本方法，
        两处口径必须一致，否则会出现「明明没变却总报扣减不符」。
        """
        r = await db.execute(
            select(func.coalesce(func.sum(TaskFinanceDoc.actual_amount), 0))
            .where(
                TaskFinanceDoc.task_id == task_id,
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.doc_type.in_(
                    (DocType.PREPAY, DocType.SUPPLEMENT)
                ),
                TaskFinanceDoc.status == FIN_PAID,
            )
        )
        return Decimal(str(r.scalar() or 0))

    # ------------------------------------------------------------------
    # 闸口：编辑与删除拦截
    # ------------------------------------------------------------------
    @staticmethod
    async def assert_unbound(
        db: AsyncSession, task_id: int, *, action: str = "update",
    ) -> None:
        """任务已进入应付流程时拒绝业务侧改成本字段。"""
        label = _ACTION_LABELS.get(action, "修改")
        r = await db.execute(
            select(Task.is_locked, Task.is_payroll_bound, Task.task_no).where(
                Task.id == task_id, Task.is_deleted == 0,
            )
        )
        row = r.one_or_none()
        if row is None:
            raise BizException("任务单不存在")
        is_locked, payroll_bound, task_no = row
        if int(is_locked or 0) == 1:
            raise BizException(
                f"任务 {task_no} 的费用已结算并锁定，不能{label}；"
                "如需变更请先由财务撤销结算"
            )
        if int(payroll_bound or 0) == 1:
            raise BizException(
                f"任务 {task_no} 已纳入司机工资单，不能{label}；"
                "如需变更请先从工资单中移除"
            )
        if await ConsistencyChecker.is_biz_doc_bound(
            db, ReconKind.CARRIER, task_id,
        ):
            raise BizException(
                f"任务 {task_no} 已加入承运商对账单，不能{label}；"
                "如需变更请先从对账单中移除该任务"
            )

    # ------------------------------------------------------------------
    # 闸口：变更置脏（文档 09 §3.3）
    # ------------------------------------------------------------------
    @staticmethod
    async def on_carrier_cost_changed(
        db: AsyncSession,
        task_id: int,
        old_amount: Optional[Decimal],
        new_amount: Optional[Decimal],
    ) -> int:
        """承运成本变化（含计费引擎重算回填）→ 置脏承运商对账行。"""
        if _same_amount(old_amount, new_amount):
            return 0
        return await ConsistencyChecker.mark_dirty_by_task(
            db, task_id,
            f"承运成本由 {_fmt_amount(old_amount)} 变为 {_fmt_amount(new_amount)}",
        )

    @staticmethod
    async def on_signed_quantity_changed(
        db: AsyncSession, task_id: int, old_qty: object, new_qty: object,
    ) -> int:
        """交车台数变化 → 置脏承运商对账行。"""
        if int(old_qty or 0) == int(new_qty or 0):
            return 0
        return await ConsistencyChecker.mark_dirty_by_task(
            db, task_id,
            f"签收台数由 {int(old_qty or 0)} 变为 {int(new_qty or 0)}",
        )

    @staticmethod
    async def on_mileage_changed(
        db: AsyncSession, task_id: int, old_mileage: object, new_mileage: object,
    ) -> int:
        """调令里程变化 → 置脏按公里计费的对账行。"""
        if _same_amount(
            _to_decimal(old_mileage), _to_decimal(new_mileage)
        ):
            return 0
        return await ConsistencyChecker.mark_dirty_by_task(
            db, task_id,
            f"调令里程由 {old_mileage or '未填'} 变为 {new_mileage or '未填'}",
        )

    @staticmethod
    async def on_status_reverted(
        db: AsyncSession, task_id: int, old_status: int, new_status: int,
    ) -> int:
        """任务状态逆向（5→4 等）→ 置脏承运商对账行。"""
        if int(new_status) >= int(old_status):
            return 0
        return await ConsistencyChecker.mark_dirty_by_task(
            db, task_id, "业务单据已回退至未交车，对账数据需重新核对",
        )

    @staticmethod
    async def on_items_changed(
        db: AsyncSession, task_id: int, detail: Optional[str] = None,
    ) -> int:
        """任务挂接明细增删 → 置脏承运商对账行。"""
        return await ConsistencyChecker.mark_dirty_by_task(
            db, task_id, detail or "任务挂接已变更，对账台数可能不准",
        )

    @staticmethod
    async def on_prepay_changed(
        db: AsyncSession,
        task_id: int,
        old_amount: Optional[Decimal],
        new_amount: Optional[Decimal],
    ) -> int:
        """任务级预付 / 补款支付或撤销 → 置脏承运商对账行的扣减额。"""
        if _same_amount(old_amount, new_amount):
            return 0
        return await ConsistencyChecker.mark_dirty_by_task(
            db, task_id,
            f"已支付预付补款金额由 {_fmt_amount(old_amount)} "
            f"变为 {_fmt_amount(new_amount)}",
        )

    @staticmethod
    async def mark_dirty_by_waybills(
        db: AsyncSession, waybill_ids: Sequence[int], reason: str,
    ) -> int:
        """运单侧变更波及承运商对账：先找到承载这些运单的任务，再置脏。"""
        from app.modules.client.models.task.task_waybill_item import (
            TaskWaybillItem,
        )

        ids = [int(x) for x in waybill_ids if x]
        if not ids:
            return 0
        r = await db.execute(
            select(TaskWaybillItem.task_id)
            .where(
                TaskWaybillItem.waybill_id.in_(ids),
                TaskWaybillItem.is_deleted == 0,
            )
            .distinct()
        )
        affected = 0
        for task_id in r.scalars().all():
            affected += await ConsistencyChecker.mark_dirty_by_task(
                db, int(task_id), reason,
            )
        return affected


def _to_decimal(v: object) -> Optional[Decimal]:
    if v is None:
        return None
    try:
        return Decimal(str(v))
    except (TypeError, ValueError, ArithmeticError):
        return None


def _fmt_amount(v: Optional[Decimal]) -> str:
    if v is None:
        return "未填"
    return f"{Decimal(str(v)):.2f}"


def _same_amount(a: Optional[Decimal], b: Optional[Decimal]) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return Decimal(str(a)) == Decimal(str(b))
