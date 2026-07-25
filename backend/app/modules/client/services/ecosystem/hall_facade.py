"""大厅读接口的装配层（读平台库）

把「查一页挂牌」到「一页可直接返回的 JSON」之间的四步固定流程收在一处：

1. ``EcoPostQueryService`` 取分页数据（安全范围在那里收口）
2. ``load_related`` 批量取扩展表 / 目的地 / 信誉，避免 N+1
3. ``EcoViewerContextBuilder.build_for_posts`` 一次性算出查看方与整页挂牌的关系
4. ``EcoPostSerializer`` 按层级裁剪字段

这四步顺序错一步就出问题：漏了第 2 步是性能问题（20 条卡片 40 次查询），
漏了第 3 步是**安全问题**——没有洽谈关系的空上下文会让所有卡片退化到匿名层，
看起来「更安全」，实际是把已经解锁的信息又藏起来，用户会以为系统坏了。
放在 API 层各写一遍，迟早有一个接口漏掉其中一步。
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.services.ecosystem.post_query_service import (
    EcoPostQueryService,
    HallFilter,
    MyPostFilter,
)
from app.modules.client.services.ecosystem.serializer import EcoPostSerializer
from app.modules.client.services.ecosystem.viewer_context import (
    EcoViewerContextBuilder,
)
from app.modules.console.models.ecosystem.constants import PostType
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_view import SysEcoPostView

# 发布方看到的热度反馈的回溯窗口，对应前端「近 7 天有 N 家同行看过」
VIEWER_STATS_DAYS = 7


class EcoHallFacade:
    """大厅与「我发布的」读接口装配"""

    # ------------------------------------------------------------------
    # 大厅列表
    # ------------------------------------------------------------------

    @staticmethod
    async def page_hall(
        platform_db: AsyncSession,
        *,
        post_type: int,
        viewer_tenant_code: str,
        flt: HallFilter,
    ) -> Dict[str, Any]:
        posts, total = await EcoPostQueryService.page_hall(
            platform_db,
            post_type=post_type,
            viewer_tenant_code=viewer_tenant_code,
            flt=flt,
        )
        rows = await EcoHallFacade._serialize_many(
            platform_db,
            posts=posts,
            post_type=post_type,
            viewer_tenant_code=viewer_tenant_code,
        )
        return {"list": rows, "total": total, "count": total,
                "page": flt.page, "pageSize": flt.page_size}

    # ------------------------------------------------------------------
    # 挂牌详情
    # ------------------------------------------------------------------

    @staticmethod
    async def hall_detail(
        platform_db: AsyncSession,
        *,
        post_id: int,
        viewer_tenant_code: str,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """大厅详情

        取不到时的文案不能是「挂牌不存在」：绝大多数情况是被发布方下架或已成交，
        用户需要知道的是「这条没了，去看别的」，而不是怀疑自己点错了链接。
        """
        now = now or datetime.now()
        post = await EcoPostQueryService.get_hall_post(
            platform_db, post_id=post_id, viewer_tenant_code=viewer_tenant_code
        )
        if post is None:
            raise BizException("这条信息已经不在大厅里了，可能已被发布方停止展示或已达成合作")

        is_owner = post.owner_tenant_code == viewer_tenant_code
        if not is_owner:
            await EcoHallFacade._record_view(
                platform_db, post=post, viewer_tenant_code=viewer_tenant_code, now=now
            )

        return await EcoHallFacade._serialize_one(
            platform_db, post=post, viewer_tenant_code=viewer_tenant_code
        )

    # ------------------------------------------------------------------
    # 我发布的
    # ------------------------------------------------------------------

    @staticmethod
    async def page_mine(
        platform_db: AsyncSession,
        *,
        owner_tenant_code: str,
        flt: MyPostFilter,
        with_counts: bool = True,
    ) -> Dict[str, Any]:
        posts, total = await EcoPostQueryService.page_mine(
            platform_db, owner_tenant_code=owner_tenant_code, flt=flt
        )

        # 「我发布的」两个大厅混排，扩展表要按类型分别装载
        rows: List[Dict[str, Any]] = []
        for post_type in (PostType.CARGO, PostType.CAPACITY):
            group = [p for p in posts if int(p.post_type) == post_type]
            if group:
                rows.extend(
                    await EcoHallFacade._serialize_many(
                        platform_db,
                        posts=group,
                        post_type=post_type,
                        viewer_tenant_code=owner_tenant_code,
                    )
                )
        # 分组装载打乱了分页顺序，按原始顺序还原
        order = {int(p.id): i for i, p in enumerate(posts)}
        rows.sort(key=lambda r: order.get(int(r["id"]), 0))

        data: Dict[str, Any] = {
            "list": rows, "total": total, "count": total,
            "page": flt.page, "pageSize": flt.page_size,
        }
        if with_counts:
            data["statusCounts"] = await EcoPostQueryService.count_mine_by_status(
                platform_db, owner_tenant_code=owner_tenant_code, flt=flt
            )
        return data

    @staticmethod
    async def mine_detail(
        platform_db: AsyncSession, *, post_id: int, owner_tenant_code: str
    ) -> Dict[str, Any]:
        """自己发布的挂牌详情（不限状态，带热度反馈）"""
        post = await EcoHallFacade.load_own_post(
            platform_db, post_id=post_id, owner_tenant_code=owner_tenant_code
        )
        return await EcoHallFacade._serialize_one(
            platform_db, post=post, viewer_tenant_code=owner_tenant_code
        )

    @staticmethod
    async def load_own_post(
        platform_db: AsyncSession, *, post_id: int, owner_tenant_code: str
    ) -> SysEcoPost:
        post = await EcoPostQueryService.get_own_post(
            platform_db, post_id=post_id, owner_tenant_code=owner_tenant_code
        )
        if post is None:
            raise BizException("没找到这条挂牌，可能已经被删除了")
        return post

    # ------------------------------------------------------------------
    # 序列化
    # ------------------------------------------------------------------

    @staticmethod
    async def _serialize_many(
        platform_db: AsyncSession,
        *,
        posts: Sequence[SysEcoPost],
        post_type: int,
        viewer_tenant_code: str,
    ) -> List[Dict[str, Any]]:
        if not posts:
            return []

        related = await EcoPostQueryService.load_related(
            platform_db, posts, post_type
        )
        viewer = await EcoViewerContextBuilder.build_for_posts(
            platform_db, viewer_tenant_code, [p.id for p in posts]
        )

        rows: List[Dict[str, Any]] = []
        for post in posts:
            ext = related["ext"].get(post.id)
            rows.append(
                EcoPostSerializer.serialize(
                    post,
                    viewer,
                    cargo=ext if int(post.post_type) == PostType.CARGO else None,
                    capacity=ext if int(post.post_type) != PostType.CARGO else None,
                    destinations=related["dests"].get(post.id, []),
                    credit=related["credits"].get(post.owner_tenant_code),
                    detail=False,
                )
            )
        return rows

    @staticmethod
    async def _serialize_one(
        platform_db: AsyncSession,
        *,
        post: SysEcoPost,
        viewer_tenant_code: str,
    ) -> Dict[str, Any]:
        post_type = int(post.post_type)
        related = await EcoPostQueryService.load_related(
            platform_db, [post], post_type
        )
        viewer = await EcoViewerContextBuilder.build_for_posts(
            platform_db, viewer_tenant_code, [post.id]
        )
        ext = related["ext"].get(post.id)

        viewer_stats = None
        if post.owner_tenant_code == viewer_tenant_code:
            viewer_stats = await EcoHallFacade.viewer_stats(platform_db, post=post)

        return EcoPostSerializer.serialize(
            post,
            viewer,
            cargo=ext if post_type == PostType.CARGO else None,
            capacity=ext if post_type != PostType.CARGO else None,
            destinations=related["dests"].get(post.id, []),
            credit=related["credits"].get(post.owner_tenant_code),
            viewer_stats=viewer_stats,
            detail=True,
        )

    # ------------------------------------------------------------------
    # 浏览统计
    # ------------------------------------------------------------------

    @staticmethod
    async def _record_view(
        platform_db: AsyncSession,
        *,
        post: SysEcoPost,
        viewer_tenant_code: str,
        now: datetime,
    ) -> None:
        """记一次浏览

        按「挂牌 + 查看企业 + 日期」聚合，一条 upsert 完成。**失败只记日志**：
        浏览统计是给发布方看热度的，为它把一次正常的详情查看变成报错不划算。
        """
        try:
            stmt = mysql_insert(SysEcoPostView.__table__).values(
                post_id=int(post.id),
                owner_tenant_code=post.owner_tenant_code,
                viewer_tenant_code=viewer_tenant_code,
                view_date=now.date(),
                view_count=1,
                first_viewed_at=now,
                last_viewed_at=now,
            )
            await platform_db.execute(
                stmt.on_duplicate_key_update(
                    view_count=SysEcoPostView.__table__.c.view_count + 1,
                    last_viewed_at=now,
                )
            )
            # 主表的 view_count 是列表页要展示的数，与明细表一起加
            post.view_count = int(post.view_count or 0) + 1
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"挂牌浏览统计写入失败 post_id={post.id}: {exc}")

    @staticmethod
    async def viewer_stats(
        platform_db: AsyncSession,
        *,
        post: SysEcoPost,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """发布方可见的热度反馈

        给「看的人不少、只是还没人下决心」一个可见的证据。对 standard 租户尤其
        重要——它们能发布但不能主动发起意向，没有这个反馈很容易得出「发了没用」
        的结论然后弃用大厅。
        """
        now = now or datetime.now()
        since: date = (now - timedelta(days=VIEWER_STATS_DAYS)).date()

        row = (
            await platform_db.execute(
                select(
                    func.count(func.distinct(SysEcoPostView.viewer_tenant_code)),
                    func.coalesce(func.sum(SysEcoPostView.view_count), 0),
                ).where(
                    SysEcoPostView.post_id == int(post.id),
                    SysEcoPostView.view_date >= since,
                    SysEcoPostView.is_deleted == 0,
                )
            )
        ).first()

        provinces = (
            await platform_db.execute(
                select(
                    SysEcoPostView.viewer_province,
                    func.count(func.distinct(SysEcoPostView.viewer_tenant_code)),
                )
                .where(
                    SysEcoPostView.post_id == int(post.id),
                    SysEcoPostView.view_date >= since,
                    SysEcoPostView.viewer_province.isnot(None),
                    SysEcoPostView.is_deleted == 0,
                )
                .group_by(SysEcoPostView.viewer_province)
                .order_by(func.count(func.distinct(SysEcoPostView.viewer_tenant_code)).desc())
                .limit(3)
            )
        ).all()

        return {
            "days": VIEWER_STATS_DAYS,
            "viewerTenantCount": int(row[0] or 0) if row else 0,
            "viewCount": int(row[1] or 0) if row else 0,
            "topProvinces": [
                {"province": p, "tenantCount": int(c or 0)} for p, c in provinces
            ],
            "intentCount": int(post.intent_count or 0),
        }
