"""服务平台 · 挂牌发布测试

发布是唯一同时写平台库与租户库的动作，出错的后果分两档：

- **重复挂牌**：同一张任务单被挂两次，同行会收到两条一样的货，且发出去收不回来。
  查重必须走平台库，不能走可能缺失的租户侧镜像。
- **镜像缺失**：任务单少一个角标，可由巡检补偿。所以它不该阻断发布。

这两档的取舍是本模块的核心，测试重点覆盖它，以及免审直通的收口条件。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/01.架构与撮合内核设计.md §2.2
对应代码：backend/app/modules/client/services/ecosystem/publish_service.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.common.exceptions import BizException
from app.modules.client.services.ecosystem import publish_service as publish_module
from app.modules.client.services.ecosystem.content_guard import PrecheckInput
from app.modules.client.services.ecosystem.post_draft import DestDraft, PostDraft
from app.modules.client.services.ecosystem.publish_service import (
    EcoPublishService,
    PublisherContext,
)
from app.modules.console.models.ecosystem.capacity_post import SysEcoCapacityPost
from app.modules.console.models.ecosystem.cargo_post import SysEcoCargoPost
from app.modules.console.models.ecosystem.constants import (
    AuditStatus,
    PostAuditAction,
    PostStatus,
    PostType,
    PriceType,
    SourceType,
)
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_audit import SysEcoPostAudit
from app.modules.console.models.ecosystem.post_dest import SysEcoPostDest
from app.modules.console.services.ecosystem.eco_number_service import EcoNumberService
from app.modules.console.services.system.sensitive_word_service import SensitiveWordRule

NOW = datetime(2026, 7, 25, 10, 0, 0)


# ---------------------------------------------------------------------------
# 测试替身
# ---------------------------------------------------------------------------


class FakeNested:
    def __init__(self, db, fail_with=None):
        self.db = db
        self.fail_with = fail_with

    async def __aenter__(self):
        self.db.savepoints += 1
        if self.fail_with is not None:
            raise self.fail_with
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.db.rolled_back += 1
        return False


class FakeResult:
    def __init__(self, rows):
        self._rows = list(rows)

    def scalars(self):
        return self

    def all(self):
        return list(self._rows)

    def first(self):
        return self._rows[0] if self._rows else None


class FakeDb:
    """够用的 Session 替身：记录 add 的对象、模拟 flush 分配自增 ID。"""

    def __init__(self, existing_rows=(), fail_flushes: int = 0):
        self.added = []
        self.existing_rows = list(existing_rows)
        self.fail_flushes = fail_flushes
        self.flush_count = 0
        self.savepoints = 0
        self.rolled_back = 0
        self._next_id = 1000

    async def execute(self, _stmt):
        return FakeResult(self.existing_rows)

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flush_count += 1
        if self.fail_flushes > 0:
            self.fail_flushes -= 1
            raise IntegrityError(
                "INSERT", {}, Exception("Duplicate entry 'HY202607250001' for key 'uk_eco_post_no'")
            )
        for obj in self.added:
            if getattr(obj, "id", None) is None:
                self._next_id += 1
                obj.id = self._next_id

    def begin_nested(self):
        return FakeNested(self)

    def of_type(self, model):
        return [o for o in self.added if isinstance(o, model)]

    def one_of(self, model):
        rows = self.of_type(model)
        assert len(rows) == 1, f"期望恰好 1 条 {model.__name__}，实际 {len(rows)}"
        return rows[0]


class FailingTenantDb(FakeDb):
    """租户库写入失败：模拟双写窗口里的后半段挂掉。"""

    def begin_nested(self):
        return FakeNested(self, fail_with=RuntimeError("tenant db down"))


@pytest.fixture(autouse=True)
def _stub_number_generator(monkeypatch):
    """编号生成已有独立测试，这里固定输出，让断言聚焦发布逻辑。"""
    state = {"n": 0, "prefer_db_calls": []}

    async def fake_next(db, post_type, *, prefer_db=False):
        state["n"] += 1
        state["prefer_db_calls"].append(prefer_db)
        prefix = "HY" if int(post_type) == PostType.CARGO else "YL"
        return f"{prefix}20260725{state['n']:04d}"

    monkeypatch.setattr(EcoNumberService, "next_post_no", fake_next)
    return state


def cargo_draft(**overrides) -> PostDraft:
    draft = PostDraft(
        post_type=PostType.CARGO,
        source_type=SourceType.REF_TASK,
        source_id=777,
        title="杭州→成都 20台 比亚迪",
        from_province="浙江省",
        from_city="杭州市",
        from_region_code=330100,
        window_start=NOW + timedelta(days=1),
        total_quantity=20,
        price_type=PriceType.PER_UNIT,
        price_amount=Decimal("800.00"),
        contact_name="张三",
        contact_phone="13800138000",
        valid_days=7,
        destinations=[DestDraft(province="四川省", city="成都市", region_code=510100)],
        ext={"cargo_category": 1, "segment_count": 1},
    )
    for k, v in overrides.items():
        setattr(draft, k, v)
    draft.sync_primary_dest()
    return draft


def capacity_draft(**overrides) -> PostDraft:
    draft = PostDraft(
        post_type=PostType.CAPACITY,
        source_type=SourceType.REF_CAPACITY,
        source_id=555,
        title="成都→不限流向 8位板车",
        from_province="四川省",
        from_city="成都市",
        any_direction=1,
        window_start=NOW + timedelta(days=1),
        total_quantity=8,
        contact_name="李四",
        contact_phone="13900139000",
        valid_days=7,
        ext={"truck_type": "板车", "slot_count": 8},
    )
    for k, v in overrides.items():
        setattr(draft, k, v)
    draft.sync_primary_dest()
    return draft


def publisher(**overrides) -> PublisherContext:
    ctx = PublisherContext(
        tenant_code="2001",
        tenant_name="杭州速达物流有限公司",
        user_id=9,
        user_name="张三",
    )
    for k, v in overrides.items():
        setattr(ctx, k, v)
    return ctx


async def do_publish(draft=None, pub=None, tenant_db=None, platform_db=None, **kwargs):
    return await EcoPublishService.publish(
        tenant_db=tenant_db or FakeDb(),
        platform_db=platform_db or FakeDb(),
        draft=draft or cargo_draft(),
        publisher=pub or publisher(),
        now=NOW,
        **kwargs,
    )


# ---------------------------------------------------------------------------


class TestHappyPath:
    @pytest.mark.asyncio
    async def test_writes_post_ext_dest_and_audit(self):
        platform_db = FakeDb()
        await do_publish(platform_db=platform_db)
        assert len(platform_db.of_type(SysEcoPost)) == 1
        assert len(platform_db.of_type(SysEcoCargoPost)) == 1
        assert len(platform_db.of_type(SysEcoPostDest)) == 1
        assert len(platform_db.of_type(SysEcoPostAudit)) == 1

    @pytest.mark.asyncio
    async def test_children_point_at_the_new_post_id(self):
        """外键接错会让扩展信息挂到别的挂牌上，列表看不出来、详情才炸。"""
        platform_db = FakeDb()
        await do_publish(platform_db=platform_db)
        post = platform_db.one_of(SysEcoPost)
        assert platform_db.one_of(SysEcoCargoPost).post_id == post.id
        assert platform_db.one_of(SysEcoPostDest).post_id == post.id
        assert platform_db.one_of(SysEcoPostAudit).post_id == post.id

    @pytest.mark.asyncio
    async def test_default_goes_to_audit_queue(self):
        result = await do_publish()
        assert result.status == PostStatus.AUDITING
        assert result.audit_status == AuditStatus.PENDING
        assert result.auto_listed is False

    @pytest.mark.asyncio
    async def test_validity_window_from_valid_days(self):
        platform_db = FakeDb()
        await do_publish(draft=cargo_draft(valid_days=15), platform_db=platform_db)
        post = platform_db.one_of(SysEcoPost)
        assert post.valid_from == NOW
        assert post.valid_until == NOW + timedelta(days=15)

    @pytest.mark.asyncio
    async def test_owner_name_is_masked_for_the_card(self):
        platform_db = FakeDb()
        await do_publish(platform_db=platform_db)
        post = platform_db.one_of(SysEcoPost)
        assert post.owner_tenant_name == "杭州速达物流有限公司"
        assert post.owner_masked_name == "杭州**物流"

    @pytest.mark.asyncio
    async def test_audit_trail_records_submit(self):
        platform_db = FakeDb()
        await do_publish(platform_db=platform_db)
        trail = platform_db.one_of(SysEcoPostAudit)
        assert trail.action == PostAuditAction.SUBMIT
        assert trail.to_status == PostStatus.AUDITING
        assert trail.operator_tenant_code == "2001"

    @pytest.mark.asyncio
    async def test_capacity_uses_its_own_extension_table(self):
        """内核按 post_type 分发扩展表，接错会把运力字段写进货源表。"""
        platform_db = FakeDb()
        await do_publish(draft=capacity_draft(), platform_db=platform_db)
        assert len(platform_db.of_type(SysEcoCapacityPost)) == 1
        assert platform_db.of_type(SysEcoCargoPost) == []

    @pytest.mark.asyncio
    async def test_capacity_post_no_uses_capacity_prefix(self):
        result = await do_publish(draft=capacity_draft())
        assert result.post_no.startswith("YL")

    @pytest.mark.asyncio
    async def test_any_direction_writes_no_dest_row(self):
        """接受任意流向靠主表标记表达，写目的地行会让筛选出现矛盾结果。"""
        platform_db = FakeDb()
        await do_publish(draft=capacity_draft(), platform_db=platform_db)
        assert platform_db.of_type(SysEcoPostDest) == []
        assert platform_db.one_of(SysEcoPost).to_province is None


class TestDuplicateGuard:
    @pytest.mark.asyncio
    async def test_existing_active_post_blocks_republish(self):
        existing = SysEcoPost(post_no="HY202607250001")
        with pytest.raises(BizException) as e:
            await do_publish(platform_db=FakeDb(existing_rows=[existing]))
        assert "HY202607250001" in str(e.value)

    @pytest.mark.asyncio
    async def test_duplicate_message_tells_user_where_to_look(self):
        """光说「重复发布」没用，用户下一步是想去看那条挂牌。"""
        existing = SysEcoPost(post_no="HY202607250001")
        with pytest.raises(BizException) as e:
            await do_publish(platform_db=FakeDb(existing_rows=[existing]))
        assert "我发布的" in str(e.value)

    @pytest.mark.asyncio
    async def test_nothing_is_written_when_duplicated(self):
        existing = SysEcoPost(post_no="HY202607250001")
        platform_db = FakeDb(existing_rows=[existing])
        tenant_db = FakeDb()
        with pytest.raises(BizException):
            await do_publish(platform_db=platform_db, tenant_db=tenant_db)
        assert platform_db.added == []
        assert tenant_db.added == []

    @pytest.mark.asyncio
    async def test_manual_publish_skips_duplicate_query(self):
        """手工发布没有源单，无从查重；此时不该被别人的历史挂牌挡住。"""
        existing = SysEcoPost(post_no="HY202607250001")
        draft = cargo_draft(source_type=SourceType.MANUAL, source_id=None)
        result = await do_publish(
            draft=draft, platform_db=FakeDb(existing_rows=[existing])
        )
        assert result.post_no.startswith("HY")


class TestWhitelistFastPath:
    @pytest.mark.asyncio
    async def test_whitelist_tenant_is_listed_immediately(self):
        result = await do_publish(pub=publisher(audit_whitelist=True))
        assert result.status == PostStatus.LISTED
        assert result.audit_status == AuditStatus.WHITELIST_PASS
        assert result.auto_listed is True

    @pytest.mark.asyncio
    async def test_listed_at_is_stamped_on_fast_path(self):
        platform_db = FakeDb()
        await do_publish(pub=publisher(audit_whitelist=True), platform_db=platform_db)
        assert platform_db.one_of(SysEcoPost).listed_at == NOW

    @pytest.mark.asyncio
    async def test_non_whitelist_has_no_listed_at(self):
        platform_db = FakeDb()
        await do_publish(platform_db=platform_db)
        assert platform_db.one_of(SysEcoPost).listed_at is None

    @pytest.mark.asyncio
    async def test_suspicious_content_revokes_the_fast_path(self):
        """白名单是对历史表现的信任，不是对单条内容的豁免。

        否则白名单账号一旦被盗用，违规内容会绕过全部人工环节直接进大厅。
        """
        precheck = PrecheckInput(posts_last_24h=999)
        result = await do_publish(
            pub=publisher(audit_whitelist=True), precheck=precheck
        )
        assert result.auto_listed is False
        assert result.status == PostStatus.AUDITING
        assert result.suspicious_flags

    @pytest.mark.asyncio
    async def test_fast_path_records_whitelist_action(self):
        platform_db = FakeDb()
        await do_publish(pub=publisher(audit_whitelist=True), platform_db=platform_db)
        assert (
            platform_db.one_of(SysEcoPostAudit).action
            == PostAuditAction.WHITELIST_PASS
        )


class TestHallDisabled:
    @pytest.mark.asyncio
    async def test_disabled_tenant_cannot_publish(self):
        with pytest.raises(BizException):
            await do_publish(pub=publisher(hall_enabled=False))

    @pytest.mark.asyncio
    async def test_disabled_reason_is_surfaced_to_user(self):
        with pytest.raises(BizException) as e:
            await do_publish(
                pub=publisher(hall_enabled=False, disabled_reason="存在虚假信息举报")
            )
        assert "存在虚假信息举报" in str(e.value)

    @pytest.mark.asyncio
    async def test_disabled_without_reason_points_to_support(self):
        with pytest.raises(BizException) as e:
            await do_publish(pub=publisher(hall_enabled=False))
        assert "客服" in str(e.value)

    @pytest.mark.asyncio
    async def test_check_happens_before_any_write(self):
        platform_db = FakeDb()
        with pytest.raises(BizException):
            await do_publish(pub=publisher(hall_enabled=False), platform_db=platform_db)
        assert platform_db.added == []


class TestDraftValidation:
    """库里是非空约束的字段，必须在这里拦住并说清缺什么。"""

    @pytest.mark.asyncio
    async def test_missing_province_is_rejected(self):
        with pytest.raises(BizException) as e:
            await do_publish(draft=cargo_draft(from_province=None))
        assert "地址" in str(e.value)

    @pytest.mark.asyncio
    async def test_missing_window_start_is_rejected(self):
        with pytest.raises(BizException):
            await do_publish(draft=cargo_draft(window_start=None))

    @pytest.mark.asyncio
    async def test_blank_title_is_rejected(self):
        with pytest.raises(BizException):
            await do_publish(draft=cargo_draft(title="   "))

    @pytest.mark.asyncio
    async def test_missing_contact_is_rejected(self):
        with pytest.raises(BizException):
            await do_publish(draft=cargo_draft(contact_phone=""))

    @pytest.mark.asyncio
    async def test_inverted_time_window_is_rejected(self):
        draft = cargo_draft(
            window_start=NOW + timedelta(days=3), window_end=NOW + timedelta(days=1)
        )
        with pytest.raises(BizException):
            await do_publish(draft=draft)

    @pytest.mark.asyncio
    async def test_unknown_post_type_is_rejected(self):
        with pytest.raises(BizException):
            await do_publish(draft=cargo_draft(post_type=99))

    @pytest.mark.asyncio
    async def test_zero_valid_days_is_rejected(self):
        with pytest.raises(BizException):
            await do_publish(draft=cargo_draft(valid_days=0))


class TestPrecheckIntegration:
    @pytest.mark.asyncio
    async def test_contact_info_in_title_blocks_publish(self):
        draft = cargo_draft(title="杭州→成都 有货电话13800138000")
        draft.guard_texts = {"标题": draft.title}
        with pytest.raises(BizException) as e:
            await do_publish(draft=draft, precheck=PrecheckInput())
        assert "标题" in str(e.value)

    @pytest.mark.asyncio
    async def test_sensitive_word_blocks_publish(self):
        draft = cargo_draft()
        draft.guard_texts = {"其他要求": "需要走私通道"}
        rules = [SensitiveWordRule(word="走私", category=1, action=1)]
        with pytest.raises(BizException):
            await do_publish(
                draft=draft, precheck=PrecheckInput(sensitive_words=rules)
            )

    @pytest.mark.asyncio
    async def test_nothing_written_when_blocked(self):
        draft = cargo_draft()
        draft.guard_texts = {"其他要求": "微信13800138000"}
        platform_db = FakeDb()
        with pytest.raises(BizException):
            await do_publish(
                draft=draft, platform_db=platform_db, precheck=PrecheckInput()
            )
        assert platform_db.added == []

    @pytest.mark.asyncio
    async def test_suspicious_flags_are_persisted_for_reviewer(self):
        """可疑标记要落库，审核员才能在队列里看到标红原因。"""
        platform_db = FakeDb()
        await do_publish(
            platform_db=platform_db, precheck=PrecheckInput(posts_last_24h=999)
        )
        assert platform_db.one_of(SysEcoPost).precheck_flags

    @pytest.mark.asyncio
    async def test_soft_expired_license_flags_but_does_not_block(self):
        """保险过期不拦发布，但要落进 precheck_flags 让审核员看见。"""
        draft = capacity_draft()
        draft.soft_expired_licenses = ["车辆保险"]
        platform_db = FakeDb()
        result = await do_publish(
            draft=draft, platform_db=platform_db, precheck=PrecheckInput()
        )
        assert result.post_no
        assert "insurance_expired" in result.suspicious_flags
        assert platform_db.one_of(SysEcoPost).precheck_flags == ["insurance_expired"]

    @pytest.mark.asyncio
    async def test_soft_expired_license_revokes_whitelist_fast_path(self):
        """标红了就不该直通——否则审核员根本没机会看到这条提示。"""
        draft = capacity_draft()
        draft.soft_expired_licenses = ["车辆保险"]
        result = await do_publish(
            draft=draft, pub=publisher(audit_whitelist=True), precheck=PrecheckInput()
        )
        assert result.auto_listed is False

    @pytest.mark.asyncio
    async def test_hard_expired_license_blocks(self):
        draft = capacity_draft()
        draft.expired_licenses = ["道路运输证"]
        with pytest.raises(BizException) as e:
            await do_publish(draft=draft, precheck=PrecheckInput())
        assert "道路运输证" in str(e.value)

    @pytest.mark.asyncio
    async def test_clean_post_has_no_flags(self):
        platform_db = FakeDb()
        await do_publish(platform_db=platform_db, precheck=PrecheckInput())
        assert platform_db.one_of(SysEcoPost).precheck_flags is None

    @pytest.mark.asyncio
    async def test_route_facts_come_from_draft_not_caller(self):
        """起终点相同必须被拦住，且判定素材以 draft 为准，不信调用方另填的值。"""
        draft = cargo_draft(
            destinations=[DestDraft(province="浙江省", city="杭州市")]
        )
        draft.sync_primary_dest()
        with pytest.raises(BizException):
            await do_publish(draft=draft, precheck=PrecheckInput())

    @pytest.mark.asyncio
    async def test_precheck_none_skips_all_rules(self):
        """运营补录场景：不传预检素材即跳过，不能因此报错。"""
        draft = cargo_draft(title="联系13800138000")
        draft.guard_texts = {"标题": draft.title}
        result = await do_publish(draft=draft, precheck=None)
        assert result.post_no


class TestTenantMirror:
    @pytest.mark.asyncio
    async def test_ref_mirrors_post_identity(self):
        tenant_db = FakeDb()
        result = await do_publish(tenant_db=tenant_db)
        ref = tenant_db.one_of(publish_module.BizEcoPostRef)
        assert ref.post_id == result.post_id
        assert ref.post_no == result.post_no
        assert ref.post_status == result.status
        assert ref.source_id == 777

    @pytest.mark.asyncio
    async def test_mirror_failure_does_not_fail_publish(self):
        """挂牌已在平台库建好，为一个展示角标回滚整个发布对用户是更差的结果。"""
        result = await do_publish(tenant_db=FailingTenantDb())
        assert result.post_no
        assert result.ref_synced is False

    @pytest.mark.asyncio
    async def test_successful_mirror_is_reported(self):
        result = await do_publish()
        assert result.ref_synced is True

    @pytest.mark.asyncio
    async def test_platform_is_written_before_tenant(self):
        """顺序反了就拿不到 post_id，租户镜像只能填空值。"""
        platform_db = FakeDb()
        tenant_db = FakeDb()
        await do_publish(platform_db=platform_db, tenant_db=tenant_db)
        assert tenant_db.one_of(publish_module.BizEcoPostRef).post_id == (
            platform_db.one_of(SysEcoPost).id
        )


class TestPostNoConflictRetry:
    @pytest.mark.asyncio
    async def test_duplicate_post_no_is_retried(self):
        platform_db = FakeDb(fail_flushes=1)
        result = await do_publish(platform_db=platform_db)
        assert result.post_no.endswith("0002")

    @pytest.mark.asyncio
    async def test_retry_switches_to_db_watermark(self, _stub_number_generator):
        """重试必须以库内水位取号，否则会反复撞同一批号。"""
        await do_publish(platform_db=FakeDb(fail_flushes=1))
        assert _stub_number_generator["prefer_db_calls"] == [False, True]

    @pytest.mark.asyncio
    async def test_persistent_conflict_gives_friendly_error(self):
        with pytest.raises(BizException) as e:
            await do_publish(platform_db=FakeDb(fail_flushes=99))
        assert "重试" in str(e.value)

    @pytest.mark.asyncio
    async def test_unrelated_integrity_error_is_not_swallowed(self):
        """别的约束冲突说明有真 bug，重试只会掩盖它。"""

        class OtherErrorDb(FakeDb):
            async def flush(self):
                raise IntegrityError(
                    "INSERT", {}, Exception("cannot be null: contact_name")
                )

        with pytest.raises(IntegrityError):
            await do_publish(platform_db=OtherErrorDb())


class TestUserFacingMessages:
    @pytest.mark.asyncio
    async def test_audit_path_sets_expectation(self):
        result = await do_publish()
        assert "审核" in result.message

    @pytest.mark.asyncio
    async def test_fast_path_message_says_it_is_live(self):
        result = await do_publish(pub=publisher(audit_whitelist=True))
        assert "同行" in result.message

    @pytest.mark.asyncio
    async def test_message_names_the_right_hall(self):
        cargo = await do_publish()
        capacity = await do_publish(draft=capacity_draft())
        assert "货源大厅" in cargo.message
        assert "运力大厅" in capacity.message
