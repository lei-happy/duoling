"""服务平台 · 发布上下文装载测试

本模块守四条底线：

1. **缺记录一律取安全侧默认**：名片与信誉都是懒加载表，查不到时必须当作
   「未认证、非白名单」。反过来会让一个运营还没碰过的新租户直接拿到认证层
   可见范围——这个错误不会报错，只会静默泄露。
2. **关停到期自动恢复**：一次「停 7 天」的处置不能因为没人记得回来解封
   而变成永久封停。
3. **预检素材一处装齐**：四个入口（发布货源 / 发布运力 / 编辑 / 重新上架）
   共用一份装载逻辑，任何一处漏带敏感词库都等于那条路径上的词库静默失效。
4. **相似判定不能只比线路**：专线公司天天发同一条线路，只比线路会把它的每条
   挂牌都标成可疑，标记泛滥等于把规则关掉。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.3
对应代码：backend/app/modules/client/services/ecosystem/publish_context.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
from typing import Any, List, Optional

import pytest
from sqlalchemy.dialects import mysql

from app.modules.client.services.ecosystem.post_draft import PostDraft
from app.modules.client.services.ecosystem.publish_context import (
    EcoPublishContextService,
    TenantHallContext,
)
from app.modules.console.models.ecosystem.constants import PostType
from app.modules.console.models.ecosystem.tenant_profile import SysEcoTenantProfile

NOW = datetime(2026, 7, 25, 10, 0, 0)
TENANT = "hz001"


# ---------------------------------------------------------------------------
# 测试替身
# ---------------------------------------------------------------------------


class FakeResult:
    def __init__(self, rows: Optional[List[Any]] = None):
        self._rows = list(rows or [])

    def first(self):
        return self._rows[0] if self._rows else None

    def scalars(self):
        return self

    def all(self):
        return list(self._rows)


class FakeDb:
    """按调用顺序吐出预置结果，同时录下每条 statement 供断言"""

    def __init__(self, results: Optional[List[Any]] = None):
        self.results = list(results or [])
        self.statements: List[Any] = []
        self.added: List[Any] = []
        self.flush_count = 0

    async def execute(self, stmt):
        self.statements.append(stmt)
        if not self.results:
            return FakeResult([])
        nxt = self.results.pop(0)
        return nxt if isinstance(nxt, FakeResult) else FakeResult(nxt)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flush_count += 1

    def sql(self, index: int = -1) -> str:
        return str(
            self.statements[index].compile(
                dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}
            )
        )


def tenant_row(**kwargs):
    """`load_tenant` 那条 join 查询返回的一行"""
    defaults = dict(
        tenant_name="杭州佳达物流有限公司",
        created_at=NOW - timedelta(days=400),
        profile_id=1,
        masked_name="杭州佳**物流",
        license_verified=1,
        hall_enabled=1,
        disabled_reason=None,
        disabled_until=None,
        default_valid_days=7,
        default_visibility_level=2,
        default_contact_visibility=3,
        contact_name="张经理",
        contact_phone="13800001111",
        audit_whitelist=0,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def stub_sensitive_words(monkeypatch):
    """默认给两条词库规则，避免每个用例都去打桩"""

    async def _rules(db, scope):
        return [
            SimpleNamespace(word="代开发票", category=4, action=1),
            SimpleNamespace(word="某某平台", category=4, action=2),
        ]

    monkeypatch.setattr(
        "app.modules.client.services.ecosystem.publish_context."
        "SensitiveWordService.get_rules",
        _rules,
    )


# ---------------------------------------------------------------------------
# 身份快照
# ---------------------------------------------------------------------------


class TestLoadTenant:
    @pytest.mark.asyncio
    async def test_full_profile(self):
        db = FakeDb([[tenant_row(audit_whitelist=1)]])
        ctx = await EcoPublishContextService.load_tenant(db, TENANT, now=NOW)

        assert ctx.tenant_code == TENANT
        assert ctx.tenant_name == "杭州佳达物流有限公司"
        assert ctx.masked_name == "杭州佳**物流"
        assert ctx.license_verified is True
        assert ctx.audit_whitelist is True
        assert ctx.hall_enabled is True
        assert ctx.profile_exists is True
        assert ctx.tenant_age_days == 400
        assert ctx.default_contact_name == "张经理"

    @pytest.mark.asyncio
    async def test_missing_profile_falls_back_to_safe_side(self):
        """名片没建：未认证、非白名单，但大厅能力照常开着"""
        db = FakeDb(
            [[tenant_row(profile_id=None, masked_name=None, license_verified=None,
                         hall_enabled=None, default_valid_days=None,
                         default_visibility_level=None,
                         default_contact_visibility=None,
                         contact_name=None, contact_phone=None,
                         audit_whitelist=None)]]
        )
        ctx = await EcoPublishContextService.load_tenant(db, TENANT, now=NOW)

        assert ctx.license_verified is False
        assert ctx.audit_whitelist is False
        assert ctx.profile_exists is False
        # 缺记录不等于被关停：新租户必须能正常进大厅
        assert ctx.hall_enabled is True
        assert ctx.default_valid_days == 7
        assert ctx.default_visibility_level == 2
        assert ctx.default_contact_visibility == 3

    @pytest.mark.asyncio
    async def test_tenant_not_found(self):
        db = FakeDb([[]])
        ctx = await EcoPublishContextService.load_tenant(db, TENANT, now=NOW)

        assert ctx.tenant_code == TENANT
        assert ctx.tenant_name == ""
        assert ctx.license_verified is False
        assert ctx.audit_whitelist is False
        assert ctx.tenant_age_days is None

    @pytest.mark.asyncio
    async def test_hall_disabled_carries_reason(self):
        db = FakeDb(
            [[tenant_row(hall_enabled=0, disabled_reason="多次发布虚假货源")]]
        )
        ctx = await EcoPublishContextService.load_tenant(db, TENANT, now=NOW)

        assert ctx.hall_enabled is False
        assert ctx.disabled_reason == "多次发布虚假货源"

    @pytest.mark.asyncio
    async def test_disabled_until_expired_recovers(self):
        """停到昨天为止的处置，今天自动恢复，且不再挂着原因"""
        db = FakeDb(
            [[tenant_row(hall_enabled=0, disabled_reason="临时关停",
                         disabled_until=NOW - timedelta(days=1))]]
        )
        ctx = await EcoPublishContextService.load_tenant(db, TENANT, now=NOW)

        assert ctx.hall_enabled is True
        assert ctx.disabled_reason is None

    @pytest.mark.asyncio
    async def test_disabled_until_in_future_keeps_disabled(self):
        db = FakeDb(
            [[tenant_row(hall_enabled=0, disabled_reason="临时关停",
                         disabled_until=NOW + timedelta(days=3))]]
        )
        ctx = await EcoPublishContextService.load_tenant(db, TENANT, now=NOW)

        assert ctx.hall_enabled is False
        assert ctx.disabled_reason == "临时关停"

    @pytest.mark.asyncio
    async def test_permanent_disable_without_until(self):
        db = FakeDb([[tenant_row(hall_enabled=0, disabled_until=None)]])
        ctx = await EcoPublishContextService.load_tenant(db, TENANT, now=NOW)

        assert ctx.hall_enabled is False

    @pytest.mark.asyncio
    async def test_query_filters_deleted_tenant(self):
        db = FakeDb([[tenant_row()]])
        await EcoPublishContextService.load_tenant(db, TENANT, now=NOW)
        sql = db.sql()

        assert "sys_tenant" in sql
        assert "LEFT OUTER JOIN sys_eco_tenant_profile" in sql
        assert "LEFT OUTER JOIN sys_eco_tenant_credit" in sql
        assert "sys_tenant.is_deleted = 0" in sql


class TestMaskedName:
    def test_falls_back_to_computed_mask(self):
        ctx = TenantHallContext(
            tenant_code=TENANT, tenant_name="杭州佳达物流有限公司", masked_name=None
        )
        assert ctx.display_masked_name
        assert "佳达" not in ctx.display_masked_name

    def test_prefers_stored_mask(self):
        ctx = TenantHallContext(
            tenant_code=TENANT, tenant_name="杭州佳达物流有限公司",
            masked_name="杭州佳**物流",
        )
        assert ctx.display_masked_name == "杭州佳**物流"


class TestEnsureProfile:
    @pytest.mark.asyncio
    async def test_creates_when_missing(self):
        db = FakeDb()
        ctx = TenantHallContext(
            tenant_code=TENANT, tenant_name="杭州佳达物流有限公司",
            profile_exists=False,
        )
        await EcoPublishContextService.ensure_profile(db, ctx)

        assert len(db.added) == 1
        row = db.added[0]
        assert isinstance(row, SysEcoTenantProfile)
        assert row.tenant_code == TENANT
        assert row.masked_name
        assert ctx.profile_exists is True

    @pytest.mark.asyncio
    async def test_noop_when_exists(self):
        db = FakeDb()
        ctx = TenantHallContext(tenant_code=TENANT, profile_exists=True)
        await EcoPublishContextService.ensure_profile(db, ctx)

        assert db.added == []
        assert db.flush_count == 0


class TestContextMapping:
    def test_publisher(self):
        ctx = TenantHallContext(
            tenant_code=TENANT, tenant_name="杭州佳达物流有限公司",
            masked_name="杭州佳**物流", audit_whitelist=True,
            hall_enabled=False, disabled_reason="临时关停",
        )
        publisher = EcoPublishContextService.publisher(
            ctx, user_id=7, user_name="张经理"
        )

        assert publisher.tenant_code == TENANT
        assert publisher.tenant_name == "杭州佳达物流有限公司"
        assert publisher.masked_name == "杭州佳**物流"
        assert publisher.user_id == 7
        assert publisher.audit_whitelist is True
        assert publisher.hall_enabled is False
        assert publisher.disabled_reason == "临时关停"

    def test_owner(self):
        ctx = TenantHallContext(tenant_code=TENANT, audit_whitelist=True)
        owner = EcoPublishContextService.owner(ctx, user_id=7, user_name="张经理")

        assert owner.tenant_code == TENANT
        assert owner.user_id == 7
        assert owner.user_name == "张经理"
        assert owner.audit_whitelist is True


# ---------------------------------------------------------------------------
# 预检素材
# ---------------------------------------------------------------------------


def make_draft(**kwargs) -> PostDraft:
    defaults = dict(
        post_type=PostType.CARGO,
        from_province="浙江省",
        from_city="杭州市",
        to_province="四川省",
        to_city="成都市",
        total_quantity=8,
        window_start=NOW + timedelta(days=1),
    )
    defaults.update(kwargs)
    return PostDraft(**defaults)


class TestLoadPrecheck:
    @pytest.mark.asyncio
    async def test_gathers_db_facts(self):
        # 第一条查询：(累计发布数, 近 24h 发布数)；第二条：相似挂牌
        db = FakeDb([[(12, 3)], ["HY202607240007"]])
        ctx = TenantHallContext(tenant_code=TENANT, tenant_age_days=18)

        data = await EcoPublishContextService.load_precheck(
            db, ctx=ctx, draft=make_draft(), now=NOW
        )

        assert len(data.sensitive_words) == 2
        assert data.posts_last_24h == 3
        assert data.is_first_post is False
        assert data.tenant_age_days == 18
        assert data.similar_post_no == "HY202607240007"
        assert data.now == NOW
        # 一期没有同线路均价基线，报价异常规则保持关闭
        assert data.price_ratio_to_baseline is None

    @pytest.mark.asyncio
    async def test_first_post_flag(self):
        db = FakeDb([[(0, 0)], []])
        ctx = TenantHallContext(tenant_code=TENANT, tenant_age_days=2)

        data = await EcoPublishContextService.load_precheck(
            db, ctx=ctx, draft=make_draft(), now=NOW
        )

        assert data.is_first_post is True
        assert data.posts_last_24h == 0
        assert data.similar_post_no is None

    @pytest.mark.asyncio
    async def test_no_rows_at_all(self):
        db = FakeDb([[], []])
        ctx = TenantHallContext(tenant_code=TENANT)

        data = await EcoPublishContextService.load_precheck(
            db, ctx=ctx, draft=make_draft(), now=NOW
        )

        assert data.posts_last_24h == 0
        assert data.is_first_post is True

    @pytest.mark.asyncio
    async def test_without_draft_skips_similarity(self):
        """不传草稿时仍要带上词库等素材，只是跳过相似判定"""
        db = FakeDb([[(4, 1)]])
        ctx = TenantHallContext(tenant_code=TENANT)

        data = await EcoPublishContextService.load_precheck(db, ctx=ctx, now=NOW)

        assert data.similar_post_no is None
        assert len(data.sensitive_words) == 2
        assert len(db.statements) == 1

    @pytest.mark.asyncio
    async def test_counts_exclude_self_on_edit(self):
        db = FakeDb([[(4, 1)], []])
        ctx = TenantHallContext(tenant_code=TENANT)

        await EcoPublishContextService.load_precheck(
            db, ctx=ctx, draft=make_draft(), now=NOW, exclude_post_id=555
        )

        count_sql = db.sql(0)
        similar_sql = db.sql(1)
        # 编辑时不排除自己，等于每次编辑都把自己判成「与近 7 天某条高度相似」
        assert "sys_eco_post.id != 555" in count_sql
        assert "sys_eco_post.id != 555" in similar_sql


class TestSimilarPostQuery:
    @pytest.mark.asyncio
    async def test_requires_route_date_and_quantity(self):
        db = FakeDb([[(4, 1)], []])
        ctx = TenantHallContext(tenant_code=TENANT)

        await EcoPublishContextService.load_precheck(
            db, ctx=ctx, draft=make_draft(), now=NOW
        )
        sql = db.sql(1)

        assert "from_province = '浙江省'" in sql
        assert "from_city = '杭州市'" in sql
        assert "to_province = '四川省'" in sql
        # 同线路之外还要同台数、同装车日，否则专线公司条条都被标可疑
        assert "total_quantity = 8" in sql
        assert "date(sys_eco_post.window_start)" in sql
        assert "LIMIT 1" in sql

    @pytest.mark.asyncio
    async def test_null_destination_matches_null(self):
        db = FakeDb([[(4, 1)], []])
        ctx = TenantHallContext(tenant_code=TENANT)

        await EcoPublishContextService.load_precheck(
            db, ctx=ctx,
            draft=make_draft(to_province=None, to_city=None, any_direction=1),
            now=NOW,
        )
        sql = db.sql(1)

        assert "to_province IS NULL" in sql
        assert "to_city IS NULL" in sql

    @pytest.mark.asyncio
    async def test_skips_when_origin_unknown(self):
        """出发地解析不出来的草稿本来就发不出去，不必再查相似"""
        db = FakeDb([[(4, 1)]])
        ctx = TenantHallContext(tenant_code=TENANT)

        data = await EcoPublishContextService.load_precheck(
            db, ctx=ctx, draft=make_draft(from_province=None), now=NOW
        )

        assert data.similar_post_no is None
        assert len(db.statements) == 1

    @pytest.mark.asyncio
    async def test_excludes_cancelled_and_rejected(self):
        db = FakeDb([[(4, 1)], []])
        ctx = TenantHallContext(tenant_code=TENANT)

        await EcoPublishContextService.load_precheck(
            db, ctx=ctx, draft=make_draft(), now=NOW
        )
        sql = db.sql(1)

        assert "status NOT IN (9, 2)" in sql
