"""任务单装卸记录 Service

负责创建 / 列举 / 撤销装卸事件，并在同一事务内：
1. 写入 ``biz_task_loading_record`` 与桥接 ``biz_task_loading_record_item``；
2. 推进选中的 ``TaskWaybillItem.status``（装车 0→1 / 卸车 1→2）；
3. 调用 ``_aggregate_load_status_from_items`` 聚合 ``Task.status``（1↔2 / 3↔4）；
4. 调用 ``WaybillStatusAggregator.aggregate_by_task`` 聚合关联运单。

业务规则（详见《调度工作台与状态机重构方案》）：
- 装车事件：``task.status`` 必须 ∈ {1 已派车, 2 已装车}（允许补录）；选中 item 当前 status<1
- 卸车事件：``task.status`` 必须 ∈ {3 在途, 4 已到达}（允许补录）；选中 item 当前 status==1
- 多调令任务必须指定 ``dispatch_order_id``；单调令可省略
"""

from datetime import datetime
from typing import Iterable, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_dispatch_order import TaskDispatchOrder
from app.modules.client.models.task.task_loading_record import (
    TaskLoadingRecord,
    TaskLoadingRecordItem,
)
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.schemas.task.task_loading_record import (
    TaskLoadingRecordCreate,
    TaskLoadingRecordItemOut,
    TaskLoadingRecordOut,
)
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_ARRIVED,
    TASK_DISPATCHED,
    TASK_LOADED,
    TASK_ON_WAY,
    TASK_STATUS_LABELS,
)
from app.modules.client.services.task.task_waybill_item_service import (
    TaskWaybillItemService,
)
from app.modules.client.services.waybill.waybill_status_aggregator import (
    WaybillStatusAggregator,
)


_LOAD_OK_TASK_STATES = {TASK_DISPATCHED, TASK_LOADED}
_UNLOAD_OK_TASK_STATES = {TASK_ON_WAY, TASK_ARRIVED}


