"""
企业端运输任务单 API

接口前缀：/business/task
- 任务单主接口（含详情聚合 segments + waybillItems + 当前财务摘要）
- 货物挂接子接口
- 分段子接口
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import TenantException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import (
    TenantDb,
    ensure_biz_company_activity_table,
    get_current_user,
    get_tenant_db,
)
from app.core.security import TokenData
from app.modules.client.schemas.task.task import (
    TaskAssignCarrierRequest,
    TaskCarrierAssignmentInfo,
    TaskBatchStatusRequest,
    TaskBatchCarrierAssignmentRequest,
    TaskCancelRequest,
    TaskCreate,
    TaskForceCancelRequest,
    TaskListItemOut,
    TaskOut,
    TaskPlanRouteRequest,
    TaskRevertStatusRequest,
    TaskStatusEventOut,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.modules.client.schemas.task.task_alert import TaskAlertOut
from app.modules.client.schemas.task.task_dispatch_order import (
    TaskDispatchOrderOut,
    TaskDispatchOrderStatusUpdate,
)
from app.modules.client.schemas.task.task_loading_record import (
    TaskLoadingRecordCreate,
    TaskLoadingRecordOut,
)
from app.modules.client.schemas.task.task_waybill_item import (
    TaskWaybillItemIn,
    TaskWaybillItemOut,
    TaskWaybillItemStatusUpdate,
)
from app.modules.client.services.company_activity_service import (
    CompanyActivityService,
)
from app.modules.client.services.task.task_finance_service import (
    TaskFinanceService,
)
from app.modules.client.services.task.task_loading_record_service import (
    TaskLoadingRecordService,
)
from app.modules.client.services.task.task_alert_service import TaskAlertService
from app.modules.client.services.task.task_service import TaskService
from app.modules.client.services.task.task_status_event_service import (
    TaskStatusEventService,
)
from app.modules.client.services.task.task_waybill_item_service import (
    TaskWaybillItemService,
)
from app.modules.client.services.waybill.waybill_service import WaybillService

router = APIRouter()


async def _task_detail_dump(
    db: AsyncSession,
    task,
    *,
    segments=None,
    waybill_items=None,
):
    """聚合 dispatch orders + waybillItems，并为挂接行补齐车系图（与计划列表一致）。"""
    segs = (
        segments
        if segments is not None
        else await TaskService.list_dispatch_orders(db, task.id)
    )
    items = (
        waybill_items
        if waybill_items is not None
        else await TaskWaybillItemService.list_items_of_task(db, task.id)
    )
    lookup = await WaybillService._series_image_lookup_map(db)
    wb_summary_map = await TaskService.aggregate_waybill_status_summary(
        db, [task.id],
    )
    return TaskOut.from_model(
        task, segments=segs, waybill_items=items, series_lookup=lookup,
        waybill_status_summary=wb_summary_map.get(int(task.id)),
    ).model_dump()


_TASK_STATUS_LABELS = {
    -1: "待分配",
    0: "待派车", 1: "已派车", 2: "已装车", 3: "在途",
    4: "已到达", 5: "已交车", 7: "已关闭", 9: "已取消",
}


def _require_tenant(current_user: TokenData) -> None:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")


# ============================================================
# 任务单 CRUD
# ============================================================

@router.get("")
async def page_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    carrierType: Optional[int] = None,
    carrierId: Optional[int] = None,
    capacityId: Optional[int] = None,
    status: Optional[int] = None,
    customerId: Optional[int] = None,
    originKeyword: Optional[str] = None,
    destinationKeyword: Optional[str] = None,
    createdAtStart: Optional[date] = None,
    createdAtEnd: Optional[date] = None,
    timeField: Optional[str] = Query(
        None,
        description=(
            "时间维度："
            "stageEnteredAt(进入当前阶段) | createdAt(制单)"
            " | assignedAt | dispatchedAt | actualLoadTime | signedAt；"
            "后四个为节点维度，会排除尚未走到该节点的任务"
        ),
    ),
    timeStart: Optional[date] = None,
    timeEnd: Optional[date] = None,
    alertLevel: Optional[str] = Query(
        None,
        description=(
            "预警子集：normal(无活跃预警) | warn(仅关注) | critical(存在严重)"
            " | any(存在任意预警)"
        ),
    ),
    onlyOverdue: bool = Query(
        False, description="【已废弃】等价于 alertLevel=any，请改用 alertLevel"
    ),
    onlyNormal: bool = Query(
        False, description="【已废弃】等价于 alertLevel=normal，请改用 alertLevel"
    ),
    inTransitOverdue: bool = Query(
        False,
        description="【已废弃】在途合并池逾期列表：status∈{2,3} 且存在活跃预警",
    ),
    inTransitOnlyNormal: bool = Query(
        False,
        description="【已废弃】在途合并池正常列表：status∈{2,3} 且无活跃预警",
    ),
    plateNumber: Optional[str] = Query(None, description="车牌号（模糊匹配主车牌）"),
    sortField: Optional[str] = Query(
        None,
        description=(
            "排序字段白名单：createdAt|plannedLoadTime|plannedArriveTime"
            "|actualLoadTime|dispatchedAt|stageEnteredAt；非法值回落创建时间倒序"
        ),
    ),
    sortOrder: Optional[str] = Query(None, description="排序方向 asc|desc，默认 asc"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    items, total = await TaskService.page_tasks(
        db,
        page=page, page_size=page_size,
        keyword=keyword,
        carrier_type=carrierType,
        carrier_id=carrierId,
        capacity_id=capacityId,
        status=status,
        customer_id=customerId,
        origin_keyword=originKeyword,
        destination_keyword=destinationKeyword,
        created_at_start=createdAtStart,
        created_at_end=createdAtEnd,
        time_field=timeField,
        time_start=timeStart,
        time_end=timeEnd,
        alert_level=alertLevel,
        only_overdue=onlyOverdue,
        in_transit_overdue=inTransitOverdue,
        only_normal=onlyNormal,
        in_transit_only_normal=inTransitOnlyNormal,
        plate_number=plateNumber,
        sort_field=sortField,
        sort_order=sortOrder,
    )
    task_ids = [t.id for t in items]
    qty_map = await TaskService.aggregate_loaded_unloaded(db, task_ids)
    wb_summary_map = await TaskService.aggregate_waybill_status_summary(
        db, task_ids,
    )
    alert_map = await TaskAlertService.top_level_map(db, task_ids)
    rows = []
    for t in items:
        loaded, unloaded = qty_map.get(int(t.id), (0, 0))
        rows.append(
            TaskListItemOut.from_model(
                t, loaded_quantity=loaded, unloaded_quantity=unloaded,
                waybill_status_summary=wb_summary_map.get(int(t.id)),
                alert=alert_map.get(int(t.id)),
            ).model_dump()
        )
    return success(data={
        "list": rows,
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/check-task-no")
async def check_task_no(
    taskNo: str = Query(..., min_length=1, max_length=50),
    excludeId: Optional[int] = Query(None, ge=1),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    available = await TaskService.check_task_no(db, taskNo, excludeId)
    return success(data={"available": available})


@router.get("/workbench-stats")
async def get_workbench_stats(
    keyword: Optional[str] = None,
    carrierType: Optional[int] = None,
    carrierId: Optional[int] = None,
    capacityId: Optional[int] = None,
    customerId: Optional[int] = None,
    originKeyword: Optional[str] = None,
    destinationKeyword: Optional[str] = None,
    createdAtStart: Optional[date] = None,
    createdAtEnd: Optional[date] = None,
    timeField: Optional[str] = Query(
        None,
        description=(
            "时间维度："
            "stageEnteredAt(进入当前阶段) | createdAt(制单)"
            " | assignedAt | dispatchedAt | actualLoadTime | signedAt；"
            "后四个为节点维度，会排除尚未走到该节点的任务"
        ),
    ),
    timeStart: Optional[date] = None,
    timeEnd: Optional[date] = None,
    plateNumber: Optional[str] = Query(None, description="车牌号（模糊匹配主车牌）"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """调度工作台 KPI 聚合：各状态计数 + 异常计数（支持与列表相同的筛选条件）。"""
    stats = await TaskService.workbench_stats(
        db,
        keyword=keyword,
        carrier_type=carrierType,
        carrier_id=carrierId,
        capacity_id=capacityId,
        customer_id=customerId,
        origin_keyword=originKeyword,
        destination_keyword=destinationKeyword,
        created_at_start=createdAtStart,
        created_at_end=createdAtEnd,
        time_field=timeField,
        time_start=timeStart,
        time_end=timeEnd,
        plate_number=plateNumber,
    )
    return success(data=stats)


@router.post("/batch-status")
@operation_log(module="运输任务单", action="批量状态变更", description="批量推进任务单状态")
async def batch_update_status(
    request: Request,
    data: TaskBatchStatusRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    payload = TaskStatusUpdate(
        status=data.status,
        actualLoadTime=data.actualLoadTime,
        actualArriveTime=data.actualArriveTime,
        remark=data.remark,
    )
    result = await TaskService.batch_update_status(db, data.ids, payload)
    return success(data=result)


@router.get("/route-distance")
async def lookup_route_distance(
    originRegionId: int = Query(..., ge=1),
    destinationRegionId: int = Query(..., ge=1),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """规划路线时的里程联想：
    给定起终地区主键，从 biz_route 中匹配最新一条已启用线路，
    返回 {routeId, routeName, origin, destination, distance, estimatedHours}；
    未匹配返回 data=null。
    """
    row = await TaskService.lookup_route_distance(
        db, originRegionId, destinationRegionId,
    )
    return success(data=row)


@router.get("/candidate-waybills")
async def list_candidate_waybills(
    keyword: Optional[str] = None,
    customerId: Optional[int] = None,
    originKeyword: Optional[str] = None,
    destinationKeyword: Optional[str] = None,
    modelKeyword: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows = await TaskWaybillItemService.list_candidate_cargoes(
        db,
        keyword=keyword,
        customer_id=customerId,
        origin_keyword=originKeyword,
        destination_keyword=destinationKeyword,
        model_keyword=modelKeyword,
        offset=offset,
        limit=limit,
    )
    return success(data=rows.model_dump())


@router.get("/{task_id}")
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    task = await TaskService.get_or_404(db, task_id)
    return success(data=await _task_detail_dump(db, task))


@router.post("")
@operation_log(module="运输任务单", action="新增", description="新增运输任务单")
async def create_task(
    request: Request,
    data: TaskCreate,
    db: TenantDb,
    current_user: TokenData = Depends(get_current_user),
    _: None = Depends(ensure_biz_company_activity_table),
):
    """创建任务单。

    使用 TenantDb（commit 在响应前完成）：手动配载页创建成功后会立刻重拉
    待派候选，若仍用默认 request-scope Session，客户端可能读到未提交快照，
    已配商品车会继续出现在左侧可选列表。
    """
    _require_tenant(current_user)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    task = await TaskService.create_task(
        db, data,
        current_user_id=current_user.user_id,
        dispatcher_name=op_name,
    )
    return success(data=await _task_detail_dump(db, task))


@router.put("/{task_id}")
@operation_log(module="运输任务单", action="编辑", description="编辑运输任务单")
async def update_task(
    request: Request,
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    task = await TaskService.update_task(
        db, task_id, data, current_user_id=current_user.user_id,
    )
    return success(data=await _task_detail_dump(db, task))


@router.delete("/{task_id}")
@operation_log(module="运输任务单", action="删除", description="删除运输任务单")
async def delete_task(
    request: Request,
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await TaskService.delete_task(db, task_id)
    return success()


@router.put("/{task_id}/status")
@operation_log(module="运输任务单", action="状态变更", description="变更任务单状态")
async def update_task_status(
    request: Request,
    task_id: int,
    data: TaskStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    task = await TaskService.update_status(
        db, task_id, data, current_user_id=current_user.user_id,
    )
    return success(data=await _task_detail_dump(db, task))


@router.post("/{task_id}/plan-route")
@operation_log(
    module="运输任务单", action="规划路线", description="补齐/重做任务单分段路线",
)
async def plan_route(
    request: Request,
    task_id: int,
    data: TaskPlanRouteRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    task = await TaskService.plan_route(db, task_id, data)
    return success(data=await _task_detail_dump(db, task))


@router.post("/{task_id}/assign-carrier")
@operation_log(module="运输任务单", action="派车", description="任务单派车/换车")
async def assign_carrier(
    request: Request,
    task_id: int,
    data: TaskAssignCarrierRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    task = await TaskService.assign_carrier(
        db, task_id, data, current_user_id=current_user.user_id,
    )
    return success(data=await _task_detail_dump(db, task))


@router.post("/{task_id}/complete-carrier-assignment")
@operation_log(
    module="运输任务单",
    action="确认承运分配",
    description="待分配任务确认承运方（社会运力直达待装车，其余进入待派车）",
)
async def complete_carrier_assignment(
    request: Request,
    task_id: int,
    data: TaskCarrierAssignmentInfo,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    task = await TaskService.complete_carrier_assignment(
        db, task_id, data, current_user_id=current_user.user_id,
    )
    return success(data=await _task_detail_dump(db, task))


@router.post("/batch-complete-carrier-assignment")
@operation_log(
    module="运输任务单",
    action="批量确认承运分配",
    description="待分配任务批量确认承运方后进入待派车",
)
async def batch_complete_carrier_assignment(
    request: Request,
    data: TaskBatchCarrierAssignmentRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    result = await TaskService.batch_complete_carrier_assignment(
        db, data.ids, data.carrier, current_user_id=current_user.user_id,
    )
    return success(data=result)


@router.post("/{task_id}/cancel")
@operation_log(module="运输任务单", action="取消", description="取消任务单（释放台数）")
async def cancel_task(
    request: Request,
    task_id: int,
    data: Optional[TaskCancelRequest] = None,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    reason = data.reason if data else None
    task = await TaskService.cancel_task(
        db, task_id, reason=reason, current_user_id=current_user.user_id,
    )
    return success(data=await _task_detail_dump(db, task))


@router.post("/{task_id}/revert-status")
@operation_log(
    module="运输任务单", action="撤销状态", description="任务单单步反向跳转",
)
async def revert_task_status(
    request: Request,
    task_id: int,
    data: TaskRevertStatusRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """专项撤销：把任务单回退到上一态。

    - 合法路径见《02.计划与任务单状态机联动设计.md》§4.5 反向跳转矩阵：
      1→0 / 2→1 / 3→2 / 4→3 / 5→4
    - 联动：Item 反向同步、Waybill 聚合允许 downgrade
    """
    _require_tenant(current_user)
    task = await TaskService.revert_status(
        db, task_id,
        target_status=data.targetStatus,
        reason=data.reason,
        current_user_id=current_user.user_id,
    )
    return success(data=await _task_detail_dump(db, task))


@router.post("/{task_id}/force-cancel")
@operation_log(
    module="运输任务单", action="强制取消", description="任务单线下强制取消（2/3/4 → 9）",
)
async def force_cancel_task(
    request: Request,
    task_id: int,
    data: TaskForceCancelRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    """强制取消：直接置任务单为 ``9 已取消``。

    适用：已装车 / 在途 / 已到达 区间内的线下取消。
    - 联动：所有 item 推到 9，cargo 占用释放
    - 未支付费用单一并撤销（``data.cancelUnpaidFinanceDocs`` 为 False 则跳过）
    """
    _require_tenant(current_user)
    task = await TaskService.force_cancel(
        db, task_id,
        reason=data.reason,
        current_user_id=current_user.user_id,
        cancel_unpaid_finance_docs=bool(data.cancelUnpaidFinanceDocs),
    )
    return success(data=await _task_detail_dump(db, task))


# ============================================================
# 状态事件（时间流）
# ============================================================

@router.get("/{task_id}/status-events")
async def list_task_status_events(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """任务时间流：按时间正序返回全部状态事件（含撤销、取消与操作人）。"""
    await TaskService.get_or_404(db, task_id)
    events = await TaskStatusEventService.list_events(db, task_id)
    return success(
        data=[TaskStatusEventOut.from_model(e).model_dump() for e in events]
    )


# ============================================================
# 预警
# ============================================================

@router.get("/{task_id}/alerts")
async def list_task_alerts(
    task_id: int,
    activeOnly: bool = Query(False, description="仅返回待处理的预警"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """某任务的预警列表：活跃的排在前面，已处置的保留供复盘。"""
    await TaskService.get_or_404(db, task_id)
    rows = await TaskAlertService.list_of_task(
        db, task_id, active_only=activeOnly
    )
    return success(data=[TaskAlertOut.from_model(r).model_dump() for r in rows])


# ============================================================
# 货物挂接子接口
# ============================================================

@router.get("/{task_id}/waybill-items")
async def list_waybill_items(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    items = await TaskWaybillItemService.list_items_of_task(db, task_id)
    lookup = await WaybillService._series_image_lookup_map(db)
    return success(
        data=[
            TaskWaybillItemOut.from_model(i, series_lookup=lookup).model_dump()
            for i in items
        ]
    )


@router.post("/{task_id}/waybill-items")
@operation_log(module="运输任务单", action="挂接货物", description="批量挂接计划货物")
async def add_waybill_items(
    request: Request,
    task_id: int,
    items: list[TaskWaybillItemIn],
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    task = await TaskService.get_or_404(db, task_id)
    rows = await TaskWaybillItemService.add_items(db, task, items)
    lookup = await WaybillService._series_image_lookup_map(db)
    return success(
        data=[
            TaskWaybillItemOut.from_model(r, series_lookup=lookup).model_dump()
            for r in rows
        ]
    )


@router.put("/waybill-items/{item_id}")
@operation_log(module="运输任务单", action="更新货物状态", description="更新挂接货物状态")
async def update_waybill_item(
    request: Request,
    item_id: int,
    data: TaskWaybillItemStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    row = await TaskWaybillItemService.update_item_status(db, item_id, data)
    lookup = await WaybillService._series_image_lookup_map(db)
    return success(
        data=TaskWaybillItemOut.from_model(row, series_lookup=lookup).model_dump()
    )


@router.delete("/waybill-items/{item_id}")
@operation_log(module="运输任务单", action="取消挂接", description="取消货物挂接（释放台数）")
async def remove_waybill_item(
    request: Request,
    item_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await TaskWaybillItemService.remove_item(db, item_id)
    return success()


# ============================================================
# 调令子接口（原"分段"）
# ============================================================

@router.get("/{task_id}/dispatch-orders")
@router.get("/{task_id}/segments")  # 兼容旧路径
async def list_dispatch_orders(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    # 懒修复：历史/未规划路线的任务可能零调令，按起终点自动补一条主线路调令，
    # 避免装卸 / 司机执行环节"关联调令"为空导致流程卡死（幂等）。
    task = await TaskService.get_or_404(db, task_id)
    await TaskService.ensure_main_line_dispatch_order(db, task)
    segs = await TaskService.list_dispatch_orders(db, task_id)
    return success(
        data=[TaskDispatchOrderOut.from_model(s).model_dump() for s in segs]
    )


@router.put("/dispatch-orders/{order_id}/status")
@router.put("/segments/{order_id}/status")  # 兼容旧路径
@operation_log(module="运输任务单", action="调令状态变更", description="变更调令状态")
async def update_dispatch_order_status(
    request: Request,
    order_id: int,
    data: TaskDispatchOrderStatusUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    seg = await TaskService.update_dispatch_order_status(
        db, order_id, data.status,
        actual_load_time=data.actualLoadTime,
        actual_arrive_time=data.actualArriveTime,
        remark=data.remark,
    )
    return success(data=TaskDispatchOrderOut.from_model(seg).model_dump())


# ============================================================
# 装卸记录（多批次装/卸车）
# ============================================================

@router.get("/{task_id}/loading-records")
async def list_loading_records(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """列出某任务的全部装卸事件（含每条记录的 items 与照片）。"""
    rows = await TaskLoadingRecordService.list_records(db, task_id)
    return success(data=[r.model_dump() for r in rows])


@router.post("/{task_id}/loading-records")
@operation_log(
    module="运输任务单", action="装卸事件",
    description="创建装/卸车记录，同事务推进 item / task / waybill 状态",
)
async def create_loading_record(
    request: Request,
    task_id: int,
    data: TaskLoadingRecordCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    op_name = await CompanyActivityService.actor_display_name(
        db, current_user.user_id
    )
    rec = await TaskLoadingRecordService.create_record(
        db, task_id, data,
        operator_id=current_user.user_id,
        operator_name=op_name,
    )
    return success(data=rec.model_dump())


@router.delete("/loading-records/{record_id}")
@operation_log(
    module="运输任务单", action="撤销装卸事件",
    description="撤销一条装/卸车记录，回退 item 与 task 状态",
)
async def revoke_loading_record(
    request: Request,
    record_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    _require_tenant(current_user)
    await TaskLoadingRecordService.revoke_record(db, record_id)
    return success()


# ============================================================
# 任务单维度费用单聚合（便捷接口，作为详情页 tab 数据源）
# ============================================================

@router.get("/{task_id}/finance-docs-summary")
async def list_task_finance_summary(
    task_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    docs = await TaskFinanceService.list_docs_by_task(db, task_id)
    return success(data=[{
        "id": d.id,
        "docNo": d.doc_no,
        "docType": d.doc_type,
        "isFinal": d.is_final,
        "payeeType": d.payee_type,
        "payeeName": d.payee_name,
        "plannedAmount": float(d.planned_amount or 0),
        "actualAmount": float(d.actual_amount) if d.actual_amount is not None else None,
        "status": d.status,
        "createdAt": d.created_at,
        "plannedPayTime": d.planned_pay_time,
        "actualPayTime": d.actual_pay_time,
    } for d in docs])
