"""
API 级权限校验

提供基于角色的访问控制（RBAC）依赖项，用于路由级别的权限检查。

使用方式：
    from app.core.permissions import require_roles, require_any_role

    @router.get("/admin-only")
    async def admin_endpoint(
        user: TokenData = Depends(require_roles("admin")),
    ):
        ...

    @router.get("/manager-or-admin")
    async def manager_endpoint(
        user: TokenData = Depends(require_any_role("admin", "manager")),
    ):
        ...
"""

import os
import time
from typing import Dict, Optional, Sequence, Tuple

from fastapi import Depends, Request

from app.core.database import db_manager
from app.core.security import TokenData
from app.common.exceptions import AuthException, PermissionException


async def get_current_user(request: Request) -> TokenData:
    """获取当前登录用户（从中间件注入的 state 中获取）"""
    user = getattr(request.state, "current_user", None)
    if not user:
        raise AuthException("未登录或 Token 已过期")
    return user


# ============================================================
# 产品功能（feature）级 API 守卫（fail-closed）
#
# 菜单隐藏只防"看不见"，无法阻止知道 URL 的人直接调用后端接口。
# 这里在路由层按租户「有效版本的 feature_code 集合」做硬拦截，
# 是订阅式 SaaS 的必备安全闭环。
#
# 性能：feature 不会频繁变化，按租户做 TTL 进程内缓存，避免每个请求都查平台库。
# 缓存失效窗口与前端 menu_version 轮询同量级，可接受。
# ============================================================

_feature_cache: Dict[str, Tuple[float, frozenset]] = {}


def _feature_cache_ttl() -> int:
    return int(os.getenv("FEATURE_GUARD_CACHE_TTL", "300"))


def invalidate_feature_cache(tenant_code: Optional[str] = None) -> None:
    """授权变更后调用，使指定租户（或全部）的 feature 缓存失效。"""
    if tenant_code is None:
        _feature_cache.clear()
    else:
        _feature_cache.pop(tenant_code, None)


async def _get_tenant_features(tenant_code: str) -> frozenset:
    now = time.time()
    cached = _feature_cache.get(tenant_code)
    if cached and cached[0] > now:
        return cached[1]

    # 延迟导入避免循环依赖
    from app.modules.console.services.auth.auth_service import AuthService

    codes: frozenset = frozenset()
    async for session in db_manager.get_platform_session():
        result = await AuthService._get_tenant_feature_codes(  # noqa: SLF001
            session, tenant_code
        )
        codes = frozenset(result or [])
    _feature_cache[tenant_code] = (now + _feature_cache_ttl(), codes)
    return codes


def require_feature(*feature_codes: str):
    """
    要求当前租户的有效版本至少包含其中一个 feature_code，否则 403。

    - 平台管理员（tenant_code 为 None）直接放行；
    - 租户管理员同样受功能门控约束（功能是「按版本」开通，与角色无关）。

    用法（推荐在 include_router 时整体挂载）：
        router.include_router(
            xxx_router,
            prefix="/capacity/compliance/alerts",
            dependencies=[Depends(require_feature("fleet_compliance"))],
        )
    """

    async def _check(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        # 平台侧请求无租户上下文，不做功能门控
        if current_user.tenant_code is None:
            return current_user
        features = await _get_tenant_features(current_user.tenant_code)
        if not set(feature_codes) & features:
            raise PermissionException("当前版本未开通该功能，请升级版本后使用")
        return current_user

    return _check


def require_roles(*roles: str):
    """
    要求当前用户拥有所有指定角色。

    用法:
        Depends(require_roles("admin", "super_admin"))
    """
    async def _check(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        missing = set(roles) - set(current_user.roles)
        if missing:
            raise PermissionException(
                f"需要以下角色权限: {', '.join(missing)}"
            )
        return current_user

    return _check


def require_any_role(*roles: str):
    """
    要求当前用户拥有至少一个指定角色。

    用法:
        Depends(require_any_role("admin", "manager"))
    """
    async def _check(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        if not set(roles) & set(current_user.roles):
            raise PermissionException(
                f"需要以下角色之一: {', '.join(roles)}"
            )
        return current_user

    return _check


def require_platform_admin():
    """
    要求当前用户为平台管理员（user_type == 1 且 tenant_code 为 None）。

    用法:
        Depends(require_platform_admin())
    """
    async def _check(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        if current_user.user_type != 1 or current_user.tenant_code is not None:
            raise PermissionException("仅平台管理员可访问")
        return current_user

    return _check


def require_tenant_admin():
    """
    要求当前用户为租户管理员（user_type == 2）。

    用法:
        Depends(require_tenant_admin())
    """
    async def _check(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        if current_user.user_type != 2:
            raise PermissionException("仅租户管理员可访问")
        return current_user

    return _check
