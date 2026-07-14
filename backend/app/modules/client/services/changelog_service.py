"""
客户端工作台 - 产品版本升级说明服务

版本升级说明（changelog）配置于平台库（zt_platform），Client 通过平台库 Session
读取已发布记录，并按用户维度记录"已弹框已读"状态，实现关键版本只强制弹框一次。
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.changelog.changelog import Changelog, ChangelogRead


class ClientChangelogService:
    """租户端版本升级说明展示与已读服务"""

    @staticmethod
    async def list_published(
        db: AsyncSession, page: int = 1, limit: int = 20
    ) -> Tuple[List[Changelog], int]:
        """分页返回已发布的版本升级说明（按排序号、发布日期倒序）"""
        base = select(Changelog).where(
            Changelog.is_deleted == 0, Changelog.status == 1
        )
        total = (
            await db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0
        query = (
            base.order_by(
                Changelog.sort_order.desc(), Changelog.release_date.desc(), Changelog.id.desc()
            )
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list((await db.execute(query)).scalars().all())
        return items, total

    @staticmethod
    async def list_unread_popups(
        db: AsyncSession, user_id: int
    ) -> List[Changelog]:
        """返回当前用户尚未读过、且需要强制弹框的版本升级说明"""
        read_subq = (
            select(ChangelogRead.changelog_id)
            .where(
                ChangelogRead.user_id == user_id,
                ChangelogRead.is_deleted == 0,
            )
            .subquery()
        )
        query = (
            select(Changelog)
            .where(
                Changelog.is_deleted == 0,
                Changelog.status == 1,
                Changelog.is_popup == 1,
                Changelog.id.notin_(select(read_subq.c.changelog_id)),
            )
            .order_by(Changelog.sort_order.desc(), Changelog.release_date.desc(), Changelog.id.desc())
        )
        return list((await db.execute(query)).scalars().all())

    @staticmethod
    async def mark_read(
        db: AsyncSession,
        changelog_ids: List[int],
        user_id: int,
        tenant_code: Optional[str] = None,
    ) -> int:
        """标记版本升级说明为已读（幂等，重复标记忽略）。返回本次新增标记数量。"""
        if not changelog_ids:
            return 0

        # 已存在的已读记录，避免重复插入触发唯一约束
        existed = set(
            (
                await db.execute(
                    select(ChangelogRead.changelog_id).where(
                        ChangelogRead.user_id == user_id,
                        ChangelogRead.changelog_id.in_(changelog_ids),
                        ChangelogRead.is_deleted == 0,
                    )
                )
            )
            .scalars()
            .all()
        )
        # 仅对真实存在的已发布记录记账
        valid_ids = set(
            (
                await db.execute(
                    select(Changelog.id).where(
                        Changelog.id.in_(changelog_ids),
                        Changelog.is_deleted == 0,
                    )
                )
            )
            .scalars()
            .all()
        )

        now_t = datetime.now()
        added = 0
        for cid in set(changelog_ids):
            if cid in existed or cid not in valid_ids:
                continue
            db.add(
                ChangelogRead(
                    changelog_id=cid,
                    user_id=user_id,
                    tenant_code=tenant_code,
                    read_at=now_t,
                )
            )
            added += 1
        try:
            await db.flush()
        except IntegrityError:
            # 并发下的唯一约束冲突静默忽略
            await db.rollback()
            return 0
        return added
