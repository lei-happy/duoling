"""
客户端意见反馈服务

反馈数据存于平台库（zt_platform.sys_feedback），Client 通过平台库 Session 提交与查询。
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import FeedbackStatusEnum, UserTypeEnum
from app.common.exceptions import BizException
from app.modules.client.schemas.feedback import FeedbackCreateIn, FeedbackItemOut
from app.modules.console.models.common.feedback import Feedback
from app.modules.console.models.system.user import User


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


def _to_out(row: Feedback) -> FeedbackItemOut:
    return FeedbackItemOut(
        id=row.id,
        tenant_code=row.tenant_code,
        user_id=row.user_id,
        user_name=row.user_name,
        contact_phone=row.contact_phone,
        title=row.title,
        content=row.content,
        feedback_type=row.feedback_type,
        status=row.status,
        reply=row.reply,
        images=_parse_images(row.images),
        handler_name=row.handler_name,
        replied_at=row.replied_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class ClientFeedbackService:
    """租户端意见反馈服务"""

    @staticmethod
    async def _resolve_user_name(db: AsyncSession, user_id: int) -> Optional[str]:
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

    @staticmethod
    def _derive_title(content: str, title: Optional[str] = None) -> str:
        """列表展示用短标题：优先入参 title，否则取正文首行/前 40 字。"""
        raw = (title or "").strip()
        if raw:
            return raw[:200]
        text = (content or "").strip()
        if not text:
            return "用户反馈"
        first_line = next(
            (line.strip() for line in text.splitlines() if line.strip()),
            text,
        )
        compact = " ".join(first_line.split())
        return (compact[:40] + "…") if len(compact) > 40 else compact

    @staticmethod
    async def create(
        db: AsyncSession,
        data: FeedbackCreateIn,
        *,
        user_id: int,
        tenant_code: Optional[str],
    ) -> FeedbackItemOut:
        if not tenant_code:
            raise BizException("当前未关联企业，暂时无法提交反馈")

        user_name = await ClientFeedbackService._resolve_user_name(db, user_id)
        row = Feedback(
            tenant_code=tenant_code,
            user_id=user_id,
            user_name=user_name,
            contact_phone=(data.contact_phone or "").strip() or None,
            title=ClientFeedbackService._derive_title(data.content, data.title),
            content=data.content,
            feedback_type=data.feedback_type,
            status=int(FeedbackStatusEnum.PENDING),
            images=json.dumps(data.images or [], ensure_ascii=False),
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return _to_out(row)

    @staticmethod
    def _scope_query(
        *,
        user_id: int,
        user_type: int,
        tenant_code: Optional[str],
    ):
        query = select(Feedback).where(Feedback.is_deleted == 0)
        if not tenant_code:
            # 无租户上下文时仅能看自己（理论上 client 登录必有租户）
            return query.where(Feedback.user_id == user_id)

        query = query.where(Feedback.tenant_code == tenant_code)
        if user_type != UserTypeEnum.TENANT_ADMIN:
            query = query.where(Feedback.user_id == user_id)
        return query

    @staticmethod
    async def list_feedbacks(
        db: AsyncSession,
        *,
        user_id: int,
        user_type: int,
        tenant_code: Optional[str],
        page: int = 1,
        limit: int = 20,
        status: Optional[int] = None,
        feedback_type: Optional[int] = None,
        keyword: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> Tuple[List[FeedbackItemOut], int]:
        query = ClientFeedbackService._scope_query(
            user_id=user_id,
            user_type=user_type,
            tenant_code=tenant_code,
        )
        if status is not None:
            query = query.where(Feedback.status == status)
        if feedback_type is not None:
            query = query.where(Feedback.feedback_type == feedback_type)
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
        return [_to_out(r) for r in rows], total

    @staticmethod
    async def get_detail(
        db: AsyncSession,
        feedback_id: int,
        *,
        user_id: int,
        user_type: int,
        tenant_code: Optional[str],
    ) -> FeedbackItemOut:
        row = (
            await db.execute(
                select(Feedback).where(
                    Feedback.id == feedback_id,
                    Feedback.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("找不到这条反馈")

        if tenant_code and row.tenant_code != tenant_code:
            raise BizException("找不到这条反馈")
        if user_type != UserTypeEnum.TENANT_ADMIN and row.user_id != user_id:
            raise BizException("找不到这条反馈")

        return _to_out(row)
