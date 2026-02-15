"""
租户管理接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.schemas.tenant import TenantCreate, TenantUpdate, TenantOut, TenantListOut
from app.modules.console.services.tenant_service import TenantService

router = APIRouter()


@router.get("")
async def list_tenants(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取租户列表"""
    items, total = await TenantService.get_tenant_list(
        db, page=page, page_size=page_size, keyword=keyword, status=status
    )
    return success(data={
        "list": [TenantListOut.model_validate(t).model_dump() for t in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{tenant_id}")
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """获取租户详情"""
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    if not tenant:
        return fail("租户不存在")
    return success(data=TenantOut.model_validate(tenant).model_dump())


@router.post("")
async def create_tenant(
    data: TenantCreate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """创建租户"""
    tenant = await TenantService.create_tenant(db, data)
    return success(data=TenantOut.model_validate(tenant).model_dump(), message="创建成功")


@router.put("/{tenant_id}")
async def update_tenant(
    tenant_id: int,
    data: TenantUpdate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """更新租户"""
    tenant = await TenantService.update_tenant(db, tenant_id, data)
    return success(data=TenantOut.model_validate(tenant).model_dump(), message="更新成功")


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """删除租户"""
    await TenantService.delete_tenant(db, tenant_id)
    return success(message="删除成功")
