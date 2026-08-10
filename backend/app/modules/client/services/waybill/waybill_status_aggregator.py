"""运单状态聚合器

将分散到任务挂接货物（TaskWaybillItem）的状态，按「max progress + min final-gate」
混合策略聚合回运单（Waybill.status）。

调用入口：
- ``recompute(waybill_id, *, allow_downgrade=False)``：单运单
- ``recompute_many(waybill_ids, *, allow_downgrade=False)``：批量（自动按 id 升序加锁防死锁）
- ``aggregate_by_task(task_id, *, allow_downgrade=False)``：按任务单反推涉及的运单集合后批量聚合

聚合规则（详见《02.运单与任务单状态机联动设计.md》§4.2.2）：

- 若没有任何活跃 item（is_deleted=0 且 status != 9）：
    → 运单回到 ``1 待调度``
- 若全部 cargo 已交车（sum(item.q where status=3) >= sum(cargo.q)）：
    → ``5 已交车``（完成门槛）
- 若全部 cargo 已到达（sum(item.q where status in {2,3}) >= sum(cargo.q)）：
    → ``4 待交车``（到达门槛）
- 若任意 item 进入 status >= 1：
    → ``3 运输中``（最大推进策略）
- 否则（已挂接但尚未装车）：
    → ``2 调度中``

注意：
- ``status = 0 草稿``、``6 已回单``、``7 已关闭`` 不被聚合器覆盖（人工/终态），需走显式 API。
- ``allow_downgrade=True`` 允许从高位回退到低位（撤销交车 / 撤销到达 / 取消挂接等场景）。
- 状态变更受 ``WaybillStateMachine.assert_transition`` 约束，遇到非法跳转抛出 BizException。
"""

from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.services.state_machine.waybill_state_machine import (
    WAYBILL_CLOSED,
    WAYBILL_DELIVERED,
    WAYBILL_DRAFT,
    WAYBILL_IN_TRANSIT,
    WAYBILL_PENDING,
    WAYBILL_RECEIPTED,
    WAYBILL_SCHEDULING,
    WAYBILL_COMPLETED,
    WaybillStateMachine,
)


# 不参与聚合（人工 / 终态）；进入这些状态后聚合器跳过、不自动改写。
# - WAYBILL_DRAFT(0)：草稿，待运营手动确认
# - WAYBILL_RECEIPTED(6)：已回单，运单侧人工动作，与 item 进度无关
# - WAYBILL_CLOSED(7)：已关闭终态
_SKIP_STATES: Set[int] = {WAYBILL_DRAFT, WAYBILL_RECEIPTED, WAYBILL_CLOSED}


class WaybillStatusAggregator:
    """运单状态聚合器（无状态工具类）"""

    # ------------------------------------------------------------------
    # 单运单聚合
    # ------------------------------------------------------------------
    @staticmethod
    async def recompute(
        db: AsyncSession,
        waybill_id: int,
        *,
        allow_downgrade: bool = False,
    ) -> Optional[Waybill]:
        """重算单个运单状态。"""
        waybill = await _lock_waybill(db, waybill_id)
        if waybill is None:
            return None
        await _apply_recompute(
            db, waybill, allow_downgrade=allow_downgrade,
        )
        return waybill

    # ------------------------------------------------------------------
    # 批量聚合
    # ------------------------------------------------------------------
    @staticmethod
    async def recompute_many(
        db: AsyncSession,
        waybill_ids: Iterable[int],
        *,
        allow_downgrade: bool = False,
    ) -> List[Waybill]:
        ids = sorted({int(i) for i in waybill_ids if i})
        out: List[Waybill] = []
        for wid in ids:
            wb = await WaybillStatusAggregator.recompute(
                db, wid, allow_downgrade=allow_downgrade,
            )
            if wb is not None:
                out.append(wb)
        return out

    # ------------------------------------------------------------------
    # 按任务单反推涉及运单后批量聚合
    # ------------------------------------------------------------------
    @staticmethod
    async def aggregate_by_task(
        db: AsyncSession,
        task_id: int,
        *,
        allow_downgrade: bool = False,
    ) -> List[Waybill]:
        rid = await db.execute(
            select(func.distinct(TaskWaybillItem.waybill_id)).where(
                TaskWaybillItem.task_id == task_id,
            )
        )
        ids = [int(i) for (i,) in rid.all() if i]
        if not ids:
            return []
        return await WaybillStatusAggregator.recompute_many(
            db, ids, allow_downgrade=allow_downgrade,
        )

    # ------------------------------------------------------------------
    # 派生：计算目标状态（供单元测试 & 外部预览）
    # ------------------------------------------------------------------
    @staticmethod
    async def derive_target_status(
        db: AsyncSession, waybill_id: int,
    ) -> Tuple[int, Dict[str, int]]:
        """给定运单返回 (目标状态, 度量字典)，不写入。"""
        metrics = await _gather_metrics(db, waybill_id)
        return _decide_status(metrics), metrics

    # ------------------------------------------------------------------
    # 衍生字段：运单上"有无活跃挂接"（供前端按钮/接口校验复用）
    # ------------------------------------------------------------------
    @staticmethod
    async def has_active_task_items(
        db: AsyncSession, waybill_id: int,
    ) -> bool:
        r = await db.execute(
            select(func.count(TaskWaybillItem.id)).where(
                TaskWaybillItem.waybill_id == waybill_id,
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.status != 9,
            )
        )
        return int(r.scalar() or 0) > 0


