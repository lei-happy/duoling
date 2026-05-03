"""客户端：AI 会话与消息查询"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.ai.services.chat_service import ChatService

router = APIRouter()


class SessionRenameBody(BaseModel):
    title: str = Field(..., max_length=80, description="新的会话名称")


@router.get("")
async def page_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    employee_code: Optional[str] = Query(None, alias="employeeCode"),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    user: TokenData = Depends(get_current_user),
):
    data = await ChatService.page_sessions(
        db, user, page=page, page_size=page_size,
        employee_code=employee_code, keyword=keyword,
    )
    return success(data=data)


@router.get("/{session_id}/messages")
async def list_messages(
    session_id: int,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_tenant_db),
    user: TokenData = Depends(get_current_user),
):
    data = await ChatService.list_messages(db, user, session_id, limit=limit)
    return success(data={"list": data})


@router.put("/{session_id}")
async def rename_session(
    session_id: int,
    body: SessionRenameBody,
    db: AsyncSession = Depends(get_tenant_db),
    user: TokenData = Depends(get_current_user),
):
    """用户自定义会话名称"""
    await ChatService.rename_session(db, user, session_id, body.title)
    return success(message="已更新会话名称")


@router.delete("/{session_id}")
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    user: TokenData = Depends(get_current_user),
):
    await ChatService.delete_session(db, user, session_id)
    return success(message="会话已删除")
