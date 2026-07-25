"""服务平台 · 审核台读接口装配层测试

本模块守三条底线：

1. **审核详情一次给全**：挂牌内容、预检、源单核验、发布方档案、流水、白名单资格
   缺任何一块，审核员都会在信息不全的情况下点通过。
2. **档案只查一次**：资格判定复用已取到的档案，不再跑一轮聚合查询——那是五个
   COUNT，一次审核开两遍纯属浪费。
3. **详情页与队列的等待时长同口径**：两处不一致时审核员不知道该信哪个数。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §4.1
对应代码：backend/app/modules/console/services/ecosystem/audit_facade.py
"""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from app.common.exceptions import BizException
from app.modules.console.models.ecosystem.constants import PostType
from app.modules.console.services.ecosystem import audit_facade as facade_mod
from app.modules.console.services.ecosystem.audit_facade import EcoAuditFacade
from app.modules.console.services.ecosystem.audit_query_service import (
    AuditPostFilter,
    AuditQueueRow,
)
from tests.console.test_ecosystem_audit_serializer import (
    make_capacity,
    make_post,
    make_stats,
)

NOW = datetime(2026, 7, 25, 14, 0, 0)


class FakeDb:
    """取数全部打桩，真的落到 DB 就说明桩没打全"""

    async def execute(self, stmt):  # pragma: no cover - 打桩失败时才会走到
        raise AssertionError("本用例不应真的落到 DB，请检查打桩")


