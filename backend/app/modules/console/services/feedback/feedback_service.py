"""
意见反馈管理服务（Console）
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.common.feedback import Feedback
from app.modules.console.models.system.user import User
from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.schemas.feedback.feedback import FeedbackHandleIn, FeedbackOut


def _parse_images(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(x) for x in data if x]
    except (TypeError, json.JSONDecodeError):
        pass
    return []


def _to_out(row: Feedback, tenant_name: Optional[str] = None) -> FeedbackOut:
    return FeedbackOut(
        id=row.id,
        tenant_code=row.tenant_code,
        tenant_name=tenant_name,
        user_id=row.user_id,
        user_name=row.user_name,
        contact_phone=row.contact_phone,
        title=row.title,
        content=row.content,
        feedback_type=row.feedback_type,
        status=row.status,
        reply=row.reply,
        images=_parse_images(row.images),
        handler_id=row.handler_id,
        handler_name=row.handler_name,
        replied_at=row.replied_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class FeedbackService:
    """运营端意见反馈服务"""

    @staticmethod
    def _base_query() -> Select:
        return select(Feedback).where(Feedback.is_deleted == 0)

    @staticmethod
    async def get_by_id(db: AsyncSession, feedback_id: int) -> Optional[Feedback]:
        result = await db.execute(
            select(Feedback).where(
                Feedback.id == feedback_id,
                Feedback.is_deleted == 0,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def _tenant_name_map(
        db: AsyncSession, codes: List[str]
    ) -> dict[str, str]:
        codes = [c for c in codes if c]
        if not codes:
            return {}
        result = await db.execute(
            select(Tenant.tenant_code, Tenant.tenant_name).where(
                Tenant.tenant_code.in_(codes),
                Tenant.is_deleted == 0,
            )
        )
        return {code: name for code, name in result.all()}

    @staticmethod
    async def list_feedbacks(
        db: AsyncSession,
        *,
        page: int = 1,
        limit: int = 20,
        status: Optional[int] = None,
        feedback_type: Optional[int] = None,
        tenant_code: Optional[str] = None,
        keyword: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> Tuple[List[FeedbackOut], int]:
        query = FeedbackService._base_query()
        if status is not None:
            query = query.where(Feedback.status == status)
        if feedback_type is not None:
            query = query.where(Feedback.feedback_type == feedback_type)
        if tenant_code:
            query = query.where(Feedback.tenant_code == tenant_code)
        if keyword:
            like = f"%{keyword.strip()}%"
            query = query.where(
                or_(Feedback.title.like(like), Feedback.content.like(like))
            )
        if created_from is not None:
            query = query.where(Feedback.created_at >= created_from)
        if created_to is not None:
            query = query.where(Feedback.created_at <= created_to)

        total = (
            await db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0

        rows = list(
            (
                await db.execute(
                    query.order_by(Feedback.id.desc())
                    .offset((page - 1) * limit)
                    .limit(limit)
                )
            ).scalars().all()
        )
        name_map = await FeedbackService._tenant_name_map(
            db, [r.tenant_code or "" for r in rows]
        )
        return [
            _to_out(r, name_map.get(r.tenant_code or "")) for r in rows
        ], total

    @staticmethod
    async def get_detail(db: AsyncSession, feedback_id: int) -> FeedbackOut:
        row = await FeedbackService.get_by_id(db, feedback_id)
        if not row:
            raise BizException("找不到这条反馈")
        name_map = await FeedbackService._tenant_name_map(
            db, [row.tenant_code or ""]
        )
        return _to_out(row, name_map.get(row.tenant_code or ""))

    @staticmethod
    async def handle_feedback(
        db: AsyncSession,
        feedback_id: int,
        data: FeedbackHandleIn,
        *,
        handler_id: int,
        handler_name: Optional[str],
    ) -> FeedbackOut:
        row = await FeedbackService.get_by_id(db, feedback_id)
        if not row:
            raise BizException("找不到这条反馈")

        row.status = int(data.status)
        reply = (data.reply or "").strip() if data.reply is not None else None
        if data.reply is not None:
            row.reply = reply or None
            if reply:
                row.replied_at = datetime.now()

        row.handler_id = int(handler_id)
        row.handler_name = (handler_name or "").strip() or None

        await db.flush()
        await db.refresh(row)
        return await FeedbackService.get_detail(db, feedback_id)

    @staticmethod
    async def resolve_handler_name(db: AsyncSession, user_id: int) -> Optional[str]:
        result = await db.execute(
            select(User.real_name, User.phone).where(
                User.id == user_id,
                User.is_deleted == 0,
            )
        )
        pair = result.one_or_none()
        if not pair:
            return None
        real_name, phone = pair
        return (real_name or "").strip() or phone
