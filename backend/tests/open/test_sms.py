"""短信验证码开放接口测试

对应需求：doc/06.测试用例体系/04.开放接口与LITE与运力宝/03.短信验证码.md
对应后端：backend/app/modules/open/api/sms.py
         backend/app/modules/open/services/sms_service.py
覆盖用例：TC-OPN-SMS-001 ~ TC-OPN-SMS-010

分两层：
1. 纯逻辑：用途校验、重发/过期常量（零 DB，invalid purpose 在触库前拦截）；
2. HTTP 集成：发送验证码 / 重置密码（平台库不可达时 skip）。
"""

import pytest
from pydantic import ValidationError

from app.common.exceptions import BizException
from app.modules.open.api.sms import SmsSendRequest, SmsResetPasswordRequest
from app.modules.open.services.sms_service import (
    SmsService,
    SMS_CODE_LENGTH,
    SMS_CODE_EXPIRE_MINUTES,
    SMS_CODE_RESEND_SECONDS,
    PURPOSE_LOGIN,
    PURPOSE_RESET_PASSWORD,
    PURPOSE_TENANT_REGISTER,
)


# =====================================================================
# 1) 纯逻辑：常量 & 用途校验 & schema
# =====================================================================
class TestSmsConstants:
    def test_default_constants(self):
        assert SMS_CODE_LENGTH == 6
        assert SMS_CODE_EXPIRE_MINUTES == 5
        assert SMS_CODE_RESEND_SECONDS == 60
        assert {PURPOSE_LOGIN, PURPOSE_RESET_PASSWORD, PURPOSE_TENANT_REGISTER} == {1, 2, 4}


@pytest.mark.asyncio
class TestSmsPurposeGuard:
    """TC-OPN-SMS-002：无效用途在触库前即被拦截（db 传 None 亦不报 AttributeError）"""

    @pytest.mark.parametrize("bad_purpose", [0, 3, 5, 99, -1])
    async def test_invalid_purpose_rejected(self, bad_purpose):
        with pytest.raises(BizException):
            await SmsService.send_code(
                db=None, phone="13800000000", purpose=bad_purpose, app_type="website"
            )


class TestResetPasswordSchema:
    """TC-OPN-SMS-003：重置密码 newPassword 最短 6 位"""

    def test_valid(self):
        req = SmsResetPasswordRequest(
            phone="13800000000", code="123456", newPassword="abc123"
        )
        assert req.newPassword == "abc123"

    @pytest.mark.parametrize("pwd", ["12345", "", "a"])
    def test_short_password_rejected(self, pwd):
        with pytest.raises(ValidationError):
            SmsResetPasswordRequest(phone="13800000000", code="123456", newPassword=pwd)


class TestSendSchema:
    def test_send_request_fields(self):
        req = SmsSendRequest(phone="13800000000", purpose=4, app_type="website")
        assert req.purpose == 4
        assert req.app_type == "website"

    @pytest.mark.parametrize("phone", ["abc", "12345678901", "23800000000", ""])
    def test_invalid_phone_rejected(self, phone):
        with pytest.raises(ValidationError):
            SmsSendRequest(phone=phone, purpose=4, app_type="website")


@pytest.mark.asyncio
class TestSmsResendThrottle:
    """TC-OPN-SMS-010：重发节流按最近一次发送时间，不区分 status。"""

    async def test_consumed_record_still_throttles(self, platform_session):
        from datetime import datetime, timedelta

        from app.modules.console.models.sms.sms_code import SmsCode

        phone = "13800000077"
        platform_session.add(
            SmsCode(
                phone=phone,
                code="111111",
                purpose=PURPOSE_TENANT_REGISTER,
                status=1,
                expire_at=datetime.now() + timedelta(minutes=5),
            )
        )
        await platform_session.flush()

        with pytest.raises(BizException, match="发送过于频繁"):
            await SmsService.send_code(
                platform_session, phone, PURPOSE_TENANT_REGISTER, app_type="website"
            )


# =====================================================================
# 2) HTTP 集成：平台库不可达时 skip
# =====================================================================
@pytest.mark.asyncio
class TestSmsHttp:
    async def test_send_invalid_purpose(self, platform_client):
        """TC-OPN-SMS-005：非法用途 → 业务错误 code!=0"""
        resp = await platform_client.post(
            "/api/open/sms/send",
            json={"phone": "13800000000", "purpose": 99, "app_type": "website"},
        )
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    async def test_send_register_code_new_phone(self, platform_client):
        """TC-OPN-SMS-006：为未注册手机号发送企业注册验证码（正向，落表不发真短信）

        注意：该用例会在平台库落一条 sms_code 记录（无外层事务包裹的 HTTP 集成用例，
        属预期副作用；测试库为 CI 库可接受）。若 60s 内重复触发会命中重发限制。
        """
        resp = await platform_client.post(
            "/api/open/sms/send",
            json={"phone": "13800000009", "purpose": 4, "app_type": "website"},
        )
        assert resp.status_code == 200
        body = resp.json()
        # 命中：正常返回 code=0；若 60s 内已发过则为频率限制业务错误
        assert body["code"] in (0, -1)

    async def test_send_login_unregistered_phone(self, platform_client):
        """TC-OPN-SMS-007：未注册手机号请求 client 登录验证码 → 业务错误"""
        resp = await platform_client.post(
            "/api/open/sms/send",
            json={"phone": "13000000000", "purpose": 1, "app_type": "client"},
        )
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    async def test_reset_password_wrong_code(self, platform_client):
        """TC-OPN-SMS-008：错误验证码重置密码 → 业务错误（不改密码）"""
        resp = await platform_client.post(
            "/api/open/sms/reset-password",
            json={
                "phone": "13800000000",
                "code": "000000",
                "newPassword": "newpass123",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    async def test_send_invalid_phone_format(self, platform_client):
        """TC-OPN-SMS-009：非法手机号 → 422 参数校验（BUG-OPN-002 已修复）"""
        resp = await platform_client.post(
            "/api/open/sms/send",
            json={"phone": "abc", "purpose": 4, "app_type": "website"},
        )
        assert resp.status_code == 422
