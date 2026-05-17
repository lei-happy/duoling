"""
运输任务单 Service

职责：
1. 任务单主表 CRUD
2. 分段子表的创建/替换
3. 派车（设置承运方信息 + 冷冻快照）
4. 状态推进（含合法状态机校验）
5. 取消任务单（自动释放 cargo 台数）
6. 任务单号生成
"""

from datetime import datetime, time as dtime, date as ddate
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_segment import TaskSegment
from app.modules.client.schemas.task.task import (
    TaskAssignCarrierRequest,
    TaskCarrierInfo,
    TaskCreate,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.modules.client.schemas.task.task_segment import TaskSegmentIn
from app.modules.client.services.system_config_service import SystemConfigService
from app.modules.client.services.task.task_code_name_generator import (
    build_task_name,
    build_task_no,
    legacy_default_task_name,
)
from app.modules.client.services.task.task_waybill_item_service import (
    TaskWaybillItemService,
)


# 任务单状态机：合法跳转表
_VALID_STATUS_TRANS = {
    0: {1, 9},        # 待派车 → 已派车 / 已取消
    1: {0, 2, 9},     # 已派车 → 回退待派车 / 已装车 / 已取消
    2: {3, 9},        # 已装车 → 在途 / 已取消
    3: {4},           # 在途 → 已到达
    4: {5},           # 已到达 → 已签收
    5: {6, 7},        # 已签收 → 已结算 / 已关闭
    6: {7},           # 已结算 → 已关闭
    7: set(),
    9: set(),
}


# 状态 → 中文名（用于错误信息可读性）
_STATUS_LABELS = {
    0: "待派车", 1: "已派车", 2: "已装车", 3: "在途",
    4: "已到达", 5: "已签收", 6: "已结算", 7: "已关闭", 9: "已取消",
}


class TaskService:

    # ------------------------------------------------------------------
    # 公共：单号生成与唯一性
    # ------------------------------------------------------------------
    @staticmethod
    async def generate_task_no(db: AsyncSession) -> str:
        """按系统配置 task.no_gen_rule 生成；缺省或无效时回退 T+日期+序号"""
        raw = await SystemConfigService.get_by_key(db, "task.no_gen_rule")
        return await build_task_no(db, raw)

    @staticmethod
    def default_task_name_for_create(data: TaskCreate) -> str:
        """未配置或同步场景下的默认名称（历史逻辑）"""
        return legacy_default_task_name(data)

    @staticmethod
    async def task_no_exists(
        db: AsyncSession, task_no: str, exclude_id: Optional[int] = None,
    ) -> bool:
        stmt = select(Task.id).where(
            Task.task_no == task_no, Task.is_deleted == 0,
        )
        if exclude_id is not None:
            stmt = stmt.where(Task.id != exclude_id)
        r = await db.execute(stmt.limit(1))
        return r.scalar_one_or_none() is not None

    @staticmethod
    async def get_or_404(db: AsyncSession, task_id: int) -> Task:
        r = await db.execute(
            select(Task).where(
                Task.id == task_id, Task.is_deleted == 0,
            )
        )
        t = r.scalar_one_or_none()
        if not t:
            raise BizException("任务单不存在")
        return t

    # ------------------------------------------------------------------
    # 承运方快照解析
    # ------------------------------------------------------------------
    @staticmethod
    async def _resolve_carrier_snapshot(
        db: AsyncSession,
        carrier_info: TaskCarrierInfo,
    ) -> dict:
        """根据 carrier_type 取上游表的关键字段，填充冷冻快照。
        前端如果手动填了快照字段，以快照字段优先（仅当未填时才回填）。
        """
        snapshot = {
            "carrier_type": carrier_info.carrierType,
            "capacity_id": None,
            "carrier_id": None,
            "social_driver_id": carrier_info.socialDriverId,
            "main_driver_name": carrier_info.mainDriverName,
            "main_driver_phone": carrier_info.mainDriverPhone,
            "main_driver_id_card": carrier_info.mainDriverIdCard,
            "plate_number": carrier_info.plateNumber,
            "trailer_plate_number": carrier_info.trailerPlateNumber,
            "carrier_name": carrier_info.carrierName,
            "carrier_short_name": carrier_info.carrierShortName,
        }

        if carrier_info.carrierType == 1:
            if carrier_info.capacityId:
                cap_res = await db.execute(
                    select(Capacity).where(
                        Capacity.id == carrier_info.capacityId,
                        Capacity.is_deleted == 0,
                    )
                )
                cap = cap_res.scalar_one_or_none()
                if not cap:
                    raise BizException(
                        f"运力不存在 (id={carrier_info.capacityId})"
                    )
                snapshot["capacity_id"] = cap.id
                if not snapshot["main_driver_name"]:
                    snapshot["main_driver_name"] = cap.driver_name
                if not snapshot["main_driver_phone"]:
                    snapshot["main_driver_phone"] = cap.driver_phone
                if not snapshot["plate_number"]:
                    snapshot["plate_number"] = cap.plate_number

        elif carrier_info.carrierType == 2:
            if carrier_info.carrierId:
                car_res = await db.execute(
                    select(Carrier).where(
                        Carrier.id == carrier_info.carrierId,
                        Carrier.is_deleted == 0,
                    )
                )
                car = car_res.scalar_one_or_none()
                if not car:
                    raise BizException(
                        f"承运商不存在 (id={carrier_info.carrierId})"
                    )
                snapshot["carrier_id"] = car.id
                if not snapshot["carrier_name"]:
                    snapshot["carrier_name"] = car.carrier_name
                if not snapshot["carrier_short_name"]:
                    snapshot["carrier_short_name"] = car.short_name

        # 社会运力：完全依赖前端传入的快照字段（已在 Schema 校验必填）
        return snapshot

    # ------------------------------------------------------------------
    # 分段
    # ------------------------------------------------------------------
    @staticmethod
    async def _replace_segments(
        db: AsyncSession,
        task: Task,
        segments_in: List[TaskSegmentIn],
    ) -> List[TaskSegment]:
        # 软删现有
        old = await TaskService.list_segments(db, task.id)
        for s in old:
            s.is_deleted = 1
        await db.flush()

        ordered = sorted(segments_in, key=lambda x: x.segmentNo)
        rows: List[TaskSegment] = []
        for s in ordered:
            row = TaskSegment(
                task_id=task.id,
                segment_no=s.segmentNo,
                from_location=s.fromLocation,
                from_code=s.fromCode,
                from_region_id=s.fromRegionId,
                to_location=s.toLocation,
                to_code=s.toCode,
                to_region_id=s.toRegionId,
                mileage=s.mileage,
                planned_load_time=s.plannedLoadTime,
                planned_arrive_time=s.plannedArriveTime,
                status=0,
                remark=s.remark,
            )
            db.add(row)
            rows.append(row)
        await db.flush()

        # 主表线路冗余 + 段数
        task.segment_count = len(rows)
        if rows:
            head = rows[0]
            tail = rows[-1]
            task.origin = head.from_location
            task.origin_code = head.from_code
            task.origin_region_id = head.from_region_id
            task.destination = tail.to_location
            task.destination_code = tail.to_code
            task.destination_region_id = tail.to_region_id
            if not task.planned_load_time:
                task.planned_load_time = head.planned_load_time
            if not task.planned_arrive_time:
                task.planned_arrive_time = tail.planned_arrive_time
        await db.flush()
        return rows

    @staticmethod
    async def list_segments(
        db: AsyncSession, task_id: int
    ) -> List[TaskSegment]:
        r = await db.execute(
            select(TaskSegment).where(
                TaskSegment.task_id == task_id,
                TaskSegment.is_deleted == 0,
            ).order_by(TaskSegment.segment_no.asc())
        )
        return list(r.scalars().all())

    @staticmethod
    async def update_segment_status(
        db: AsyncSession,
        seg_id: int,
        status: int,
        actual_load_time: Optional[datetime] = None,
        actual_arrive_time: Optional[datetime] = None,
        remark: Optional[str] = None,
    ) -> TaskSegment:
        if status not in (0, 1, 2, 3, 4):
            raise BizException(f"非法段状态 {status}")
        r = await db.execute(
            select(TaskSegment).where(
                TaskSegment.id == seg_id, TaskSegment.is_deleted == 0,
            )
        )
        seg = r.scalar_one_or_none()
        if not seg:
            raise BizException("分段不存在")
        seg.status = status
        if actual_load_time is not None:
            seg.actual_load_time = actual_load_time
        if actual_arrive_time is not None:
            seg.actual_arrive_time = actual_arrive_time
        if remark is not None:
            seg.remark = remark
        await db.flush()
        return seg

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @staticmethod
    async def create_task(
        db: AsyncSession,
        data: TaskCreate,
        current_user_id: Optional[int] = None,
        dispatcher_name: Optional[str] = None,
    ) -> Task:
        # 1. 任务单号
        task_no = (data.taskNo or "").strip()
        if not task_no:
            raw_no = await SystemConfigService.get_by_key(db, "task.no_gen_rule")
            task_no = await build_task_no(db, raw_no)
        else:
            if await TaskService.task_no_exists(db, task_no):
                raise BizException(f"任务单号 {task_no} 已存在")

        task_name_in = (data.taskName or "").strip()
        if not task_name_in:
            raw_name = await SystemConfigService.get_by_key(db, "task.name_gen_rule")
            task_name_in = await build_task_name(db, data, raw_name)

        # 2. 创建主表（先空承运方）
        task = Task(
            task_no=task_no,
            task_name=task_name_in or None,
            source=int(data.source or 1),
            planned_load_time=data.plannedLoadTime,
            planned_arrive_time=data.plannedArriveTime,
            carrier_cost_amount=data.carrierCostAmount,
            carrier_cost_type=data.carrierCostType,
            cost_remark=data.costRemark,
            status=0,
            dispatcher_id=current_user_id,
            dispatcher_name=dispatcher_name,
            remark=data.remark,
            carrier_type=1,  # 占位，下面 carrier 字段会覆盖
        )

        # 3. 承运方快照
        if data.carrier is not None:
            snap = await TaskService._resolve_carrier_snapshot(db, data.carrier)
            for k, v in snap.items():
                setattr(task, k, v)
            task.status = 1  # 已派车
        else:
            task.carrier_type = 1  # 默认自有车占位

        db.add(task)
        await db.flush()

        # 4. 分段
        await TaskService._replace_segments(db, task, data.segments)

        # 5. 货物挂接
        await TaskWaybillItemService.add_items(db, task, data.waybillItems)

        await db.refresh(task)
        return task

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: int,
        data: TaskUpdate,
        current_user_id: Optional[int] = None,
    ) -> Task:
        task = await TaskService.get_or_404(db, task_id)
        if int(task.status) not in (0, 1):
            raise BizException(
                f"任务单当前状态「{_STATUS_LABELS.get(task.status, task.status)}」"
                f"不允许编辑（仅待派车/已派车可编辑）"
            )

        if data.taskName is not None:
            task.task_name = data.taskName or None
        if data.plannedLoadTime is not None:
            task.planned_load_time = data.plannedLoadTime
        if data.plannedArriveTime is not None:
            task.planned_arrive_time = data.plannedArriveTime
        if data.carrierCostType is not None:
            task.carrier_cost_type = data.carrierCostType
        if data.carrierCostAmount is not None:
            task.carrier_cost_amount = data.carrierCostAmount
        if data.costRemark is not None:
            task.cost_remark = data.costRemark
        if data.remark is not None:
            task.remark = data.remark

        if data.carrier is not None:
            snap = await TaskService._resolve_carrier_snapshot(db, data.carrier)
            for k, v in snap.items():
                setattr(task, k, v)
            if int(task.status) == 0:
                task.status = 1

        if data.segments is not None:
            if len(data.segments) < 1:
                raise BizException("至少需要 1 段运输")
            nos = [s.segmentNo for s in data.segments]
            if sorted(nos) != list(range(1, len(nos) + 1)):
                raise BizException("段序号必须从 1 开始连续")
            await TaskService._replace_segments(db, task, data.segments)

        if data.waybillItems is not None:
            if len(data.waybillItems) < 1:
                raise BizException("至少需要 1 条货物挂接")
            await TaskWaybillItemService.replace_items(
                db, task, data.waybillItems
            )

        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> None:
        task = await TaskService.get_or_404(db, task_id)
        if int(task.status) not in (0, 9):
            raise BizException("仅「待派车/已取消」状态的任务单允许删除")

        # 软删段
        for s in await TaskService.list_segments(db, task_id):
            s.is_deleted = 1

        # 释放并软删挂接
        await TaskWaybillItemService.release_all_items_of_task(db, task)

        task.is_deleted = 1
        await db.flush()

    @staticmethod
    async def cancel_task(
        db: AsyncSession,
        task_id: int,
        reason: Optional[str] = None,
    ) -> Task:
        task = await TaskService.get_or_404(db, task_id)
        if int(task.status) not in (0, 1, 2):
            raise BizException(
                f"任务单状态「{_STATUS_LABELS.get(task.status)}」不允许取消"
            )
        task.status = 9
        if reason:
            existing = (task.remark or "").rstrip()
            task.remark = (existing + "\n" if existing else "") + f"[取消原因] {reason}"
        await TaskWaybillItemService.release_all_items_of_task(db, task)
        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def update_status(
        db: AsyncSession,
        task_id: int,
        data: TaskStatusUpdate,
    ) -> Task:
        task = await TaskService.get_or_404(db, task_id)
        old = int(task.status)
        new = int(data.status)
        valid = _VALID_STATUS_TRANS.get(old, set())
        if new not in valid:
            raise BizException(
                f"状态从「{_STATUS_LABELS.get(old)}」"
                f"不能直接跳转到「{_STATUS_LABELS.get(new, new)}」"
            )
        task.status = new
        if data.actualLoadTime is not None and new in (2, 3):
            task.actual_load_time = data.actualLoadTime
        if data.actualArriveTime is not None and new in (4, 5):
            task.actual_arrive_time = data.actualArriveTime
        if data.remark:
            existing = (task.remark or "").rstrip()
            task.remark = (existing + "\n" if existing else "") + data.remark
        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def assign_carrier(
        db: AsyncSession,
        task_id: int,
        data: TaskAssignCarrierRequest,
    ) -> Task:
        task = await TaskService.get_or_404(db, task_id)
        if int(task.status) not in (0, 1):
            raise BizException("仅「待派车/已派车」状态可重新派车")
        snap = await TaskService._resolve_carrier_snapshot(db, data.carrier)
        for k, v in snap.items():
            setattr(task, k, v)
        if data.carrierCostType is not None:
            task.carrier_cost_type = data.carrierCostType
        if data.carrierCostAmount is not None:
            task.carrier_cost_amount = data.carrierCostAmount
        if data.costRemark is not None:
            task.cost_remark = data.costRemark
        if int(task.status) == 0:
            task.status = 1
        await db.flush()
        await db.refresh(task)
        return task

    # ------------------------------------------------------------------
    # 列表与详情
    # ------------------------------------------------------------------
    @staticmethod
    async def page_tasks(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        carrier_type: Optional[int] = None,
        status: Optional[int] = None,
        customer_id: Optional[int] = None,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
        created_at_start: Optional[ddate] = None,
        created_at_end: Optional[ddate] = None,
    ) -> Tuple[List[Task], int]:
        base = select(Task).where(Task.is_deleted == 0)
        cnt = select(func.count(Task.id)).where(Task.is_deleted == 0)

        if keyword:
            kw = f"%{keyword.strip()}%"
            cond = or_(
                Task.task_no.like(kw),
                Task.task_name.like(kw),
                Task.main_driver_name.like(kw),
                Task.plate_number.like(kw),
                Task.carrier_name.like(kw),
            )
            base = base.where(cond)
            cnt = cnt.where(cond)
        if carrier_type is not None:
            base = base.where(Task.carrier_type == carrier_type)
            cnt = cnt.where(Task.carrier_type == carrier_type)
        if status is not None:
            base = base.where(Task.status == status)
            cnt = cnt.where(Task.status == status)
        if origin_keyword:
            kw = f"%{origin_keyword.strip()}%"
            base = base.where(Task.origin.like(kw))
            cnt = cnt.where(Task.origin.like(kw))
        if destination_keyword:
            kw = f"%{destination_keyword.strip()}%"
            base = base.where(Task.destination.like(kw))
            cnt = cnt.where(Task.destination.like(kw))
        if created_at_start is not None:
            start_dt = datetime.combine(created_at_start, dtime.min)
            base = base.where(Task.created_at >= start_dt)
            cnt = cnt.where(Task.created_at >= start_dt)
        if created_at_end is not None:
            end_dt = datetime.combine(created_at_end, dtime.max)
            base = base.where(Task.created_at <= end_dt)
            cnt = cnt.where(Task.created_at <= end_dt)
        # customer_id 走挂接表，避免再多 join，使用 EXISTS
        if customer_id is not None:
            from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
            sub = select(TaskWaybillItem.task_id).where(
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.customer_id == customer_id,
            )
            base = base.where(Task.id.in_(sub))
            cnt = cnt.where(Task.id.in_(sub))

        total = int((await db.execute(cnt)).scalar() or 0)
        offset = max(0, (page - 1) * page_size)
        items_r = await db.execute(
            base.order_by(Task.created_at.desc(), Task.id.desc())
            .offset(offset).limit(page_size)
        )
        return list(items_r.scalars().all()), total

    @staticmethod
    async def check_task_no(
        db: AsyncSession,
        task_no: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        """返回 True = 可用（未被占用）"""
        return not (await TaskService.task_no_exists(db, task_no, exclude_id))

    # ------------------------------------------------------------------
    # 工作台聚合 + 批量操作
    # ------------------------------------------------------------------
    @staticmethod
    async def workbench_stats(db: AsyncSession) -> dict:
        """返回各状态计数 + 关键异常计数（用于调度工作台 KPI）"""
        # 各状态计数
        r = await db.execute(
            select(Task.status, func.count(Task.id))
            .where(Task.is_deleted == 0)
            .group_by(Task.status)
        )
        status_counts: dict[int, int] = {int(s): int(c) for s, c in r.all()}

        # 异常：计划装车时间已过但 status<1（待派车逾期）
        now = datetime.now()
        r_overdue_dispatch = await db.execute(
            select(func.count(Task.id)).where(
                Task.is_deleted == 0,
                Task.status == 0,
                Task.planned_load_time.isnot(None),
                Task.planned_load_time < now,
            )
        )
        overdue_dispatch = int(r_overdue_dispatch.scalar() or 0)

        # 异常：计划到达时间已过但 status<4（在途逾期未到达）
        r_overdue_arrive = await db.execute(
            select(func.count(Task.id)).where(
                Task.is_deleted == 0,
                Task.status.in_([2, 3]),
                Task.planned_arrive_time.isnot(None),
                Task.planned_arrive_time < now,
            )
        )
        overdue_arrive = int(r_overdue_arrive.scalar() or 0)

        return {
            "statusCounts": status_counts,
            "totals": {
                "pendingDispatch": status_counts.get(0, 0),
                "pendingLoad": status_counts.get(1, 0),
                "loading": status_counts.get(2, 0),
                "onWay": status_counts.get(3, 0),
                "arrived": status_counts.get(4, 0),
                "pendingSign": status_counts.get(4, 0),
                "signed": status_counts.get(5, 0),
                "pendingSettle": status_counts.get(5, 0),
                "settled": status_counts.get(6, 0),
                "closed": status_counts.get(7, 0),
                "cancelled": status_counts.get(9, 0),
            },
            "alerts": {
                "overdueDispatch": overdue_dispatch,
                "overdueArrive": overdue_arrive,
            },
        }

    @staticmethod
    async def batch_update_status(
        db: AsyncSession,
        ids: List[int],
        data: TaskStatusUpdate,
    ) -> dict:
        """批量推进状态。
        逐条复用 update_status；任一失败不阻塞其他，但收集失败原因返回。
        """
        if not ids:
            return {"success": 0, "failed": 0, "failures": []}
        success = 0
        failures: List[dict] = []
        for task_id in ids:
            try:
                await TaskService.update_status(db, int(task_id), data)
                success += 1
            except Exception as e:  # noqa: BLE001
                failures.append({"id": int(task_id), "error": str(e)})
        return {
            "success": success,
            "failed": len(failures),
            "failures": failures,
        }
