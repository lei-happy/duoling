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

from sqlalchemy import exists, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.models.route import Route
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_dispatch_order import TaskDispatchOrder
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.schemas.task.task import (
    TaskAssignCarrierRequest,
    TaskCarrierAssignmentInfo,
    TaskCarrierInfo,
    TaskCreate,
    TaskPlanRouteRequest,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.modules.client.schemas.task.task_dispatch_order import (
    TaskDispatchOrderIn,
)
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_STATUS_LABELS,
    TaskStateMachine,
)
from app.modules.client.services.system_config_service import SystemConfigService
from app.modules.client.services.task.task_code_name_generator import (
    build_task_name,
    build_task_no,
    legacy_default_task_name,
)
from app.modules.client.services.task.task_waybill_item_service import (
    TaskWaybillItemService,
)
from app.modules.client.services.waybill.waybill_status_aggregator import (
    WaybillStatusAggregator,
)


# 兼容旧引用（其它模块可能直接 import _STATUS_LABELS）
_STATUS_LABELS = TASK_STATUS_LABELS


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

    @staticmethod
    async def _resolve_carrier_assignment_snapshot(
        db: AsyncSession,
        data: TaskCarrierAssignmentInfo,
    ) -> dict:
        """待分配 → 待派车：写入承运方式及可得快照（自有车可不绑定具体运力）。"""
        ct = int(data.carrierType)
        if ct == 1 and not data.capacityId:
            return {
                "carrier_type": 1,
                "capacity_id": None,
                "carrier_id": None,
                "social_driver_id": None,
                "main_driver_name": None,
                "main_driver_phone": None,
                "main_driver_id_card": None,
                "plate_number": None,
                "trailer_plate_number": None,
                "carrier_name": None,
                "carrier_short_name": None,
            }
        info = TaskCarrierInfo(
            carrierType=data.carrierType,
            capacityId=data.capacityId,
            carrierId=data.carrierId,
            socialDriverId=data.socialDriverId,
            mainDriverName=data.mainDriverName,
            mainDriverPhone=data.mainDriverPhone,
            mainDriverIdCard=data.mainDriverIdCard,
            plateNumber=data.plateNumber,
            trailerPlateNumber=data.trailerPlateNumber,
            carrierName=data.carrierName,
            carrierShortName=data.carrierShortName,
        )
        return await TaskService._resolve_carrier_snapshot(db, info)

    # ------------------------------------------------------------------
    # 调令（原"分段"）
    # ------------------------------------------------------------------
    @staticmethod
    async def _replace_dispatch_orders(
        db: AsyncSession,
        task: Task,
        orders_in: List[TaskDispatchOrderIn],
    ) -> List[TaskDispatchOrder]:
        # 软删现有
        old = await TaskService.list_dispatch_orders(db, task.id)
        for s in old:
            s.is_deleted = 1
        await db.flush()

        ordered = sorted(orders_in, key=lambda x: x.orderNo)
        rows: List[TaskDispatchOrder] = []
        for s in ordered:
            row = TaskDispatchOrder(
                task_id=task.id,
                order_no=s.orderNo,
                dispatch_type=int(s.dispatchType or 1),
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

        # 主表线路冗余 + 调令数
        task.segment_count = len(rows)
        if rows:
            # 取首条"重驶"调令的起点 + 末条"重驶"调令的终点；若无重驶则用第一/最后
            heavy = [r for r in rows if int(r.dispatch_type or 1) == 1]
            head = heavy[0] if heavy else rows[0]
            tail = heavy[-1] if heavy else rows[-1]
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

    # 兼容旧调用方
    _replace_segments = _replace_dispatch_orders

    @staticmethod
    async def _fill_route_from_waybills(
        db: AsyncSession,
        task: Task,
    ) -> None:
        """零段任务的"线路兜底"：
        从已挂接 waybillItems 的运单聚合出 origin/destination 写入 task 主表，
        以便列表 / 详情 / 派车弹窗有"起→终"展示。

        策略：按挂接顺序（id 升序）取第一条运单的 origin / 最后一条的 destination；
        如运单缺失则保持原值（可能为空字符串）。
        """
        items_r = await db.execute(
            select(TaskWaybillItem.waybill_id)
            .where(
                TaskWaybillItem.task_id == task.id,
                TaskWaybillItem.is_deleted == 0,
            )
            .order_by(TaskWaybillItem.id.asc())
        )
        wb_ids = [int(i) for (i,) in items_r.all()]
        if not wb_ids:
            return

        # 去重保持顺序
        seen: set[int] = set()
        ordered_ids: List[int] = []
        for wid in wb_ids:
            if wid in seen:
                continue
            seen.add(wid)
            ordered_ids.append(wid)

        wb_res = await db.execute(
            select(Waybill).where(
                Waybill.id.in_(ordered_ids),
                Waybill.is_deleted == 0,
            )
        )
        wb_map = {w.id: w for w in wb_res.scalars().all()}
        ordered_wbs = [wb_map[i] for i in ordered_ids if i in wb_map]
        if not ordered_wbs:
            return

        head = ordered_wbs[0]
        tail = ordered_wbs[-1]
        if not task.origin:
            task.origin = head.origin
            task.origin_code = head.origin_code
            task.origin_region_id = head.origin_region_id
        if not task.destination:
            task.destination = tail.destination
            task.destination_code = tail.destination_code
            task.destination_region_id = tail.destination_region_id
        await db.flush()

    # ------------------------------------------------------------------
    # 路线规划（独立动作）
    # ------------------------------------------------------------------
    @staticmethod
    async def plan_route(
        db: AsyncSession,
        task_id: int,
        data: TaskPlanRouteRequest,
    ) -> Task:
        """补齐 / 重做任务单的分段路线。仅在「待分配 / 待派车 / 已派车 / 已装车」可用。"""
        task = await TaskService.get_or_404(db, task_id)
        if int(task.status) not in (-1, 0, 1, 2):
            raise BizException(
                f"任务单当前状态「{_STATUS_LABELS.get(task.status, task.status)}」"
                f"不允许调整路线（仅待分配/待派车/已派车/已装车可规划）"
            )
        await TaskService._replace_dispatch_orders(db, task, data.segments)
        await db.refresh(task)
        return task

    # ------------------------------------------------------------------
    # 里程联想（按起终地区匹配 biz_route）
    # ------------------------------------------------------------------
    @staticmethod
    async def lookup_route_distance(
        db: AsyncSession,
        origin_region_id: int,
        destination_region_id: int,
    ) -> Optional[dict]:
        """根据起终行政区匹配已维护的线路，返回 {routeId, routeName, distance, estimatedHours}。
        命中多条时取最新一条（created_at 倒序）；未命中返回 None。
        """
        r = await db.execute(
            select(Route)
            .where(
                Route.is_deleted == 0,
                Route.status == 1,
                Route.origin_region_id == origin_region_id,
                Route.destination_region_id == destination_region_id,
            )
            .order_by(Route.created_at.desc())
            .limit(1)
        )
        route = r.scalar_one_or_none()
        if not route:
            return None
        return {
            "routeId": route.id,
            "routeName": route.route_name,
            "origin": route.origin,
            "destination": route.destination,
            "distance": (
                float(route.distance) if route.distance is not None else None
            ),
            "estimatedHours": (
                float(route.estimated_hours)
                if route.estimated_hours is not None else None
            ),
        }

    @staticmethod
    async def list_dispatch_orders(
        db: AsyncSession, task_id: int
    ) -> List[TaskDispatchOrder]:
        r = await db.execute(
            select(TaskDispatchOrder).where(
                TaskDispatchOrder.task_id == task_id,
                TaskDispatchOrder.is_deleted == 0,
            ).order_by(TaskDispatchOrder.order_no.asc())
        )
        return list(r.scalars().all())

    # 兼容旧调用方（API 路径仍可能使用 list_segments）
    list_segments = list_dispatch_orders

    @staticmethod
    async def update_dispatch_order_status(
        db: AsyncSession,
        order_id: int,
        status: int,
        actual_load_time: Optional[datetime] = None,
        actual_arrive_time: Optional[datetime] = None,
        remark: Optional[str] = None,
    ) -> TaskDispatchOrder:
        if status not in (0, 1, 2, 3, 4):
            raise BizException(f"非法调令状态 {status}")
        r = await db.execute(
            select(TaskDispatchOrder).where(
                TaskDispatchOrder.id == order_id,
                TaskDispatchOrder.is_deleted == 0,
            )
        )
        seg = r.scalar_one_or_none()
        if not seg:
            raise BizException("调令不存在")
        seg.status = status
        if actual_load_time is not None:
            seg.actual_load_time = actual_load_time
        if actual_arrive_time is not None:
            seg.actual_arrive_time = actual_arrive_time
        if remark is not None:
            seg.remark = remark
        await db.flush()
        return seg

    update_segment_status = update_dispatch_order_status

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
        user_supplied_no = bool((data.taskNo or "").strip())
        task_no = (data.taskNo or "").strip()
        if user_supplied_no:
            if await TaskService.task_no_exists(db, task_no):
                raise BizException(f"任务单号 {task_no} 已存在")
        else:
            raw_no = await SystemConfigService.get_by_key(db, "task.no_gen_rule")
            task_no = await build_task_no(db, raw_no)

        task_name_in = (data.taskName or "").strip()
        if not task_name_in:
            raw_name = await SystemConfigService.get_by_key(db, "task.name_gen_rule")
            task_name_in = await build_task_name(db, data, raw_name)

        # 2. 创建主表（先空承运方）
        # 用户未手填单号时，加入重试：极端并发或软删占位场景下，
        # 即便生成器算出的序号在查询时未冲突，也可能在 INSERT 瞬间被抢占。
        max_retries = 5 if not user_supplied_no else 1
        last_err: Optional[IntegrityError] = None
        task: Optional[Task] = None
        for attempt in range(max_retries):
            task = Task(
                task_no=task_no,
                task_name=task_name_in or None,
                source=int(data.source or 1),
                planned_load_time=data.plannedLoadTime,
                planned_arrive_time=data.plannedArriveTime,
                carrier_cost_amount=data.carrierCostAmount,
                carrier_cost_type=data.carrierCostType,
                cost_remark=data.costRemark,
                status=-1,
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
            try:
                await db.flush()
                last_err = None
                break
            except IntegrityError as e:
                last_err = e
                await db.rollback()
                if user_supplied_no:
                    raise BizException(f"任务单号 {task_no} 已存在") from e
                # 仅在 task_no UNIQUE 冲突时重试；其它完整性问题原样抛出
                msg = str(getattr(e, "orig", e)).lower()
                if "task_no" not in msg and "duplicate entry" not in msg:
                    raise
                # 重新生成单号
                raw_no = await SystemConfigService.get_by_key(db, "task.no_gen_rule")
                task_no = await build_task_no(db, raw_no)
        if last_err is not None or task is None:
            assert last_err is not None
            raise BizException("任务单号生成冲突，请重试") from last_err

        # 4. 调令（允许为空：表示"配载草稿"，由 _fill_route_from_waybills 兜底起终）
        await TaskService._replace_dispatch_orders(db, task, data.segments)

        # 5. 货物挂接
        await TaskWaybillItemService.add_items(db, task, data.waybillItems)

        # 6. 若无分段，根据已挂接的运单聚合 origin/destination
        if not data.segments:
            await TaskService._fill_route_from_waybills(db, task)

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
        if int(task.status) not in (-1, 0, 1):
            raise BizException(
                f"任务单当前状态「{_STATUS_LABELS.get(task.status, task.status)}」"
                f"不允许编辑（仅待分配/待派车/已派车可编辑）"
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
            if data.segments:
                nos = [s.orderNo for s in data.segments]
                if sorted(nos) != list(range(1, len(nos) + 1)):
                    raise BizException("调令序号必须从 1 开始连续")
            await TaskService._replace_dispatch_orders(db, task, data.segments)

        if data.waybillItems is not None:
            if len(data.waybillItems) < 1:
                raise BizException("至少需要 1 条货物挂接")
            await TaskWaybillItemService.replace_items(
                db, task, data.waybillItems
            )
            # 若当前任务没有有效分段，用最新挂接的运单回填起终地
            if int(task.segment_count or 0) == 0:
                await TaskService._fill_route_from_waybills(db, task)

        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def delete_task(db: AsyncSession, task_id: int) -> None:
        task = await TaskService.get_or_404(db, task_id)
        if int(task.status) not in (-1, 0, 9):
            raise BizException("仅「待分配/待派车/已取消」状态的任务单允许删除")

        # 软删调令
        for s in await TaskService.list_dispatch_orders(db, task_id):
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
        TaskStateMachine.assert_cancellable(int(task.status))
        task.status = 9
        if reason:
            existing = (task.remark or "").rstrip()
            task.remark = (existing + "\n" if existing else "") + f"[取消原因] {reason}"
        # 释放挂接并联动运单聚合（release 内部已带 aggregator）
        await TaskWaybillItemService.release_all_items_of_task(db, task)
        # 联动撤销所有未支付的费用单（已支付走单独撤销链路）
        from app.modules.client.services.task.task_finance_service import (
            TaskFinanceService,
        )
        await TaskFinanceService.cancel_all_unpaid_docs(
            db, task.id, reason or "任务单被取消",
        )
        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def force_cancel(
        db: AsyncSession,
        task_id: int,
        reason: str,
        current_user_id: Optional[int] = None,
        cancel_unpaid_finance_docs: bool = True,
    ) -> Task:
        """强制取消（线下取消）。

        允许从 ``2/3/4`` 直接进入 ``9``；保留挂接记录但置 item.status=9。
        ``cancel_unpaid_finance_docs=True`` 时，未支付费用单一并撤销。
        """
        if not reason or not reason.strip():
            raise BizException("强制取消必须填写原因")
        task = await TaskService.get_or_404(db, task_id)
        old = int(task.status)
        TaskStateMachine.assert_force_cancellable(old)

        task.status = 9
        existing = (task.remark or "").rstrip()
        actor = f"#{current_user_id}" if current_user_id else "system"
        task.remark = (
            (existing + "\n" if existing else "")
            + f"[强制取消 {TASK_STATUS_LABELS.get(old)} → 已取消]"
            + f" by {actor}：{reason.strip()}"
        )
        await db.flush()

        # 推所有 item 到 9，并释放台数（保留挂接记录，便于追溯）
        await TaskWaybillItemService.propagate_cancel_to_items(db, task)
        await TaskWaybillItemService._refresh_task_aggregates(db, task)
        # 联动撤销所有未支付费用单
        if cancel_unpaid_finance_docs:
            from app.modules.client.services.task.task_finance_service import (
                TaskFinanceService,
            )
            await TaskFinanceService.cancel_all_unpaid_docs(
                db, task.id, reason.strip(),
            )
        await WaybillStatusAggregator.aggregate_by_task(
            db, task.id, allow_downgrade=True,
        )

        await db.refresh(task)
        return task

    @staticmethod
    async def update_status(
        db: AsyncSession,
        task_id: int,
        data: TaskStatusUpdate,
    ) -> Task:
        """状态推进的人工入口。

        合法路径仅有：0→1（派车）/ 1→0（撤回派车）/ 2→3（出发）/ 5→7（关闭）/ ?→9（取消）。
        1→2（已装车）与 3→4（已到达）已下沉为聚合态：
        - 调度员通过 ``POST /loading-records`` 添加装/卸车事件，
          由 ``TaskWaybillItemService._aggregate_load_status_from_items`` 自动写入。
        - 调用 ``update_status(task, status=2)`` / ``update_status(task, status=4)``
          会被 ``TaskStateMachine.assert_transition`` 直接拒绝。
        """
        task = await TaskService.get_or_404(db, task_id)
        old = int(task.status)
        new = int(data.status)
        TaskStateMachine.assert_transition(old, new)

        task.status = new
        if data.actualLoadTime is not None and new == 3:
            # 出发动作携带的"实际装车时间"用于补录历史装车数据兜底；
            # 正常流程已由装车记录写入。
            task.actual_load_time = data.actualLoadTime
        if data.remark:
            existing = (task.remark or "").rstrip()
            task.remark = (existing + "\n" if existing else "") + data.remark
        await db.flush()

        # 正向推进：Task → Item 同步 → 聚合 Waybill
        # - 4→5（已签收）由 item 全签收聚合自动写入，不在此处理
        # - 1→2 / 3→4 已经被 assert_transition 拦截，不会到这里
        if new == 9:
            # 走 cancel 路径不应进到这里；保底兜底
            await TaskWaybillItemService.release_all_items_of_task(db, task)
        else:
            await TaskWaybillItemService.propagate_to_items(
                db, task,
                loaded_at=data.actualLoadTime if new == 3 else None,
                unloaded_at=None,
                signed_at=None,
            )
            await WaybillStatusAggregator.aggregate_by_task(
                db, task.id, allow_downgrade=False,
            )

        await db.refresh(task)
        return task

    # ------------------------------------------------------------------
    # 反向流程
    # ------------------------------------------------------------------
    @staticmethod
    async def revert_status(
        db: AsyncSession,
        task_id: int,
        target_status: int,
        reason: str,
        current_user_id: Optional[int] = None,
    ) -> Task:
        """撤销至上一态（专项接口）。

        - 校验：``TaskStateMachine.assert_revert``
        - 联动：Item 同步反向 → Waybill 聚合（允许 downgrade）
        - 审计：必填 reason，写入 task.remark
        """
        if not reason or not reason.strip():
            raise BizException("撤销操作必须填写原因")
        task = await TaskService.get_or_404(db, task_id)
        old = int(task.status)
        target = int(target_status)
        TaskStateMachine.assert_revert(old, target)

        task.status = target
        existing = (task.remark or "").rstrip()
        actor = f"#{current_user_id}" if current_user_id else "system"
        task.remark = (
            (existing + "\n" if existing else "")
            + f"[撤销 {TASK_STATUS_LABELS.get(old)} → {TASK_STATUS_LABELS.get(target)}]"
            + f" by {actor}：{reason.strip()}"
        )
        await db.flush()

        # 反向同步 Item：只降不升；时间字段不清除
        await TaskWaybillItemService.propagate_revert_to_items(db, task)
        await WaybillStatusAggregator.aggregate_by_task(
            db, task.id, allow_downgrade=True,
        )

        await db.refresh(task)
        return task

    @staticmethod
    async def complete_carrier_assignment(
        db: AsyncSession,
        task_id: int,
        data: TaskCarrierAssignmentInfo,
    ) -> Task:
        """待分配：确认承运方式后进入待派车（status=0）。"""
        task = await TaskService.get_or_404(db, task_id)
        if int(task.status) != -1:
            raise BizException(
                "仅「待分配」状态可确认承运方分配；当前："
                f"{_STATUS_LABELS.get(int(task.status), task.status)}"
            )
        snap = await TaskService._resolve_carrier_assignment_snapshot(db, data)
        for k, v in snap.items():
            setattr(task, k, v)
        task.status = 0
        await db.flush()
        await db.refresh(task)
        return task

    @staticmethod
    async def batch_complete_carrier_assignment(
        db: AsyncSession,
        ids: List[int],
        data: TaskCarrierAssignmentInfo,
    ) -> dict:
        """批量待分配 → 待派车：逐条复用 complete_carrier_assignment。"""
        if int(data.carrierType) == 3:
            raise BizException("社会运力不支持批量分配，请逐单操作")
        if not ids:
            return {"success": 0, "failed": 0, "failures": []}
        success = 0
        failures: List[dict] = []
        for task_id in ids:
            try:
                await TaskService.complete_carrier_assignment(
                    db, int(task_id), data,
                )
                success += 1
            except Exception as e:  # noqa: BLE001
                failures.append({"id": int(task_id), "error": str(e)})
        return {
            "success": success,
            "failed": len(failures),
            "failures": failures,
        }

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
        carrier_id: Optional[int] = None,
        capacity_id: Optional[int] = None,
        status: Optional[int] = None,
        customer_id: Optional[int] = None,
        origin_keyword: Optional[str] = None,
        destination_keyword: Optional[str] = None,
        created_at_start: Optional[ddate] = None,
        created_at_end: Optional[ddate] = None,
        only_overdue: bool = False,
        in_transit_overdue: bool = False,
        only_normal: bool = False,
        in_transit_only_normal: bool = False,
    ) -> Tuple[List[Task], int]:
        base = select(Task).where(Task.is_deleted == 0)
        cnt = select(func.count(Task.id)).where(Task.is_deleted == 0)

        if keyword:
            kw = f"%{keyword.strip()}%"
            waybill_no_hit = exists(
                select(1)
                .select_from(TaskWaybillItem)
                .where(
                    TaskWaybillItem.task_id == Task.id,
                    TaskWaybillItem.is_deleted == 0,
                    TaskWaybillItem.waybill_no.isnot(None),
                    TaskWaybillItem.waybill_no.like(kw),
                )
            )
            cond = or_(
                Task.task_no.like(kw),
                Task.task_name.like(kw),
                Task.main_driver_name.like(kw),
                Task.plate_number.like(kw),
                Task.carrier_name.like(kw),
                waybill_no_hit,
            )
            base = base.where(cond)
            cnt = cnt.where(cond)
        if carrier_type is not None:
            base = base.where(Task.carrier_type == carrier_type)
            cnt = cnt.where(Task.carrier_type == carrier_type)
        if carrier_id is not None:
            base = base.where(Task.carrier_id == carrier_id)
            cnt = cnt.where(Task.carrier_id == carrier_id)
        if capacity_id is not None:
            base = base.where(Task.capacity_id == capacity_id)
            cnt = cnt.where(Task.capacity_id == capacity_id)
        now = datetime.now()
        if in_transit_overdue:
            od = (
                Task.status.in_([2, 3]),
                Task.planned_arrive_time.isnot(None),
                Task.planned_arrive_time < now,
            )
            base = base.where(*od)
            cnt = cnt.where(*od)
        elif in_transit_only_normal:
            od = (
                Task.status.in_([2, 3]),
                or_(
                    Task.planned_arrive_time.is_(None),
                    Task.planned_arrive_time >= now,
                ),
            )
            base = base.where(*od)
            cnt = cnt.where(*od)
        elif status is not None:
            base = base.where(Task.status == status)
            cnt = cnt.where(Task.status == status)
            if only_overdue:
                if status in (-1, 0):
                    od = (
                        Task.planned_load_time.isnot(None),
                        Task.planned_load_time < now,
                    )
                    base = base.where(*od)
                    cnt = cnt.where(*od)
                elif status in (2, 3):
                    od = (
                        Task.planned_arrive_time.isnot(None),
                        Task.planned_arrive_time < now,
                    )
                    base = base.where(*od)
                    cnt = cnt.where(*od)
            elif only_normal:
                if status in (-1, 0):
                    nm = or_(
                        Task.planned_load_time.is_(None),
                        Task.planned_load_time >= now,
                    )
                    base = base.where(nm)
                    cnt = cnt.where(nm)
                elif status in (2, 3):
                    nm = or_(
                        Task.planned_arrive_time.is_(None),
                        Task.planned_arrive_time >= now,
                    )
                    base = base.where(nm)
                    cnt = cnt.where(nm)
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

    @staticmethod
    async def aggregate_loaded_unloaded(
        db: AsyncSession,
        task_ids: List[int],
    ) -> dict[int, tuple[int, int]]:
        """聚合给定任务的 已装/已卸 台数，返回 {task_id: (loaded, unloaded)}。

        - loaded   = SUM(item.quantity) WHERE item.status >= 1（已装/已卸/已签收）
        - unloaded = SUM(item.quantity) WHERE item.status >= 2（已卸/已签收）

        供 TaskListItemOut 列表行 / 状态 Tag 进度 (X/Y) 文案使用。
        """
        if not task_ids:
            return {}
        ids = list({int(i) for i in task_ids if i})
        r = await db.execute(
            select(
                TaskWaybillItem.task_id,
                TaskWaybillItem.status,
                func.coalesce(func.sum(TaskWaybillItem.quantity), 0),
            )
            .where(
                TaskWaybillItem.task_id.in_(ids),
                TaskWaybillItem.is_deleted == 0,
                TaskWaybillItem.status != 9,
            )
            .group_by(TaskWaybillItem.task_id, TaskWaybillItem.status)
        )
        loaded: dict[int, int] = {}
        unloaded: dict[int, int] = {}
        for tid, st, qty in r.all():
            tid_i = int(tid)
            st_i = int(st)
            qty_i = int(qty or 0)
            if st_i >= 1:
                loaded[tid_i] = loaded.get(tid_i, 0) + qty_i
            if st_i >= 2:
                unloaded[tid_i] = unloaded.get(tid_i, 0) + qty_i
        return {
            tid: (loaded.get(tid, 0), unloaded.get(tid, 0))
            for tid in ids
        }

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

        now = datetime.now()

        # 异常：计划装车时间已过但仍处于待分配
        r_overdue_assign = await db.execute(
            select(func.count(Task.id)).where(
                Task.is_deleted == 0,
                Task.status == -1,
                Task.planned_load_time.isnot(None),
                Task.planned_load_time < now,
            )
        )
        overdue_assignment = int(r_overdue_assign.scalar() or 0)

        # 异常：计划装车时间已过但 status<1（待派车逾期，不含待分配）
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
                "pendingAssign": status_counts.get(-1, 0),
                "pendingDispatch": status_counts.get(0, 0),
                "pendingLoad": status_counts.get(1, 0),
                "loading": status_counts.get(2, 0),
                "onWay": status_counts.get(3, 0),
                "arrived": status_counts.get(4, 0),
                "pendingSign": status_counts.get(4, 0),
                "signed": status_counts.get(5, 0),
                "closed": status_counts.get(7, 0),
                "cancelled": status_counts.get(9, 0),
            },
            "alerts": {
                "overdueAssignment": overdue_assignment,
                "overdueDispatch": overdue_dispatch,
                "overdueArrive": overdue_arrive,
                "pendingLoadAlert": 0,
                "pendingSignAlert": 0,
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
