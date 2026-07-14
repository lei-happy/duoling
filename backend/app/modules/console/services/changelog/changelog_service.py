"""
产品更新日志管理服务
"""

from typing import Optional, Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.changelog.changelog import Changelog
from app.modules.console.schemas.changelog.changelog import (
    ChangelogCreate,
    ChangelogUpdate,
)


class ChangelogService:
    """产品更新日志管理服务"""

    @staticmethod
    async def create_changelog(
        db: AsyncSession, data: ChangelogCreate
    ) -> Changelog:
        """创建更新记录"""
        changelog = Changelog(**data.model_dump())
        db.add(changelog)
        await db.flush()
        # 显式回读服务端默认值（created_at/updated_at 等），避免后续同步序列化触发异步惰性加载
        await db.refresh(changelog)
        return changelog

    @staticmethod
    async def get_changelog_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        status: Optional[int] = None,
    ) -> Tuple[List[Changelog], int]:
        """获取更新记录列表（Console 用，可筛选状态）"""
        query = select(Changelog).where(Changelog.is_deleted == 0)
        if status is not None:
            query = query.where(Changelog.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Changelog.sort_order.desc(), Changelog.release_date.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = list(result.scalars().all())

        return items, total

    @staticmethod
    async def get_public_changelog_list(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Changelog], int]:
        """获取公开更新记录列表（仅已发布）"""
        return await ChangelogService.get_changelog_list(
            db, page, page_size, status=1
        )

    @staticmethod
    async def get_changelog_by_id(
        db: AsyncSession, changelog_id: int
    ) -> Optional[Changelog]:
        """根据ID获取更新记录"""
        result = await db.execute(
            select(Changelog).where(
                Changelog.id == changelog_id, Changelog.is_deleted == 0
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_changelog(
        db: AsyncSession, changelog_id: int, data: ChangelogUpdate
    ) -> Optional[Changelog]:
        """更新更新记录"""
        changelog = await ChangelogService.get_changelog_by_id(db, changelog_id)
        if not changelog:
            raise BizException("更新记录不存在")

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(changelog, key, value)

        await db.flush()
        await db.refresh(changelog)
        return changelog

    @staticmethod
    async def delete_changelog(db: AsyncSession, changelog_id: int) -> bool:
        """删除更新记录（软删除）"""
        changelog = await ChangelogService.get_changelog_by_id(db, changelog_id)
        if not changelog:
            raise BizException("更新记录不存在")
        changelog.is_deleted = 1
        await db.flush()
        return True
