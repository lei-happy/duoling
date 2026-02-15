"""
FastAPI 依赖注入

提供常用的依赖项：
- 获取平台库 Session
- 获取当前用户
- 获取租户库 Session（根据当前用户的 tenant_code）
"""

from typing import AsyncGenerator, Optional

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.core.security import TokenData
from app.common.exceptions import AuthException, TenantException


# ============================================================
# 平台库 Session
# ============================================================

async def get_platform_db() -> AsyncGenerator[AsyncSession, None]:
    """获取平台主库 Session"""
    async for session in db_manager.get_platform_session():
        yield session


# ============================================================
# 当前用户
# ============================================================

async def get_current_user(request: Request) -> TokenData:
    """获取当前登录用户（从中间件注入的 state 中获取）"""
    user = getattr(request.state, "current_user", None)
    if not user:
        raise AuthException("未登录或 Token 已过期")
    return user


async def get_current_user_optional(request: Request) -> Optional[TokenData]:
    """获取当前登录用户（可选，未登录返回 None）"""
    return getattr(request.state, "current_user", None)


# ============================================================
# 租户库 Session
# ============================================================

async def get_tenant_code(request: Request) -> str:
    """获取当前请求的租户编码"""
    tenant_code = getattr(request.state, "tenant_code", None)
    if not tenant_code:
        raise TenantException("缺少租户信息，请确认登录状态")
    return tenant_code


async def get_tenant_db(
    tenant_code: str = Depends(get_tenant_code),
) -> AsyncGenerator[AsyncSession, None]:
    """获取当前租户的数据库 Session"""
    async for session in db_manager.get_tenant_session(tenant_code):
        yield session
