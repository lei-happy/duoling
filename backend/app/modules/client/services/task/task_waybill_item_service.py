"""
任务单货物挂接 Service

核心职责：
1. 候选计划 cargo 行查询（剩余可分配台数 > 0）
2. 挂接 / 批量挂接 / 取消挂接 / 状态推进
3. cargo.allocated_quantity 的原子维护
4. 任务单 total_quantity / waybill_count 冗余聚合
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.schemas.task.task_waybill_item import (
    CandidateCargoListOut,
    CandidateCargoOut,
    TaskWaybillItemIn,
    TaskWaybillItemStatusUpdate,
)
from app.modules.client.schemas.waybill.waybill_task_link import (
    WaybillLinkedTaskItemOut,
    WaybillLinkedTaskOut,
    WaybillLinkedTasksOut,
)
from app.modules.client.schemas.waybill.waybill import waybill_brand_model_key
from app.modules.client.services.state_machine.item_state_machine import (
    ITEM_SIGNED,
    ITEM_UNFINISHED_THRESHOLD,
    ItemStateMachine,
)
from app.modules.client.services.state_machine.waybill_state_machine import (
    WAYBILL_RECEIPTED,
)
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_ARRIVED,
    TASK_DISPATCHED,
    TASK_LOADED,
    TASK_ON_WAY,
    TASK_SIGNED,
)
from app.modules.client.models.task.task_status_event import (
    TASK_EVENT_ARRIVE,
    TASK_EVENT_DELIVER,
    TASK_EVENT_LOAD,
    TASK_EVENT_REVERT_ARRIVE,
    TASK_EVENT_REVERT_DELIVER,
    TASK_EVENT_REVERT_LOAD,
    TASK_EVENT_SOURCE_SYSTEM,
)
from app.modules.client.services.task.task_status_event_service import (
    TaskStatusEventService,
)
from app.modules.client.services.waybill.waybill_service import WaybillService
from app.modules.client.services.waybill.waybill_status_aggregator import (
    WaybillStatusAggregator,
)

# 兼容旧引用：直接复用状态机里定义的阈值
UNFINISHED_THRESHOLD = ITEM_UNFINISHED_THRESHOLD


class TaskWaybillItemService:

    # ------------------------------------------------------------------
    # 候选查询
    # ------------------------------------------------------------------
    @staticmethod
    def _candidate_waybill_conditions(
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
    ):
        conds = [
            Waybill.is_deleted == 0,
            Waybill.status.in_([1, 2, 3]),
        ]
        if keyword:
            kw = f"%{keyword.strip()}%"
            conds.append(or_(
                Waybill.waybill_no.like(kw),
                Waybill.customer_name.like(kw),
            ))
        if customer_id is not None:
            conds.append(Waybill.customer_id == customer_id)
        if origin_keyword:
            conds.append(Waybill.origin.like(f"%{origin_keyword.strip()}%"))
        if destination_keyword:
            conds.append(
                Waybill.destination.like(f"%{destination_keyword.strip()}%")
            )
        return conds

    @staticmethod
    def _candidate_remaining_expr():
        return WaybillCargo.quantity - func.coalesce(
            WaybillCargo.allocated_quantity, 0
        )

    @staticmethod
    def _candidate_cargo_model_condition(
        model_keyword: Optional[str] = None,
    ):
        if not model_keyword or not str(model_keyword).strip():
            return None
        kw = f"%{str(model_keyword).strip()}%"
        return or_(
            WaybillCargo.vehicle_brand.like(kw),
            WaybillCargo.vehicle_model.like(kw),
        )

    @staticmethod
    def _candidate_cargo_where(
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
        model_keyword: Optional[str] = None,
    ):
        remaining = TaskWaybillItemService._candidate_remaining_expr()
        conds = [
            WaybillCargo.is_deleted == 0,
            remaining > 0,
            *TaskWaybillItemService._candidate_waybill_conditions(
                keyword=keyword,
                customer_id=customer_id,
                origin_keyword=origin_keyword,
                destination_keyword=destination_keyword,
            ),
        ]
        model_cond = TaskWaybillItemService._candidate_cargo_model_condition(
            model_keyword
        )
        if model_cond is not None:
            conds.append(model_cond)
        return remaining, conds

    @staticmethod
    async def count_candidate_cargoes(
        db: AsyncSession,
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
        model_keyword: Optional[str] = None,
    ) -> Tuple[int, int, int]:
        """统计待配计划数、cargo 明细行数、剩余可配总台数（不受 list limit 影响）。"""
        remaining, conds = TaskWaybillItemService._candidate_cargo_where(
            keyword=keyword,
            customer_id=customer_id,
            origin_keyword=origin_keyword,
            destination_keyword=destination_keyword,
            model_keyword=model_keyword,
        )
        q = (
            select(
                func.count(func.distinct(Waybill.id)).label("waybill_count"),
                func.count(WaybillCargo.id).label("cargo_line_count"),
                func.coalesce(func.sum(remaining), 0).label("quantity_total"),
            )
            .select_from(WaybillCargo)
            .join(Waybill, Waybill.id == WaybillCargo.waybill_id)
            .where(*conds)
        )
        row = (await db.execute(q)).one()
        waybill_count = int(row.waybill_count or 0)
        cargo_line_count = int(row.cargo_line_count or 0)
        quantity_total = int(row.quantity_total or 0)
        # 明细行数 >= 计划数；若异常则纠正字段顺序（兼容部分驱动返回列序不一致）
        if waybill_count > cargo_line_count:
            waybill_count, cargo_line_count = cargo_line_count, waybill_count
        return waybill_count, cargo_line_count, quantity_total

    @staticmethod
    async def list_candidate_cargoes(
        db: AsyncSession,
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
        model_keyword: Optional[str] = None,
        offset: int = 0,
        limit: int = 200,
    ) -> CandidateCargoListOut:
        """挂接器左栏：返回剩余台数 > 0 的计划 cargo 行候选。

        新语义（参考《02.计划与任务单状态机联动设计.md》§4.2）：

        - 1 待调度：完全可发运；
        - 2 调度中：仍可挂接（cargo.remaining_quantity > 0，支持拆单分批）；
        - 3 运输中：仍允许新挂接尾段，只要剩余台数 > 0；
        - 4+ 已送达/已完成/已关闭：不允许新挂接。
        """
        waybill_count, line_count, quantity_total = (
            await TaskWaybillItemService.count_candidate_cargoes(
                db,
                keyword=keyword,
                customer_id=customer_id,
                origin_keyword=origin_keyword,
                destination_keyword=destination_keyword,
                model_keyword=model_keyword,
            )
        )

        _, conds = TaskWaybillItemService._candidate_cargo_where(
            keyword=keyword,
            customer_id=customer_id,
            origin_keyword=origin_keyword,
            destination_keyword=destination_keyword,
            model_keyword=model_keyword,
        )
        cg_q = (
            select(WaybillCargo, Waybill)
            .join(Waybill, Waybill.id == WaybillCargo.waybill_id)
            .where(*conds)
            .order_by(
                Waybill.created_at.desc(),
                WaybillCargo.waybill_id,
                WaybillCargo.sort_order,
            )
            .offset(max(0, int(offset)))
            .limit(max(1, int(limit)))
        )
        rows = list((await db.execute(cg_q)).all())
        if not rows:
            return CandidateCargoListOut(
                items=[],
                waybillCount=waybill_count,
                lineCount=line_count,
                quantityTotal=quantity_total,
                truncated=int(offset) < line_count,
            )

        series_lookup = await WaybillService._series_image_lookup_map(db)

        out: List[CandidateCargoOut] = []
        for c, w in rows:
            remaining = max(0, int(c.quantity) - int(c.allocated_quantity or 0))
            img_key = waybill_brand_model_key(c.vehicle_brand, c.vehicle_model)
            series_image = series_lookup.get(img_key)
            out.append(CandidateCargoOut(
                waybillId=w.id,
                waybillNo=w.waybill_no,
                customerId=w.customer_id,
                customerName=w.customer_name,
                origin=w.origin,
                destination=w.destination,
                dealerName=w.dealer_name,
                requiredLoadTime=w.required_load_time,
                waybillCreatedAt=w.created_at,
                waybillStatus=w.status,
                cargoId=c.id,
                vehicleBrand=c.vehicle_brand,
                vehicleModel=c.vehicle_model,
                vin=c.vin,
                seriesImage=series_image,
                quantity=int(c.quantity),
                allocatedQuantity=int(c.allocated_quantity or 0),
                remainingQuantity=remaining,
            ))
        return CandidateCargoListOut(
            items=out,
            waybillCount=waybill_count,
            lineCount=line_count,
            quantityTotal=quantity_total,
            truncated=(int(offset) + len(out)) < line_count,
        )

    # ------------------------------------------------------------------
    # 挂接核心：cargo 行原子加减
    # ------------------------------------------------------------------
    @staticmethod
    async def _bump_cargo_allocated(
        db: AsyncSession,
        cargo_id: int,
        delta: int,
    ) -> WaybillCargo:
        """原子调整 cargo.allocated_quantity；增量后必须 <= quantity 且 >= 0"""
        # 先锁定行
        res = await db.execute(
            select(WaybillCargo).where(
                WaybillCargo.id == cargo_id,
                WaybillCargo.is_deleted == 0,
            ).with_for_update()
        )
        cargo = res.scalar_one_or_none()
        if not cargo:
            raise BizException(f"计划货物行不存在 (cargo_id={cargo_id})")
        new_allocated = int(cargo.allocated_quantity or 0) + delta
        if new_allocated < 0:
            new_allocated = 0
        if new_allocated > int(cargo.quantity):
            raise BizException(
                f"计划 {cargo.waybill_id} 货物行可分配台数不足："
                f"原台数 {cargo.quantity} / 已分配 {cargo.allocated_quantity or 0} / "
                f"本次新增 {delta}"
            )
        cargo.allocated_quantity = new_allocated
        await db.flush()
        return cargo

    @staticmethod
    async def _build_item_snapshot(
        db: AsyncSession,
        task: Task,
        in_data: TaskWaybillItemIn,
    ) -> TaskWaybillItem:
        """从入参构建 TaskWaybillItem，含计划/货物冗余快照填充"""
        wb_res = await db.execute(
            select(Waybill).where(
                Waybill.id == in_data.waybillId,
                Waybill.is_deleted == 0,
            )
        )
        wb = wb_res.scalar_one_or_none()
        if not wb:
            raise BizException(f"计划不存在 (id={in_data.waybillId})")

        cg_res = await db.execute(
            select(WaybillCargo).where(
                WaybillCargo.id == in_data.waybillCargoId,
                WaybillCargo.is_deleted == 0,
            )
        )
        cargo = cg_res.scalar_one_or_none()
        if not cargo:
            raise BizException(f"计划货物行不存在 (id={in_data.waybillCargoId})")
        if cargo.waybill_id != wb.id:
            raise BizException("货物行不属于该计划")

        return TaskWaybillItem(
            task_id=task.id,
            waybill_id=wb.id,
            waybill_cargo_id=cargo.id,
            waybill_no=wb.waybill_no,
            customer_id=wb.customer_id,
            customer_name=wb.customer_name,
            vehicle_brand=cargo.vehicle_brand,
            vehicle_model=cargo.vehicle_model,
            dealer_name=wb.dealer_name,
            quantity=int(in_data.quantity),
            dispatch_order_id=in_data.dispatchOrderId,
            status=0,
            remark=in_data.remark,
        )

    @staticmethod
    async def add_items(
        db: AsyncSession,
        task: Task,
        items_in: List[TaskWaybillItemIn],
    ) -> List[TaskWaybillItem]:
        """批量挂接到任务单（不替换，追加）"""
        added: List[TaskWaybillItem] = []
        affected_wb: set[int] = set()
        for it in items_in:
            await TaskWaybillItemService._bump_cargo_allocated(
                db, it.waybillCargoId, int(it.quantity)
            )
            row = await TaskWaybillItemService._build_item_snapshot(db, task, it)
            db.add(row)
            await db.flush()
            added.append(row)
            affected_wb.add(int(row.waybill_id))
        await TaskWaybillItemService._refresh_task_aggregates(db, task)
        # 挂接是正向推进：禁用 downgrade
        await WaybillStatusAggregator.recompute_many(
            db, affected_wb, allow_downgrade=False,
        )
        return added

    @staticmethod
    async def replace_items(
        db: AsyncSession,
        task: Task,
        items_in: List[TaskWaybillItemIn],
    ) -> List[TaskWaybillItem]:
        """整单替换：先释放所有未交车的挂接，再批量挂接"""
        existing = await TaskWaybillItemService.list_items_of_task(db, task.id)
        affected_wb: set[int] = set()
        for old in existing:
            if int(old.status) < UNFINISHED_THRESHOLD:
                await TaskWaybillItemService._bump_cargo_allocated(
                    db, old.waybill_cargo_id, -int(old.quantity)
                )
            old.is_deleted = 1
            affected_wb.add(int(old.waybill_id))
        await db.flush()
        new_rows = await TaskWaybillItemService.add_items(db, task, items_in)
        # 替换可能让原本挂接的计划回退到待调度
        await WaybillStatusAggregator.recompute_many(
            db, affected_wb, allow_downgrade=True,
        )
        return new_rows

    @staticmethod
    async def remove_item(
        db: AsyncSession, item_id: int,
    ) -> Task:
        """取消挂接（释放台数）；返回所属 task 供调用方更新冗余/状态"""
        res = await db.execute(
            select(TaskWaybillItem).where(
                TaskWaybillItem.id == item_id,
                TaskWaybillItem.is_deleted == 0,
            )
        )
        item = res.scalar_one_or_none()
        if not item:
            raise BizException("挂接记录不存在")
        if int(item.status) >= UNFINISHED_THRESHOLD:
            raise BizException("已交车的货物不可取消挂接")
        waybill_id = int(item.waybill_id)
        await TaskWaybillItemService._bump_cargo_allocated(
            db, item.waybill_cargo_id, -int(item.quantity)
        )
        item.is_deleted = 1
        await db.flush()

        # 更新任务单冗余
        task_res = await db.execute(
            select(Task).where(Task.id == item.task_id, Task.is_deleted == 0)
        )
        task = task_res.scalar_one_or_none()
        if task is not None:
            await TaskWaybillItemService._refresh_task_aggregates(db, task)
        # 取消挂接可能让计划回退
        await WaybillStatusAggregator.recompute(
            db, waybill_id, allow_downgrade=True,
        )
        return task

    @staticmethod
    async def update_item_status(
        db: AsyncSession,
        item_id: int,
        data: TaskWaybillItemStatusUpdate,
    ) -> TaskWaybillItem:
        res = await db.execute(
            select(TaskWaybillItem).where(
                TaskWaybillItem.id == item_id,
                TaskWaybillItem.is_deleted == 0,
            )
        )
        item = res.scalar_one_or_none()
        if not item:
            raise BizException("挂接记录不存在")

        old_status = int(item.status)
        new_status = int(data.status)

        # 独立性防护：计划已进入「已回单(6)」后，底单已交付货主，
        # 禁止 item 级"撤销交车"（3→2）直接回退，必须先在计划侧撤销回单。
        if old_status == ITEM_SIGNED and new_status < ITEM_SIGNED:
            wb_r = await db.execute(
                select(Waybill.status).where(Waybill.id == item.waybill_id)
            )
            wb_status = wb_r.scalar_one_or_none()
            if wb_status is not None and int(wb_status) >= WAYBILL_RECEIPTED:
                raise BizException("计划已回单，请先在计划侧撤销回单后再撤销交车")

        await TaskWaybillItemService._switch_item_status(
            db, item, new_status,
            loaded_at=data.loadedAt,
            unloaded_at=data.unloadedAt,
            signed_at=data.signedAt,
        )
        if data.dispatchOrderId is not None:
            item.dispatch_order_id = data.dispatchOrderId
        if data.remark is not None:
            item.remark = data.remark
        await db.flush()

        # 聚合上推：
        # - item 全装车 / 撤销最后一条装车 → task.status 1↔2
        # - item 全卸车 / 撤销最后一条卸车 → task.status 3↔4
        # - item 全交车 / 撤销交车 → task.status 4↔5
        task_res = await db.execute(
            select(Task).where(
                Task.id == item.task_id,
                Task.is_deleted == 0,
            )
        )
        task = task_res.scalar_one_or_none()
        if task is not None:
            await TaskWaybillItemService._aggregate_load_status_from_items(
                db, task,
            )
            await TaskWaybillItemService._aggregate_task_status_from_items(
                db, task,
            )

        # 单条 item 变更后聚合计划状态（含可能的回退）
        await WaybillStatusAggregator.recompute(
            db, int(item.waybill_id),
            allow_downgrade=(new_status < old_status),
        )
        return item

    # ------------------------------------------------------------------
    # Item → Task 反向聚合
    # ------------------------------------------------------------------
    @staticmethod
    async def _aggregate_load_status_from_items(
        db: AsyncSession,
        task: Task,
    ) -> None:
        """根据当前任务下 item 的状态分布，自动在 1↔2 / 3↔4 间推进 task.status。

        规则：
        - task.status == 1 且所有活跃 item.status >= 1 → 1→2（已装车，写 actual_load_time）
        - task.status == 2 且存在任一活跃 item.status < 1（撤销最后一条装车）→ 2→1
        - task.status == 3 且所有活跃 item.status >= 2 → 3→4（已到达，写 actual_arrive_time）
        - task.status == 4 且存在任一活跃 item.status < 2（撤销最后一条卸车）→ 4→3

        本方法直接改写 task.status（不走 ``TaskStateMachine.assert_transition``）；
        因为 1→2 / 3→4 已下沉为聚合态，状态机不再公开此路径。
        """
        cur = int(task.status)
        if cur not in (
            TASK_DISPATCHED, TASK_LOADED, TASK_ON_WAY, TASK_ARRIVED,
        ):
            return
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        active = [it for it in items if int(it.status) != 9]
        if not active:
            return
        all_loaded = all(int(it.status) >= 1 for it in active)
        all_unloaded = all(int(it.status) >= 2 for it in active)

        changed = False
        if cur == TASK_DISPATCHED and all_loaded:
            loaded_times = [it.loaded_at for it in active if it.loaded_at is not None]
            if loaded_times:
                task.actual_load_time = max(loaded_times)
            TaskStatusEventService.apply_status(
                db, task, TASK_LOADED,
                event_type=TASK_EVENT_LOAD,
                source=TASK_EVENT_SOURCE_SYSTEM,
                reason="全部挂接货物已装车",
            )
            changed = True
        elif cur == TASK_LOADED and not all_loaded:
            # 撤销最后一条装车（item 1→0），任务回退到已派车
            task.actual_load_time = None
            TaskStatusEventService.apply_status(
                db, task, TASK_DISPATCHED,
                event_type=TASK_EVENT_REVERT_LOAD,
                source=TASK_EVENT_SOURCE_SYSTEM,
                reason="装车记录被撤回",
            )
            changed = True
        elif cur == TASK_ON_WAY and all_unloaded:
            unloaded_times = [
                it.unloaded_at for it in active if it.unloaded_at is not None
            ]
            if unloaded_times:
                task.actual_arrive_time = max(unloaded_times)
            TaskStatusEventService.apply_status(
                db, task, TASK_ARRIVED,
                event_type=TASK_EVENT_ARRIVE,
                source=TASK_EVENT_SOURCE_SYSTEM,
                reason="全部挂接货物已卸车",
            )
            changed = True
        elif cur == TASK_ARRIVED and not all_unloaded:
            # 撤销最后一条卸车（item 2→1），任务回退到在途
            task.actual_arrive_time = None
            TaskStatusEventService.apply_status(
                db, task, TASK_ON_WAY,
                event_type=TASK_EVENT_REVERT_ARRIVE,
                source=TASK_EVENT_SOURCE_SYSTEM,
                reason="卸车记录被撤回",
            )
            changed = True

        if changed:
            await db.flush()

    @staticmethod
    async def _aggregate_task_status_from_items(
        db: AsyncSession,
        task: Task,
    ) -> None:
        """根据当前任务下 item 的状态分布，自动调整 task.status 在 4↔5 间切换。

        规则：
        - task.status == 4 且所有活跃 item.status == 3 → 自动 4→5（写 task.signed_at）
        - task.status == 5 且存在任一活跃 item.status < 3（撤销交车）→ 自动 5→4

        其他状态不在此聚合范围；6 已结算/7 已关闭 不再由此触发。
        """
        cur = int(task.status)
        if cur not in (TASK_ARRIVED, TASK_SIGNED):
            return
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        # 只看活跃 item（已取消的 9 不参与聚合）
        active = [int(it.status) for it in items if int(it.status) != 9]
        if not active:
            return
        all_signed = all(s == 3 for s in active)

        if cur == TASK_ARRIVED and all_signed:
            TaskStatusEventService.apply_status(
                db, task, TASK_SIGNED,
                event_type=TASK_EVENT_DELIVER,
                source=TASK_EVENT_SOURCE_SYSTEM,
                reason="全部挂接货物已交车",
            )
            await db.flush()
        elif cur == TASK_SIGNED and not all_signed:
            TaskStatusEventService.apply_status(
                db, task, TASK_ARRIVED,
                event_type=TASK_EVENT_REVERT_DELIVER,
                source=TASK_EVENT_SOURCE_SYSTEM,
                reason="存在被撤销交车的挂接货物",
            )
            await db.flush()

    # ------------------------------------------------------------------
    # Task → Item 同步（正向 / 反向）
    # ------------------------------------------------------------------
    @staticmethod
    async def _switch_item_status(
        db: AsyncSession,
        item: TaskWaybillItem,
        new_status: int,
        *,
        loaded_at: Optional[datetime] = None,
        unloaded_at: Optional[datetime] = None,
        signed_at: Optional[datetime] = None,
    ) -> None:
        """异步单条 item 切换：维护 allocated + 状态 + 时间字段。"""
        old_status = int(item.status)
        if old_status == new_status:
            return
        ItemStateMachine.assert_transition(old_status, new_status)

        # 释放占用：未完结 → 完结/取消
        if old_status < UNFINISHED_THRESHOLD <= new_status:
            await TaskWaybillItemService._bump_cargo_allocated(
                db, item.waybill_cargo_id, -int(item.quantity)
            )
        # 重新占用：完结 → 未完结（撤销交车）
        elif old_status >= UNFINISHED_THRESHOLD > new_status:
            await TaskWaybillItemService._bump_cargo_allocated(
                db, item.waybill_cargo_id, int(item.quantity)
            )

        item.status = new_status
        if loaded_at is not None:
            item.loaded_at = loaded_at
        if unloaded_at is not None:
            item.unloaded_at = unloaded_at
        if signed_at is not None:
            item.signed_at = signed_at

    @staticmethod
    async def propagate_to_items(
        db: AsyncSession,
        task: Task,
        *,
        loaded_at: Optional[datetime] = None,
        unloaded_at: Optional[datetime] = None,
        signed_at: Optional[datetime] = None,
        only_unfinished: bool = True,
    ) -> List[int]:
        """根据当前 ``task.status`` 把所有 active item 正向推进到对应状态。

        - 只升不降（max progress）：如已超过推导目标则保持
        - ``only_unfinished=True`` 时跳过 status == 9 (已取消) 的 item
        - 返回受影响的计划 id 列表

        本方法不调用 aggregator；调用方应在 propagate 完后调用
        ``WaybillStatusAggregator.aggregate_by_task(task.id)`` 完成聚合。
        """
        target = ItemStateMachine.derive_from_task(int(task.status))
        if target is None:
            return []
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        affected_wb: set[int] = set()
        for it in items:
            if only_unfinished and int(it.status) == 9:
                continue
            cur = int(it.status)
            if target <= cur:
                continue
            await TaskWaybillItemService._switch_item_status(
                db, it, target,
                loaded_at=loaded_at,
                unloaded_at=unloaded_at,
                signed_at=signed_at,
            )
            affected_wb.add(int(it.waybill_id))
        await db.flush()
        return list(affected_wb)

    @staticmethod
    async def propagate_revert_to_items(
        db: AsyncSession,
        task: Task,
        *,
        only_active: bool = True,
    ) -> List[int]:
        """根据当前 ``task.status`` 把所有 active item 反向回退到对应状态。

        - 只降不升：如当前 item.status 已低于推导目标，保持不变
        - 时间字段不清除（保留历史事实，参考设计文档 §4.5）
        - 返回受影响的计划 id 列表
        """
        target = ItemStateMachine.derive_from_task(int(task.status))
        if target is None:
            return []
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        affected_wb: set[int] = set()
        for it in items:
            if only_active and int(it.status) == 9:
                continue
            cur = int(it.status)
            if target >= cur:
                continue
            await TaskWaybillItemService._switch_item_status(db, it, target)
            affected_wb.add(int(it.waybill_id))
        await db.flush()
        return list(affected_wb)

    @staticmethod
    async def propagate_cancel_to_items(
        db: AsyncSession,
        task: Task,
    ) -> List[int]:
        """强制取消任务时，把所有 item 推到 ``9 已取消`` 并释放台数。

        与 ``release_all_items_of_task`` 不同：本方法不软删 item，
        而是保留挂接记录、状态置 9，以便审计追溯。台数同步释放。
        """
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        affected_wb: set[int] = set()
        for it in items:
            if int(it.status) == 9:
                continue
            await TaskWaybillItemService._switch_item_status(db, it, 9)
            affected_wb.add(int(it.waybill_id))
        await db.flush()
        return list(affected_wb)

    # ------------------------------------------------------------------
    # 查询与冗余聚合
    # ------------------------------------------------------------------
    @staticmethod
    async def list_items_of_task(
        db: AsyncSession, task_id: int,
    ) -> List[TaskWaybillItem]:
        res = await db.execute(
            select(TaskWaybillItem).where(
                TaskWaybillItem.task_id == task_id,
                TaskWaybillItem.is_deleted == 0,
            ).order_by(TaskWaybillItem.id.asc())
        )
        return list(res.scalars().all())

    @staticmethod
    async def list_linked_tasks_for_waybill(
        db: AsyncSession, waybill_id: int,
    ) -> WaybillLinkedTasksOut:
        """按计划 ID 查询活跃任务挂接，按任务聚合（供计划列表「已调度」弹框）。"""
        wb_res = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = wb_res.scalar_one_or_none()
        if waybill is None:
            raise BizException("计划不存在或已删除")

        res = await db.execute(
            select(TaskWaybillItem, Task)
            .join(Task, Task.id == TaskWaybillItem.task_id)
            .where(
                TaskWaybillItem.waybill_id == waybill_id,
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.status != 9,
                Task.is_deleted == 0,
            )
            .order_by(TaskWaybillItem.task_id.asc(), TaskWaybillItem.id.asc())
        )
        rows = res.all()

        grouped: dict[int, WaybillLinkedTaskOut] = {}
        for item, task in rows:
            task_id = int(task.id)
            line = WaybillLinkedTaskItemOut(
                id=int(item.id),
                quantity=int(item.quantity or 0),
                vehicleBrand=item.vehicle_brand,
                vehicleModel=item.vehicle_model,
                itemStatus=int(item.status or 0),
            )
            if task_id not in grouped:
                grouped[task_id] = WaybillLinkedTaskOut(
                    taskId=task_id,
                    taskNo=task.task_no,
                    taskStatus=int(task.status or 0),
                    mainDriverName=task.main_driver_name,
                    mainDriverPhone=task.main_driver_phone,
                    plateNumber=task.plate_number,
                    allocatedQuantity=int(item.quantity or 0),
                    items=[line],
                )
            else:
                entry = grouped[task_id]
                entry.allocatedQuantity += int(item.quantity or 0)
                entry.items.append(line)

        return WaybillLinkedTasksOut(
            waybillId=int(waybill.id),
            waybillNo=waybill.waybill_no,
            tasks=list(grouped.values()),
        )

    @staticmethod
    async def _refresh_task_aggregates(db: AsyncSession, task: Task) -> None:
        """重新统计 task.total_quantity / waybill_count"""
        res = await db.execute(
            select(
                func.coalesce(func.sum(TaskWaybillItem.quantity), 0),
                func.count(func.distinct(TaskWaybillItem.waybill_id)),
            ).where(
                TaskWaybillItem.task_id == task.id,
                TaskWaybillItem.is_deleted == 0,
            )
        )
        total_qty, wb_count = res.one()
        task.total_quantity = int(total_qty or 0)
        task.waybill_count = int(wb_count or 0)
        await db.flush()

    @staticmethod
    async def release_all_items_of_task(
        db: AsyncSession, task: Task,
    ) -> None:
        """取消任务单时调用：释放所有未交车挂接占用的台数并软删

        软删后调用 aggregator 让对应计划回退到合理状态（待调度 / 调度中）。
        """
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        affected_wb: set[int] = set()
        for it in items:
            if int(it.status) < UNFINISHED_THRESHOLD:
                await TaskWaybillItemService._bump_cargo_allocated(
                    db, it.waybill_cargo_id, -int(it.quantity)
                )
            it.is_deleted = 1
            affected_wb.add(int(it.waybill_id))
        await db.flush()
        await TaskWaybillItemService._refresh_task_aggregates(db, task)
        await WaybillStatusAggregator.recompute_many(
            db, affected_wb, allow_downgrade=True,
        )
