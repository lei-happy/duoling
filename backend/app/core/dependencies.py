"""
FastAPI 依赖注入

提供常用的依赖项：
- 获取平台库 Session
- 获取当前用户
- 获取租户库 Session（根据当前用户的 tenant_code）
"""

from typing import Annotated, AsyncGenerator, Optional, Set

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
    """获取当前请求的租户编码

    Token 过期/无效时中间件不会注入 current_user，应走 401，
    而不是「缺租户」400——否则前端只会 toast，不会回登录页。
    """
    tenant_code = getattr(request.state, "tenant_code", None)
    if tenant_code:
        return tenant_code
    if not getattr(request.state, "current_user", None):
        raise AuthException("未登录或 Token 已过期")
    raise TenantException("缺少租户信息，请确认登录状态")


async def ensure_biz_login_log_table(
    tenant_code: str = Depends(get_tenant_code),
) -> None:
    """
    老租户库在新增 biz_login_log 模型前已初始化，可能缺少该表；
    首次访问登录记录接口时按需补建（与 fix_tenant_tables 行为一致）。
    """
    await db_manager.ensure_tenant_tables(tenant_code, ["biz_login_log"])


async def ensure_biz_company_activity_table(
    tenant_code: str = Depends(get_tenant_code),
) -> None:
    """老租户库可能缺少工作台「最新动态」表，首次访问时幂等补建。"""
    await db_manager.ensure_tenant_tables(tenant_code, ["biz_company_activity"])


# ai_assistant 在 enterprise 版本默认开通，但 required_tables 是后期补充的；
# 老租户库可能缺 biz_ai_* 表。首次访问 AI 接口时幂等补建。
_AI_TENANT_TABLES = [
    "biz_ai_session",
    "biz_ai_message",
    "biz_ai_tool_call_log",
    "biz_ai_context",
]
_ai_checked_tenants: Set[str] = set()


async def ensure_biz_ai_tables(
    tenant_code: str = Depends(get_tenant_code),
) -> None:
    """首次访问当前租户的 AI 接口时，按需补建 biz_ai_* 4 张表

    带进程内缓存，避免每次请求都查 information_schema。
    """
    if tenant_code in _ai_checked_tenants:
        return
    await db_manager.ensure_tenant_tables(tenant_code, _AI_TENANT_TABLES)
    _ai_checked_tenants.add(tenant_code)


async def get_tenant_db(
    tenant_code: str = Depends(get_tenant_code),
) -> AsyncGenerator[AsyncSession, None]:
    """获取当前租户的数据库 Session

    默认 ``Depends(get_tenant_db)`` 为 request scope：响应发给客户端之后才
    ``commit``。写接口若会被前端立刻跟读（创建后刷新列表等），请改用
    ``TenantDb``，否则客户端可能读到提交前的旧快照。
    """
    async for session in db_manager.get_tenant_session(tenant_code):
        yield session


# 写后立刻读：在返回响应前跑完 pre_commit hooks + commit
TenantDb = Annotated[AsyncSession, Depends(get_tenant_db, scope="function")]
