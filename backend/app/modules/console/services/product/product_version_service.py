"""
产品版本管理服务
"""

from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.schemas.product.product_version import (
    ProductVersionCreate,
    ProductVersionUpdate,
)


class ProductVersionService:
    """产品版本管理服务"""

    @staticmethod
    async def create_version(
        db: AsyncSession, data: ProductVersionCreate
    ) -> ProductVersion:
        """创建产品版本"""
        existing = await db.execute(
            select(ProductVersion).where(
                ProductVersion.version_code == data.version_code,
                ProductVersion.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException("版本编码已存在")

        version = ProductVersion(**data.model_dump())
        db.add(version)
        await db.flush()
        return version

    @staticmethod
    async def get_version_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ProductVersion], int]:
        """获取产品版本列表"""
        query = select(ProductVersion).where(ProductVersion.is_deleted == 0)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(ProductVersion.sort_order)
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_version_by_id(
        db: AsyncSession, version_id: int
    ) -> Optional[ProductVersion]:
        """根据ID获取产品版本"""
        result = await db.execute(
            select(ProductVersion).where(
                ProductVersion.id == version_id, ProductVersion.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_version(
        db: AsyncSession, version_id: int, data: ProductVersionUpdate
    ) -> Optional[ProductVersion]:
        """更新产品版本"""
        version = await ProductVersionService.get_version_by_id(db, version_id)
        if not version:
            raise BizException("产品版本不存在")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(version, key, value)

        await db.flush()
        return version

    @staticmethod
    async def delete_version(db: AsyncSession, version_id: int) -> bool:
        """删除产品版本（软删除）"""
        version = await ProductVersionService.get_version_by_id(db, version_id)
        if not version:
            raise BizException("产品版本不存在")
        version.is_deleted = 1
        await db.flush()
        return True
