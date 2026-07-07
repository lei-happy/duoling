"""账号与组织 · 客户端登录（平台库，反向为主）测试

登录走平台库 sys_user / sys_user_tenant。为避免依赖具体种子账号，
这里以**反向用例**为主（不存在的手机号、错误密码、缺租户），
在平台库连接可用时执行、事务回滚不落库；无 DB 时 skip。

对应需求：项目文档/02.需求文档/02.企业端/01.账号与组织/**
对应接口：POST /api/client/auth/login
对应代码：backend/app/modules/console/services/auth/auth_service.py::client_login
覆盖用例：TC-CLI-AUTH-001 ~ TC-CLI-AUTH-006
"""

from __future__ import annotations

import pytest

from app.common.exceptions import AuthException
from app.modules.console.schemas.auth.auth import LoginRequest
from app.modules.console.services.auth.auth_service import AuthService


class TestClientLoginReverse:
    async def test_unknown_phone_rejected(self, platform_session):
        req = LoginRequest(phone="19900000000", password="whatever123")
        with pytest.raises(AuthException):
            await AuthService.client_login(platform_session, req)

    async def test_wrong_password_rejected(self, platform_session):
        # 极大概率不存在的账号；即便存在，随机密码也不会通过校验
        req = LoginRequest(phone="13000000001", password="definitely-wrong-pwd")
        with pytest.raises(AuthException):
            await AuthService.client_login(platform_session, req)

    async def test_empty_phone_rejected(self, platform_session):
        req = LoginRequest(phone="", password="x")
        with pytest.raises(AuthException):
            await AuthService.client_login(platform_session, req)
