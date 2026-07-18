"""
企业最新动态（租户库）

列表按 Asia/Shanghai 日历日过滤；与 biz_operation_log 分工不同。
"""

from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.models.workbench.company_activity import BizCompanyActivity

TZ_SH = ZoneInfo("Asia/Shanghai")


class CompanyActivityService:
    """企业动态读写"""

    @staticmethod
    def _shanghai_day_bounds_naive() -> tuple[datetime, datetime]:
        """
        当日 [start, end) 的 naive datetime，与 occurred_at 列比较。
        假定 occurred_at 与各业务模块写入一致（通常为应用主机本地时间的 naive）。
        注释：若数据库与应用服务器时区不一致，需单独校准部署约定。
        """
        now_sh = datetime.now(TZ_SH)
        start = now_sh.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return start.replace(tzinfo=None), end.replace(tzinfo=None)

    @staticmethod
    def _format_display_time(occurred_at: datetime) -> str:
        """时间轴右侧 HH:mm。"""
        if occurred_at.tzinfo is not None:
            dt = occurred_at.astimezone(TZ_SH)
        else:
            dt = occurred_at.replace(tzinfo=TZ_SH)
        return dt.strftime("%H:%M")

    @staticmethod
    def _today_filter():
        start_naive, end_naive = CompanyActivityService._shanghai_day_bounds_naive()
        return and_(
            BizCompanyActivity.is_deleted == 0,
            BizCompanyActivity.occurred_at >= start_naive,
            BizCompanyActivity.occurred_at < end_naive,
        )

    @staticmethod
    def _row_to_item(row: BizCompanyActivity) -> Dict[str, Any]:
        return {
            "id": row.id,
            "occurred_at": row.occurred_at,
            "display_time": CompanyActivityService._format_display_time(row.occurred_at),
            "summary": row.summary,
            "event_code": row.event_code,
            "actor_display_name": row.actor_display_name,
        }

    @staticmethod
    async def list_today(
        db: AsyncSession,
        *,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        page = await CompanyActivityService.page_today(
            db, page=1, page_size=limit
        )
        return page["items"]

    @staticmethod
    async def page_today(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        today_filter = CompanyActivityService._today_filter()
        count_q = select(func.count()).select_from(BizCompanyActivity).where(
            today_filter
        )
        total = (await db.execute(count_q)).scalar() or 0
        pages = max(1, math.ceil(total / page_size)) if page_size else 1

        q = (
            select(BizCompanyActivity)
            .where(today_filter)
            .order_by(BizCompanyActivity.occurred_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(q)
        rows = result.scalars().all()
        items = [CompanyActivityService._row_to_item(row) for row in rows]
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": pages,
        }

    @staticmethod
    async def record(
        db: AsyncSession,
        *,
        occurred_at: datetime,
        event_code: str,
        summary: str,
        actor_user_id: Optional[int] = None,
        actor_display_name: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> BizCompanyActivity:
        row = BizCompanyActivity(
            occurred_at=occurred_at,
            actor_user_id=actor_user_id,
            actor_display_name=actor_display_name,
            event_code=event_code,
            summary=summary,
            payload=payload,
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def actor_display_name(
        db: AsyncSession, user_id: Optional[int]
    ) -> Optional[str]:
        """当前操作人在租户内的展示名（biz_user.real_name）。"""
        if not user_id:
            return None
        result = await db.execute(
            select(BizUser.real_name).where(BizUser.id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def seed_demo_if_dev(db: AsyncSession) -> int:
        """开发环境插入演示数据（当日若干条），幂等：当日已有数据则跳过。"""
        existing = await CompanyActivityService.list_today(db, limit=1)
        if existing:
            return 0

        now = datetime.now()
        samples = [
            (
                now,
                "demo.task_done",
                "SunSmile 解决了bug 登录提示操作失败",
            ),
            (
                now - timedelta(minutes=60),
                "demo.task_done",
                "Jasmine 解决了bug 按钮颜色与设计不符",
            ),
            (
                now - timedelta(minutes=120),
                "demo.assign",
                "项目经理 指派了任务 解决项目一的bug",
            ),
        ]
        for occurred_at, code, summary in samples:
            db.add(
                BizCompanyActivity(
                    occurred_at=occurred_at,
                    actor_user_id=None,
                    actor_display_name=None,
                    event_code=code,
                    summary=summary,
                    payload=None,
                )
            )
        await db.flush()
        return len(samples)
