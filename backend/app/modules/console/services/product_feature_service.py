"""
产品功能清单管理服务
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.common.exceptions import BizException
from app.modules.console.models.product_feature import ProductFeature, VersionFeature
from app.modules.console.schemas.product_feature import (
    ProductFeatureCreate, ProductFeatureUpdate,
)


class ProductFeatureService:

    # ---- 功能清单 CRUD ----

    @staticmethod
    async def list_features(
        db: AsyncSession,
        module: Optional[str] = None,
        status: Optional[int] = None,
    ) -> list:
        query = select(ProductFeature).where(ProductFeature.is_deleted == 0)
        if module:
            query = query.where(ProductFeature.module == module)
        if status is not None:
            query = query.where(ProductFeature.status == status)
        query = query.order_by(ProductFeature.sort_order, ProductFeature.id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create_feature(db: AsyncSession, data: ProductFeatureCreate) -> ProductFeature:
        existing = await db.execute(
            select(ProductFeature).where(
                ProductFeature.feature_code == data.feature_code,
                ProductFeature.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"功能编码 {data.feature_code} 已存在")

        feature = ProductFeature(
            feature_code=data.feature_code,
            feature_name=data.feature_name,
            module=data.module,
            description=data.description,
            required_tables=data.required_tables,
            sort_order=data.sort_order,
        )
        db.add(feature)
        await db.flush()
        return feature

    @staticmethod
    async def update_feature(
        db: AsyncSession, feature_id: int, data: ProductFeatureUpdate
    ) -> ProductFeature:
        result = await db.execute(
            select(ProductFeature).where(
                ProductFeature.id == feature_id,
                ProductFeature.is_deleted == 0,
            )
        )
        feature = result.scalar_one_or_none()
        if not feature:
            raise BizException("功能项不存在")

        for field in ("feature_name", "module", "description", "required_tables", "sort_order", "status"):
            val = getattr(data, field, None)
            if val is not None:
                setattr(feature, field, val)

        await db.flush()
        return feature

    @staticmethod
    async def delete_feature(db: AsyncSession, feature_id: int) -> None:
        result = await db.execute(
            select(ProductFeature).where(
                ProductFeature.id == feature_id,
                ProductFeature.is_deleted == 0,
            )
        )
        feature = result.scalar_one_or_none()
        if not feature:
            raise BizException("功能项不存在")
        feature.is_deleted = 1
        await db.flush()

    # ---- 版本-功能关联 ----

    @staticmethod
    async def get_version_features(db: AsyncSession, version_id: int) -> list:
        """获取版本的功能清单"""
        result = await db.execute(
            select(VersionFeature, ProductFeature)
            .join(ProductFeature, VersionFeature.feature_id == ProductFeature.id)
            .where(
                VersionFeature.version_id == version_id,
                VersionFeature.is_deleted == 0,
                VersionFeature.status == 1,
                ProductFeature.is_deleted == 0,
            )
            .order_by(ProductFeature.sort_order)
        )
        rows = result.all()
        return [
            {
                "id": vf.id,
                "version_id": vf.version_id,
                "feature_id": vf.feature_id,
                "status": vf.status,
                "feature_code": pf.feature_code,
                "feature_name": pf.feature_name,
                "module": pf.module,
                "required_tables": pf.required_tables,
            }
            for vf, pf in rows
        ]

    @staticmethod
    async def assign_features(
        db: AsyncSession, version_id: int, feature_ids: List[int]
    ) -> None:
        """批量设置版本的功能清单（全量替换）"""
        # 软删除现有关联
        existing = await db.execute(
            select(VersionFeature).where(
                VersionFeature.version_id == version_id,
                VersionFeature.is_deleted == 0,
            )
        )
        for vf in existing.scalars().all():
            vf.is_deleted = 1

        # 创建新关联
        for fid in feature_ids:
            vf = VersionFeature(
                version_id=version_id,
                feature_id=fid,
                status=1,
            )
            db.add(vf)

        await db.flush()
        logger.info(f"版本 {version_id} 已更新功能清单: {feature_ids}")

    @staticmethod
    async def get_feature_codes_by_version_ids(
        db: AsyncSession, version_ids: List[int]
    ) -> List[str]:
        """根据版本ID列表获取所有 feature_code"""
        if not version_ids:
            return []
        result = await db.execute(
            select(ProductFeature.feature_code)
            .join(VersionFeature, VersionFeature.feature_id == ProductFeature.id)
            .where(
                VersionFeature.version_id.in_(version_ids),
                VersionFeature.is_deleted == 0,
                VersionFeature.status == 1,
                ProductFeature.is_deleted == 0,
                ProductFeature.status == 1,
            )
        )
        return list(set(result.scalars().all()))

    @staticmethod
    async def get_required_tables_by_version_id(
        db: AsyncSession, version_id: int
    ) -> List[str]:
        """根据版本ID获取所有需要的租户库表名"""
        result = await db.execute(
            select(ProductFeature.required_tables)
            .join(VersionFeature, VersionFeature.feature_id == ProductFeature.id)
            .where(
                VersionFeature.version_id == version_id,
                VersionFeature.is_deleted == 0,
                VersionFeature.status == 1,
                ProductFeature.is_deleted == 0,
                ProductFeature.status == 1,
            )
        )
        tables = set()
        for row in result.scalars().all():
            if row and isinstance(row, list):
                tables.update(row)
        return list(tables)