# ----------------------------------------------------------------------
# 内部实现
# ----------------------------------------------------------------------
async def _lock_waybill(
    db: AsyncSession, waybill_id: int,
) -> Optional[Waybill]:
    r = await db.execute(
        select(Waybill)
        .where(Waybill.id == waybill_id, Waybill.is_deleted == 0)
        .with_for_update()
    )
    return r.scalar_one_or_none()


async def _gather_metrics(
    db: AsyncSession, waybill_id: int,
) -> Dict[str, int]:
    """汇总该运单的度量。

    返回字段：
    - total_cargo_quantity：所有 cargo 行台数之和（基准）
    - active_quantity：active item（is_deleted=0 且 status != 9）的台数总和
    - loaded_plus_quantity：item.status >= 1 的台数总和（已装车 + 在途 + 已交车）
    - arrived_plus_quantity：item.status >= 2 的台数总和（在途/到达 + 已交车）
    - signed_quantity：item.status == 3 的台数
    """
    # 基准：cargo 总台数
    r_cargo = await db.execute(
        select(func.coalesce(func.sum(WaybillCargo.quantity), 0)).where(
            WaybillCargo.waybill_id == waybill_id,
            WaybillCargo.is_deleted == 0,
        )
    )
    total_cargo = int(r_cargo.scalar() or 0)

    # 各阶段台数：一次性 group by 拿出来
    r_items = await db.execute(
        select(TaskWaybillItem.status, func.coalesce(func.sum(TaskWaybillItem.quantity), 0))
        .where(
            TaskWaybillItem.waybill_id == waybill_id,
            TaskWaybillItem.is_deleted == 0,
        )
        .group_by(TaskWaybillItem.status)
    )

    by_status: Dict[int, int] = defaultdict(int)
    for s, q in r_items.all():
        by_status[int(s)] += int(q or 0)

    active = sum(q for s, q in by_status.items() if s != 9)
    loaded_plus = sum(q for s, q in by_status.items() if s in (1, 2, 3))
    arrived_plus = sum(q for s, q in by_status.items() if s in (2, 3))
    signed = by_status.get(3, 0)

    return {
        "total_cargo_quantity": total_cargo,
        "active_quantity": active,
        "loaded_plus_quantity": loaded_plus,
        "arrived_plus_quantity": arrived_plus,
        "signed_quantity": signed,
    }


def _decide_status(metrics: Dict[str, int]) -> int:
    total = metrics["total_cargo_quantity"]
    active = metrics["active_quantity"]
    if total <= 0:
        return WAYBILL_PENDING
    if active <= 0:
        return WAYBILL_PENDING
    # 完成门槛
    if metrics["signed_quantity"] >= total:
        return WAYBILL_COMPLETED
    # 到达门槛
    if metrics["arrived_plus_quantity"] >= total:
        return WAYBILL_DELIVERED
    # 运输中（最大推进策略）
    if metrics["loaded_plus_quantity"] > 0:
        return WAYBILL_IN_TRANSIT
    # 兜底：有挂接但都未装车 → 调度中
    return WAYBILL_SCHEDULING


async def _apply_recompute(
    db: AsyncSession,
    waybill: Waybill,
    *,
    allow_downgrade: bool,
) -> None:
    cur = int(waybill.status or 0)
    if cur in _SKIP_STATES:
        # 已关闭 / 草稿：聚合器不动
        return

    metrics = await _gather_metrics(db, waybill.id)
    target = _decide_status(metrics)
    if target == cur:
        return

    if target < cur and not allow_downgrade:
        # 正向链路下不允许回退
        return

    # 校验跳转合法性
    WaybillStateMachine.assert_transition(cur, target)
    waybill.status = target
    await db.flush()