class TaskLoadingRecordService:
    """装卸事件服务"""

    # ------------------------------------------------------------------
    # 列表
    # ------------------------------------------------------------------
    @staticmethod
    async def list_records(
        db: AsyncSession, task_id: int,
    ) -> List[TaskLoadingRecordOut]:
        r = await db.execute(
            select(TaskLoadingRecord)
            .where(
                TaskLoadingRecord.task_id == task_id,
                TaskLoadingRecord.is_deleted == 0,
            )
            .order_by(TaskLoadingRecord.happened_at.asc(), TaskLoadingRecord.id.asc())
        )
        records = list(r.scalars().all())
        if not records:
            return []
        record_ids = [rec.id for rec in records]
        ri_r = await db.execute(
            select(TaskLoadingRecordItem)
            .where(
                TaskLoadingRecordItem.record_id.in_(record_ids),
                TaskLoadingRecordItem.is_deleted == 0,
            )
        )
        ri_rows = list(ri_r.scalars().all())

        item_ids = sorted({int(ri.item_id) for ri in ri_rows})
        items_map: dict[int, TaskWaybillItem] = {}
        if item_ids:
            it_r = await db.execute(
                select(TaskWaybillItem).where(TaskWaybillItem.id.in_(item_ids))
            )
            items_map = {int(it.id): it for it in it_r.scalars().all()}

        ri_by_record: dict[int, List] = {}
        for ri in ri_rows:
            ri_by_record.setdefault(int(ri.record_id), []).append(ri)

        out: List[TaskLoadingRecordOut] = []
        for rec in records:
            children = ri_by_record.get(int(rec.id), [])
            children_out = [
                TaskLoadingRecordItemOut.from_models(ri, items_map.get(int(ri.item_id)))
                for ri in children
            ]
            out.append(TaskLoadingRecordOut.from_model(rec, items=children_out))
        return out

    # ------------------------------------------------------------------
    # 创建
    # ------------------------------------------------------------------
    @staticmethod
    async def create_record(
        db: AsyncSession,
        task_id: int,
        data: TaskLoadingRecordCreate,
        *,
        operator_id: Optional[int] = None,
        operator_name: Optional[str] = None,
    ) -> TaskLoadingRecordOut:
        task = await TaskLoadingRecordService._load_or_raise(db, task_id)
        cur_task_status = int(task.status)
        event_type = int(data.eventType)

        # 1. 校验任务状态
        if event_type == 1 and cur_task_status not in _LOAD_OK_TASK_STATES:
            raise BizException(
                f"任务当前状态「{TASK_STATUS_LABELS.get(cur_task_status)}」"
                f"不允许添加装车记录"
            )
        if event_type == 2 and cur_task_status not in _UNLOAD_OK_TASK_STATES:
            raise BizException(
                f"任务当前状态「{TASK_STATUS_LABELS.get(cur_task_status)}」"
                f"不允许添加卸车记录"
            )

        # 2. 校验调令归属
        await TaskLoadingRecordService._validate_dispatch_order(
            db, task, data.dispatchOrderId,
        )

        # 3. 锁定 + 校验 items
        items_map = await TaskLoadingRecordService._load_items_map(
            db, task_id, [it.itemId for it in data.items],
        )
        target_item_status = 1 if event_type == 1 else 2
        precondition_status = 0 if event_type == 1 else 1
        for in_it in data.items:
            it = items_map[in_it.itemId]
            if int(it.status) != precondition_status:
                raise BizException(
                    f"挂接行 #{it.id} 当前状态={int(it.status)}，"
                    f"不能添加 {'装' if event_type == 1 else '卸'}车记录"
                )
            if int(in_it.quantity) <= 0 or int(in_it.quantity) > int(it.quantity):
                raise BizException(
                    f"挂接行 #{it.id} 装/卸台数 {in_it.quantity} 超出范围 "
                    f"(item.quantity={it.quantity})"
                )

        # 4. 写主记录
        rec = TaskLoadingRecord(
            task_id=task_id,
            dispatch_order_id=data.dispatchOrderId,
            event_type=event_type,
            happened_at=data.happenedAt,
            location=data.location,
            location_code=data.locationCode,
            location_region_id=data.locationRegionId,
            quantity=sum(int(it.quantity) for it in data.items),
            photo_urls=list(data.photoUrls or []),
            operator_id=operator_id,
            operator_name=operator_name,
            remark=data.remark,
        )
        db.add(rec)
        await db.flush()

        # 5. 写桥接 + 推进 item 状态
        for in_it in data.items:
            it = items_map[in_it.itemId]
            ri = TaskLoadingRecordItem(
                record_id=rec.id,
                item_id=it.id,
                quantity=int(in_it.quantity),
            )
            db.add(ri)
            await TaskWaybillItemService._switch_item_status(
                db, it, target_item_status,
                loaded_at=data.happenedAt if event_type == 1 else None,
                unloaded_at=data.happenedAt if event_type == 2 else None,
            )
        await db.flush()

        # 6. 聚合 task → waybill
        await TaskWaybillItemService._aggregate_load_status_from_items(db, task)
        await TaskWaybillItemService._aggregate_task_status_from_items(db, task)
        await WaybillStatusAggregator.aggregate_by_task(
            db, task_id, allow_downgrade=False,
        )

        await db.refresh(rec)
        # 重新加载桥接 + item，便于回包
        return await TaskLoadingRecordService.get_record_dump(db, rec.id)

    # ------------------------------------------------------------------
    # 撤销（删除最后一次记录，回退 item 状态）
    # ------------------------------------------------------------------
    @staticmethod
    async def revoke_record(
        db: AsyncSession, record_id: int,
    ) -> None:
        r = await db.execute(
            select(TaskLoadingRecord).where(
                TaskLoadingRecord.id == record_id,
                TaskLoadingRecord.is_deleted == 0,
            )
        )
        rec = r.scalar_one_or_none()
        if not rec:
            raise BizException("装卸记录不存在")

        task = await TaskLoadingRecordService._load_or_raise(db, int(rec.task_id))
        event_type = int(rec.event_type)
        target_item_status = 0 if event_type == 1 else 1

        ri_r = await db.execute(
            select(TaskLoadingRecordItem).where(
                TaskLoadingRecordItem.record_id == rec.id,
                TaskLoadingRecordItem.is_deleted == 0,
            )
        )
        ri_rows = list(ri_r.scalars().all())
        item_ids = [int(ri.item_id) for ri in ri_rows]
        items_map = await TaskLoadingRecordService._load_items_map(
            db, int(rec.task_id), item_ids, lock=False,
        )

        # 校验：撤销不能跨过更晚的记录（即对该 item 不能有后续装/卸事件）
        # 简化策略：当前 item.status 必须 == 撤销前事件目标态
        expected_status = 1 if event_type == 1 else 2
        for it in items_map.values():
            if int(it.status) != expected_status:
                raise BizException(
                    f"挂接行 #{it.id} 当前状态={int(it.status)} 与"
                    f"撤销目标不一致；请先撤销其后续事件"
                )

        for ri in ri_rows:
            it = items_map[int(ri.item_id)]
            await TaskWaybillItemService._switch_item_status(
                db, it, target_item_status,
            )
            ri.is_deleted = 1
        rec.is_deleted = 1
        await db.flush()

        # 回退聚合
        await TaskWaybillItemService._aggregate_load_status_from_items(db, task)
        await TaskWaybillItemService._aggregate_task_status_from_items(db, task)
        await WaybillStatusAggregator.aggregate_by_task(
            db, int(rec.task_id), allow_downgrade=True,
        )

    # ------------------------------------------------------------------
    # 单条详情
    # ------------------------------------------------------------------
    @staticmethod
    async def get_record_dump(
        db: AsyncSession, record_id: int,
    ) -> TaskLoadingRecordOut:
        r = await db.execute(
            select(TaskLoadingRecord).where(
                TaskLoadingRecord.id == record_id,
                TaskLoadingRecord.is_deleted == 0,
            )
        )
        rec = r.scalar_one_or_none()
        if not rec:
            raise BizException("装卸记录不存在")
        ri_r = await db.execute(
            select(TaskLoadingRecordItem).where(
                TaskLoadingRecordItem.record_id == rec.id,
                TaskLoadingRecordItem.is_deleted == 0,
            )
        )
        ri_rows = list(ri_r.scalars().all())
        item_ids = sorted({int(ri.item_id) for ri in ri_rows})
        items_map: dict[int, TaskWaybillItem] = {}
        if item_ids:
            it_r = await db.execute(
                select(TaskWaybillItem).where(TaskWaybillItem.id.in_(item_ids))
            )
            items_map = {int(it.id): it for it in it_r.scalars().all()}
        children = [
            TaskLoadingRecordItemOut.from_models(ri, items_map.get(int(ri.item_id)))
            for ri in ri_rows
        ]
        return TaskLoadingRecordOut.from_model(rec, items=children)

    # ------------------------------------------------------------------
    # 内部辅助
    # ------------------------------------------------------------------
    @staticmethod
    async def _load_or_raise(db: AsyncSession, task_id: int) -> Task:
        r = await db.execute(
            select(Task).where(Task.id == task_id, Task.is_deleted == 0)
        )
        task = r.scalar_one_or_none()
        if not task:
            raise BizException("任务单不存在")
        return task

    @staticmethod
    async def _validate_dispatch_order(
        db: AsyncSession, task: Task, dispatch_order_id: Optional[int],
    ) -> None:
        if dispatch_order_id is None:
            # 多调令任务必填
            r = await db.execute(
                select(TaskDispatchOrder.id).where(
                    TaskDispatchOrder.task_id == task.id,
                    TaskDispatchOrder.is_deleted == 0,
                )
            )
            count = len(r.all())
            if count > 1:
                raise BizException("多调令任务必须指定 dispatch_order_id")
            return
        r = await db.execute(
            select(TaskDispatchOrder).where(
                TaskDispatchOrder.id == dispatch_order_id,
                TaskDispatchOrder.task_id == task.id,
                TaskDispatchOrder.is_deleted == 0,
            )
        )
        if r.scalar_one_or_none() is None:
            raise BizException(
                f"调令 {dispatch_order_id} 不属于任务 #{task.id}"
            )

    @staticmethod
    async def _load_items_map(
        db: AsyncSession,
        task_id: int,
        item_ids: Iterable[int],
        *,
        lock: bool = True,
    ) -> dict[int, TaskWaybillItem]:
        ids = sorted({int(i) for i in item_ids})
        if not ids:
            raise BizException("装卸记录至少包含一行 item")
        stmt = select(TaskWaybillItem).where(
            TaskWaybillItem.id.in_(ids),
            TaskWaybillItem.task_id == task_id,
            TaskWaybillItem.is_deleted == 0,
        )
        if lock:
            stmt = stmt.with_for_update()
        r = await db.execute(stmt)
        rows = list(r.scalars().all())
        if len(rows) != len(ids):
            raise BizException("部分挂接行不存在或已删除")
        return {int(it.id): it for it in rows}
