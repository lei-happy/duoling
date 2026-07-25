"""服务平台 · 审核台序列化器测试

本模块守四条底线：

1. **审核台不脱敏**：联系方式、车牌、司机姓名必须原样输出——「联系方式违规」
   是驳回原因之一，看不到原文就审不出问题。
2. **源单核验不能把「无从核验」说成「一致」**：手工发布的挂牌没有源单可比，
   ``sourceConsistent`` 必须是 None，否则审核员会对最该警惕的一类挂牌放松要求。
3. **时效字段来自取数层，不在序列化层重算**：队列、详情、积压三处必须同一口径。
4. **枚举一律带 Label**：运营后台不该靠前端再维护一份状态码字典。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §4.1
对应代码：backend/app/modules/console/services/ecosystem/audit_serializer.py
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from app.modules.console.models.ecosystem.constants import (
    AuditStatus,
    PostAuditAction,
    PostRejectReason,
    PostStatus,
    PostType,
    SourceType,
)
from app.modules.console.services.ecosystem import audit_sla
from app.modules.console.services.ecosystem.audit_query_service import AuditQueueRow
from app.modules.client.services.ecosystem.content_guard import SuspiciousFlag
from app.modules.console.services.ecosystem.audit_serializer import (
    PRECHECK_FLAG_LABELS,
    EcoAuditSerializer,
)

NOW = datetime(2026, 7, 25, 14, 0, 0)


def make_post(**kwargs):
    defaults = dict(
        id=101,
        post_no="HY202607250001",
        post_type=PostType.CARGO,
        title="杭州→成都 商品车 8 台",
        status=PostStatus.AUDITING,
        audit_status=AuditStatus.PENDING,
        is_top=0,
        owner_tenant_code="hz001",
        owner_tenant_name="杭州佳达物流有限公司",
        owner_masked_name="杭州佳达***",
        publisher_user_id=9,
        publisher_name="张三",
        from_province="浙江省",
        from_city="杭州市",
        from_district="萧山区",
        from_region_code=330109,
        from_name="杭州萧山",
        to_province="四川省",
        to_city="成都市",
        to_district="龙泉驿区",
        to_region_code=510112,
        to_name="成都龙泉驿",
        any_direction=0,
        window_start=datetime(2026, 7, 27, 8, 0, 0),
        window_end=datetime(2026, 7, 28, 18, 0, 0),
        total_quantity=8,
        quantity_unit="台",
        remaining_quantity=8,
        price_type=2,
        price_amount=Decimal("1200.00"),
        price_include_tax=1,
        price_negotiable=1,
        cooperation_type=1,
        keep_listed_after_deal=0,
        contact_name="张三",
        contact_phone="13800001111",
        contact_backup="0571-88889999",
        visibility_level=2,
        contact_visibility=3,
        apply_block_rule=1,
        extra_block_tenants=None,
        source_type=SourceType.SYSTEM_DOC,
        source_id=5001,
        source_snapshot_at=datetime(2026, 7, 25, 9, 0, 0),
        source_changed=0,
        source_changed_at=None,
        valid_from=datetime(2026, 7, 25, 9, 0, 0),
        valid_until=datetime(2026, 8, 1, 9, 0, 0),
        top_until=None,
        delist_reason=None,
        delist_remark=None,
        view_count=12,
        viewer_count=5,
        intent_count=2,
        deal_count=0,
        last_active_at=NOW,
        submitted_at=datetime(2026, 7, 25, 9, 0, 0),
        listed_at=None,
        audit_at=None,
        audit_by=None,
        audit_reason=None,
        precheck_flags=None,
        created_at=datetime(2026, 7, 25, 8, 50, 0),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def make_capacity(**kwargs):
    defaults = dict(
        post_granularity=1,
        truck_type="轿运车",
        slot_count=8,
        truck_length=Decimal("17.50"),
        rated_load=Decimal("30.00"),
        truck_quantity=1,
        plate_number="浙A12345",
        plate_masked="浙A***45",
        plate_public=0,
        has_trailer=1,
        trailer_plate_number="浙A67890挂",
        driver_name="王大山",
        driver_display="王师傅",
        driver_years=8,
        driver_order_count=120,
        departure_ready_at=datetime(2026, 7, 26, 8, 0, 0),
        pickup_radius=50,
        good_at_categories=["商品车"],
        can_invoice=1,
        invoice_type="专票9%",
        has_insurance=1,
        service_promise="准时到达",
        settle_require=2,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# ---------------------------------------------------------------------------
# 摘要与全字段
# ---------------------------------------------------------------------------


class TestPostSummary:
    def test_labels_are_translated(self):
        data = EcoAuditSerializer.post_summary(make_post())
        assert data["statusLabel"] == "待审核"
        assert data["auditStatusLabel"] == "待审核"
        assert data["postTypeLabel"] == "货源"

    def test_flag_count_helps_triage(self):
        """审核员先看有可疑标记的那批，所以列表就要给出标记数"""
        flags = [
            {"code": "contact_in_text", "level": "block"},
            {"code": "price_abnormal", "level": "warn"},
        ]
        data = EcoAuditSerializer.post_summary(make_post(precheck_flags=flags))
        assert data["precheckFlagCount"] == 2
        assert data["precheckFlags"] == flags

    def test_datetime_is_formatted(self):
        data = EcoAuditSerializer.post_summary(make_post())
        assert data["submittedAt"] == "2026-07-25 09:00:00"
        assert data["listedAt"] is None

    def test_price_is_json_safe(self):
        data = EcoAuditSerializer.post_summary(make_post())
        assert data["priceAmount"] == 1200.0
        assert isinstance(data["priceAmount"], float)

    def test_summary_has_no_contact(self):
        """列表不带联系方式：一屏 20 条手机号既没用，也扩大了泄露面"""
        data = EcoAuditSerializer.post_summary(make_post())
        assert "contactPhone" not in data


class TestPostFull:
    def test_contact_is_visible_to_ops(self):
        """联系方式违规是驳回原因之一，审核台必须能看到原文"""
        data = EcoAuditSerializer.post_full(make_post())
        assert data["contactName"] == "张三"
        assert data["contactPhone"] == "13800001111"
        assert data["contactBackup"] == "0571-88889999"

    def test_driver_name_only_here(self):
        """司机姓名落了库但只允许审核台输出：核验车牌与司机的对应关系需要它"""
        data = EcoAuditSerializer.post_full(
            make_post(post_type=PostType.CAPACITY), capacity=make_capacity()
        )
        assert data["capacity"]["driverName"] == "王大山"
        assert data["capacity"]["plateNumber"] == "浙A12345"

    def test_cargo_block_only_for_cargo(self):
        data = EcoAuditSerializer.post_full(make_post())
        assert "capacity" not in data
        assert "cargo" not in data  # 未传扩展对象时不臆造空块

    def test_destinations_are_ordered_payload(self):
        dests = [
            SimpleNamespace(province="四川省", city="成都市", region_code=510100, sort_order=0),
            SimpleNamespace(province="重庆市", city=None, region_code=500000, sort_order=1),
        ]
        data = EcoAuditSerializer.post_full(make_post(), destinations=dests)
        assert data["destinations"][0]["city"] == "成都市"
        assert data["destinations"][1]["city"] is None
        assert data["destinations"][1]["sortOrder"] == 1


# ---------------------------------------------------------------------------
# 判断依据
# ---------------------------------------------------------------------------


class TestPrecheck:
    def test_blocking_flag_is_summarized(self):
        data = EcoAuditSerializer.precheck(
            make_post(precheck_flags=[{"code": "x", "level": "block"}])
        )
        assert data["hasBlocking"] is True

    def test_warn_only_is_not_blocking(self):
        data = EcoAuditSerializer.precheck(
            make_post(precheck_flags=[{"code": "x", "level": "warn"}])
        )
        assert data["hasBlocking"] is False
        assert data["flagCount"] == 1

    def test_empty_flags(self):
        data = EcoAuditSerializer.precheck(make_post())
        assert data["flags"] == []
        assert data["flagCount"] == 0
        assert data["hasBlocking"] is False

    def test_every_suspicious_flag_has_a_label(self):
        """新增一条可疑规则却忘了配措辞，审核台就会显示 ``new_tenant`` 这种编码

        落库的是编码，措辞在 ``PRECHECK_FLAG_LABELS`` 里，两边由这条用例锁住。
        """
        codes = {
            value
            for name, value in vars(SuspiciousFlag).items()
            if not name.startswith("_") and isinstance(value, str)
        }
        assert codes
        assert codes - set(PRECHECK_FLAG_LABELS) == set()


class TestSourceCheck:
    def test_manual_post_is_unknown_not_consistent(self):
        """手工发布没有源单可比，一致性必须是「无从核验」而不是 True"""
        data = EcoAuditSerializer.source_check(
            make_post(source_type=SourceType.MANUAL, source_id=None)
        )
        assert data["hasSource"] is False
        assert data["sourceConsistent"] is None
        assert "重点看" in data["hint"]

    def test_source_changed_is_inconsistent(self):
        data = EcoAuditSerializer.source_check(
            make_post(source_changed=1, source_changed_at=NOW)
        )
        assert data["sourceConsistent"] is False
        assert data["sourceChangedAt"] == "2026-07-25 14:00:00"

    def test_clean_system_source(self):
        data = EcoAuditSerializer.source_check(make_post())
        assert data["hasSource"] is True
        assert data["sourceConsistent"] is True
        assert data["sourceId"] == 5001

    def test_source_type_system_without_id_is_not_verifiable(self):
        """来源标了系统单据却没有单号，属于脏数据，同样不能当成一致"""
        data = EcoAuditSerializer.source_check(make_post(source_id=None))
        assert data["hasSource"] is False
        assert data["sourceConsistent"] is None


# ---------------------------------------------------------------------------
# 队列行与时效
# ---------------------------------------------------------------------------


class TestQueueRow:
    def test_urgency_label_comes_from_sla_module(self):
        row = AuditQueueRow(
            post=make_post(),
            waited_minutes=95,
            urgency=audit_sla.AuditUrgency.WARNING,
            deadline=datetime(2026, 7, 25, 11, 0, 0),
        )
        data = EcoAuditSerializer.queue_row(row)
        assert data["waitedMinutes"] == 95
        assert data["urgencyLabel"] == "即将超时"
        assert data["isOverdue"] is False
        assert data["deadline"] == "2026-07-25 11:00:00"

    def test_overdue_row(self):
        row = AuditQueueRow(
            post=make_post(),
            waited_minutes=200,
            urgency=audit_sla.AuditUrgency.OVERDUE,
        )
        data = EcoAuditSerializer.queue_row(row)
        assert data["isOverdue"] is True
        assert data["urgencyLabel"] == "已超时"

    def test_row_without_submitted_at_is_safe(self):
        """草稿类脏数据没有进队时间，序列化不能炸"""
        data = EcoAuditSerializer.queue_row(AuditQueueRow(post=make_post()))
        assert data["waitedMinutes"] == 0
        assert data["deadline"] is None


# ---------------------------------------------------------------------------
# 租户档案与流水
# ---------------------------------------------------------------------------


def make_stats(**kwargs):
    defaults = dict(
        tenant_code="hz001",
        tenant_name="杭州佳达物流有限公司",
        masked_name="杭州佳达***",
        license_verified=True,
        transport_license_verified=True,
        realname_verified=True,
        hall_enabled=True,
        audit_whitelist=False,
        whitelist_source=None,
        whitelist_at=None,
        whitelist_revoked_at=None,
        whitelist_revoke_reason=None,
        publish_restricted_until=None,
        intent_restricted_until=None,
        publish_count=20,
        listed_count=18,
        pending_count=1,
        reject_count=2,
        reject_count_recent=0,
        force_delist_count=1,
        force_delist_count_recent=0,
        spot_check_fail_count=0,
        deal_count=6,
        deal_completed_count=5,
        report_valid_count=0,
        report_valid_count_recent=0,
        first_publish_at=datetime(2026, 5, 12, 9, 20, 0),
        recent_posts=[],
        pass_rate=Decimal("90.00"),
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


class TestTenantContext:
    def test_recent_counters_are_kept_apart(self):
        """累计数与 90 天回溯数并列给出：去年被下架过和上周被下架过不是一回事"""
        data = EcoAuditSerializer.tenant_context(make_stats())
        assert data["forceDelistCount"] == 1
        assert data["forceDelistCountRecent"] == 0

    def test_pass_rate_is_float(self):
        data = EcoAuditSerializer.tenant_context(make_stats())
        assert data["passRate"] == 90.0

    def test_pass_rate_none_when_never_published(self):
        """没发过就没有通过率，给 None 而不是 0——0% 会被读成「一次都没通过」"""
        data = EcoAuditSerializer.tenant_context(
            make_stats(publish_count=0, pass_rate=None)
        )
        assert data["passRate"] is None

    def test_recent_posts_are_flattened(self):
        stats = make_stats(recent_posts=[make_post(id=77, status=PostStatus.LISTED)])
        data = EcoAuditSerializer.tenant_context(stats)
        assert data["recentPosts"][0]["id"] == 77
        assert data["recentPosts"][0]["statusLabel"] == "展示中"


class TestAuditTrail:
    def test_action_and_reason_are_translated(self):
        rows = [
            SimpleNamespace(
                id=3,
                action=PostAuditAction.REJECT,
                from_status=PostStatus.AUDITING,
                to_status=PostStatus.REJECTED,
                operator_type=2,
                operator_id=1,
                operator_name="李运营",
                operator_tenant_code=None,
                reason_code=PostRejectReason.CONTACT_VIOLATION,
                reason="其他要求里写了手机号",
                changed_fields=None,
                created_at=NOW,
            )
        ]
        data = EcoAuditSerializer.audit_trail(rows)[0]
        assert data["actionLabel"] == "审核驳回"
        assert data["reasonLabel"] == "联系方式违规"
        assert data["operatorTypeLabel"] == "平台运营"
        assert data["fromStatusLabel"] == "待审核"

    def test_edit_trail_carries_changed_fields(self):
        """上一轮改了哪些字段决定这一轮该重点看什么"""
        rows = [
            SimpleNamespace(
                id=4,
                action=PostAuditAction.EDIT,
                from_status=PostStatus.LISTED,
                to_status=PostStatus.AUDITING,
                operator_type=1,
                operator_id=8,
                operator_name="张三",
                operator_tenant_code="hz001",
                reason_code=None,
                reason="编辑挂牌",
                changed_fields={"totalQuantity": {"old": 8, "new": 12}},
                created_at=NOW,
            )
        ]
        data = EcoAuditSerializer.audit_trail(rows)[0]
        assert data["changedFields"]["totalQuantity"]["new"] == 12
        assert data["reasonLabel"] is None

    def test_empty_trail(self):
        assert EcoAuditSerializer.audit_trail([]) == []


# ---------------------------------------------------------------------------
# 白名单与动作结果
# ---------------------------------------------------------------------------


class TestEligibility:
    def test_eligible_and_manual_allowed_are_separate(self):
        """两者合成一个布尔值，运营遇到「该放行但不满足自动条件」就只剩改库这条路"""
        result = SimpleNamespace(
            tenant_code="hz001",
            eligible=False,
            manual_allowed=True,
            summary="累计发布 3 条，还差 2 条",
            items=[
                SimpleNamespace(
                    code="license_verified", label="企业认证", passed=True,
                    detail="已通过营业执照核验", blocking=True,
                ),
                SimpleNamespace(
                    code="publish_volume", label="历史挂牌", passed=False,
                    detail="累计发布 3 条，还差 2 条", blocking=False,
                ),
            ],
        )
        data = EcoAuditSerializer.eligibility(result)
        assert data["eligible"] is False
        assert data["manualAllowed"] is True
        assert data["items"][0]["blocking"] is True
        assert data["items"][1]["detail"] == "累计发布 3 条，还差 2 条"


class TestActionResults:
    def test_action_result_exposes_ref_sync_state(self):
        """角标没同步不是失败，前端不能提示成审核失败"""
        result = SimpleNamespace(
            post_id=101,
            post_no="HY202607250001",
            status=PostStatus.LISTED,
            audit_status=AuditStatus.APPROVED,
            changed=True,
            ref_synced=False,
            whitelist_revoked=False,
            invalidated_intents=[],
        )
        data = EcoAuditSerializer.action_result(result)
        assert data["statusLabel"] == "展示中"
        assert data["auditStatusLabel"] == "审核通过"
        assert data["refSynced"] is False
        assert data["invalidatedIntentCount"] == 0

    def test_batch_result_lists_failures(self):
        result = SimpleNamespace(
            success_count=2,
            succeeded=["HY001", "HY002"],
            failed=[
                SimpleNamespace(post_id=9, post_no="HY009", message="已被发布方撤回")
            ],
        )
        data = EcoAuditSerializer.batch_result(result)
        assert data["successCount"] == 2
        assert data["failed"][0]["postNo"] == "HY009"

    def test_whitelist_member_row(self):
        credit = SimpleNamespace(
            tenant_code="hz001",
            whitelist_at=NOW,
            whitelist_source=2,
            whitelist_by=1,
            whitelist_revoked_at=None,
            whitelist_revoke_reason=None,
            publish_count=20,
            listed_count=18,
            deal_count=6,
            deal_completed_count=5,
            force_delist_count=2,
            report_valid_count=0,
        )
        data = EcoAuditSerializer.whitelist_member((credit, "杭州佳达物流有限公司"))
        assert data["tenantName"] == "杭州佳达物流有限公司"
        assert data["whitelistSourceLabel"] == "人工授予"
        # 白名单列表带上违规数，运营才能发现「被下架过 2 次却还在白名单里」
        assert data["forceDelistCount"] == 2

    def test_backlog_carries_sla_thresholds(self):
        stats = SimpleNamespace(
            pending=12, pending_overdue=3, pending_flagged=5,
            spot_check_pending=7, spot_check_overdue=1,
        )
        data = EcoAuditSerializer.backlog(stats)
        assert data["pendingOverdue"] == 3
        assert data["slaMinutes"] == audit_sla.SLA_MINUTES
        assert data["warnMinutes"] == audit_sla.WARN_MINUTES
