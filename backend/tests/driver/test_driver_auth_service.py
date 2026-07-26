"""驾驶员登录 / 多企业切换服务测试

集成层连平台库 ``zt_platform_ci``（事务回滚）。核心校验 driver 登录入口的
反向路径：未注册手机号、非驾驶员账号、未授权企业切换等应被 ``AuthException`` 拒绝。
正向登录依赖库内预置的 user_type=3 账号，测试环境不保证存在，故不做正向断言，
仅覆盖不依赖具体数据的反向与边界路径。

另含纯单元测试：登录失败诊断文案、camelCase 响应序列化。

对应需求：doc/02.需求文档/03.移动端/02.驾驶员H5端/01.账号体系与多企业切换.md
覆盖用例：TC-DRV-AUTH-001/002/003/004/005/006/007
"""

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.common.exceptions import AuthException, BizException
from app.modules.console.schemas.auth.auth import (
    ChangePasswordRequest,
    LoginRequest,
    LoginResponse,
    LoginUserInfo,
    MultiTenantResponse,
    RefreshTokenResponse,
    SwitchTenantRequest,
    TenantOption,
)
from app.modules.console.services.auth.auth_service import AuthService
from app.modules.driver.api.auth import _dump_login_camel
from app.modules.driver.services.driver_auth_service import DriverAuthService


# =====================================================================
# 纯单元：camelCase 响应序列化
# =====================================================================
class TestDumpLoginCamel:
    def test_login_response_camel(self):
        resp = LoginResponse(
            access_token="at",
            refresh_token="rt",
            expires_in=7200,
            user=LoginUserInfo(
                user_id=1,
                phone="13800138000",
                real_name="张三",
                user_type=3,
                tenant_code="1001",
                roles=["driver"],
                force_change_pwd=1,
            ),
        )
        data = _dump_login_camel(resp)
        assert data["accessToken"] == "at"
        assert data["refreshToken"] == "rt"
        assert data["expiresIn"] == 7200
        assert data["user"]["userId"] == 1
        assert data["user"]["tenantCode"] == "1001"
        assert data["user"]["forceChangePwd"] == 1
        assert data["user"]["realName"] == "张三"
        assert "access_token" not in data

    def test_multi_tenant_response(self):
        resp = MultiTenantResponse(
            tenants=[
                TenantOption(tenantCode="1001", tenantName="企业A"),
            ]
        )
        data = _dump_login_camel(resp)
        assert data["needSelectTenant"] is True
        assert data["tenants"][0]["tenantCode"] == "1001"

    def test_refresh_response_camel(self):
        resp = RefreshTokenResponse(
            access_token="a",
            refresh_token="r",
            expires_in=3600,
        )
        data = _dump_login_camel(resp)
        assert data["accessToken"] == "a"
        assert data["refreshToken"] == "r"
        assert "user" not in data


