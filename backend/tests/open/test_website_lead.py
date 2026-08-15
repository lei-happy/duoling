"""官网留资接口测试

对应后端：backend/app/modules/open/api/website_lead.py
         backend/app/modules/open/services/website_lead_service.py
         backend/app/modules/open/schemas/website_lead.py

分两层：
1. 纯逻辑：schema 校验与来源 IP 解析（零 DB）；
2. Service 集成：写入落库、蜜罐、手机号/IP 频控（平台库不可达时 skip）。

Service 层用例走 ``platform_session`` 外层事务，结束回滚，不污染开发库。
"""

import json

import pytest
from pydantic import ValidationError

from app.modules.open.api.website_lead import _client_ip
from app.modules.open.models.website_lead import WebsiteLead
from app.modules.open.schemas.website_lead import LeadSubmitRequest
from app.modules.open.services import website_lead_service
from app.modules.open.services.website_lead_service import WebsiteLeadService


def make_payload(**override) -> LeadSubmitRequest:
    """最小合法留资请求体。"""
    data = dict(
        company_name="测试轿运物流",
        contact_person="张三",
        contact_phone="13800000000",
    )
    data.update(override)
    return LeadSubmitRequest(**data)


class _FakeClient:
    def __init__(self, host):
        self.host = host


class _FakeRequest:
    """只提供 _client_ip 需要的两个属性，避免造完整 Request。"""

    def __init__(self, headers=None, host=None):
        self.headers = headers or {}
        self.client = _FakeClient(host) if host else None


# =====================================================================
# 1) 纯逻辑：schema 校验与来源 IP 解析（零 DB）
# =====================================================================
class TestLeadSchema:
    def test_minimal_valid(self):
        p = make_payload()
        assert p.contact_phone == "13800000000"
        assert p.fleet_size is None

    @pytest.mark.parametrize(
        "phone",
        ["12345678901", "1380000000", "138000000000", "abcdefghijk", "23800000000", ""],
    )
    def test_invalid_phone_rejected(self, phone):
        with pytest.raises(ValidationError):
            make_payload(contact_phone=phone)

    def test_phone_whitespace_stripped(self):
        assert make_payload(contact_phone=" 13800000000 ").contact_phone == "13800000000"

    def test_company_and_person_stripped(self):
        p = make_payload(company_name="  测试轿运物流  ", contact_person=" 张三 ")
        assert p.company_name == "测试轿运物流"
        assert p.contact_person == "张三"

    def test_company_name_too_short(self):
        with pytest.raises(ValidationError):
            make_payload(company_name="甲")

    @pytest.mark.parametrize("size", ["lt10", "10-30", "30-100", "gt100"])
    def test_fleet_size_accepted(self, size):
        assert make_payload(fleet_size=size).fleet_size == size

    def test_fleet_size_unknown_rejected(self):
        with pytest.raises(ValidationError):
            make_payload(fleet_size="huge")

    @pytest.mark.parametrize("score", [-1, 81])
    def test_total_score_out_of_range(self, score):
        with pytest.raises(ValidationError):
            make_payload(total_score=score)

    def test_dim_score_out_of_range(self):
        with pytest.raises(ValidationError):
            make_payload(dim_a=21)

    def test_self_check_result_carried(self):
        p = make_payload(
            stage_band="L3",
            stage_name="单点数字化",
            total_score=42,
            dim_a=12,
            dim_b=10,
            dim_c=11,
            dim_d=9,
            profile_answers={"P1": "a", "P2": "b", "P3": "c"},
        )
        assert p.stage_band == "L3"
        assert p.profile_answers["P2"] == "b"


class TestClientIp:
    def test_prefers_first_forwarded_hop(self):
        req = _FakeRequest(
            headers={"x-forwarded-for": "203.0.113.9, 10.0.0.1, 10.0.0.2"},
            host="10.0.0.2",
        )
        assert _client_ip(req) == "203.0.113.9"

    def test_forwarded_value_truncated_to_column_width(self):
        req = _FakeRequest(headers={"x-forwarded-for": "9" * 200})
        assert len(_client_ip(req)) == 64

    def test_falls_back_to_peer_address(self):
        assert _client_ip(_FakeRequest(host="198.51.100.7")) == "198.51.100.7"

    def test_no_client_returns_none(self):
        assert _client_ip(_FakeRequest()) is None


