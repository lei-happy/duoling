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

from typing import Sequence

from fastapi import Depends, Request

from app.core.security import TokenData
from app.common.exceptions import AuthException, PermissionException


async def get_current_user(request: Request) -> TokenData:
    """获取当前登录用户（从中间件注入的 state 中获取）"""
    user = getattr(request.state, "current_user", None)
    if not user:
        raise AuthException("未登录或 Token 已过期")
    return user


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