# =====================================================================
# 纯单元：登录失败诊断文案
# =====================================================================
class TestLoginDiagnoseMessages:
    async def test_no_driver_tenant_link_raises_account_missing(self):
        """有 sys_user 但无任何 user_type=3 关联 → 账号不存在"""
        user = SimpleNamespace(id=42, phone="13900001111")

        empty_result = MagicMock()
        empty_result.scalars.return_value.all.return_value = []

        db = AsyncMock()
        db.execute = AsyncMock(return_value=empty_result)

        with pytest.raises(AuthException, match="账号不存在"):
            await DriverAuthService._resolve_tenants_and_login(db, user, None)

    async def test_single_inactive_resigned_message(self):
        """仅有停用关联 + biz_driver.status=2 → 含企业名的离职文案"""
        user = SimpleNamespace(id=42, phone="13900001111")
        ut = SimpleNamespace(
            user_id=42, tenant_code="1001", user_type=3, status=0, is_deleted=0
        )
        tenant = SimpleNamespace(
            tenant_code="1001",
            tenant_name="某某物流",
            status=1,
            expire_time=None,
            is_deleted=0,
        )

        ut_result = MagicMock()
        ut_result.scalars.return_value.all.return_value = [ut]

        tenant_result = MagicMock()
        tenant_result.scalar_one_or_none.return_value = tenant

        db = AsyncMock()

        async def _execute(stmt):
            # 第一次：查 all user_tenants；后续：查 Tenant
            sql = str(stmt)
            if "sys_user_tenant" in sql.lower() or "user_tenant" in sql.lower():
                return ut_result
            return tenant_result

        # 更稳妥：按调用顺序返回
        db.execute = AsyncMock(side_effect=[ut_result, tenant_result])

        with patch.object(
            DriverAuthService,
            "_load_driver_status",
            new=AsyncMock(return_value=2),
        ):
            with pytest.raises(AuthException, match="当前账号在某某物流已离职"):
                await DriverAuthService._resolve_tenants_and_login(db, user, None)

    async def test_single_inactive_frozen_message(self):
        user = SimpleNamespace(id=42, phone="13900001111")
        ut = SimpleNamespace(
            user_id=42, tenant_code="1001", user_type=3, status=0, is_deleted=0
        )
        tenant = SimpleNamespace(
            tenant_code="1001",
            tenant_name="冻结企业",
            status=1,
            expire_time=None,
            is_deleted=0,
        )
        ut_result = MagicMock()
        ut_result.scalars.return_value.all.return_value = [ut]
        tenant_result = MagicMock()
        tenant_result.scalar_one_or_none.return_value = tenant
        db = AsyncMock()
        db.execute = AsyncMock(side_effect=[ut_result, tenant_result])

        with patch.object(
            DriverAuthService,
            "_load_driver_status",
            new=AsyncMock(return_value=0),
        ):
            with pytest.raises(AuthException, match="当前账号在冻结企业已被冻结"):
                await DriverAuthService._resolve_tenants_and_login(db, user, None)

    async def test_multi_inactive_generic_message(self):
        user = SimpleNamespace(id=42, phone="13900001111")
        uts = [
            SimpleNamespace(
                user_id=42, tenant_code="1001", user_type=3, status=0, is_deleted=0
            ),
            SimpleNamespace(
                user_id=42, tenant_code="1002", user_type=3, status=0, is_deleted=0
            ),
        ]
        ut_result = MagicMock()
        ut_result.scalars.return_value.all.return_value = uts

        def _tenant(code, name):
            r = MagicMock()
            r.scalar_one_or_none.return_value = SimpleNamespace(
                tenant_code=code,
                tenant_name=name,
                status=1,
                expire_time=None,
                is_deleted=0,
            )
            return r

        db = AsyncMock()
        db.execute = AsyncMock(
            side_effect=[ut_result, _tenant("1001", "企业A"), _tenant("1002", "企业B")]
        )

        with patch.object(
            DriverAuthService,
            "_load_driver_status",
            new=AsyncMock(return_value=2),
        ):
            with pytest.raises(AuthException, match="您的驾驶员账号已停用"):
                await DriverAuthService._resolve_tenants_and_login(db, user, None)

    async def test_unknown_phone_with_sys_driver_archive(self):
        """有 sys_driver 档案但无 sys_user → 账号不存在"""
        db = AsyncMock()
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None
        sd_result = MagicMock()
        sd_result.scalar_one_or_none.return_value = 1
        db.execute = AsyncMock(side_effect=[user_result, sd_result])

        with pytest.raises(AuthException, match="账号不存在"):
            await DriverAuthService.driver_login(
                db, LoginRequest(phone="13800138000", password="x")
            )

    async def test_unknown_phone_without_archive(self):
        """完全无记录 → 手机号或密码错误（防枚举）"""
        db = AsyncMock()
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None
        sd_result = MagicMock()
        sd_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(side_effect=[user_result, sd_result])

        with pytest.raises(AuthException, match="手机号或密码错误"):
            await DriverAuthService.driver_login(
                db, LoginRequest(phone="13800138000", password="x")
            )

    async def test_raise_unknown_phone_fallback(self):
        db = AsyncMock()
        sd_result = MagicMock()
        sd_result.scalar_one_or_none.return_value = None
        db.execute = AsyncMock(return_value=sd_result)
        with pytest.raises(AuthException, match="自定义文案"):
            await DriverAuthService._raise_unknown_phone(
                db, "13800138000", fallback="自定义文案"
            )


# =====================================================================
# 集成（真实平台库，事务回滚）
# =====================================================================
class TestDriverAuthIntegration:
    async def test_login_unknown_phone_rejected(self, platform_session):
        # 极不可能存在的随机手机号 → 手机号或密码错误
        phone = "1" + uuid.uuid4().int.__str__()[:10]
        with pytest.raises(AuthException, match="手机号或密码错误"):
            await DriverAuthService.driver_login(
                platform_session, LoginRequest(phone=phone, password="whatever123")
            )

    async def test_login_sys_driver_without_user_account(self, platform_session):
        """平台有 sys_driver 摘要但无 sys_user → 账号不存在"""
        from app.modules.console.models.driver.sys_driver import SysDriver

        phone = "1" + uuid.uuid4().int.__str__()[:10]
        platform_session.add(
            SysDriver(
                tenant_code="1001",
                biz_driver_id=999_001,
                driver_code=f"T{phone[-6:]}",
                name="测试未开通",
                phone=phone,
                status=1,
            )
        )
        await platform_session.flush()

        with pytest.raises(AuthException, match="账号不存在"):
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

    async def test_user_info_unknown_user_rejected(self, platform_session):
        """TC-DRV-AUTH user-info 反向：用户不存在"""
        with pytest.raises(AuthException):
            await AuthService.get_user_info(
                platform_session,
                user_id=999_000_111,
                app_type="client",
                tenant_code="1001",
            )

    async def test_change_password_unknown_user_rejected(self, platform_session):
        """TC-DRV-AUTH 改密反向：用户不存在"""
        with pytest.raises(BizException, match="用户不存在"):
            await AuthService.change_password(
                platform_session,
                user_id=999_000_111,
                request=ChangePasswordRequest(
                    oldPassword="old123456",
                    newPassword="new123456",
                ),
            )
