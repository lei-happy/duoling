"""get_tenant_code：未登录应 401，已登录缺租户才 400

Token 过期时 TenantMiddleware 不会注入 current_user / tenant_code。
若此时抛 TenantException（400「缺少租户信息」），司机端只会 toast，不会回登录页。
"""

from types import SimpleNamespace

import pytest

from app.common.exceptions import AuthException, TenantException
from app.core.dependencies import get_tenant_code
from app.core.security import TokenData


def _req(*, tenant_code=None, current_user=None):
    return SimpleNamespace(
        state=SimpleNamespace(tenant_code=tenant_code, current_user=current_user)
    )


class TestGetTenantCode:
    async def test_missing_user_is_auth_error(self):
        with pytest.raises(AuthException, match="未登录或 Token 已过期"):
            await get_tenant_code(_req())

    async def test_logged_in_without_tenant_is_tenant_error(self):
        user = TokenData(
            user_id=1, phone="13800000000", user_type=3, tenant_code=None
        )
        with pytest.raises(TenantException, match="缺少租户信息"):
            await get_tenant_code(_req(current_user=user))

    async def test_returns_tenant_code(self):
        user = TokenData(
            user_id=1, phone="13800000000", user_type=3, tenant_code="1001"
        )
        code = await get_tenant_code(_req(tenant_code="1001", current_user=user))
        assert code == "1001"