def make_eligibility(**kwargs):
    defaults = dict(
        tenant_code="hz001",
        eligible=True,
        manual_allowed=True,
        summary="已满足免审白名单的全部条件",
        items=[],
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@pytest.fixture
def stub_detail(monkeypatch):
    """把审核详情要用到的五路取数替换成可观测的桩"""
    calls: Dict[str, Any] = {"stats": [], "eligibility": [], "trail": []}
    post = make_post(post_type=PostType.CAPACITY)

    async def _get_post(db, post_id):
        calls["get_post"] = post_id
        return post

    async def _load_related(db, posts, post_type):
        calls["load_related"] = (tuple(p.id for p in posts), post_type)
        return {
            "ext": {post.id: make_capacity()},
            "dests": {post.id: []},
            "credits": {},
        }

    async def _load_stats(db, tenant_code, **kwargs):
        calls["stats"].append((tenant_code, kwargs.get("exclude_post_id")))
        return make_stats(tenant_code=tenant_code)

    async def _evaluate(db, tenant_code, **kwargs):
        calls["eligibility"].append((tenant_code, kwargs.get("stats") is not None))
        return make_eligibility(tenant_code=tenant_code)

    async def _trail(db, post_id, **kwargs):
        calls["trail"].append(post_id)
        return []

    monkeypatch.setattr(
        facade_mod.EcoAuditQueryService, "get_post", staticmethod(_get_post)
    )
    monkeypatch.setattr(
        facade_mod.EcoPostQueryService, "load_related", staticmethod(_load_related)
    )
    monkeypatch.setattr(
        facade_mod.EcoAuditQueryService,
        "load_tenant_stats",
        staticmethod(_load_stats),
    )
    monkeypatch.setattr(
        facade_mod.EcoWhitelistService, "evaluate", staticmethod(_evaluate)
    )
    monkeypatch.setattr(
        facade_mod.EcoAuditQueryService,
        "load_audit_trail",
        staticmethod(_trail),
    )
    calls["post"] = post
    return calls


# ---------------------------------------------------------------------------
# 审核详情
# ---------------------------------------------------------------------------


class TestDetail:
    @pytest.mark.asyncio
    async def test_all_evidence_blocks_present(self, stub_detail):
        data = await EcoAuditFacade.detail(FakeDb(), 101, now=NOW)
        for key in (
            "post",
            "precheck",
            "sourceCheck",
            "ownerContext",
            "whitelistEligibility",
            "auditTrail",
            "sla",
        ):
            assert key in data, f"审核详情缺少 {key}"

    @pytest.mark.asyncio
    async def test_capacity_ext_is_attached_by_type(self, stub_detail):
        """运力挂牌装运力扩展，装错类型会让审核员看到一个空白的车辆信息块"""
        data = await EcoAuditFacade.detail(FakeDb(), 101, now=NOW)
        assert data["post"]["capacity"]["truckType"] == "轿运车"
        assert "cargo" not in data["post"]

    @pytest.mark.asyncio
    async def test_stats_loaded_once_and_reused(self, stub_detail):
        """资格判定复用档案，避免同一次审核跑两轮聚合"""
        await EcoAuditFacade.detail(FakeDb(), 101, now=NOW)
        assert len(stub_detail["stats"]) == 1
        assert stub_detail["eligibility"] == [("hz001", True)]

    @pytest.mark.asyncio
    async def test_current_post_excluded_from_recent(self, stub_detail):
        """右侧「该企业最近发布」不该把正在审的这条也列进去"""
        await EcoAuditFacade.detail(FakeDb(), 101, now=NOW)
        assert stub_detail["stats"][0][1] == 101

    @pytest.mark.asyncio
    async def test_sla_block_has_no_duplicate_post(self, stub_detail):
        """时效块复用队列行的算法，但不重复塞一份挂牌进去"""
        data = await EcoAuditFacade.detail(FakeDb(), 101, now=NOW)
        assert "post" not in data["sla"]
        assert data["sla"]["waitedMinutes"] > 0
        assert data["sla"]["urgencyLabel"]

    @pytest.mark.asyncio
    async def test_missing_post_says_what_happened(self, monkeypatch):
        async def _none(db, post_id):
            return None

        monkeypatch.setattr(
            facade_mod.EcoAuditQueryService, "get_post", staticmethod(_none)
        )
        with pytest.raises(BizException) as e:
            await EcoAuditFacade.detail(FakeDb(), 999, now=NOW)
        assert "没找到" in str(e.value)


# ---------------------------------------------------------------------------
# 队列分页
# ---------------------------------------------------------------------------


class TestQueuePages:
    @pytest.mark.asyncio
    async def test_pending_page_shape(self, monkeypatch):
        rows: List[AuditQueueRow] = [
            AuditQueueRow(post=make_post(id=1), waited_minutes=30),
            AuditQueueRow(post=make_post(id=2), waited_minutes=130, urgency=2),
        ]

        async def _page(db, flt, **kwargs):
            return rows, 42

        monkeypatch.setattr(
            facade_mod.EcoAuditQueryService, "page_pending", staticmethod(_page)
        )
        data = await EcoAuditFacade.page_pending(
            FakeDb(), AuditPostFilter(page=2, size=20)
        )
        assert data["total"] == 42
        assert data["count"] == 42
        assert data["page"] == 2
        assert data["pageSize"] == 20
        assert [r["post"]["id"] for r in data["list"]] == [1, 2]

    @pytest.mark.asyncio
    async def test_page_size_is_clamped_in_payload(self, monkeypatch):
        """回给前端的 pageSize 必须是实际生效的值，不是用户传的原值"""

        async def _page(db, flt, **kwargs):
            return [], 0

        monkeypatch.setattr(
            facade_mod.EcoAuditQueryService, "page_all", staticmethod(_page)
        )
        data = await EcoAuditFacade.page_all(FakeDb(), AuditPostFilter(size=9999))
        assert data["pageSize"] == 100

    @pytest.mark.asyncio
    async def test_backlog_is_translated(self, monkeypatch):
        async def _stats(db, **kwargs):
            return SimpleNamespace(
                pending=5, pending_overdue=1, pending_flagged=2,
                spot_check_pending=3, spot_check_overdue=0,
            )

        monkeypatch.setattr(
            facade_mod.EcoAuditQueryService, "backlog_stats", staticmethod(_stats)
        )
        data = await EcoAuditFacade.backlog(FakeDb())
        assert data["pending"] == 5
        assert data["spotCheckPending"] == 3


# ---------------------------------------------------------------------------
# 租户档案与白名单列表
# ---------------------------------------------------------------------------


class TestTenantProfile:
    @pytest.mark.asyncio
    async def test_profile_pairs_stats_with_eligibility(self, monkeypatch):
        """白名单页与审核详情问同一个问题，给同一份结构，前端才能共用组件"""

        async def _stats(db, tenant_code, **kwargs):
            return make_stats(tenant_code=tenant_code)

        async def _evaluate(db, tenant_code, **kwargs):
            assert kwargs.get("stats") is not None, "档案已取过，不该再跑一轮聚合"
            return make_eligibility(tenant_code=tenant_code)

        monkeypatch.setattr(
            facade_mod.EcoAuditQueryService,
            "load_tenant_stats",
            staticmethod(_stats),
        )
        monkeypatch.setattr(
            facade_mod.EcoWhitelistService, "evaluate", staticmethod(_evaluate)
        )
        data = await EcoAuditFacade.tenant_profile(FakeDb(), "hz001", now=NOW)
        assert data["tenant"]["tenantCode"] == "hz001"
        assert data["eligibility"]["eligible"] is True

    @pytest.mark.asyncio
    async def test_whitelist_page(self, monkeypatch):
        credit = SimpleNamespace(
            tenant_code="hz001",
            whitelist_at=NOW,
            whitelist_source=1,
            whitelist_by=None,
            whitelist_revoked_at=None,
            whitelist_revoke_reason=None,
            publish_count=20,
            listed_count=18,
            deal_count=6,
            deal_completed_count=5,
            force_delist_count=0,
            report_valid_count=0,
        )

        async def _page(db, **kwargs):
            return [(credit, "杭州佳达物流有限公司")], 1

        monkeypatch.setattr(
            facade_mod.EcoWhitelistService, "page_members", staticmethod(_page)
        )
        data = await EcoAuditFacade.page_whitelist(FakeDb(), page=1, size=20)
        assert data["total"] == 1
        assert data["list"][0]["whitelistSourceLabel"] == "自动授予"
