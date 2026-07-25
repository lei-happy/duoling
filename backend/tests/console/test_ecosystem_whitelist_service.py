"""服务平台 · 免审白名单测试

本模块守四条底线：

1. **认证不能被人工授予绕过**：`04` §5.1 明确「认证是参与大厅的前提」，
   未核验营业执照的租户免审直通，等于连最基本的身份门槛都让掉了。
2. **发布量与成交量可以由运营酌情放行**：运营线下认识这家企业、或者刚签的
   重点客户，这类判断本来就该由人来做。
3. **移出后有冷静期**：否则抽检发现问题移出的租户第二天就被自动流程放回来，
   处置等于没有发生。
4. **判定结果逐条可读**：只回 ``eligible: false`` 等于没回答运营那句
   「这家为什么还没进白名单」。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.2
对应代码：backend/app/modules/console/services/ecosystem/whitelist_service.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pytest

from app.common.exceptions import BizException
from app.modules.console.models.ecosystem.constants import (
    WHITELIST_CLEAN_DAYS,
    WHITELIST_MIN_DEAL,
    WHITELIST_MIN_PUBLISH,
    WHITELIST_RECOVER_DAYS,
    WhitelistSource,
)
from app.modules.console.models.ecosystem.tenant_credit import SysEcoTenantCredit
from app.modules.console.services.ecosystem.audit_query_service import (
    EcoAuditQueryService,
    OpsContext,
    TenantAuditStats,
)
from app.modules.console.services.ecosystem.whitelist_service import (
    EcoWhitelistService,
    WhitelistCheck,
)

NOW = datetime(2026, 7, 25, 10, 0, 0)
TENANT = "T001"
OPS = OpsContext(user_id=90, user_name="运营小李")


# ---------------------------------------------------------------------------
# 测试替身
# ---------------------------------------------------------------------------


class FakeResult:
    def __init__(self, rows=()):
        self._rows = list(rows)

    def scalars(self):
        return self

    def first(self):
        return self._rows[0] if self._rows else None

    def all(self):
        return list(self._rows)


class FakeDb:
    def __init__(self, credit: Optional[SysEcoTenantCredit] = None):
        self.credit = credit
        self.added: List = []
        self.flush_count = 0

    async def execute(self, stmt):
        return FakeResult([self.credit] if self.credit is not None else [])

    def add(self, obj):
        self.added.append(obj)
        if isinstance(obj, SysEcoTenantCredit):
            self.credit = obj

    async def flush(self):
        self.flush_count += 1


def qualified(**overrides) -> TenantAuditStats:
    """一个刚好满足全部条件的租户档案"""
    fields = dict(
        tenant_code=TENANT,
        tenant_name="杭州速达物流有限公司",
        license_verified=True,
        hall_enabled=True,
        publish_count=WHITELIST_MIN_PUBLISH,
        listed_count=WHITELIST_MIN_PUBLISH,
        reject_count=0,
        reject_count_recent=0,
        force_delist_count_recent=0,
        report_valid_count_recent=0,
        deal_count=2,
        deal_completed_count=WHITELIST_MIN_DEAL,
        whitelist_revoked_at=None,
    )
    fields.update(overrides)
    return TenantAuditStats(**fields)


def make_credit(**overrides) -> SysEcoTenantCredit:
    fields = dict(id=1, tenant_code=TENANT, audit_whitelist=0, is_deleted=0)
    fields.update(overrides)
    return SysEcoTenantCredit(**fields)


@pytest.fixture
def canned_stats(monkeypatch):
    """把租户档案换成可控的替身，让判定成为纯逻辑测试"""

    holder: Dict[str, TenantAuditStats] = {"stats": qualified()}

    async def fake_load(db, tenant_code, **kwargs):
        return holder["stats"]

    monkeypatch.setattr(
        EcoAuditQueryService, "load_tenant_stats", staticmethod(fake_load)
    )
    return holder


def check(result, code: str):
    return next(i for i in result.items if i.code == code)


# ---------------------------------------------------------------------------
# 资格判定
# ---------------------------------------------------------------------------


class TestEvaluate:
    @pytest.mark.asyncio
    async def test_fully_qualified_tenant_is_eligible(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified()
        )

        assert result.eligible is True
        assert result.manual_allowed is True
        assert result.unmet == []
        assert result.summary == "已满足免审白名单的全部条件"

    @pytest.mark.asyncio
    async def test_all_documented_conditions_are_checked(self):
        """漏一条就是给免审开了个后门，逐条钉死"""
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified()
        )

        assert {i.code for i in result.items} == {
            WhitelistCheck.HALL_ENABLED,
            WhitelistCheck.LICENSE_VERIFIED,
            WhitelistCheck.PUBLISH_VOLUME,
            WhitelistCheck.NO_REJECT,
            WhitelistCheck.DEAL_RECORD,
            WhitelistCheck.NO_VIOLATION,
            WhitelistCheck.RECOVER_PERIOD,
        }

    @pytest.mark.asyncio
    async def test_unverified_license_blocks_everything(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified(license_verified=False)
        )

        assert result.eligible is False
        # 认证是硬条件，人工也不能放行
        assert result.manual_allowed is False
        assert check(result, WhitelistCheck.LICENSE_VERIFIED).blocking is True

    @pytest.mark.asyncio
    async def test_disabled_hall_blocks_everything(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified(hall_enabled=False)
        )

        assert result.manual_allowed is False
        assert "大厅能力已被关停" in check(result, WhitelistCheck.HALL_ENABLED).detail

    @pytest.mark.asyncio
    async def test_insufficient_publish_count_reports_the_gap(self):
        """运营要的是「还差几条」，不是「不满足」"""
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified(publish_count=2)
        )

        item = check(result, WhitelistCheck.PUBLISH_VOLUME)
        assert item.passed is False
        assert f"还差 {WHITELIST_MIN_PUBLISH - 2} 条" in item.detail
        # 数量类条件人工可以放行
        assert item.blocking is False
        assert result.manual_allowed is True

    @pytest.mark.asyncio
    async def test_publish_count_above_threshold_passes(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified(publish_count=50)
        )

        assert check(result, WhitelistCheck.PUBLISH_VOLUME).passed is True

    @pytest.mark.asyncio
    async def test_recent_reject_blocks_auto_grant(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified(reject_count_recent=1)
        )

        assert result.eligible is False
        assert "被驳回过 1 次" in check(result, WhitelistCheck.NO_REJECT).detail

    @pytest.mark.asyncio
    async def test_old_reject_outside_window_does_not_block(self):
        """一次一年前的驳回永久堵住免审通道，与「移出 30 天即可再进」自相矛盾"""
        result = await EcoWhitelistService.evaluate(
            FakeDb(),
            TENANT,
            now=NOW,
            stats=qualified(reject_count=9, reject_count_recent=0),
        )

        assert check(result, WhitelistCheck.NO_REJECT).passed is True
        assert result.eligible is True

    @pytest.mark.asyncio
    async def test_no_completed_deal_blocks_auto_grant(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified(deal_completed_count=0)
        )

        assert result.eligible is False
        assert "还没有完成过一单" in check(result, WhitelistCheck.DEAL_RECORD).detail

    @pytest.mark.asyncio
    async def test_force_delist_is_a_violation(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified(force_delist_count_recent=1)
        )

        item = check(result, WhitelistCheck.NO_VIOLATION)
        assert item.passed is False
        assert "被强制下架 1 次" in item.detail

    @pytest.mark.asyncio
    async def test_valid_report_is_a_violation(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified(report_valid_count_recent=2)
        )

        assert "被举报成立 2 次" in check(result, WhitelistCheck.NO_VIOLATION).detail

    @pytest.mark.asyncio
    async def test_both_violation_types_are_listed(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(),
            TENANT,
            now=NOW,
            stats=qualified(force_delist_count_recent=1, report_valid_count_recent=1),
        )

        detail = check(result, WhitelistCheck.NO_VIOLATION).detail
        assert "被强制下架" in detail and "被举报成立" in detail

    @pytest.mark.asyncio
    async def test_clean_window_is_the_documented_one(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified()
        )

        assert (
            f"近 {WHITELIST_CLEAN_DAYS} 天"
            in check(result, WhitelistCheck.NO_VIOLATION).detail
        )

    @pytest.mark.asyncio
    async def test_recover_period_blocks_return(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(),
            TENANT,
            now=NOW,
            stats=qualified(whitelist_revoked_at=NOW - timedelta(days=3)),
        )

        item = check(result, WhitelistCheck.RECOVER_PERIOD)
        assert item.passed is False
        assert "之后才能重新进入" in item.detail
        assert result.eligible is False

    @pytest.mark.asyncio
    async def test_recover_period_expires(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(),
            TENANT,
            now=NOW,
            stats=qualified(
                whitelist_revoked_at=NOW - timedelta(days=WHITELIST_RECOVER_DAYS + 1)
            ),
        )

        assert check(result, WhitelistCheck.RECOVER_PERIOD).passed is True
        assert result.eligible is True

    @pytest.mark.asyncio
    async def test_recover_period_boundary_is_inclusive(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(),
            TENANT,
            now=NOW,
            stats=qualified(
                whitelist_revoked_at=NOW - timedelta(days=WHITELIST_RECOVER_DAYS)
            ),
        )

        assert check(result, WhitelistCheck.RECOVER_PERIOD).passed is True

    @pytest.mark.asyncio
    async def test_never_revoked_passes_recover_check(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(), TENANT, now=NOW, stats=qualified()
        )

        assert "没有被移出过" in check(result, WhitelistCheck.RECOVER_PERIOD).detail

    @pytest.mark.asyncio
    async def test_summary_lists_every_unmet_condition(self):
        result = await EcoWhitelistService.evaluate(
            FakeDb(),
            TENANT,
            now=NOW,
            stats=qualified(publish_count=0, deal_completed_count=0),
        )

        assert len(result.unmet) == 2
        assert "还差" in result.summary
        assert "完成过一单" in result.summary

    @pytest.mark.asyncio
    async def test_evaluate_loads_stats_when_not_given(self, canned_stats):
        canned_stats["stats"] = qualified(publish_count=1)

        result = await EcoWhitelistService.evaluate(FakeDb(), TENANT, now=NOW)

        assert result.eligible is False


# ---------------------------------------------------------------------------
# 授予
# ---------------------------------------------------------------------------


class TestGrant:
    @pytest.mark.asyncio
    async def test_manual_grant_marks_credit(self, canned_stats):
        credit = make_credit()
        db = FakeDb(credit=credit)

        result = await EcoWhitelistService.grant(
            db, TENANT, operator=OPS, source=WhitelistSource.MANUAL, now=NOW
        )

        assert credit.audit_whitelist == 1
        assert credit.whitelist_at == NOW
        assert credit.whitelist_by == OPS.user_id
        assert credit.whitelist_source == WhitelistSource.MANUAL
        assert result.audit_whitelist is True
        assert result.changed is True

    @pytest.mark.asyncio
    async def test_manual_grant_may_waive_volume_thresholds(self, canned_stats):
        """运营线下认识这家企业，这类判断本来就该由人来做"""
        canned_stats["stats"] = qualified(publish_count=0, deal_completed_count=0)
        credit = make_credit()
        db = FakeDb(credit=credit)

        await EcoWhitelistService.grant(
            db, TENANT, operator=OPS, source=WhitelistSource.MANUAL, now=NOW
        )

        assert credit.audit_whitelist == 1

    @pytest.mark.asyncio
    async def test_manual_grant_cannot_waive_certification(self, canned_stats):
        canned_stats["stats"] = qualified(license_verified=False)
        db = FakeDb(credit=make_credit())

        with pytest.raises(BizException, match="营业执照"):
            await EcoWhitelistService.grant(
                db, TENANT, operator=OPS, source=WhitelistSource.MANUAL, now=NOW
            )

    @pytest.mark.asyncio
    async def test_manual_grant_cannot_waive_disabled_hall(self, canned_stats):
        canned_stats["stats"] = qualified(hall_enabled=False)
        db = FakeDb(credit=make_credit())

        with pytest.raises(BizException, match="大厅能力"):
            await EcoWhitelistService.grant(
                db, TENANT, operator=OPS, source=WhitelistSource.MANUAL, now=NOW
            )

    @pytest.mark.asyncio
    async def test_auto_grant_requires_every_condition(self, canned_stats):
        canned_stats["stats"] = qualified(deal_completed_count=0)
        db = FakeDb(credit=make_credit())

        with pytest.raises(BizException, match="还不满足免审条件"):
            await EcoWhitelistService.grant(
                db, TENANT, source=WhitelistSource.AUTO, now=NOW
            )

    @pytest.mark.asyncio
    async def test_auto_grant_records_source(self, canned_stats):
        credit = make_credit()
        db = FakeDb(credit=credit)

        await EcoWhitelistService.grant(
            db, TENANT, source=WhitelistSource.AUTO, now=NOW
        )

        assert credit.whitelist_source == WhitelistSource.AUTO
        assert credit.whitelist_by is None

    @pytest.mark.asyncio
    async def test_already_whitelisted_is_idempotent(self, canned_stats):
        credit = make_credit(audit_whitelist=1, whitelist_at=NOW - timedelta(days=5))
        db = FakeDb(credit=credit)

        result = await EcoWhitelistService.grant(db, TENANT, operator=OPS, now=NOW)

        assert result.changed is False
        assert credit.whitelist_at == NOW - timedelta(days=5)

    @pytest.mark.asyncio
    async def test_credit_row_is_created_on_demand(self, canned_stats):
        """信誉表是懒加载的，白名单操作是它的第一个写入方，取不到就补建"""
        db = FakeDb(credit=None)

        await EcoWhitelistService.grant(db, TENANT, operator=OPS, now=NOW)

        assert isinstance(db.credit, SysEcoTenantCredit)
        assert db.credit.tenant_code == TENANT
        assert db.credit.audit_whitelist == 1

    @pytest.mark.asyncio
    async def test_blank_tenant_code_is_rejected(self, canned_stats):
        with pytest.raises(BizException, match="请选择要操作的企业"):
            await EcoWhitelistService.grant(FakeDb(), "", operator=OPS, now=NOW)

    @pytest.mark.asyncio
    async def test_grant_message_explains_what_changes(self, canned_stats):
        db = FakeDb(credit=make_credit())

        result = await EcoWhitelistService.grant(db, TENANT, operator=OPS, now=NOW)

        assert "直接上架" in result.message and "抽检" in result.message


# ---------------------------------------------------------------------------
# 移出
# ---------------------------------------------------------------------------


class TestRevoke:
    @pytest.mark.asyncio
    async def test_revoke_records_time_and_reason(self):
        credit = make_credit(
            audit_whitelist=1, whitelist_source=WhitelistSource.AUTO
        )
        db = FakeDb(credit=credit)

        result = await EcoWhitelistService.revoke(
            db, TENANT, reason="抽检不通过：线路与实际不符", operator=OPS, now=NOW
        )

        assert credit.audit_whitelist == 0
        assert credit.whitelist_revoked_at == NOW
        assert credit.whitelist_revoke_reason == "抽检不通过：线路与实际不符"
        assert credit.whitelist_source is None
        assert result.changed is True

    @pytest.mark.asyncio
    async def test_revoke_message_mentions_recover_period(self):
        db = FakeDb(credit=make_credit(audit_whitelist=1))

        result = await EcoWhitelistService.revoke(
            db, TENANT, reason="举报成立", now=NOW
        )

        assert str(WHITELIST_RECOVER_DAYS) in result.message

    @pytest.mark.asyncio
    async def test_reason_is_required(self):
        db = FakeDb(credit=make_credit(audit_whitelist=1))

        with pytest.raises(BizException, match="请填写移出白名单的原因"):
            await EcoWhitelistService.revoke(db, TENANT, reason="   ", now=NOW)

    @pytest.mark.asyncio
    async def test_revoking_a_non_member_still_records_the_action(self):
        """连续爽约触发时租户可能本来就不在白名单里，处置记录不能因此丢掉"""
        credit = make_credit(audit_whitelist=0)
        db = FakeDb(credit=credit)

        result = await EcoWhitelistService.revoke(
            db, TENANT, reason="30 天内爽约 2 次", now=NOW
        )

        assert result.changed is False
        assert credit.whitelist_revoked_at == NOW
        assert credit.whitelist_revoke_reason == "30 天内爽约 2 次"

    @pytest.mark.asyncio
    async def test_long_reason_is_truncated(self):
        credit = make_credit(audit_whitelist=1)
        db = FakeDb(credit=credit)

        await EcoWhitelistService.revoke(db, TENANT, reason="很长的原因" * 100, now=NOW)

        assert len(credit.whitelist_revoke_reason) <= 255

    @pytest.mark.asyncio
    async def test_revoke_then_grant_is_blocked_by_recover_period(self, canned_stats):
        """移出当天就能重新自动进入，等于处置没有发生"""
        credit = make_credit(audit_whitelist=1)
        db = FakeDb(credit=credit)
        await EcoWhitelistService.revoke(db, TENANT, reason="抽检不通过", now=NOW)
        canned_stats["stats"] = qualified(whitelist_revoked_at=credit.whitelist_revoked_at)

        with pytest.raises(BizException, match="还不满足免审条件"):
            await EcoWhitelistService.grant(
                db, TENANT, source=WhitelistSource.AUTO, now=NOW
            )


# ---------------------------------------------------------------------------
# 自动同步
# ---------------------------------------------------------------------------


class TestSyncAuto:
    @pytest.mark.asyncio
    async def test_grants_when_qualified(self, canned_stats):
        credit = make_credit()
        db = FakeDb(credit=credit)

        result = await EcoWhitelistService.sync_auto(db, TENANT, now=NOW)

        assert credit.audit_whitelist == 1
        assert result.source == WhitelistSource.AUTO

    @pytest.mark.asyncio
    async def test_stays_quiet_when_not_qualified(self, canned_stats):
        """不够资格就什么都不做，而不是抛异常——它跑在 Worker 里，不是用户操作"""
        canned_stats["stats"] = qualified(publish_count=1)
        credit = make_credit()
        db = FakeDb(credit=credit)

        result = await EcoWhitelistService.sync_auto(db, TENANT, now=NOW)

        assert credit.audit_whitelist == 0
        assert result.changed is False
        assert "还差" in result.message

    @pytest.mark.asyncio
    async def test_never_revokes(self, canned_stats):
        """自动流程只做加法：摘牌是处置动作，必须有明确触发事件与原因"""
        canned_stats["stats"] = qualified(force_delist_count_recent=3)
        credit = make_credit(audit_whitelist=1)
        db = FakeDb(credit=credit)

        result = await EcoWhitelistService.sync_auto(db, TENANT, now=NOW)

        assert credit.audit_whitelist == 1
        assert result.changed is False

    @pytest.mark.asyncio
    async def test_already_whitelisted_short_circuits(self, canned_stats):
        credit = make_credit(audit_whitelist=1, whitelist_source=WhitelistSource.AUTO)
        db = FakeDb(credit=credit)

        result = await EcoWhitelistService.sync_auto(db, TENANT, now=NOW)

        assert result.changed is False
        assert result.audit_whitelist is True
