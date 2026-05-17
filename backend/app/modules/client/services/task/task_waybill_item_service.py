"""
任务单货物挂接 Service

核心职责：
1. 候选运单 cargo 行查询（剩余可分配台数 > 0）
2. 挂接 / 批量挂接 / 取消挂接 / 状态推进
3. cargo.allocated_quantity 的原子维护
4. 任务单 total_quantity / waybill_count 冗余聚合
"""

from typing import List, Optional

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.schemas.task.task_waybill_item import (
    CandidateCargoOut,
    TaskWaybillItemIn,
    TaskWaybillItemStatusUpdate,
)
from app.modules.client.schemas.waybill.waybill import waybill_brand_model_key
from app.modules.client.services.waybill.waybill_service import WaybillService

# 挂接行未完结的状态阈值：status < UNFINISHED_THRESHOLD 才占用台数
# 0-待装车 1-已装车 2-已卸车 都计入"占用"；3-已签收 视为已完成可释放
UNFINISHED_THRESHOLD = 3


class TaskWaybillItemService:

    # ------------------------------------------------------------------
    # 候选查询
    # ------------------------------------------------------------------
    @staticmethod
    async def list_candidate_cargoes(
        db: AsyncSession,
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
        limit: int = 200,
    ) -> List[CandidateCargoOut]:
        """挂接器左栏：返回剩余台数 > 0 的运单 cargo 行候选。

        发运准入：仅"已确认 / 已调度"的运单可被挂入新任务单。
        - 0 待确认：客户未确认，不允许发运；
        - 1 已确认：完全可发运；
        - 2 已调度：仍可挂接（前提是 cargo.remaining_quantity > 0，支持拆单分批）；
        - 3+ 运输中/已完成/已取消：不允许新挂接。
        """
        wb_q = select(Waybill).where(
            Waybill.is_deleted == 0,
            Waybill.status.in_([1, 2]),
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            wb_q = wb_q.where(or_(
                Waybill.waybill_no.like(kw),
                Waybill.customer_name.like(kw),
            ))
        if customer_id is not None:
            wb_q = wb_q.where(Waybill.customer_id == customer_id)
        if origin_keyword:
            wb_q = wb_q.where(Waybill.origin.like(f"%{origin_keyword.strip()}%"))
        if destination_keyword:
            wb_q = wb_q.where(
                Waybill.destination.like(f"%{destination_keyword.strip()}%")
            )

        wb_q = wb_q.order_by(Waybill.created_at.desc()).limit(limit * 2)
        wbs = list((await db.execute(wb_q)).scalars().all())
        if not wbs:
            return []
        wb_ids = [w.id for w in wbs]
        wb_map = {w.id: w for w in wbs}

        cg_q = select(WaybillCargo).where(
            WaybillCargo.is_deleted == 0,
            WaybillCargo.waybill_id.in_(wb_ids),
        ).order_by(WaybillCargo.waybill_id, WaybillCargo.sort_order)
        cargoes = list((await db.execute(cg_q)).scalars().all())

        series_lookup = await WaybillService._series_image_lookup_map(db)

        out: List[CandidateCargoOut] = []
        for c in cargoes:
            remaining = max(0, int(c.quantity) - int(c.allocated_quantity or 0))
            if remaining <= 0:
                continue
            w = wb_map.get(c.waybill_id)
            if w is None:
                continue
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
                waybillStatus=w.status,
                cargoId=c.id,
                vehicleBrand=c.vehicle_brand,
                vehicleModel=c.vehicle_model,
                seriesImage=series_image,
                quantity=int(c.quantity),
                allocatedQuantity=int(c.allocated_quantity or 0),
                remainingQuantity=remaining,
            ))
            if len(out) >= limit:
                break
        return out

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
            raise BizException(f"运单货物行不存在 (cargo_id={cargo_id})")
        new_allocated = int(cargo.allocated_quantity or 0) + delta
        if new_allocated < 0:
            new_allocated = 0
        if new_allocated > int(cargo.quantity):
            raise BizException(
                f"运单 {cargo.waybill_id} 货物行可分配台数不足："
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
        """从入参构建 TaskWaybillItem，含运单/货物冗余快照填充"""
        wb_res = await db.execute(
            select(Waybill).where(
                Waybill.id == in_data.waybillId,
                Waybill.is_deleted == 0,
            )
        )
        wb = wb_res.scalar_one_or_none()
        if not wb:
            raise BizException(f"运单不存在 (id={in_data.waybillId})")

        cg_res = await db.execute(
            select(WaybillCargo).where(
                WaybillCargo.id == in_data.waybillCargoId,
                WaybillCargo.is_deleted == 0,
            )
        )
        cargo = cg_res.scalar_one_or_none()
        if not cargo:
            raise BizException(f"运单货物行不存在 (id={in_data.waybillCargoId})")
        if cargo.waybill_id != wb.id:
            raise BizException("货物行不属于该运单")

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
            segment_id=in_data.segmentId,
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
        for it in items_in:
            await TaskWaybillItemService._bump_cargo_allocated(
                db, it.waybillCargoId, int(it.quantity)
            )
            row = await TaskWaybillItemService._build_item_snapshot(db, task, it)
            db.add(row)
            await db.flush()
            added.append(row)
        await TaskWaybillItemService._refresh_task_aggregates(db, task)
        return added

    @staticmethod
    async def replace_items(
        db: AsyncSession,
        task: Task,
        items_in: List[TaskWaybillItemIn],
    ) -> List[TaskWaybillItem]:
        """整单替换：先释放所有未签收的挂接，再批量挂接"""
        existing = await TaskWaybillItemService.list_items_of_task(db, task.id)
        for old in existing:
            if int(old.status) < UNFINISHED_THRESHOLD:
                await TaskWaybillItemService._bump_cargo_allocated(
                    db, old.waybill_cargo_id, -int(old.quantity)
                )
            old.is_deleted = 1
        await db.flush()
        return await TaskWaybillItemService.add_items(db, task, items_in)

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
            raise BizException("已签收的货物不可取消挂接")
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
        if new_status not in (0, 1, 2, 3):
            raise BizException(f"非法状态 {new_status}")

        # 从未完结进入"已签收"，释放占用
        if old_status < UNFINISHED_THRESHOLD <= new_status:
            await TaskWaybillItemService._bump_cargo_allocated(
                db, item.waybill_cargo_id, -int(item.quantity)
            )
        # 从"已签收"回退到未完结，重新占用
        if old_status >= UNFINISHED_THRESHOLD > new_status:
            await TaskWaybillItemService._bump_cargo_allocated(
                db, item.waybill_cargo_id, int(item.quantity)
            )

        item.status = new_status
        if data.loadedAt is not None:
            item.loaded_at = data.loadedAt
        if data.unloadedAt is not None:
            item.unloaded_at = data.unloadedAt
        if data.signedAt is not None:
            item.signed_at = data.signedAt
        if data.segmentId is not None:
            item.segment_id = data.segmentId
        if data.remark is not None:
            item.remark = data.remark
        await db.flush()
        return item

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
        """取消任务单时调用：释放所有未签收挂接占用的台数并软删"""
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        for it in items:
            if int(it.status) < UNFINISHED_THRESHOLD:
                await TaskWaybillItemService._bump_cargo_allocated(
                    db, it.waybill_cargo_id, -int(it.quantity)
                )
            it.is_deleted = 1
        await db.flush()
        await TaskWaybillItemService._refresh_task_aggregates(db, task)
