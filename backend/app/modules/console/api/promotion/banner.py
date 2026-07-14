"""
推广位 Banner 管理接口（Console）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success, fail
from app.modules.console.schemas.promotion.banner import (
    BannerCreate,
    BannerUpdate,
    BannerOut,
)
from app.modules.console.services.promotion.banner_service import BannerService

router = APIRouter()


@router.get("/page")
async def page_banners(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    target_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """分页查询 Banner"""
    items, total = await BannerService.page(
        db, page=page, limit=limit, keyword=keyword,
        status=status, target_type=target_type,
    )
    return success(data={
        "list": [BannerOut.model_validate(x).model_dump(mode="json") for x in items],
        "total": total,
        "page": page,
        "limit": limit,
    })


@router.get("/version-options")
async def version_options(
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """定向下拉：产品版本"""
    return success(data=await BannerService.version_options(db))


@router.get("/tenant-options")
async def tenant_options(
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """定向下拉：租户"""
    return success(data=await BannerService.tenant_options(db, keyword=keyword))


@router.get("/{banner_id}")
async def get_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """Banner 详情"""
    banner = await BannerService.get_by_id(db, banner_id)
    if not banner:
        return fail("Banner 不存在")
    return success(data=BannerOut.model_validate(banner).model_dump(mode="json"))


@router.post("")
async def create_banner(
    data: BannerCreate,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """新建 Banner（默认草稿）"""
    banner = await BannerService.create(db, data, created_by=current_user.user_id)
    return success(data=BannerOut.model_validate(banner).model_dump(mode="json"), message="创建成功")


@router.put("/{banner_id}")
async def update_banner(
    banner_id: int,
    data: BannerUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """更新 Banner"""
    banner = await BannerService.update(db, banner_id, data)
    return success(data=BannerOut.model_validate(banner).model_dump(mode="json"), message="更新成功")


@router.delete("/{banner_id}")
async def delete_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """删除 Banner（软删除）"""
    await BannerService.delete(db, banner_id)
    return success(message="删除成功")


@router.post("/{banner_id}/publish")
async def publish_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """上线"""
    await BannerService.change_status(db, banner_id, "published")
    return success(message="已上线")


@router.post("/{banner_id}/offline")
async def offline_banner(
    banner_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """下线"""
    await BannerService.change_status(db, banner_id, "offline")
    return success(message="已下线")


@router.get("/{banner_id}/stats")
async def banner_stats(
    banner_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """聚合统计：总览 + 按租户"""
    summary = await BannerService.stats_summary(db, banner_id)
    by_tenant = await BannerService.stats_by_tenant(db, banner_id)
    return success(data={"summary": summary, "by_tenant": by_tenant})


@router.get("/{banner_id}/events")
async def banner_events(
    banner_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = Query(None, description="view/click"),
    tenant_code: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """事件明细分页：哪些租户的哪些用户在何时 view/click"""
    items, total = await BannerService.event_page(
        db, banner_id, page=page, limit=limit,
        event_type=event_type, tenant_code=tenant_code,
    )
    from app.modules.console.schemas.promotion.banner import BannerEventItem
    return success(data={
        "list": [BannerEventItem.model_validate(x).model_dump(mode="json") for x in items],
        "total": total,
        "page": page,
        "limit": limit,
    })
