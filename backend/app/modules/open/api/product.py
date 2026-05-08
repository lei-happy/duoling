"""
产品信息公开查询接口
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db
from app.common.response import success
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.models.product.product_feature import (
    ProductFeature, VersionFeature,
)
from app.modules.console.schemas.product.product_version import ProductVersionOut

router = APIRouter()


@router.get("/versions")
async def list_product_versions(
    db: AsyncSession = Depends(get_platform_db),
):
    """获取产品版本列表（公开，无需登录）"""
    result = await db.execute(
        select(ProductVersion)
        .where(ProductVersion.is_deleted == 0, ProductVersion.status == 1)
        .order_by(ProductVersion.sort_order)
    )
    items = result.scalars().all()
    return success(data=[ProductVersionOut.model_validate(v).model_dump(by_alias=True) for v in items])


@router.get("/version-features")
async def list_version_features_matrix(
    db: AsyncSession = Depends(get_platform_db),
):
    """版本×功能矩阵（公开，无需登录）。

    返回三块：
      - versions: [{ id, versionCode, versionName, description, maxUsers, maxVehicles, price, sortOrder }]
      - modules: 已 distinct 的功能模块编码列表（用于前端分组），按出现次序
      - features: [{ featureCode, featureName, module, sortOrder, includedIn: ['lite','basic',...] }]

    供"查看升级方案"对比页使用，前端无需自己拼版本-功能映射。
    """
    v_res = await db.execute(
        select(ProductVersion)
        .where(ProductVersion.is_deleted == 0, ProductVersion.status == 1)
        .order_by(ProductVersion.sort_order, ProductVersion.id)
    )
    versions = list(v_res.scalars().all())

    f_res = await db.execute(
        select(ProductFeature)
        .where(ProductFeature.is_deleted == 0, ProductFeature.status == 1)
        .order_by(ProductFeature.sort_order, ProductFeature.id)
    )
    features = list(f_res.scalars().all())

    vf_res = await db.execute(
        select(VersionFeature.version_id, VersionFeature.feature_id)
        .where(VersionFeature.is_deleted == 0, VersionFeature.status == 1)
    )
    vf_pairs = vf_res.all()

    version_id_to_code = {v.id: v.version_code for v in versions}
    feature_id_to_codes_in_versions: dict = {f.id: [] for f in features}
    for version_id, feature_id in vf_pairs:
        if feature_id in feature_id_to_codes_in_versions and version_id in version_id_to_code:
            feature_id_to_codes_in_versions[feature_id].append(
                version_id_to_code[version_id]
            )

    modules: list = []
    for f in features:
        if f.module and f.module not in modules:
            modules.append(f.module)

    return success(data={
        "versions": [
            {
                "id": v.id,
                "versionCode": v.version_code,
                "versionName": v.version_name,
                "description": v.description,
                "maxUsers": v.max_users,
                "maxVehicles": v.max_vehicles,
                "price": v.price,
                "sortOrder": v.sort_order,
            }
            for v in versions
        ],
        "modules": modules,
        "features": [
            {
                "featureCode": f.feature_code,
                "featureName": f.feature_name,
                "module": f.module,
                "description": f.description,
                "sortOrder": f.sort_order,
                "includedIn": sorted(set(feature_id_to_codes_in_versions.get(f.id, []))),
            }
            for f in features
        ],
    })
