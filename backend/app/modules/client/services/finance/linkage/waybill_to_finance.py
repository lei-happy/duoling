"""运单 → 客户应收 联动闸口

业务模块（06 运单 / 计费引擎）与客户对账之间的唯一中转层：业务侧只调用本模块，
不直接 import 财务内部实现，财务侧改结构不牵动业务代码。

本模块提供三类能力：

1. **候选池**：哪些运单可以加入客户对账单（``list_candidates``）；
2. **业务事实**：签收台数与交车时间的聚合口径（``signed_quantity_map``），
   对账行写快照与核对器比对现值都走同一份口径，避免两处算法不一致；
3. **闸口**：编辑/删除拦截（``assert_unbound``）与变更置脏（``on_*_changed``）。

置脏原因文案在此统一生成（「运费金额由 X 变为 Y」），不由各调用点自行拼装——
文案是给对账岗看的，散落编写会出现同一类变更三种说法。

> 「运单完成即进入候选池」是**查询派生**的，不需要业务侧回调写标记：
> 候选池按 ``status`` / ``is_locked`` / 是否已挂接实时过滤，多一个软标记只会
> 多一处可能与事实不同步的状态。
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.services.finance.recon.consistency_checker import (
    ConsistencyChecker,
)
from app.modules.client.services.finance.recon.diff_constants import ReconKind

# 运单可纳入客户对账的状态：5 已交车（含之后的 6 已回单）
WAYBILL_RECONCILABLE_STATUSES = (5, 6)
# 挂接明细「已交车」状态（``TaskWaybillItem.status``）
ITEM_SIGNED_STATUS = 3

# 编辑拦截的动作文案（错误提示要说清是哪一步被拦）
_ACTION_LABELS = {
    "update": "修改",
    "delete": "删除",
    "recalc": "重新计费",
}


class WaybillToFinance:
    """运单侧联动闸口"""

    # ------------------------------------------------------------------
    # 业务事实聚合
    # ------------------------------------------------------------------
    @staticmethod
    async def signed_quantity_map(
        db: AsyncSession, waybill_ids: Sequence[int],
    ) -> Dict[int, int]:
        """批量返回运单的已交车台数（一次查询，避免逐行 N+1）。

        口径：该运单在各任务挂接明细中 ``status=3 已交车`` 的 ``quantity`` 合计。
        对账行写 ``signed_quantity_snapshot`` 与核对器比对现值都用本方法。
        """
        ids = [int(x) for x in waybill_ids if x]
        if not ids:
            return {}
        r = await db.execute(
            select(
                TaskWaybillItem.waybill_id,
                func.coalesce(func.sum(TaskWaybillItem.quantity), 0),
            )
            .where(
                TaskWaybillItem.waybill_id.in_(ids),
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.status == ITEM_SIGNED_STATUS,
            )
            .group_by(TaskWaybillItem.waybill_id)
        )
        got = {int(wid): int(qty or 0) for wid, qty in r.all()}
        return {i: got.get(i, 0) for i in ids}

    @staticmethod
    async def signed_at_map(
        db: AsyncSession, waybill_ids: Sequence[int],
    ) -> Dict[int, Optional[datetime]]:
        """批量返回运单的交车时间（取挂接明细中最晚的 ``signed_at``）。

        对账周期按交车时间过滤，用最晚一台的时间：只要还有车没交完，这张运单
        就不该落进本期对账。
        """
        ids = [int(x) for x in waybill_ids if x]
        if not ids:
            return {}
        r = await db.execute(
            select(
                TaskWaybillItem.waybill_id,
                func.max(TaskWaybillItem.signed_at),
            )
            .where(
                TaskWaybillItem.waybill_id.in_(ids),
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.status == ITEM_SIGNED_STATUS,
            )
            .group_by(TaskWaybillItem.waybill_id)
        )
        got = {int(wid): at for wid, at in r.all()}
        return {i: got.get(i) for i in ids}

    # ------------------------------------------------------------------
    # 候选池
    # ------------------------------------------------------------------
    @staticmethod
    async def list_candidates(
        db: AsyncSession,
        *,
        customer_id: int,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        keyword: Optional[str] = None,
        exclude_recon_id: Optional[int] = None,
        limit: int = 500,
    ) -> List[Waybill]:
        """返回可加入客户对账单的运单候选（文档 02 §3.4）。

        过滤条件：指定客户、已交车、未被结算锁定、未挂在任何非撤销对账单。
        ``period_start/end`` 按交车时间过滤（以最晚一台为准）。

        ``exclude_recon_id`` 用于「给某张已存在的对账单补挂运单」的场景：
        本单自己已挂的行不算冲突。
        """
        stmt = select(Waybill).where(
            Waybill.customer_id == customer_id,
            Waybill.is_deleted == 0,
            Waybill.status.in_(WAYBILL_RECONCILABLE_STATUSES),
            Waybill.is_locked == 0,
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(
                Waybill.waybill_no.like(kw),
                Waybill.dealer_name.like(kw),
            ))

        bound = ConsistencyChecker.bound_biz_ids(
            ReconKind.CUSTOMER, exclude_recon_id=exclude_recon_id,
        )
        if bound is not None:
            stmt = stmt.where(Waybill.id.notin_(bound))

        if period_start is not None or period_end is not None:
            signed = (
                select(
                    TaskWaybillItem.waybill_id.label("wid"),
                    func.max(TaskWaybillItem.signed_at).label("signed_at"),
                )
                .where(
                    TaskWaybillItem.is_deleted == 0,
                    TaskWaybillItem.status == ITEM_SIGNED_STATUS,
                )
                .group_by(TaskWaybillItem.waybill_id)
                .subquery()
            )
            conds = [signed.c.signed_at.isnot(None)]
            if period_start is not None:
                conds.append(signed.c.signed_at >= period_start)
            if period_end is not None:
                conds.append(signed.c.signed_at <= period_end)
            stmt = stmt.join(signed, signed.c.wid == Waybill.id).where(and_(*conds))

        r = await db.execute(
            stmt.order_by(Waybill.id.asc()).limit(max(1, int(limit)))
        )
        return list(r.scalars().all())

    # ------------------------------------------------------------------
    # 闸口：编辑与删除拦截
    # ------------------------------------------------------------------
    @staticmethod
    async def assert_unbound(
        db: AsyncSession, waybill_id: int, *, action: str = "update",
    ) -> None:
        """运单已进入财务流程时拒绝业务侧改动（文档 02 §六 闸口 7）。

        两级拦截语义不同：
        - ``is_locked=1``：已收款终态锁定，需高权限解锁才能动；
        - 已挂非撤销对账单：软锁定，撤销或退回对账单即自动解除。
        """
        label = _ACTION_LABELS.get(action, "修改")
        r = await db.execute(
            select(Waybill.is_locked, Waybill.waybill_no).where(
                Waybill.id == waybill_id, Waybill.is_deleted == 0,
            )
        )
        row = r.one_or_none()
        if row is None:
            raise BizException("运单不存在")
        is_locked, waybill_no = row
        if int(is_locked or 0) == 1:
            raise BizException(
                f"运单 {waybill_no} 的费用已结清并锁定，不能{label}；"
                "如需变更请先由财务撤销收款"
            )

        if await ConsistencyChecker.is_biz_doc_bound(
            db, ReconKind.CUSTOMER, waybill_id,
        ):
            raise BizException(
                f"运单 {waybill_no} 已加入客户对账单，不能{label}；"
                "如需变更请先从对账单中移除该运单"
            )

    # ------------------------------------------------------------------
    # 闸口：变更置脏（文档 09 §3.3）
    # ------------------------------------------------------------------
    @staticmethod
    async def on_freight_amount_changed(
        db: AsyncSession,
        waybill_id: int,
        old_amount: Optional[Decimal],
        new_amount: Optional[Decimal],
    ) -> int:
        """运费金额变化（含计费引擎重算回填）→ 置脏客户对账行。"""
        if _same_amount(old_amount, new_amount):
            return 0
        return await ConsistencyChecker.mark_dirty_by_waybill(
            db, waybill_id,
            f"运费金额由 {_fmt_amount(old_amount)} 变为 {_fmt_amount(new_amount)}",
        )

    @staticmethod
    async def on_signed_quantity_changed(
        db: AsyncSession, waybill_id: int, old_qty: Any, new_qty: Any,
    ) -> int:
        """签收台数变化（含撤销签收）→ 置脏客户对账行。"""
        if int(old_qty or 0) == int(new_qty or 0):
            return 0
        return await ConsistencyChecker.mark_dirty_by_waybill(
            db, waybill_id,
            f"签收台数由 {int(old_qty or 0)} 变为 {int(new_qty or 0)}",
        )

    @staticmethod
    async def on_status_reverted(
        db: AsyncSession, waybill_id: int, old_status: int, new_status: int,
    ) -> int:
        """运单状态逆向（5→4 等）→ 置脏客户对账行。"""
        if int(new_status) >= int(old_status):
            return 0
        return await ConsistencyChecker.mark_dirty_by_waybill(
            db, waybill_id, "业务单据已回退至未交车，对账数据需重新核对",
        )

    @staticmethod
    async def on_items_changed(
        db: AsyncSession, waybill_id: int, detail: Optional[str] = None,
    ) -> int:
        """挂接明细增删（``biz_task_waybill_item``）→ 置脏客户对账行。"""
        return await ConsistencyChecker.mark_dirty_by_waybill(
            db, waybill_id, detail or "任务挂接已变更，对账台数可能不准",
        )


def _fmt_amount(v: Optional[Decimal]) -> str:
    """金额文案：空值显示「未填」，避免提示语里出现 None。"""
    if v is None:
        return "未填"
    return f"{Decimal(str(v)):.2f}"


def _same_amount(a: Optional[Decimal], b: Optional[Decimal]) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return Decimal(str(a)) == Decimal(str(b))
