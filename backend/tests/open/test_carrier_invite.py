"""承运商邀请着陆页 / 激活开放接口测试

对应需求：doc/06.测试用例体系/04.开放接口与LITE与运力宝/05.运力宝证照监控与承运商建档.md
对应后端：backend/app/modules/open/api/carrier_invite.py
         backend/app/modules/client/services/partner/carrier_invite_service.py
         backend/app/modules/open/schemas/carrier_invite.py
覆盖用例：TC-OPN-INVITE-001 ~ TC-OPN-INVITE-008

分两层：
1. 纯逻辑：脱敏、邀请码/URL 生成、激活请求 schema 校验（零 DB）；
2. HTTP 集成：着陆页信息 / 激活反向校验（平台库不可达时 skip）。
"""

import re

import pytest
from pydantic import ValidationError

from app.modules.client.services.partner.carrier_invite_service import (
    CarrierInviteService,
)
from app.modules.open.schemas.carrier_invite import CarrierInviteActivateRequest


# =====================================================================
# 1) 纯逻辑
# =====================================================================
class TestMaskPhone:
    """TC-OPN-INVITE-001：手机号脱敏（前 3 后 4）"""

    def test_mask_standard(self):
        assert CarrierInviteService._mask_phone("13812345678") == "138****5678"

    def test_mask_short_untouched(self):
        assert CarrierInviteService._mask_phone("123") == "123"

    def test_mask_empty(self):
        assert CarrierInviteService._mask_phone("") == ""


class TestInviteCodeToken:
    """TC-OPN-INVITE-002：邀请码/URL/token 生成规则"""

    def test_invite_code_length_and_charset(self):
        code = CarrierInviteService._gen_invite_code()
        # token_urlsafe(16) 去除 -/_ 后再截断至多 24 位，实际约 22 位；仅要求非空且不含 -/_
        assert 0 < len(code) <= 24
        assert "-" not in code and "_" not in code
        # 唯一性：两次生成不应相同
        assert code != CarrierInviteService._gen_invite_code()

    def test_invite_token_hashed(self):
        raw, hashed = CarrierInviteService._gen_invite_token()
        assert raw != hashed
        assert re.fullmatch(r"[0-9a-f]{64}", hashed)  # sha256 hex

    def test_build_invite_url(self):
        url = CarrierInviteService._build_invite_url("ABC123")
        assert url.endswith("/invite-landing/ABC123")
        assert "//invite-landing" not in url  # 末尾斜杠已剥离


class TestActivateSchema:
    """TC-OPN-INVITE-003/004：激活请求 schema 校验"""

    def _base(self, **override):
        data = dict(
            inviteCode="code123",
            contactPhone="13800000000",
            smsCode="123456",
            realName="李四",
            tenantName="被邀请企业",
        )
        data.update(override)
        return data

    def test_valid(self):
        req = CarrierInviteActivateRequest(**self._base())
        assert req.contactPhone == "13800000000"

    @pytest.mark.parametrize("code", ["12345", "abcdef", "1234567"])
    def test_bad_sms_code(self, code):
        with pytest.raises(ValidationError):
            CarrierInviteActivateRequest(**self._base(smsCode=code))

    def test_bad_phone(self):
        with pytest.raises(ValidationError):
            CarrierInviteActivateRequest(**self._base(contactPhone="12345"))


# =====================================================================
# 2) HTTP 集成：平台库不可达时 skip
# =====================================================================
@pytest.mark.asyncio
class TestCarrierInviteHttp:
    async def test_get_info_nonexistent(self, platform_client):
        """TC-OPN-INVITE-005：不存在的邀请码 → 业务错误 code!=0"""
        resp = await platform_client.get(
            "/api/open/carrier-invite/NON_EXISTENT_CODE_XYZ"
        )
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    async def test_activate_nonexistent_invite(self, platform_client):
        """TC-OPN-INVITE-006：对不存在邀请激活 → 业务错误（不创建租户）"""
        resp = await platform_client.post(
            "/api/open/carrier-invite/activate",
            json={
                "inviteCode": "NON_EXISTENT_CODE_XYZ",
                "contactPhone": "13800000000",
                "smsCode": "123456",
                "realName": "李四",
                "tenantName": "被邀请企业_勿用",
            },
        )
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    async def test_activate_bad_payload_422(self, platform_client):
        """TC-OPN-INVITE-007：激活缺失必填字段 → 422"""
        resp = await platform_client.post(
            "/api/open/carrier-invite/activate",
            json={"inviteCode": "x"},
        )
        assert resp.status_code == 422
