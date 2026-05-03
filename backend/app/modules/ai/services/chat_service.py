"""会话与消息管理服务（租户库）"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.core.security import TokenData
from app.modules.ai.models.tenant.biz_ai_message import BizAiMessage
from app.modules.ai.models.tenant.biz_ai_session import BizAiSession


class ChatService:

    @staticmethod
    def _generate_session_no() -> str:
        return f"AI{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6]}"

    @staticmethod
    async def get_or_create_session(
        tenant_db: AsyncSession,
        user: TokenData,
        employee_code: str,
        employee_name: Optional[str],
        session_id: Optional[int] = None,
    ) -> BizAiSession:
        if session_id:
            row = (
                await tenant_db.execute(
                    select(BizAiSession).where(
                        BizAiSession.id == session_id,
                        BizAiSession.is_deleted == 0,
                    )
                )
            ).scalar_one_or_none()
            if not row:
                raise BizException("会话不存在")
            if row.user_id != user.user_id:
                raise BizException("无权访问该会话")
            return row

        row = BizAiSession(
            session_no=ChatService._generate_session_no(),
            user_id=user.user_id,
            employee_code=employee_code,
            employee_name=employee_name,
            status=1,
            message_count=0,
        )
        tenant_db.add(row)
        await tenant_db.flush()
        await tenant_db.commit()
        return row

    @staticmethod
    async def page_sessions(
        tenant_db: AsyncSession,
        user: TokenData,
        page: int = 1,
        page_size: int = 20,
        employee_code: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        base = select(BizAiSession).where(
            BizAiSession.is_deleted == 0,
            BizAiSession.user_id == user.user_id,
        )
        if employee_code:
            base = base.where(BizAiSession.employee_code == employee_code)
        if keyword:
            base = base.where(BizAiSession.title.contains(keyword))
        count_q = select(func.count()).select_from(base.subquery())
        total = (await tenant_db.execute(count_q)).scalar() or 0

        rows = (
            await tenant_db.execute(
                base.order_by(BizAiSession.last_message_at.desc(), BizAiSession.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()

        from app.modules.ai.schemas.client.chat import SessionOut

        return {
            "list": [SessionOut.from_model(r).model_dump() for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def list_messages(
        tenant_db: AsyncSession,
        user: TokenData,
        session_id: int,
        limit: int = 100,
    ) -> list[dict]:
        sess = (
            await tenant_db.execute(
                select(BizAiSession).where(
                    BizAiSession.id == session_id,
                    BizAiSession.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not sess or sess.user_id != user.user_id:
            raise BizException("会话不存在或无权访问")

        rows = (
            await tenant_db.execute(
                select(BizAiMessage)
                .where(
                    BizAiMessage.session_id == session_id,
                    BizAiMessage.is_deleted == 0,
                )
                .order_by(BizAiMessage.id.asc())
                .limit(limit)
            )
        ).scalars().all()

        from app.modules.ai.schemas.client.chat import MessageOut

        return [MessageOut.from_model(r).model_dump() for r in rows]

    @staticmethod
    async def rename_session(
        tenant_db: AsyncSession,
        user: TokenData,
        session_id: int,
        title: str,
    ) -> None:
        """用户自定义会话标题"""
        title = (title or "").strip()
        if not title:
            raise BizException("会话名称不能为空")
        if len(title) > 80:
            raise BizException("会话名称不能超过 80 个字符")

        sess = (
            await tenant_db.execute(
                select(BizAiSession).where(
                    BizAiSession.id == session_id,
                    BizAiSession.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not sess or sess.user_id != user.user_id:
            raise BizException("会话不存在或无权访问")
        sess.title = title
        await tenant_db.flush()
        await tenant_db.commit()

    @staticmethod
    async def delete_session(
        tenant_db: AsyncSession, user: TokenData, session_id: int
    ) -> None:
        sess = (
            await tenant_db.execute(
                select(BizAiSession).where(
                    BizAiSession.id == session_id,
                    BizAiSession.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not sess or sess.user_id != user.user_id:
            raise BizException("会话不存在或无权访问")
        sess.is_deleted = 1
        await tenant_db.flush()
        await tenant_db.commit()
