"""
租户管理接口
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.schemas.tenant import (
    TenantCreate, TenantUpdate, TenantStatusUpdate, TenantOut,
    TenantProductCreate, TenantProductOut,
)
from app.modules.console.services.tenant_service import TenantService

router = APIRouter()


# ============================================================
# 租户 CRUD
# ============================================================

@router.get("/page")
async def page_tenants(
    page: int = Query(1),
    limit: int = Query(20),
    keyword: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询租户"""
    result = await TenantService.page_tenants(
        db, page=page, limit=limit, keyword=keyword, status=status
    )
    return success(data=result)


@router.get("/{tenant_id}")
async def get_tenant(
    tenant_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """获取租户详情"""
    tenant = await TenantService.get_tenant_by_id(db, tenant_id)
    if not tenant:
        return fail("租户不存在")
    return success(data=TenantOut.from_model(tenant).model_dump())


@router.post("")
async def create_tenant(
    data: TenantCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """创建租户（注册企业）"""
    tenant = await TenantService.create_tenant(db, data)
    return success(data=TenantOut.from_model(tenant).model_dump(), message="创建成功")


@router.put("")
async def update_tenant(
    data: TenantUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """更新租户"""
    tenant = await TenantService.update_tenant(db, data)
    return success(data=TenantOut.from_model(tenant).model_dump(), message="更新成功")


@router.delete("/batch")
async def batch_delete_tenants(
    ids: List[int] = Body(..., embed=False),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """批量删除租户"""
    await TenantService.batch_delete(db, ids)
    return success(message="删除成功")


@router.put("/status")
async def update_tenant_status(
    data: TenantStatusUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """更新租户状态（启用/停用）"""
    await TenantService.update_status(db, data.id, data.status)
    return success(message="操作成功")


# ============================================================
# 租户产品授权
# ============================================================

@router.get("/{tenant_id}/products")
async def list_tenant_products(
    tenant_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """查询企业已授权的产品列表"""
    items = await TenantService.list_tenant_products(db, tenant_id)
    return success(data=[p.model_dump() for p in items])


@router.post("/{tenant_id}/products")
async def assign_product(
    tenant_id: int,
    data: TenantProductCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """为企业开通产品版本授权"""
    product = await TenantService.assign_product(db, tenant_id, data)
    return success(
        data=TenantProductOut.from_model(product).model_dump(),
        message="授权成功"
    )


@router.delete("/{tenant_id}/products/{product_id}")
async def remove_product(
    tenant_id: int,
    product_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """取消产品授权"""
    await TenantService.remove_product(db, tenant_id, product_id)
    return success(message="已取消授权")
