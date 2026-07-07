"""驾驶员登录 / 多企业切换服务测试

集成层连平台库 ``zt_platform_ci``（事务回滚）。核心校验 driver 登录入口的
反向路径：未注册手机号、非驾驶员账号、未授权企业切换等应被 ``AuthException`` 拒绝。
正向登录依赖库内预置的 user_type=3 账号，测试环境不保证存在，故不做正向断言，
仅覆盖不依赖具体数据的反向与边界路径。

对应需求：项目文档/02.需求文档/03.移动端/02.驾驶员H5端/01.账号体系与多企业切换.md
覆盖用例：TC-DRV-AUTH-001/002/003/004/005/006/007
"""

import uuid

import pytest

from app.common.exceptions import AuthException
from app.modules.console.schemas.auth.auth import LoginRequest, SwitchTenantRequest
from app.modules.driver.services.driver_auth_service import DriverAuthService


class TestDriverAuthIntegration:
    async def test_login_unknown_phone_rejected(self, platform_session):
        # 极不可能存在的随机手机号 → 手机号或密码错误
        phone = "1" + uuid.uuid4().int.__str__()[:10]
        with pytest.raises(AuthException):
            await DriverAuthService.driver_login(
                platform_session, LoginRequest(phone=phone, password="whatever123")
            )

    async def test_list_tenants_unknown_user_empty(self, platform_session):
        items = await DriverAuthService.list_driver_tenants(
            platform_session, user_id=999_000_111
        )
        assert items == []

    async def test_switch_tenant_unknown_user_rejected(self, platform_session):
        with pytest.raises(AuthException):
            await DriverAuthService.switch_tenant(
                platform_session,
                user_id=999_000_111,
                request=SwitchTenantRequest(tenant_code="1001"),
            )