# =====================================================================
# 2) Service 集成：需平台库；不可达时 skip
# =====================================================================
@pytest.mark.asyncio
class TestLeadServiceWrite:
    async def _submit(self, db, payload, **override):
        kwargs = dict(client_ip="203.0.113.9", user_agent="pytest-ua", referrer=None)
        kwargs.update(override)
        return await WebsiteLeadService.submit(db, payload, **kwargs)

    async def test_lead_persisted_with_self_check_result(self, platform_session):
        """留资落库，自测档位与四维分数一并带过来——销售靠这几个分数排优先级。"""
        payload = make_payload(
            contact_phone="13900000001",
            fleet_size="10-30",
            pain_point="  运价算不清  ",
            profile_answers={"P1": "a", "P2": "b"},
            stage_band="L4",
            stage_name="链路打通",
            total_score=48,
            dim_a=13,
            dim_b=12,
            dim_c=12,
            dim_d=11,
            source_page="/assessment",
        )
        assert await self._submit(platform_session, payload) is True

        lead = (
            await platform_session.execute(
                WebsiteLead.__table__.select().where(
                    WebsiteLead.contact_phone == "13900000001"
                )
            )
        ).mappings().one()

        assert lead["company_name"] == "测试轿运物流"
        assert lead["fleet_size"] == "10-30"
        assert lead["pain_point"] == "运价算不清"
        assert json.loads(lead["profile_answers"])["P1"] == "a"
        assert lead["stage_band"] == "L4"
        assert lead["total_score"] == 48
        assert lead["dim_d"] == 11
        assert lead["client_ip"] == "203.0.113.9"
        assert lead["source_page"] == "/assessment"
        # 新线索默认落在「待联系」，等运营端跟进
        assert lead["status"] == 0

    async def test_blank_pain_point_stored_as_null(self, platform_session):
        payload = make_payload(contact_phone="13900000002", pain_point="   ")
        assert await self._submit(platform_session, payload) is True

        row = (
            await platform_session.execute(
                WebsiteLead.__table__.select().where(
                    WebsiteLead.contact_phone == "13900000002"
                )
            )
        ).mappings().one()
        assert row["pain_point"] is None

    async def test_overlong_ua_and_referrer_truncated(self, platform_session):
        payload = make_payload(contact_phone="13900000003")
        assert (
            await self._submit(
                platform_session,
                payload,
                user_agent="u" * 400,
                referrer="https://example.com/" + "r" * 400,
            )
            is True
        )

        row = (
            await platform_session.execute(
                WebsiteLead.__table__.select().where(
                    WebsiteLead.contact_phone == "13900000003"
                )
            )
        ).mappings().one()
        assert len(row["user_agent"]) == 255
        assert len(row["referrer"]) == 255


@pytest.mark.asyncio
class TestLeadServiceAntiSpam:
    async def _count(self, db, phone):
        from sqlalchemy import func, select

        result = await db.execute(
            select(func.count())
            .select_from(WebsiteLead)
            .where(WebsiteLead.contact_phone == phone)
        )
        return int(result.scalar() or 0)

    async def test_honeypot_submission_dropped(self, platform_session):
        """蜜罐字段被填 = 自动填表脚本，直接丢弃且不落库。"""
        payload = make_payload(contact_phone="13900000010", website="http://spam.example")
        accepted = await WebsiteLeadService.submit(
            platform_session, payload, client_ip="203.0.113.10", user_agent=None, referrer=None
        )
        assert accepted is False
        assert await self._count(platform_session, "13900000010") == 0

    async def test_whitespace_only_honeypot_is_not_spam(self, platform_session):
        """浏览器自动填充可能塞进空白，不能据此判为脚本。"""
        payload = make_payload(contact_phone="13900000011", website="   ")
        accepted = await WebsiteLeadService.submit(
            platform_session, payload, client_ip="203.0.113.11", user_agent=None, referrer=None
        )
        assert accepted is True

    async def test_phone_limit_blocks_beyond_quota(self, platform_session):
        """同号 24 小时内前 3 条放行，第 4 条拦截。"""
        phone = "13900000020"
        for _ in range(website_lead_service._PHONE_LIMIT):
            assert (
                await WebsiteLeadService.submit(
                    platform_session,
                    make_payload(contact_phone=phone),
                    client_ip=None,
                    user_agent=None,
                    referrer=None,
                )
                is True
            )

        assert (
            await WebsiteLeadService.submit(
                platform_session,
                make_payload(contact_phone=phone),
                client_ip=None,
                user_agent=None,
                referrer=None,
            )
            is False
        )
        assert await self._count(platform_session, phone) == website_lead_service._PHONE_LIMIT

    async def test_ip_limit_blocks_beyond_quota(self, platform_session):
        """同出口 IP 1 小时内超额后拦截，换手机号也不放行。"""
        ip = "203.0.113.200"
        for i in range(website_lead_service._IP_LIMIT):
            assert (
                await WebsiteLeadService.submit(
                    platform_session,
                    make_payload(contact_phone=f"139000001{i:02d}"),
                    client_ip=ip,
                    user_agent=None,
                    referrer=None,
                )
                is True
            )

        assert (
            await WebsiteLeadService.submit(
                platform_session,
                make_payload(contact_phone="13911119999"),
                client_ip=ip,
                user_agent=None,
                referrer=None,
            )
            is False
        )

    async def test_missing_ip_skips_ip_limit(self, platform_session):
        """取不到 IP 时只按手机号限流，不能因此把人全拦下。"""
        for i in range(website_lead_service._IP_LIMIT + 2):
            assert (
                await WebsiteLeadService.submit(
                    platform_session,
                    make_payload(contact_phone=f"139000002{i:02d}"),
                    client_ip=None,
                    user_agent=None,
                    referrer=None,
                )
                is True
            )
