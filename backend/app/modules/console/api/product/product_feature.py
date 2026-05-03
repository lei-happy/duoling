"""
产品功能清单管理 API
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.common.response import success
from app.modules.console.schemas.product.product_feature import (
    ProductFeatureCreate, ProductFeatureUpdate,
    ProductFeatureOut, VersionFeatureAssign,
)
from app.modules.console.services.product.product_feature_service import ProductFeatureService

router = APIRouter()


@router.get("")
async def list_features(
    module: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None, description="按功能编码/名称模糊匹配"),
    page: Optional[int] = Query(None, description="为空时返回全量列表（兼容旧调用）"),
    page_size: Optional[int] = Query(None, alias="pageSize"),
    db: AsyncSession = Depends(get_platform_db),
    _=Depends(get_current_user),
):
    """获取功能清单列表

    - 不传 page 时：返回全量数组（兼容版本-功能配置弹窗等旧调用）
    - 传 page 时：返回 {list, total, page, pageSize}，并附带每条 assignedVersions
    """
    if page is None:
        items = await ProductFeatureService.list_features(
            db, module=module, status=status, keyword=keyword,
        )
        return success(
            data=[
                ProductFeatureOut.model_validate(f).model_dump(by_alias=True)
                for f in items
            ]
        )

    page_size = page_size or 20
    paged = await ProductFeatureService.page_features(
        db,
        page=page,
        page_size=page_size,
        module=module,
        status=status,
        keyword=keyword,
    )
    assigned_map = paged["assignedVersionsMap"]
    list_data = []
    for f in paged["list"]:
        out = ProductFeatureOut.model_validate(f).model_dump(by_alias=True)
        out["assignedVersions"] = assigned_map.get(f.id, [])
        list_data.append(out)
    return success(data={
        "list": list_data,
        "total": paged["total"],
        "page": paged["page"],
        "pageSize": paged["pageSize"],
    })


@router.get("/health-check")
async def feature_health_check(
    db: AsyncSession = Depends(get_platform_db),
    _=Depends(get_current_user),
):
    """全链路一致性体检：返回脏 feature_code / 未绑版本的 feature_code 清单"""
    result = await ProductFeatureService.health_check(db)
    return success(data=result)


@router.post("")
async def create_feature(
    data: ProductFeatureCreate,
    db: AsyncSession = Depends(get_platform_db),
    _=Depends(get_current_user),
):
    """创建功能项"""
    feature = await ProductFeatureService.create_feature(db, data)
    return success(data=ProductFeatureOut.model_validate(feature).model_dump(by_alias=True))


@router.put("/{feature_id}")
async def update_feature(
    feature_id: int,
    data: ProductFeatureUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _=Depends(get_current_user),
):
    """更新功能项"""
    feature = await ProductFeatureService.update_feature(db, feature_id, data)
    return success(data=ProductFeatureOut.model_validate(feature).model_dump(by_alias=True))


@router.delete("/{feature_id}")
async def delete_feature(
    feature_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _=Depends(get_current_user),
):
    """删除功能项"""
    await ProductFeatureService.delete_feature(db, feature_id)
    return success()


@router.get("/version/{version_id}")
async def get_version_features(
    version_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _=Depends(get_current_user),
):
    """获取版本的功能清单"""
    items = await ProductFeatureService.get_version_features(db, version_id)
    return success(data=items)


@router.post("/version/assign")
async def assign_version_features(
    data: VersionFeatureAssign,
    db: AsyncSession = Depends(get_platform_db),
    _=Depends(get_current_user),
):
    """批量分配功能到版本（全量替换）"""
    await ProductFeatureService.assign_features(db, data.version_id, data.feature_ids)
    return success()
