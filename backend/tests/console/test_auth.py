"""运营后台端 - 认证与鉴权接口测试

覆盖用例：TC-CON-AUTH-001 ~ TC-CON-AUTH-012
对应需求：项目文档/02.需求文档/01.运营后台/**（认证登录 / 个人配置）
对应后端：backend/app/modules/console/api/auth/auth.py
          backend/app/modules/console/services/auth/auth_service.py

分两层：
1. 纯逻辑（零 DB）：JWT 签发/解析、工作台配置校验；无论有无数据库都应通过。
2. 集成（连平台库 zt_platform_ci，外层事务回滚不落库）：登录、鉴权、刷新、
   个人配置保存。无 DB 时相关 fixture 自动 skip。
"""

import pytest

from app.core.security import (
    TokenData,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
)
from app.modules.console.services.auth.auth_service import AuthService
from app.common.exceptions import AuthException


# =====================================================================
# 1) 纯逻辑：JWT 与配置校验（零 DB，恒定可跑）
# =====================================================================
class TestAuthPureLogic:
    def _admin_token_data(self) -> TokenData:
        return TokenData(
            user_id=1, phone="13800000000", user_type=0,
            tenant_code=None, roles=["super_admin"],
        )

    def test_access_token_roundtrip(self):
        """TC-CON-AUTH-001：access_token 签发后可正确解析回原始载荷"""
        token = create_access_token(self._admin_token_data())
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded.user_id == 1
        assert decoded.phone == "13800000000"
        assert decoded.user_type == 0
        assert "super_admin" in decoded.roles

    def test_decode_invalid_token_returns_none(self):
        """TC-CON-AUTH-002：非法 token 解析应返回 None（不抛异常）"""
        assert decode_access_token("not-a-jwt") is None
        assert decode_access_token("") is None

    def test_refresh_token_not_accepted_as_access(self):
        """TC-CON-AUTH-003：refresh_token 不得被 access 解析函数接受"""
        refresh = create_refresh_token(self._admin_token_data())
        assert decode_access_token(refresh) is None
        rt = decode_refresh_token(refresh)
        assert rt is not None and rt.user_id == 1

    def test_workplace_config_none_ok(self):
        """TC-CON-AUTH-004：工作台配置为 None 时校验通过"""
        AuthService._validate_workplace_config(None)  # 不抛异常即通过

    def test_workplace_config_valid_ok(self):
        AuthService._validate_workplace_config(
            {"version": 1, "quickActions": ["a", "b"]}
        )

    def test_workplace_config_quick_actions_not_list(self):
        """TC-CON-AUTH-005：quickActions 非数组应被拒绝"""
        with pytest.raises(AuthException):
            AuthService._validate_workplace_config({"quickActions": "x"})

    def test_workplace_config_too_many_quick_actions(self):
        """TC-CON-AUTH-006：quickActions 超过 12 项应被拒绝"""
        with pytest.raises(AuthException):
            AuthService._validate_workplace_config(
                {"quickActions": [str(i) for i in range(13)]}
            )

    def test_workplace_config_empty_item_rejected(self):
        with pytest.raises(AuthException):
            AuthService._validate_workplace_config({"quickActions": ["", " "]})


# =====================================================================
# 2) 集成：登录 / 鉴权 / 刷新 / 个人配置
# =====================================================================
class TestConsoleLogin:
    async def test_login_success(self, client):
        """TC-CON-AUTH-007：管理员账号密码正确 → 返回 token 与用户信息"""
        resp = await client.post(
            "/api/console/auth/login",
            json={"phone": "13800000000", "password": "admin123"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["access_token"]
        assert data["refresh_token"]
        assert data["user"]["user_type"] == 0
        assert data["user"]["phone"] == "13800000000"

    async def test_login_wrong_password(self, client):
        """TC-CON-AUTH-008：密码错误 → HTTP 401，code=401"""
        resp = await client.post(
            "/api/console/auth/login",
            json={"phone": "13800000000", "password": "wrong-pwd"},
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == 401

    async def test_login_nonexistent_phone(self, client):
        """TC-CON-AUTH-009：手机号不存在 → HTTP 401"""
        resp = await client.post(
            "/api/console/auth/login",
            json={"phone": "10000000000", "password": "admin123"},
        )
        assert resp.status_code == 401
        assert resp.json()["code"] == 401

    async def test_login_missing_field_422(self, client):
        """TC-CON-AUTH-010：缺失必填字段 password → HTTP 422 参数校验错误"""
        resp = await client.post(
            "/api/console/auth/login",
            json={"phone": "13800000000"},
        )
        assert resp.status_code == 422


class TestAuthGuard:
    async def test_user_info_without_token(self, client):
        """TC-CON-AUTH-011：未携带 token 访问受保护接口 → HTTP 401"""
        resp = await client.get("/api/console/auth/user-info")
        assert resp.status_code == 401
        assert resp.json()["code"] == 401

    async def test_user_info_with_token(self, auth_client):
        """TC-CON-AUTH-012：携带有效 token → 返回用户信息（含角色/权限）"""
        resp = await auth_client.get("/api/console/auth/user-info")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["phone"] == "13800000000"
        assert isinstance(body["data"]["roles"], list)
        assert isinstance(body["data"]["authorities"], list)

    async def test_refresh_token_flow(self, client):
        """TC-CON-AUTH-013：用登录拿到的 refresh_token 刷新出新 access_token"""
        login = await client.post(
            "/api/console/auth/login",
            json={"phone": "13800000000", "password": "admin123"},
        )
        refresh = login.json()["data"]["refresh_token"]
        resp = await client.post(
            "/api/console/auth/refresh",
            json={"refresh_token": refresh},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert body["data"]["access_token"]

    async def test_refresh_with_invalid_token(self, client):
        """TC-CON-AUTH-014：非法 refresh_token → HTTP 401"""
        resp = await client.post(
            "/api/console/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert resp.status_code == 401


class TestWorkplaceConfigApi:
    async def test_update_workplace_config_ok(self, auth_client):
        """TC-CON-AUTH-015：保存合法工作台配置 → code=0"""
        resp = await auth_client.put(
            "/api/console/auth/user-workplace-config",
            json={"workplaceConfig": {"version": 1, "quickActions": ["tenant", "user"]}},
        )
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    async def test_update_workplace_config_invalid_returns_401(self, auth_client):
        """TC-CON-AUTH-016：非法工作台配置当前返回 HTTP 401（见 BUG-CON-002）。

        校验失败本应是「业务/参数错误(400)」，但服务用 AuthException 抛出，
        被全局处理器映射为 401。此处断言当前实际行为并关联缺陷。
        """
        resp = await auth_client.put(
            "/api/console/auth/user-workplace-config",
            json={"workplaceConfig": {"quickActions": [str(i) for i in range(20)]}},
        )
        assert resp.status_code == 401
