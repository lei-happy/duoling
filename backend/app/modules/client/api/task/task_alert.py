"""
企业端任务预警 API

接口前缀：
- /business/task-alert       预警实例的查询与处置
- /business/task-alert-rule  预警阈值规则配置

导入本模块会连带导入 alert 子域，从而完成「状态变更即时重算」钩子的注册。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.exceptions import BizException
from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.task.task_alert import (
    TaskAlertBatchDismissRequest,
    TaskAlertDismissRequest,
    TaskAlertOut,
    TaskAlertResolveRequest,
    TaskAlertRuleConflictOut,
    TaskAlertRuleCreate,
    TaskAlertRuleOut,
    TaskAlertRuleUpdate,
)
from app.modules.client.services.task.alert import TaskAlertEngine, catalog_payload
from app.modules.client.services.task.task_alert_rule_service import (
    TaskAlertRuleService,
    scope_summary,
)
from app.modules.client.services.task.task_alert_service import TaskAlertService

alert_router = APIRouter()
alert_rule_router = APIRouter()


def _operator(current_user: TokenData) -> tuple[Optional[int], Optional[str]]:
    return (
        getattr(current_user, "user_id", None),
        getattr(current_user, "nickname", None)
        or getattr(current_user, "username", None),
    )


# ============================================================
# 预警实例
# ============================================================

@alert_router.get("")
async def page_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    stage: Optional[int] = None,
    level: Optional[int] = Query(None, description="1-关注 2-严重"),
    status: Optional[int] = Query(
        None, description="0-待处理 1-已处理 2-已忽略 3-已自动消除"
    ),
    ruleCode: Optional[str] = None,
    keyword: Optional[str] = Query(None, description="任务单号模糊匹配"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await TaskAlertService.page_alerts(
        db,
        page=page,
        page_size=page_size,
        stage=stage,
        level=level,
        status=status,
        rule_code=ruleCode,
        keyword=keyword,
    )
    return success(data={
        "list": [TaskAlertOut.from_model(r).model_dump() for r in rows],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@alert_router.post("/{alert_id}/claim")
@operation_log(module="任务预警", action="认领", description="认领一条任务预警")
async def claim_alert(
    request: Request,
    alert_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_id, user_name = _operator(current_user)
    row = await TaskAlertService.claim(
        db, alert_id, user_id=user_id, user_name=user_name
    )
    return success(data=TaskAlertOut.from_model(row).model_dump(), message="已认领")


@alert_router.post("/{alert_id}/resolve")
@operation_log(module="任务预警", action="处理", description="标记预警已处理")
async def resolve_alert(
    request: Request,
    alert_id: int,
    data: TaskAlertResolveRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_id, _name = _operator(current_user)
    row = await TaskAlertService.resolve(
        db, alert_id, user_id=user_id, remark=data.remark
    )
    return success(data=TaskAlertOut.from_model(row).model_dump(), message="已标记处理")


@alert_router.post("/{alert_id}/dismiss")
@operation_log(module="任务预警", action="忽略", description="忽略一条任务预警")
async def dismiss_alert(
    request: Request,
    alert_id: int,
    data: TaskAlertDismissRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_id, _name = _operator(current_user)
    row = await TaskAlertService.dismiss(
        db, alert_id, user_id=user_id, reason=data.reason
    )
    return success(data=TaskAlertOut.from_model(row).model_dump(), message="已忽略")


@alert_router.post("/batch-dismiss")
@operation_log(module="任务预警", action="批量忽略", description="批量忽略任务预警")
async def batch_dismiss(
    request: Request,
    data: TaskAlertBatchDismissRequest,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_id, _name = _operator(current_user)
    if data.ids:
        result = await TaskAlertService.batch_dismiss(
            db, data.ids, user_id=user_id, reason=data.reason
        )
    elif data.taskIds:
        result = await TaskAlertService.dismiss_by_tasks(
            db, data.taskIds, user_id=user_id, reason=data.reason
        )
    else:
        raise BizException("请选择要忽略的预警")
    return success(
        data=result, message=f"已忽略 {result.get('success', 0)} 条预警"
    )


@alert_router.post("/recompute")
@operation_log(module="任务预警", action="重算", description="手动触发预警重算")
async def recompute(
    request: Request,
    taskId: Optional[int] = Query(None, description="留空则全量重算本租户"),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    if taskId:
        stats = await TaskAlertEngine.recompute_tasks(db, [taskId], commit=False)
    else:
        stats = await TaskAlertEngine.scan_tenant(db)
    return success(data=stats, message="预警已重新计算")


# ============================================================
# 预警规则
# ============================================================

@alert_rule_router.get("/catalog")
async def get_catalog(
    _: TokenData = Depends(get_current_user),
):
    """规则类型目录与内置默认阈值（配置页据此渲染表单）。"""
    return success(data=catalog_payload())


@alert_rule_router.get("/defaults")
async def list_defaults(
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows = await TaskAlertRuleService.list_defaults(db)
    names = await TaskAlertRuleService.resolve_scope_names(db, rows)
    return success(data=[
        TaskAlertRuleOut.from_model(
            r, scope_summary=scope_summary(r, names)
        ).model_dump()
        for r in rows
    ])


@alert_rule_router.get("")
async def page_rules(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    ruleCode: Optional[str] = None,
    status: Optional[int] = None,
    isDefault: Optional[bool] = Query(
        None, description="true 只看默认阈值，false 只看覆盖规则，留空全部"
    ),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows, total = await TaskAlertRuleService.page_rules(
        db,
        page=page,
        page_size=page_size,
        rule_code=ruleCode,
        status=status,
        only_default=isDefault,
    )
    names = await TaskAlertRuleService.resolve_scope_names(db, rows)
    return success(data={
        "list": [
            TaskAlertRuleOut.from_model(
                r, scope_summary=scope_summary(r, names)
            ).model_dump()
            for r in rows
        ],
        "count": total,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@alert_rule_router.post("/check-conflict")
async def check_conflict(
    data: TaskAlertRuleCreate,
    excludeId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    rows = await TaskAlertRuleService.find_conflicts(
        db, data, exclude_id=excludeId
    )
    names = await TaskAlertRuleService.resolve_scope_names(db, rows)
    payload = TaskAlertRuleConflictOut(
        hasConflict=bool(rows),
        conflicts=[
            TaskAlertRuleOut.from_model(r, scope_summary=scope_summary(r, names))
            for r in rows
        ],
        message=(
            "已有一条适用范围和优先级完全相同的规则，两条会互相覆盖。"
            "建议调整适用范围或优先级，让生效顺序清晰可预期。"
            if rows else None
        ),
    )
    return success(data=payload.model_dump())


@alert_rule_router.post("")
@operation_log(module="任务预警规则", action="新增", description="新增预警阈值规则")
async def create_rule(
    request: Request,
    data: TaskAlertRuleCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    row = await TaskAlertRuleService.create(db, data)
    names = await TaskAlertRuleService.resolve_scope_names(db, [row])
    return success(
        data=TaskAlertRuleOut.from_model(
            row, scope_summary=scope_summary(row, names)
        ).model_dump(),
        message="规则已保存，下一轮预警计算即生效",
    )


@alert_rule_router.put("/{rule_id}")
@operation_log(module="任务预警规则", action="编辑", description="编辑预警阈值规则")
async def update_rule(
    request: Request,
    rule_id: int,
    data: TaskAlertRuleUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    row = await TaskAlertRuleService.update(db, rule_id, data)
    names = await TaskAlertRuleService.resolve_scope_names(db, [row])
    return success(
        data=TaskAlertRuleOut.from_model(
            row, scope_summary=scope_summary(row, names)
        ).model_dump(),
        message="规则已更新，下一轮预警计算即生效",
    )


@alert_rule_router.delete("/{rule_id}")
@operation_log(module="任务预警规则", action="删除", description="删除预警阈值规则")
async def delete_rule(
    request: Request,
    rule_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await TaskAlertRuleService.remove(db, rule_id)
    return success(message="规则已删除")
