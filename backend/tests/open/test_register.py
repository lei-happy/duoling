"""企业自助注册接口测试

对应需求：doc/02.需求文档/01.运营后台/09.产品管理（开放侧）
         doc/06.测试用例体系/04.开放接口与LITE与运力宝/01.企业自助注册.md
对应后端：backend/app/modules/open/api/register.py
         backend/app/modules/open/services/register_service.py
         backend/app/modules/open/schemas/register.py
覆盖用例：TC-OPN-REGISTER-001 ~ TC-OPN-REGISTER-012

分两层：
1. 纯逻辑：手机号正则、schema 校验（零 DB）；
2. HTTP 集成：phone-available / register / progress（平台库不可达时 skip）。

注：自助注册已下线改走留资，register / progress 两个路由只保留引导文案，
用例相应改为验证「挡得住」而不是原来的建库流程；schema 仍有承运商邀请在用，
所以纯逻辑部分保留。
"""

import re

import pytest
from pydantic import ValidationError

from app.modules.open.schemas.register import (
    RegisterPayload,
    RegisterSubmitRequest,
)
from app.modules.open.api.register import _PHONE_RE


# =====================================================================
# 1) 纯逻辑：手机号正则与 schema 校验（零 DB）
# =====================================================================
class TestPhoneRegex:
    """TC-OPN-REGISTER-002/003：手机号格式校验"""

    @pytest.mark.parametrize("phone", ["13800000000", "19912345678", "17600001111"])
    def test_valid_mobile(self, phone):
        assert _PHONE_RE.match(phone)

    @pytest.mark.parametrize(
        "phone",
        ["12345678901", "1380000000", "138000000000", "abcdefghijk", "23800000000", ""],
    )
    def test_invalid_mobile(self, phone):
        assert not _PHONE_RE.match(phone)


class TestRegisterPayloadSchema:
    """TC-OPN-REGISTER-004：RegisterPayload 手机号校验器"""

    def test_valid_payload(self):
        p = RegisterPayload(
            tenant_name="测试物流",
            contact_person="张三",
            contact_phone="13800000000",
        )
        assert p.contact_phone == "13800000000"

    def test_invalid_phone_rejected(self):
        with pytest.raises(ValidationError):
            RegisterPayload(
                tenant_name="测试物流",
                contact_person="张三",
                contact_phone="123",
            )


class TestRegisterSubmitSchema:
    """TC-OPN-REGISTER-005/006：注册提交 sms_code 6 位数字约束"""

    def _base(self, **override):
        data = dict(
            tenant_name="测试物流",
            contact_person="张三",
            contact_phone="13800000000",
            sms_code="123456",
        )
        data.update(override)
        return data

    def test_valid_submit(self):
        req = RegisterSubmitRequest(**self._base())
        assert req.sms_code == "123456"

    @pytest.mark.parametrize("code", ["12345", "1234567", "abcdef", "12 456", ""])
    def test_invalid_sms_code(self, code):
        with pytest.raises(ValidationError):
            RegisterSubmitRequest(**self._base(sms_code=code))

    def test_missing_sms_code(self):
        data = self._base()
        data.pop("sms_code")
        with pytest.raises(ValidationError):
            RegisterSubmitRequest(**data)


# =====================================================================
# 2) HTTP 集成：需平台库；不可达时 skip
# =====================================================================
@pytest.mark.asyncio
class TestRegisterHttp:
    async def test_phone_available_valid(self, platform_client):
        """TC-OPN-REGISTER-007：查询手机号是否已关联企业（正向）"""
        resp = await platform_client.get(
            "/api/open/register/phone-available", params={"phone": "13800000000"}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 0
        assert "registered" in body["data"]
        assert isinstance(body["data"]["registered"], bool)

    async def test_phone_available_bad_format(self, platform_client):
        """TC-OPN-REGISTER-008：非法手机号 → 业务错误（code!=0）"""
        # 长度非 11 位被 Query 约束拦成 422；11 位但非法号段走 BizException(code=-1)
        resp = await platform_client.get(
            "/api/open/register/phone-available", params={"phone": "23800000000"}
        )
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    async def test_phone_available_length_422(self, platform_client):
        """TC-OPN-REGISTER-009：手机号长度不足 → 422 参数校验"""
        resp = await platform_client.get(
            "/api/open/register/phone-available", params={"phone": "138"}
        )
        assert resp.status_code == 422

    async def test_register_closed_with_guidance(self, platform_client):
        """TC-OPN-REGISTER-010：自助注册已下线 → 业务错误并引导留资（不落库）

        路由保留是为了让旧书签与外部链接不至于 404；提交什么内容都不再建库。
        """
        resp = await platform_client.post(
            "/api/open/register",
            json={
                "tenant_name": "自动化测试企业_勿用",
                "contact_person": "测试员",
                "contact_phone": "13800000000",
                "sms_code": "123456",
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] != 0
        assert "留下联系方式" in body["message"]

    async def test_register_closed_even_without_body(self, platform_client):
        """TC-OPN-REGISTER-011：空请求体同样被挡下，不因缺字段泄露旧校验规则"""
        resp = await platform_client.post("/api/open/register", json={})
        assert resp.status_code == 200
        assert resp.json()["code"] != 0

    async def test_progress_closed(self, platform_client):
        """TC-OPN-REGISTER-012：注册进度查询已下线 → 业务错误"""
        resp = await platform_client.get("/api/open/register/progress/not-a-uuid")
        assert resp.status_code == 200
        assert resp.json()["code"] != 0
