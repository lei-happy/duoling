"""
客户端工作台 - 待办
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import TenantException
from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.workbench.todo_task import TodoTaskCreate, TodoTaskUpdate, TodoTaskStatusBody
from app.modules.client.services.todo_task_service import TodoTaskService

router = APIRouter()


def _require_tenant(current_user: TokenData) -> str:
    if not current_user.tenant_code:
        raise TenantException("缺少租户信息")
    return current_user.tenant_code


@router.get("/users-for-assign")
async def users_for_assign(
    q: Optional[str] = Query(None, description="姓名/昵称/手机号关键词"),
    current_user: TokenData = Depends(get_current_user),
    tenant_db: AsyncSession = Depends(get_tenant_db),
):
    """可指派员工（biz_user.id + 展示名）"""
    _require_tenant(current_user)
    data = await TodoTaskService.list_assignable_users(tenant_db, keyword=q)
    return success(data=data)


@router.get("/stats")
async def todo_stats(
    my_tasks: bool = Query(
        True,
        description="仅与我相关：指派给我或我创建的",
    ),
    current_user: TokenData = Depends(get_current_user),
    pdb: AsyncSession = Depends(get_platform_db),
    tenant_db: AsyncSession = Depends(get_tenant_db),
):
    tenant_code = _require_tenant(current_user)
    data = await TodoTaskService.stats(
        pdb,
        tenant_db,
        tenant_code,
        current_user.user_id,
        my_tasks=my_tasks,
    )
    return success(data=data)


@router.get("/tasks")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[int] = Query(None, ge=0, le=3),
    my_tasks: bool = Query(
        True,
        description="仅与我相关：指派给我或我创建的",
    ),
    current_user: TokenData = Depends(get_current_user),
    pdb: AsyncSession = Depends(get_platform_db),
    tenant_db: AsyncSession = Depends(get_tenant_db),
):
    tenant_code = _require_tenant(current_user)
    data = await TodoTaskService.page_tasks(
        pdb,
        tenant_db,
        tenant_code,
        current_user.user_id,
        page=page,
        page_size=page_size,
        status=status,
        my_tasks=my_tasks,
    )
    return success(data=data)


@router.post("")
async def create_task(
    body: TodoTaskCreate,
    current_user: TokenData = Depends(get_current_user),
    pdb: AsyncSession = Depends(get_platform_db),
    tenant_db: AsyncSession = Depends(get_tenant_db),
):
    tenant_code = _require_tenant(current_user)
    data = await TodoTaskService.create_task(
        pdb,
        tenant_db,
        tenant_code,
        current_user.user_id,
        body,
    )
    return success(data=data)


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    body: TodoTaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    pdb: AsyncSession = Depends(get_platform_db),
    tenant_db: AsyncSession = Depends(get_tenant_db),
):
    tenant_code = _require_tenant(current_user)
    patch_keys = set(body.model_dump(exclude_unset=True).keys())
    data = await TodoTaskService.apply_task_update(
        pdb,
        tenant_db,
        tenant_code,
        task_id,
        body,
        patch_keys,
    )
    return success(data=data)


@router.patch("/{task_id}/status")
async def patch_status(
    task_id: int,
    body: TodoTaskStatusBody,
    current_user: TokenData = Depends(get_current_user),
    pdb: AsyncSession = Depends(get_platform_db),
):
    tenant_code = _require_tenant(current_user)
    data = await TodoTaskService.set_status(pdb, tenant_code, task_id, body.status)
    return success(data=data)


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: TokenData = Depends(get_current_user),
    pdb: AsyncSession = Depends(get_platform_db),
):
    tenant_code = _require_tenant(current_user)
    await TodoTaskService.delete_task(pdb, tenant_code, task_id)
    return success(message="删除成功")
