"""
驾驶员任务服务（薄层包装）

设计原则：
1. 状态推进、状态机校验、Item/Waybill 联动等业务**完全复用**
   ``client/services/task/*``，不重复实现
2. 此 Service 只做"按当前 driver 过滤 + 入参翻译 + 输出裁剪"三件事
3. confirm-load / depart / confirm-arrive 的物理动作：
   - confirm-load：通过 ``TaskLoadingRecordService.create_record`` (event_type=1)
     聚合 1→2（与企业端调度员保持完全一致）
   - depart：通过 ``TaskService.update_status`` 2→3
   - confirm-arrive：通过 ``TaskLoadingRecordService.create_record`` (event_type=2)
     聚合 3→4
   - sign-item：通过 ``TaskWaybillItemService.update_item_status`` 把单行 item
     推到 status=3，由 ``_aggregate_task_status_from_items`` 自动驱动 task 4→5
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException, PermissionException
from app.core.security import TokenData
from app.modules.ai.security.permission_guard import PermissionGuard
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_dispatch_order import TaskDispatchOrder
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.schemas.task.task import TaskStatusUpdate
from app.modules.client.schemas.task.task_loading_record import (
    TaskLoadingRecordCreate,
    TaskLoadingRecordItemIn,
)
from app.modules.client.schemas.task.task_waybill_item import (
    TaskWaybillItemStatusUpdate,
)
from app.modules.client.services.task.task_loading_record_service import (
    TaskLoadingRecordService,
)
from app.modules.client.services.task.task_service import TaskService
from app.modules.client.services.task.task_waybill_item_service import (
    TaskWaybillItemService,
)
from app.modules.driver.schemas.task import (
    DriverAcceptTaskRequest,
    DriverConfirmArriveRequest,
    DriverConfirmLoadRequest,
    DriverDepartRequest,
    DriverRejectTaskRequest,
    DriverRevertSignRequest,
    DriverSignItemRequest,
    DriverTaskDetail,
    DriverTaskItem,
    DriverTaskListItem,
    DriverTaskSegment,
)
from app.modules.driver.services.driver_context import DriverContext


_REVERT_SIGN_PERMISSION = "operation:task:revert-sign"


class DriverTaskService:
    """驾驶员任务服务（按当前 driver 过滤的薄层）"""

    # ------------------------------------------------------------------
    # 当前 driver 可见任务过滤
    # ------------------------------------------------------------------
    @staticmethod
    async def _visible_capacity_ids(
        db: AsyncSession, driver_id: int
    ) -> List[int]:
        """返回该驾驶员当前及历史关联的 capacity_id 集合（用于 task.capacity_id 过滤）"""
        res = await db.execute(
            select(Capacity.id).where(Capacity.driver_id == driver_id)
        )
        return [int(r) for r in res.scalars().all()]

    @staticmethod
    async def _accepted_task_ids(
        db: AsyncSession, task_ids: List[int]
    ) -> set:
        """返回这些任务中"至少有一条调令已接收（accepted_at 非空）"的 task_id 集合。"""
        if not task_ids:
            return set()
        res = await db.execute(
            select(TaskDispatchOrder.task_id)
            .where(
                TaskDispatchOrder.task_id.in_(task_ids),
                TaskDispatchOrder.accepted_at.isnot(None),
                TaskDispatchOrder.is_deleted == 0,
            )
            .distinct()
        )
        return {int(r) for r in res.scalars().all()}

    @staticmethod
    async def _task_accepted_at(
        db: AsyncSession, task_id: int
    ) -> Optional[datetime]:
        """任务维度接收时间：取该任务下最早的一条 accepted_at。"""
        res = await db.execute(
            select(func.min(TaskDispatchOrder.accepted_at)).where(
                TaskDispatchOrder.task_id == task_id,
                TaskDispatchOrder.accepted_at.isnot(None),
                TaskDispatchOrder.is_deleted == 0,
            )
        )
        return res.scalar_one_or_none()

    @staticmethod
    def _build_visibility_condition(capacity_ids: List[int], driver_id: int):
        """构造 SQL 过滤条件：自有车 capacity_id 命中 / 社会运力 social_driver_id 命中"""
        from sqlalchemy import or_

        conds = []
        if capacity_ids:
            conds.append(Task.capacity_id.in_(capacity_ids))
        # 社会运力（远期）—— 当前 social_driver_id 可能为空，保留口子
        conds.append(Task.social_driver_id == driver_id)
        return or_(*conds)

    # ------------------------------------------------------------------
    # 列表
    # ------------------------------------------------------------------
    @staticmethod
    async def list_my_tasks(
        db: AsyncSession,
        ctx: DriverContext,
        *,
        status: Optional[int] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 15,
    ) -> Tuple[List[DriverTaskListItem], int]:
        capacity_ids = await DriverTaskService._visible_capacity_ids(
            db, ctx.driver_id
        )
        visibility = DriverTaskService._build_visibility_condition(
            capacity_ids, ctx.driver_id
        )

        base_conds = [
            Task.is_deleted == 0,
            visibility,
        ]
        if status is not None:
            base_conds.append(Task.status == status)
        if keyword:
            kw = f"%{keyword.strip()}%"
            from sqlalchemy import or_
            base_conds.append(
                or_(
                    Task.task_no.like(kw),
                    Task.task_name.like(kw),
                    Task.plate_number.like(kw),
                    Task.origin.like(kw),
                    Task.destination.like(kw),
                )
            )

        count_stmt = select(func.count(Task.id)).where(*base_conds)
        total = int((await db.execute(count_stmt)).scalar_one())

        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        list_stmt = (
            select(Task)
            .where(*base_conds)
            # MySQL 不支持 `NULLS LAST` 字面量语法（仅 PG/Oracle 支持），
            # 用 `col IS NULL` 布尔表达式升序模拟"空值置底"：
            # 非空(0) 排在空值(1) 前，再按计划装车时间倒序、id 倒序。
            .order_by(
                Task.planned_load_time.is_(None).asc(),
                Task.planned_load_time.desc(),
                Task.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = (await db.execute(list_stmt)).scalars().all()

        accepted_ids = await DriverTaskService._accepted_task_ids(
            db, [int(t.id) for t in rows]
        )
        items = [
            DriverTaskService._to_list_item(t, accepted=int(t.id) in accepted_ids)
            for t in rows
        ]
        return items, total

    # ------------------------------------------------------------------
    # 详情
    # ------------------------------------------------------------------
    @staticmethod
    async def get_my_task(
        db: AsyncSession, ctx: DriverContext, task_id: int
    ) -> DriverTaskDetail:
        task = await DriverTaskService._get_visible_task_or_404(db, ctx, task_id)
        # 段
        seg_rows = (
            await db.execute(
                select(TaskDispatchOrder)
                .where(
                    TaskDispatchOrder.task_id == task.id,
                    TaskDispatchOrder.is_deleted == 0,
                )
                .order_by(TaskDispatchOrder.order_no.asc())
            )
        ).scalars().all()
        # 货物
        item_rows = await TaskWaybillItemService.list_items_of_task(db, task.id)

        accepted_at = await DriverTaskService._task_accepted_at(db, task.id)
        base = DriverTaskService._to_list_item(
            task, accepted=accepted_at is not None, accepted_at=accepted_at
        )
        return DriverTaskDetail(
            **base.model_dump(),
            segments=[
                DriverTaskSegment(
                    id=s.id,
                    segmentNo=int(s.order_no),
                    fromLocation=s.from_location,
                    toLocation=s.to_location,
                    plannedLoadTime=s.planned_load_time,
                    plannedArriveTime=s.planned_arrive_time,
                    acceptedAt=s.accepted_at,
                    actualLoadTime=s.actual_load_time,
                    actualArriveTime=s.actual_arrive_time,
                    status=int(s.status),
                    mileage=(float(s.mileage) if s.mileage is not None else None),
                )
                for s in seg_rows
            ],
            items=[DriverTaskService._to_item_out(it) for it in item_rows],
            remark=task.remark,
        )

    # ------------------------------------------------------------------
    # 动作：接收调令（轻量）→ 写 dispatch_order.accepted_at，不改 task.status
    # ------------------------------------------------------------------
    @staticmethod
    async def accept(
        db: AsyncSession,
        ctx: DriverContext,
        task_id: int,
        data: DriverAcceptTaskRequest,
    ) -> DriverTaskDetail:
        task = await DriverTaskService._get_visible_task_or_404(db, ctx, task_id)
        # 仅"已派车"状态可接单（-1 待分配 / 0 待派车 尚未派到司机）
        if int(task.status) != 1:
            raise BizException("仅「已派车」的任务可接收调令")
        # 兜底：没有任何调令时先生成主线路调令
        await TaskService.ensure_main_line_dispatch_order(db, task)
        orders = await TaskService.list_dispatch_orders(db, task.id)
        now = datetime.now()
        touched = 0
        for o in orders:
            if o.accepted_at is None:
                o.accepted_at = now
                touched += 1
        if touched == 0:
            raise BizException("该任务的调令已全部接收")
        await db.flush()
        return await DriverTaskService.get_my_task(db, ctx, task.id)

    # ------------------------------------------------------------------
    # 动作：拒绝调令 → task 1→0 退回待派车池 + remark 记录
    # ------------------------------------------------------------------
    @staticmethod
    async def reject(
        db: AsyncSession,
        ctx: DriverContext,
        task_id: int,
        data: DriverRejectTaskRequest,
    ) -> None:
        task = await DriverTaskService._get_visible_task_or_404(db, ctx, task_id)
        if int(task.status) != 1:
            raise BizException("仅「已派车」且未装车的任务可拒单")
        await TaskService.revert_status(
            db, task.id,
            target_status=0,
            reason=f"[司机拒单] {data.reason}（driver={ctx.driver.name}#{ctx.driver_id}）",
            current_user_id=ctx.user_id,
        )

    # ------------------------------------------------------------------
    # 动作：确认装车 → 创建装车记录（event=1，所有 item 整票装车）
    # ------------------------------------------------------------------
    @staticmethod
    async def confirm_load(
        db: AsyncSession,
        ctx: DriverContext,
        task_id: int,
        data: DriverConfirmLoadRequest,
    ) -> DriverTaskDetail:
        task = await DriverTaskService._get_visible_task_or_404(db, ctx, task_id)
        # 接单前置校验：必须先接收调令
        accepted_at = await DriverTaskService._task_accepted_at(db, task.id)
        if accepted_at is None:
            raise BizException("请先接收调令，再确认装车")
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        # 仅 status<1 的 item 需要装车
        pending = [it for it in items if int(it.status) < 1]
        if not pending:
            raise BizException("当前任务下没有待装车的运单")

        rec_in = TaskLoadingRecordCreate(
            eventType=1,
            dispatchOrderId=None,
            happenedAt=data.actualLoadTime or datetime.now(),
            location=data.location,
            items=[
                TaskLoadingRecordItemIn(itemId=int(it.id), quantity=int(it.quantity))
                for it in pending
            ],
            photoUrls=data.photoUrls,
            remark=data.remark,
        )
        await TaskLoadingRecordService.create_record(
            db, task.id, rec_in,
            operator_id=ctx.user_id,
            operator_name=ctx.driver.name,
        )
        return await DriverTaskService.get_my_task(db, ctx, task.id)

    # ------------------------------------------------------------------
    # 动作：出发 → task.status 2→3
    # ------------------------------------------------------------------
    @staticmethod
    async def depart(
        db: AsyncSession,
        ctx: DriverContext,
        task_id: int,
        data: DriverDepartRequest,
    ) -> DriverTaskDetail:
        task = await DriverTaskService._get_visible_task_or_404(db, ctx, task_id)
        await TaskService.update_status(
            db, task.id,
            TaskStatusUpdate(
                status=3,
                actualLoadTime=data.actualLoadTime,
                remark=data.remark,
            ),
        )
        return await DriverTaskService.get_my_task(db, ctx, task.id)

    # ------------------------------------------------------------------
    # 动作：确认到达 → 创建卸车记录（event=2，所有 item 整票卸车，自动聚合 3→4）
    # ------------------------------------------------------------------
    @staticmethod
    async def confirm_arrive(
        db: AsyncSession,
        ctx: DriverContext,
        task_id: int,
        data: DriverConfirmArriveRequest,
    ) -> DriverTaskDetail:
        task = await DriverTaskService._get_visible_task_or_404(db, ctx, task_id)
        items = await TaskWaybillItemService.list_items_of_task(db, task.id)
        pending = [it for it in items if 1 <= int(it.status) < 2]
        if not pending:
            raise BizException("当前任务下没有可标记到达的运单（请先确认装车并出发）")

        rec_in = TaskLoadingRecordCreate(
            eventType=2,
            dispatchOrderId=None,
            happenedAt=data.actualArriveTime or datetime.now(),
            location=data.location,
            items=[
                TaskLoadingRecordItemIn(itemId=int(it.id), quantity=int(it.quantity))
                for it in pending
            ],
            photoUrls=data.photoUrls,
            remark=data.remark,
        )
        await TaskLoadingRecordService.create_record(
            db, task.id, rec_in,
            operator_id=ctx.user_id,
            operator_name=ctx.driver.name,
        )
        return await DriverTaskService.get_my_task(db, ctx, task.id)

    # ------------------------------------------------------------------
    # 动作：item 签收 → item.status=3，聚合驱动 task 4→5
    # ------------------------------------------------------------------
    @staticmethod
    async def sign_item(
        db: AsyncSession,
        ctx: DriverContext,
        item_id: int,
        data: DriverSignItemRequest,
    ) -> None:
        item = await DriverTaskService._get_visible_item_or_404(db, ctx, item_id)
        cur = int(item.status)
        if cur >= 3:
            raise BizException("该运单已签收")
        await TaskWaybillItemService.update_item_status(
            db, item.id,
            TaskWaybillItemStatusUpdate(
                status=3,
                signedAt=data.signedAt or datetime.now(),
                remark=data.remark,
            ),
        )

    @staticmethod
    async def revert_sign_item(
        db: AsyncSession,
        ctx: DriverContext,
        item_id: int,
        data: DriverRevertSignRequest,
        *,
        actor: TokenData,
    ) -> None:
        item = await DriverTaskService._get_visible_item_or_404(db, ctx, item_id)
        allowed = await PermissionGuard.user_has_menu_permission(
            db, actor, _REVERT_SIGN_PERMISSION
        )
        if not allowed:
            raise PermissionException(
                f"当前用户缺少权限码 {_REVERT_SIGN_PERMISSION}，无法撤销签收"
            )
        if int(item.status) != 3:
            raise BizException("仅「已签收」的运单可撤销签收")
        await TaskWaybillItemService.update_item_status(
            db, item.id,
            TaskWaybillItemStatusUpdate(
                status=2,
                remark=f"[司机撤销签收] {data.reason}",
            ),
        )

    # ------------------------------------------------------------------
    # 私有：可见性校验
    # ------------------------------------------------------------------
    @staticmethod
    async def _get_visible_task_or_404(
        db: AsyncSession, ctx: DriverContext, task_id: int
    ) -> Task:
        task = await TaskService.get_or_404(db, task_id)
        capacity_ids = await DriverTaskService._visible_capacity_ids(
            db, ctx.driver_id
        )
        ok = False
        if task.capacity_id is not None and int(task.capacity_id) in capacity_ids:
            ok = True
        elif (
            task.social_driver_id is not None
            and int(task.social_driver_id) == ctx.driver_id
        ):
            ok = True
        if not ok:
            raise BizException("无权访问该任务单")
        return task

    @staticmethod
    async def _get_visible_item_or_404(
        db: AsyncSession, ctx: DriverContext, item_id: int
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
        # 通过 task 进行可见性二次校验
        await DriverTaskService._get_visible_task_or_404(db, ctx, int(item.task_id))
        return item

    # ------------------------------------------------------------------
    # 输出裁剪
    # ------------------------------------------------------------------
    @staticmethod
    def _to_list_item(
        t: Task,
        *,
        accepted: bool = False,
        accepted_at: Optional[datetime] = None,
    ) -> DriverTaskListItem:
        return DriverTaskListItem(
            id=int(t.id),
            taskNo=t.task_no,
            taskName=t.task_name,
            status=int(t.status),
            accepted=accepted,
            acceptedAt=accepted_at,
            origin=t.origin,
            destination=t.destination,
            plannedLoadTime=t.planned_load_time,
            plannedArriveTime=t.planned_arrive_time,
            actualLoadTime=t.actual_load_time,
            actualArriveTime=t.actual_arrive_time,
            totalQuantity=int(t.total_quantity or 0),
            waybillCount=int(t.waybill_count or 0),
            customerName=None,  # 司机端不强求客户名
            mainDriverName=t.main_driver_name,
            plateNumber=t.plate_number,
            carrierType=int(t.carrier_type or 1),
            prepaidAmount=float(t.prepaid_amount or 0),
            settledAmount=float(t.settled_amount or 0),
            carrierCostAmount=(
                float(t.carrier_cost_amount)
                if t.carrier_cost_amount is not None
                else None
            ),
        )

    @staticmethod
    def _to_item_out(it: TaskWaybillItem) -> DriverTaskItem:
        return DriverTaskItem(
            id=int(it.id),
            waybillId=int(it.waybill_id),
            waybillNo=it.waybill_no,
            customerName=it.customer_name,
            vehicleBrand=it.vehicle_brand,
            vehicleModel=it.vehicle_model,
            dealerName=it.dealer_name,
            quantity=int(it.quantity or 0),
            status=int(it.status or 0),
            loadedAt=it.loaded_at,
            unloadedAt=it.unloaded_at,
            signedAt=it.signed_at,
        )
