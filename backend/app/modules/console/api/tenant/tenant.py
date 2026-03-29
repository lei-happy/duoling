"""
租户管理接口
"""

from typing import Optional, List

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.schemas.tenant.tenant import (
    TenantCreate, TenantUpdate, TenantStatusUpdate, TenantOut,
    TenantProductCreate, TenantProductOut,
    TenantFollowPoolUpdate,
)
from app.modules.console.services.tenant.tenant_service import TenantService

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
    lifecycle: Optional[str] = Query(None, description="生命周期: new/trial/follow_up/paid/churned/all"),
    versionCode: Optional[str] = Query(None, description="版本编码筛选(付费客户): pro/enterprise"),
    expireWarning: bool = Query(False, description="仅显示到期预警客户"),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询租户"""
    result = await TenantService.page_tenants(
        db, page=page, limit=limit, keyword=keyword, status=status,
        lifecycle=lifecycle, version_code=versionCode,
        expire_warning=expireWarning,
    )
    return success(data=result)


# ============================================================
# 生命周期统计（放在 /{tenant_id} 之前避免路由冲突）
# ============================================================

@router.get("/stats")
async def tenant_stats(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """各生命周期阶段客户数量统计"""
    stats = await TenantService.lifecycle_stats(db)
    return success(data=stats)


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
    tenant, _is_existing_user = await TenantService.create_tenant(db, data)
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


@router.post("/check-expirations")
async def check_expirations(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """手动触发过期检查"""
    affected = await TenantService.check_expirations(db)
    return success(data={"affected": affected}, message=f"检查完成，{affected} 个客户状态已更新")


# ============================================================
# 跟进池
# ============================================================

@router.put("/follow-pool")
async def update_follow_pool(
    data: TenantFollowPoolUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """标记/移出跟进池"""
    await TenantService.update_follow_pool(db, data)
    action = "已加入跟进池" if data.inFollowPool == 1 else "已移出跟进池"
    return success(message=action)


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
