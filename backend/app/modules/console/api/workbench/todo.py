"""
管理后台 - 各租户待办汇总查询（只读平台库 + 冗余姓名）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.client.services.todo_task_service import TodoTaskService

router = APIRouter()


@router.get("/page")
async def page_tenant_todos(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    tenant_code: Optional[str] = Query(None, alias="tenantCode"),
    status: Optional[int] = Query(None, ge=0, le=3),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询租户待办（跨租户运营可见）"""
    items, total = await TodoTaskService.page_for_console(
        db,
        page=page,
        page_size=limit,
        tenant_code=tenant_code,
        status=status,
    )
    return success(data={"list": items, "count": total})
