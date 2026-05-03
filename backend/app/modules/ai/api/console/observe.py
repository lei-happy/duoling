"""
Console 端：AI 调用观测

工具调用日志按租户独立库查询；运营端通过 tenant_code 切换租户查看。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.common.exceptions import BizException
from app.common.response import success
from app.core.database import db_manager
from app.core.dependencies import get_current_user
from app.core.security import TokenData
from app.modules.ai.services.audit_service import (
    AuditService,
    fetch_tenant_codes_for_audit,
)

router = APIRouter()


@router.get("/tenants")
async def list_audit_tenants(
    _: TokenData = Depends(get_current_user),
):
    """列出已开通 ai_assistant 的租户编码列表（供日志查询切换）"""
    codes = await fetch_tenant_codes_for_audit()
    return success(data={"list": codes})


@router.get("/tool-logs")
async def page_tool_logs(
    tenant_code: str = Query(..., alias="tenantCode"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    session_id: Optional[int] = Query(None, alias="sessionId"),
    tool_code: Optional[str] = Query(None, alias="toolCode"),
    status: Optional[str] = None,
    user_id: Optional[int] = Query(None, alias="userId"),
    _: TokenData = Depends(get_current_user),
):
    if not tenant_code:
        raise BizException("缺少 tenantCode 参数")
    db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
    factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001
    async with factory() as session:
        data = await AuditService.page_tool_logs(
            session,
            page=page, page_size=page_size,
            session_id=session_id, tool_code=tool_code,
            status=status, user_id=user_id,
        )
    return success(data=data)


@router.get("/stats")
async def tenant_stats(
    tenant_code: str = Query(..., alias="tenantCode"),
    days: int = Query(7, ge=1, le=90),
    _: TokenData = Depends(get_current_user),
):
    if not tenant_code:
        raise BizException("缺少 tenantCode 参数")
    db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
    factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001
    async with factory() as session:
        data = await AuditService.get_tenant_stats(session, days=days)
    return success(data=data)


# ============ 会话浏览（运营回放视图） ============


@router.get("/sessions")
async def page_sessions(
    tenant_code: str = Query(..., alias="tenantCode"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    employee_code: Optional[str] = Query(None, alias="employeeCode"),
    user_id: Optional[int] = Query(None, alias="userId"),
    status: Optional[int] = None,
    _: TokenData = Depends(get_current_user),
):
    """分页列出某租户的所有 AI 会话"""
    if not tenant_code:
        raise BizException("缺少 tenantCode 参数")
    db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
    factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001
    async with factory() as session:
        data = await AuditService.page_sessions(
            session,
            page=page,
            page_size=page_size,
            keyword=keyword,
            employee_code=employee_code,
            user_id=user_id,
            status=status,
        )
    return success(data=data)


@router.get("/sessions/{session_id}/messages")
async def session_messages(
    session_id: int,
    tenant_code: str = Query(..., alias="tenantCode"),
    limit: int = Query(200, ge=1, le=500),
    _: TokenData = Depends(get_current_user),
):
    """列出某会话的全部消息（运营回放）"""
    if not tenant_code:
        raise BizException("缺少 tenantCode 参数")
    db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
    factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001
    async with factory() as session:
        data = await AuditService.list_session_messages(
            session, session_id=session_id, limit=limit
        )
    return success(data=data)
