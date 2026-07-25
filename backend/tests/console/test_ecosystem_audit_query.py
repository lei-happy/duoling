"""服务平台 · 审核台取数测试

本模块守三条底线：

1. **审核台看全量**：运营端的查询**不能**带上租户端那套可见性过滤
   （屏蔽名单、有效期、只看展示中）。带上了，审核员就看不到过期挂牌、
   看不到被屏蔽的挂牌，队列里凭空少掉一批。
2. **待审队列两个状态都要判**：只判 ``audit_status`` 会把已被强制下架的脏数据
   留在队列里，审核员点通过会把它重新推回大厅。
3. **队列排序按进队时间正序**：倒序会让高峰期最早提交的那批永远排在最后，
   SLA 从尾部开始崩。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §4.1
对应代码：backend/app/modules/console/services/ecosystem/audit_query_service.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.dialects import mysql

from app.modules.console.models.ecosystem.constants import (
    AuditStatus,
    CooperationType,
    PostStatus,
    PostType,
    PriceType,
)
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.services.ecosystem import audit_sla
from app.modules.console.services.ecosystem.audit_query_service import (
    MAX_PAGE_SIZE,
    AuditPostFilter,
    AuditQueueRow,
    EcoAuditQueryService,
    TenantAuditStats,
    _asc_nulls_first,
    _desc_nulls_last,
)

NOW = datetime(2026, 7, 25, 10, 0, 0)
TENANT = "T001"


def sql(stmt) -> str:
    return str(
        stmt.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True})
    )


def where_of(stmt) -> str:
    """只取 WHERE 子句：断言「某条件不存在」时 SELECT 的列名会一路误命中"""
    return sql(stmt).split("WHERE", 1)[1]


def pending_sql(flt: AuditPostFilter = None) -> str:
    return sql(EcoAuditQueryService._pending_scope(flt or AuditPostFilter(), NOW))


def base_where(flt: AuditPostFilter = None) -> str:
    return where_of(EcoAuditQueryService._base_scope(flt or AuditPostFilter(), NOW))


# ---------------------------------------------------------------------------
# 安全与范围
# ---------------------------------------------------------------------------


class TestScopeBaseline:
    def test_soft_deleted_excluded(self):
        assert "sys_eco_post.is_deleted = 0" in base_where()

    def test_no_block_rule_filter(self):
        """租户屏蔽名单是租户之间的事，运营必须能看到被屏蔽的挂牌"""
        assert "sys_eco_block_rule" not in pending_sql()

    def test_no_validity_filter(self):
        """过期挂牌照样要能查到，否则审核历史一到期就凭空消失"""
        assert "valid_until" not in base_where()

    def test_no_owner_tenant_filter_by_default(self):
        """运营的职责就是跨租户处置，默认不带归属条件"""
        assert "owner_tenant_code" not in base_where()

    def test_tenant_filter_applies_when_asked(self):
        flt = AuditPostFilter(tenant_code=TENANT)
        assert f"sys_eco_post.owner_tenant_code = '{TENANT}'" in base_where(flt)

    def test_visible_in_hall_status_not_forced(self):
        """审核台要看草稿、驳回、下架，不能只看展示中"""
        assert f"sys_eco_post.status = {PostStatus.LISTED}" not in pending_sql()


# ---------------------------------------------------------------------------
# 待审队列
# ---------------------------------------------------------------------------


class TestPendingScope:
    def test_requires_pending_audit_status(self):
        assert f"sys_eco_post.audit_status = {AuditStatus.PENDING}" in pending_sql()

    def test_requires_auditing_post_status(self):
        """只判 audit_status 会让已被强制下架的脏数据留在队列里"""
        assert f"sys_eco_post.status = {PostStatus.AUDITING}" in pending_sql()

    def test_post_type_filter(self):
        flt = AuditPostFilter(post_type=PostType.CAPACITY)
        assert f"sys_eco_post.post_type = {PostType.CAPACITY}" in pending_sql(flt)

    def test_keyword_searches_no_title_and_company(self):
        flt = AuditPostFilter(keyword="杭州")
        text = pending_sql(flt)
        # 编译成 MySQL 文本时 % 会被转义成 %%
        assert "sys_eco_post.post_no LIKE '%%杭州%%'" in text
        assert "sys_eco_post.title LIKE '%%杭州%%'" in text
        assert "sys_eco_post.owner_tenant_name LIKE '%%杭州%%'" in text

    def test_keyword_is_trimmed(self):
        flt = AuditPostFilter(keyword="  杭州  ")
        assert "LIKE '%%杭州%%'" in pending_sql(flt)

    def test_flagged_only_filters_on_precheck_flags(self):
        flt = AuditPostFilter(flagged_only=True)
        assert "precheck_flags IS NOT NULL" in pending_sql(flt)

    def test_flagged_only_off_by_default(self):
        assert "precheck_flags" not in base_where()

    def test_overdue_only_uses_the_shared_sla_line(self):
        """SQL 里的超时界必须来自同一份工作时段规则，否则会和标红对不上"""
        flt = AuditPostFilter(overdue_only=True)
        line = audit_sla.overdue_before(NOW)
        assert f"sys_eco_post.submitted_at < '{line:%Y-%m-%d %H:%M:%S}'" in (
            pending_sql(flt)
        )

    def test_submitted_range_filters(self):
        flt = AuditPostFilter(
            submitted_from=NOW - timedelta(days=1), submitted_to=NOW
        )
        text = pending_sql(flt)
        assert "sys_eco_post.submitted_at >=" in text
        assert "sys_eco_post.submitted_at <=" in text


class TestSpotCheckScope:
    def test_requires_whitelist_pass(self):
        text = sql(EcoAuditQueryService._spot_check_scope(AuditPostFilter(), NOW))
        assert f"sys_eco_post.audit_status = {AuditStatus.WHITELIST_PASS}" in text

    def test_does_not_require_listed_status(self):
        """免审直通的挂牌可能已经成交或下架，违规内容已经产生影响，不能免检"""
        text = where_of(
            EcoAuditQueryService._spot_check_scope(AuditPostFilter(), NOW)
        )
        assert f"sys_eco_post.status = {PostStatus.LISTED}" not in text


# ---------------------------------------------------------------------------
# 排序
# ---------------------------------------------------------------------------


class TestQueueOrdering:
    """MySQL 不支持 ``NULLS FIRST/LAST``

    SQLAlchemy 的 ``.nulls_first()`` 会把它原样编译进 SQL，语法错误只有真的
    连库执行时才会暴露——只断言 WHERE 的用例一个都拦不住。这里直接盯编译结果。
    """

    def test_no_standard_nulls_syntax(self):
        stmt = select(SysEcoPost).order_by(
            *_asc_nulls_first(SysEcoPost.submitted_at)
        )
        assert "NULLS" not in sql(stmt).upper()

    def test_asc_puts_empty_submitted_at_first(self):
        """进队时间为空是异常数据，该排在队首被人看见"""
        text = sql(select(SysEcoPost).order_by(*_asc_nulls_first(SysEcoPost.submitted_at)))
        assert "ORDER BY sys_eco_post.submitted_at IS NULL DESC" in text
        assert "sys_eco_post.submitted_at ASC" in text

    def test_desc_puts_empty_last(self):
        text = sql(select(SysEcoPost).order_by(*_desc_nulls_last(SysEcoPost.submitted_at)))
        assert "ORDER BY sys_eco_post.submitted_at IS NULL ASC" in text
        assert "sys_eco_post.submitted_at DESC" in text


# ---------------------------------------------------------------------------
# 分页
# ---------------------------------------------------------------------------


class TestPaging:
    def test_first_page_offset_is_zero(self):
        assert AuditPostFilter(page=1, size=20).offset == 0

    def test_offset_uses_clamped_limit(self):
        """页大小被截断后 offset 必须跟着截断值算，否则翻页会跳过数据"""
        flt = AuditPostFilter(page=3, size=500)
        assert flt.limit == MAX_PAGE_SIZE
        assert flt.offset == MAX_PAGE_SIZE * 2

    def test_size_upper_bound(self):
        assert AuditPostFilter(size=9999).limit == MAX_PAGE_SIZE

    def test_size_lower_bound(self):
        assert AuditPostFilter(size=0).limit == 1

    def test_page_lower_bound(self):
        assert AuditPostFilter(page=0).offset == 0
        assert AuditPostFilter(page=-5).offset == 0


# ---------------------------------------------------------------------------
# 队列行的紧迫度
# ---------------------------------------------------------------------------


def make_post(**overrides) -> SysEcoPost:
    fields = dict(
        id=1,
        post_no="HY202607250001",
        post_type=PostType.CARGO,
        owner_tenant_code=TENANT,
        owner_tenant_name="杭州速达物流有限公司",
        owner_masked_name="杭州**物流",
        title="杭州→成都 20台",
        status=PostStatus.AUDITING,
        audit_status=AuditStatus.PENDING,
        submitted_at=NOW - timedelta(hours=3),
        created_at=NOW - timedelta(days=2),
        valid_from=NOW,
        valid_until=NOW + timedelta(days=7),
        from_province="浙江省",
        window_start=NOW + timedelta(days=1),
        price_type=PriceType.NEGOTIABLE,
        cooperation_type=CooperationType.ONCE,
        contact_name="张三",
        contact_phone="13800000000",
    )
    fields.update(overrides)
    return SysEcoPost(**fields)


class TestQueueRow:
    def test_waiting_is_measured_in_work_minutes(self):
        """7:00 提交、10:00 现在：只算 8:30 之后的 90 分钟，不是 180 分钟"""
        row = EcoAuditQueryService._to_row(make_post(), NOW)

        assert row.waited_minutes == 90
        assert row.urgency == audit_sla.AuditUrgency.WARNING
        assert row.is_overdue is False

    def test_overnight_post_is_overdue(self):
        row = EcoAuditQueryService._to_row(
            make_post(submitted_at=NOW - timedelta(days=1)), NOW
        )

        assert row.urgency == audit_sla.AuditUrgency.OVERDUE
        assert row.is_overdue is True

    def test_fresh_post_is_normal(self):
        row = EcoAuditQueryService._to_row(
            make_post(submitted_at=NOW - timedelta(minutes=10)), NOW
        )

        assert row.urgency == audit_sla.AuditUrgency.NORMAL
        assert row.is_overdue is False

    def test_deadline_is_exposed_for_display(self):
        row = EcoAuditQueryService._to_row(
            make_post(submitted_at=NOW - timedelta(minutes=10)), NOW
        )

        assert row.deadline == NOW + timedelta(minutes=110)

    def test_missing_submitted_at_falls_back_to_created_at(self):
        """历史数据没有进队时间，退回创建时间也好过让它没有紧迫度"""
        row = EcoAuditQueryService._to_row(make_post(submitted_at=None), NOW)

        assert row.urgency == audit_sla.AuditUrgency.OVERDUE

    def test_no_timestamp_at_all_degrades_quietly(self):
        row = EcoAuditQueryService._to_row(
            make_post(submitted_at=None, created_at=None), NOW
        )

        assert isinstance(row, AuditQueueRow)
        assert row.urgency == audit_sla.AuditUrgency.NORMAL
        assert row.deadline is None


# ---------------------------------------------------------------------------
# 租户档案
# ---------------------------------------------------------------------------


class TestTenantStats:
    def test_pass_rate_is_none_without_publishes(self):
        """0% 会被读成「一次都没通过」，与「还没发过」是两件不同的事"""
        assert TenantAuditStats(tenant_code=TENANT).pass_rate is None

    def test_pass_rate_is_percentage(self):
        stats = TenantAuditStats(
            tenant_code=TENANT, publish_count=8, listed_count=6
        )
        assert stats.pass_rate == Decimal("75.00")

    def test_pass_rate_full(self):
        stats = TenantAuditStats(
            tenant_code=TENANT, publish_count=5, listed_count=5
        )
        assert stats.pass_rate == Decimal("100.00")

    def test_pass_rate_zero_when_never_listed(self):
        stats = TenantAuditStats(
            tenant_code=TENANT, publish_count=3, listed_count=0
        )
        assert stats.pass_rate == Decimal("0.00")

    def test_defaults_are_safe_for_a_brand_new_tenant(self):
        stats = TenantAuditStats(tenant_code=TENANT)

        assert stats.hall_enabled is True
        assert stats.audit_whitelist is False
        assert stats.license_verified is False
        assert stats.recent_posts == []
