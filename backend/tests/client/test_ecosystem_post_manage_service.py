"""服务平台 · 挂牌管理测试

本模块守四条底线：

1. **越权**：只能操作自己的挂牌，且「不存在」与「不属于你」返回同一句话，
   不给外部留跨租户的存在性探测口子。
2. **编辑与洽谈的关系**：改核心信息会退回重审，但已有意向一律不动；
   停止展示则要让待响应与洽谈中的意向失效，而已选定的不能动（背后有成交单）。
3. **重新上架必须重审**：不给免审直通，否则下架再上架就绕过了运营处置。
4. **有效期只有一条修改路径**：编辑不碰有效期，否则反复保存就能无限续命。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §3.6
          doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.4
对应代码：backend/app/modules/client/services/ecosystem/post_manage_service.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

import pytest

from app.common.exceptions import BizException
from app.modules.client.models.ecosystem.post_ref import BizEcoPostRef
from app.modules.client.services.ecosystem.content_guard import (
    PrecheckInput,
    SensitiveWordRule,
    SuspiciousFlag,
)
from app.modules.client.services.ecosystem.post_draft import DestDraft, PostDraft
from app.modules.client.services.ecosystem.post_edit_policy import MAIN_FIELDS
from app.modules.client.services.ecosystem.post_manage_service import (
    EcoPostManageService,
    OwnerContext,
)
from app.modules.console.models.ecosystem.capacity_post import SysEcoCapacityPost
from app.modules.console.models.ecosystem.cargo_post import SysEcoCargoPost
from app.modules.console.models.ecosystem.constants import (
    MAX_VALID_DAYS,
    AuditStatus,
    CooperationType,
    DelistReason,
    IntentInvalidReason,
    IntentStatus,
    PostAuditAction,
    PostStatus,
    PostType,
    PriceType,
)
from app.modules.console.models.ecosystem.intent import SysEcoIntent
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_audit import SysEcoPostAudit
from app.modules.console.models.ecosystem.post_dest import SysEcoPostDest
from app.modules.console.models.system.sensitive_word import (
    SensitiveWordAction,
    SensitiveWordCategory,
)

NOW = datetime(2026, 7, 25, 10, 0, 0)
TENANT = "T001"
OTHER_TENANT = "T999"


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
        return False


class FakeResult:
    def __init__(self, rows=(), scalar=None):
        self._rows = list(rows)
        self._scalar = scalar

    def scalars(self):
        return self

    def all(self):
        return list(self._rows)

    def first(self):
        return self._rows[0] if self._rows else None

    def scalar(self):
        return self._scalar


def _entity_of(stmt):
    """从 select 语句里认出主实体，认不出就当成聚合查询"""
    try:
        for desc in stmt.column_descriptions:
            entity = desc.get("entity")
            if entity is not None:
                return entity
    except Exception:  # pragma: no cover
        return None
    return None


class FakeDb:
    """按实体分发的 Session 替身

    挂牌管理一次操作要读挂牌、扩展表、目的地、意向四张表，单一返回值的替身
    不够用，所以按 select 的主实体分发。
    """

    def __init__(self, rows: Optional[Dict[type, List]] = None, count: int = 0):
        self.rows: Dict[type, List] = dict(rows or {})
        self.count = count
        self.added: List = []
        self.flush_count = 0
        self.savepoints = 0
        self._next_id = 5000

    async def execute(self, stmt):
        entity = _entity_of(stmt)
        if entity is None:
            return FakeResult(scalar=self.count)
        return FakeResult(self.rows.get(entity, []))

    def add(self, obj):
        self.added.append(obj)

    async def flush(self):
        self.flush_count += 1
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
    """租户库写入失败：角标同步挂掉，但不该阻断主流程"""

    def begin_nested(self):
        return FakeNested(self, fail_with=RuntimeError("tenant db down"))


# ---------------------------------------------------------------------------
# 数据构造
# ---------------------------------------------------------------------------


def make_post(**overrides) -> SysEcoPost:
    post = SysEcoPost(
        post_no="HY202607250001",
        post_type=PostType.CARGO,
        owner_tenant_code=TENANT,
        owner_tenant_name="杭州速达物流有限公司",
        owner_masked_name="杭州**物流",
        publisher_user_id=1,
        publisher_name="张三",
        title="杭州→成都 20台 比亚迪",
        status=PostStatus.LISTED,
        delist_reason=None,
        delist_remark=None,
        is_top=0,
        source_type=1,
        source_id=777,
        source_snapshot_at=NOW - timedelta(days=1),
        source_changed=0,
        source_changed_at=None,
        valid_from=NOW - timedelta(days=2),
        valid_until=NOW + timedelta(days=5),
        from_province="浙江省",
        from_city="杭州市",
        from_district="萧山区",
        from_region_code=330109,
        from_name="浙江省杭州市萧山区",
        to_province="四川省",
        to_city="成都市",
        to_district=None,
        to_region_code=510100,
        to_name="四川省成都市",
        any_direction=0,
        window_start=NOW + timedelta(days=1),
        window_end=None,
        total_quantity=20,
        quantity_unit="台",
        remaining_quantity=20,
        price_type=PriceType.PER_UNIT,
        price_amount=Decimal("800.00"),
        price_include_tax=0,
        price_negotiable=1,
        cooperation_type=CooperationType.ONCE,
        keep_listed_after_deal=0,
        contact_name="张三",
        contact_phone="13800138000",
        contact_backup=None,
        visibility_level=2,
        contact_visibility=3,
        apply_block_rule=1,
        extra_block_tenants=None,
        view_count=10,
        viewer_count=6,
        intent_count=0,
        deal_count=0,
        audit_status=AuditStatus.APPROVED,
        audit_at=NOW - timedelta(days=2),
        audit_by=9,
        audit_reason=None,
        precheck_flags=None,
        listed_at=NOW - timedelta(days=2),
        last_active_at=NOW - timedelta(hours=3),
    )
    post.id = 101
    post.is_deleted = 0
    for k, v in overrides.items():
        setattr(post, k, v)
    return post


def make_cargo_ext(**overrides) -> SysEcoCargoPost:
    ext = SysEcoCargoPost(
        post_id=101,
        cargo_category=1,
        segment_count=1,
        allow_split=0,
        require_insurance=0,
        time_negotiable=1,
        other_requirements="需要带挂",
    )
    ext.id = 201
    ext.is_deleted = 0
    for k, v in overrides.items():
        setattr(ext, k, v)
    return ext


def make_dest(province="四川省", city="成都市", region_code=510100, sort_order=0):
    dest = SysEcoPostDest(
        post_id=101,
        post_type=PostType.CARGO,
        province=province,
        city=city,
        region_code=region_code,
        sort_order=sort_order,
    )
    dest.id = 300 + sort_order
    dest.is_deleted = 0
    return dest


def make_intent(status: int, no: str = "YX202607250001", tenant="T002") -> SysEcoIntent:
    intent = SysEcoIntent(
        intent_no=no,
        post_id=101,
        post_type=PostType.CARGO,
        owner_tenant_code=TENANT,
        initiator_tenant_code=tenant,
        initiator_tenant_name="成都远行物流有限公司",
        status=status,
    )
    intent.id = 400 + status
    intent.is_deleted = 0
    return intent


def make_ref() -> BizEcoPostRef:
    ref = BizEcoPostRef(
        source_type=1,
        source_id=777,
        post_id=101,
        post_no="HY202607250001",
        post_type=PostType.CARGO,
        post_status=PostStatus.LISTED,
        sync_pending=0,
    )
    ref.id = 1
    ref.is_deleted = 0
    return ref


def draft_matching(post: SysEcoPost, *, ext=None, dests=(), **overrides) -> PostDraft:
    """与挂牌完全一致的草稿，用来精确制造「只改了 X」"""
    draft = PostDraft(post_type=post.post_type)
    for name in MAIN_FIELDS:
        setattr(draft, name, getattr(post, name))
    draft.remaining_quantity = post.remaining_quantity
    draft.destinations = [
        DestDraft(
            province=d.province,
            city=d.city,
            region_code=d.region_code,
            sort_order=d.sort_order,
        )
        for d in dests
    ]
    draft.ext = dict(ext or {})
    for k, v in overrides.items():
        setattr(draft, k, v)
    return draft


def platform_db(post: SysEcoPost, *, ext=None, dests=(), intents=(), count=0) -> FakeDb:
    return FakeDb(
        rows={
            SysEcoPost: [post],
            SysEcoCargoPost: [ext] if ext is not None else [],
            SysEcoCapacityPost: [],
            SysEcoPostDest: list(dests),
            SysEcoIntent: list(intents),
        },
        count=count,
    )


def tenant_db(with_ref: bool = True) -> FakeDb:
    return FakeDb(rows={BizEcoPostRef: [make_ref()] if with_ref else []})


OWNER = OwnerContext(tenant_code=TENANT, user_id=1, user_name="张三")
WHITELIST_OWNER = OwnerContext(
    tenant_code=TENANT, user_id=1, user_name="张三", audit_whitelist=True
)


def blocked_precheck() -> PrecheckInput:
    return PrecheckInput(texts={"其他要求": "电话 13800138000"})


def review_word_precheck() -> PrecheckInput:
    return PrecheckInput(
        sensitive_words=[
            SensitiveWordRule(
                word="低价甩",
                category=SensitiveWordCategory.OTHER,
                action=SensitiveWordAction.REVIEW,
            )
        ]
    )


# ---------------------------------------------------------------------------
# 越权与取数
# ---------------------------------------------------------------------------


class TestOwnership:
    @pytest.mark.asyncio
    async def test_other_tenants_post_is_not_found(self):
        post = make_post(owner_tenant_code=OTHER_TENANT)
        # WHERE 里带了归属条件，替身按实体返回，这里模拟查不到
        db = FakeDb(rows={SysEcoPost: []})
        with pytest.raises(BizException) as e:
            await EcoPostManageService.delist(
                tenant_db=tenant_db(),
                platform_db=db,
                post_id=post.id,
                owner=OWNER,
                now=NOW,
            )
        assert "没找到这条挂牌" in e.value.message

    @pytest.mark.asyncio
    async def test_missing_and_forbidden_share_one_message(self):
        """两句文案分开等于给外部一个跨租户的存在性探测器"""
        db = FakeDb(rows={SysEcoPost: []})
        messages = set()
        for post_id in (101, 999999):
            with pytest.raises(BizException) as e:
                await EcoPostManageService.delist(
                    tenant_db=tenant_db(),
                    platform_db=db,
                    post_id=post_id,
                    owner=OWNER,
                    now=NOW,
                )
            messages.add(e.value.message)
        assert len(messages) == 1

    @pytest.mark.asyncio
    async def test_empty_tenant_code_is_a_programming_error(self):
        """租户身份缺失必须炸在开发期，不能静默放行"""
        with pytest.raises(ValueError):
            await EcoPostManageService.delist(
                tenant_db=tenant_db(),
                platform_db=platform_db(make_post()),
                post_id=101,
                owner=OwnerContext(tenant_code=""),
                now=NOW,
            )


# ---------------------------------------------------------------------------
# 编辑
# ---------------------------------------------------------------------------


class TestEditGuards:
    @pytest.mark.asyncio
    async def test_auditing_post_cannot_be_edited_but_gets_a_way_out(self):
        post = make_post(status=PostStatus.AUDITING, audit_status=AuditStatus.PENDING)
        with pytest.raises(BizException) as e:
            await EcoPostManageService.edit(
                tenant_db=tenant_db(),
                platform_db=platform_db(post, ext=make_cargo_ext()),
                post_id=101,
                owner=OWNER,
                draft=draft_matching(post, title="新标题"),
                now=NOW,
            )
        assert "待审核" in e.value.message
        assert "2 小时" in e.value.message

    @pytest.mark.asyncio
    async def test_locked_post_cannot_be_edited(self):
        post = make_post(status=PostStatus.LOCKED)
        with pytest.raises(BizException) as e:
            await EcoPostManageService.edit(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                draft=draft_matching(post, title="新标题"),
                now=NOW,
            )
        assert "已锁定" in e.value.message
        assert "我的合作" in e.value.message

    @pytest.mark.asyncio
    async def test_post_type_cannot_be_switched(self):
        post = make_post()
        draft = draft_matching(post)
        draft.post_type = PostType.CAPACITY
        with pytest.raises(BizException) as e:
            await EcoPostManageService.edit(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                draft=draft,
                now=NOW,
            )
        assert "类型不能修改" in e.value.message

    @pytest.mark.asyncio
    async def test_no_change_saves_nothing(self):
        post = make_post()
        ext = make_cargo_ext()
        dests = [make_dest()]
        db = platform_db(post, ext=ext, dests=dests)
        result = await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=db,
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, ext={"cargo_category": 1}, dests=dests),
            now=NOW,
        )
        assert "没有变化" in result.message
        assert db.of_type(SysEcoPostAudit) == []
        assert result.require_reaudit is False

    @pytest.mark.asyncio
    async def test_blocked_content_rejects_before_touching_the_post(self):
        post = make_post()
        ext = make_cargo_ext()
        dests = [make_dest()]
        db = platform_db(post, ext=ext, dests=dests)
        with pytest.raises(BizException) as e:
            await EcoPostManageService.edit(
                tenant_db=tenant_db(),
                platform_db=db,
                post_id=101,
                owner=OWNER,
                draft=draft_matching(
                    post,
                    dests=dests,
                    ext={"other_requirements": "有事打 13800138000"},
                    guard_texts={"其他要求": "有事打 13800138000"},
                ),
                precheck=PrecheckInput(),
                now=NOW,
            )
        assert "联系方式" in e.value.message
        assert ext.other_requirements == "需要带挂"
        assert db.of_type(SysEcoPostAudit) == []

    @pytest.mark.asyncio
    async def test_precheck_is_skipped_when_nothing_changed(self):
        """没有改动就没有可检的内容，早退在预检之前，避免白跑一遍词库"""
        post = make_post()
        dests = [make_dest()]
        result = await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(
                post, dests=dests, guard_texts={"标题": "有事打 13800138000"}
            ),
            precheck=PrecheckInput(),
            now=NOW,
        )
        assert "没有变化" in result.message


class TestEditTiering:
    @pytest.mark.asyncio
    async def test_fast_edit_stays_in_the_hall(self):
        post = make_post()
        dests = [make_dest()]
        db = platform_db(post, ext=make_cargo_ext(), dests=dests)
        tdb = tenant_db()
        result = await EcoPostManageService.edit(
            tenant_db=tdb,
            platform_db=db,
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, contact_name="李四"),
            now=NOW,
        )
        assert post.status == PostStatus.LISTED
        assert result.require_reaudit is False
        assert result.changed_labels == ["联系方式"]
        # 状态没变就不需要回写角标
        assert tdb.flush_count == 0

    @pytest.mark.asyncio
    async def test_fast_edit_keeps_the_original_audit_status(self):
        """免审直通待抽检的挂牌，不能被一次改联系人洗成正式通过"""
        post = make_post(audit_status=AuditStatus.WHITELIST_PASS)
        dests = [make_dest()]
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, contact_name="李四"),
            now=NOW,
        )
        assert post.audit_status == AuditStatus.WHITELIST_PASS

    @pytest.mark.asyncio
    async def test_core_edit_goes_back_to_the_audit_queue(self):
        post = make_post()
        dests = [make_dest()]
        db = platform_db(post, ext=make_cargo_ext(), dests=dests)
        tdb = tenant_db()
        result = await EcoPostManageService.edit(
            tenant_db=tdb,
            platform_db=db,
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, window_start=NOW + timedelta(days=3)),
            now=NOW,
        )
        assert post.status == PostStatus.AUDITING
        assert post.audit_status == AuditStatus.PENDING
        assert result.require_reaudit is True
        assert "时间安排" in result.changed_labels
        assert tdb.rows[BizEcoPostRef][0].post_status == PostStatus.AUDITING

    @pytest.mark.asyncio
    async def test_core_edit_clears_the_previous_rejection(self):
        """驳回理由留着会让用户以为又被驳了"""
        post = make_post(audit_reason="信息不完整")
        dests = [make_dest()]
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, total_quantity=15),
            now=NOW,
        )
        assert post.audit_reason is None
        assert post.audit_at is None
        assert post.audit_by is None

    @pytest.mark.asyncio
    async def test_whitelist_tenant_keeps_a_core_edit_listed(self):
        post = make_post()
        dests = [make_dest()]
        result = await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=WHITELIST_OWNER,
            draft=draft_matching(post, dests=dests, total_quantity=15),
            now=NOW,
        )
        assert post.status == PostStatus.LISTED
        assert post.audit_status == AuditStatus.WHITELIST_PASS
        assert result.require_reaudit is False

    @pytest.mark.asyncio
    async def test_suspicious_content_upgrades_a_fast_edit_to_full(self):
        """预检放过但需要人看一眼的内容，不能继续留在大厅"""
        post = make_post()
        dests = [make_dest()]
        result = await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(
                post,
                dests=dests,
                title="低价甩一批车",
                guard_texts={"标题": "低价甩一批车"},
            ),
            precheck=review_word_precheck(),
            now=NOW,
        )
        assert post.status == PostStatus.AUDITING
        assert result.require_reaudit is True
        assert SuspiciousFlag.SENSITIVE_WORD_REVIEW in result.suspicious_flags
        assert post.precheck_flags == [SuspiciousFlag.SENSITIVE_WORD_REVIEW]

    @pytest.mark.asyncio
    async def test_suspicious_content_revokes_the_whitelist_fast_path(self):
        post = make_post()
        dests = [make_dest()]
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=WHITELIST_OWNER,
            draft=draft_matching(
                post,
                dests=dests,
                title="低价甩一批车",
                guard_texts={"标题": "低价甩一批车"},
            ),
            precheck=review_word_precheck(),
            now=NOW,
        )
        assert post.status == PostStatus.AUDITING
        assert post.audit_status == AuditStatus.PENDING

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status",
        [PostStatus.DRAFT, PostStatus.REJECTED, PostStatus.DELISTED],
    )
    async def test_offline_statuses_stay_where_they_are(self, status):
        """草稿/驳回/已下架编辑后不该自动进审核队列，否则没有「先存着」的空间"""
        post = make_post(status=status, audit_status=AuditStatus.REJECTED)
        dests = [make_dest()]
        result = await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, from_city="宁波市"),
            now=NOW,
        )
        assert post.status == status
        assert post.audit_status == AuditStatus.REJECTED
        assert result.require_reaudit is False

    @pytest.mark.asyncio
    async def test_editing_a_rejected_post_keeps_the_reason_visible(self):
        post = make_post(
            status=PostStatus.REJECTED,
            audit_status=AuditStatus.REJECTED,
            audit_reason="线路信息不清楚",
        )
        dests = [make_dest()]
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, from_name="浙江省宁波市北仑区"),
            now=NOW,
        )
        assert post.audit_reason == "线路信息不清楚"


class TestEditSideEffects:
    @pytest.mark.asyncio
    async def test_active_intents_survive_a_core_edit(self):
        """洽谈是双方建立起来的关系，不能因为发布方挪了个时间就被系统掐断"""
        post = make_post(intent_count=2)
        dests = [make_dest()]
        talking = make_intent(IntentStatus.TALKING)
        pending = make_intent(IntentStatus.PENDING, no="YX202607250002", tenant="T003")
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(
                post, ext=make_cargo_ext(), dests=dests, intents=[talking, pending]
            ),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, window_start=NOW + timedelta(days=4)),
            now=NOW,
        )
        assert talking.status == IntentStatus.TALKING
        assert pending.status == IntentStatus.PENDING
        assert post.intent_count == 2

    @pytest.mark.asyncio
    async def test_validity_is_never_touched_by_an_edit(self):
        post = make_post()
        original_from, original_until = post.valid_from, post.valid_until
        dests = [make_dest()]
        draft = draft_matching(post, dests=dests, contact_name="李四")
        draft.valid_days = 30
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft,
            now=NOW,
        )
        assert post.valid_from == original_from
        assert post.valid_until == original_until

    @pytest.mark.asyncio
    async def test_source_changed_flag_is_cleared(self):
        """用户已经按最新情况改过了，催更标记不清会被巡检当成没更新而下架"""
        post = make_post(source_changed=1, source_changed_at=NOW - timedelta(hours=5))
        dests = [make_dest()]
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, total_quantity=18),
            now=NOW,
        )
        assert post.source_changed == 0
        assert post.source_changed_at is None

    @pytest.mark.asyncio
    async def test_audit_trail_records_what_changed(self):
        post = make_post()
        dests = [make_dest()]
        db = platform_db(post, ext=make_cargo_ext(), dests=dests)
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=db,
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, price_amount=Decimal("900")),
            now=NOW,
        )
        trail = db.one_of(SysEcoPostAudit)
        assert trail.action == PostAuditAction.EDIT
        assert trail.from_status == PostStatus.LISTED
        assert "报价" in trail.reason
        assert trail.operator_tenant_code == TENANT

    @pytest.mark.asyncio
    async def test_ext_values_are_written_back(self):
        post = make_post()
        ext = make_cargo_ext(other_requirements="需要带挂")
        dests = [make_dest()]
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=ext, dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft_matching(
                post, dests=dests, ext={"other_requirements": "不需要带挂"}
            ),
            now=NOW,
        )
        assert ext.other_requirements == "不需要带挂"

    @pytest.mark.asyncio
    async def test_missing_ext_row_is_created(self):
        post = make_post()
        dests = [make_dest()]
        db = platform_db(post, ext=None, dests=dests)
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=db,
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=dests, ext={"cargo_category": 2}),
            now=NOW,
        )
        created = db.one_of(SysEcoCargoPost)
        assert created.cargo_category == 2
        assert created.post_id == 101

    @pytest.mark.asyncio
    async def test_destinations_are_rewritten_wholesale(self):
        post = make_post()
        old = make_dest()
        db = platform_db(post, ext=make_cargo_ext(), dests=[old])
        draft = draft_matching(post, dests=[old])
        draft.destinations = [
            DestDraft(province="湖北省", city="武汉市", region_code=420100, sort_order=0)
        ]
        draft.sync_primary_dest()
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=db,
            post_id=101,
            owner=OWNER,
            draft=draft,
            now=NOW,
        )
        assert old.is_deleted == 1
        created = db.one_of(SysEcoPostDest)
        assert created.province == "湖北省"

    @pytest.mark.asyncio
    async def test_destinations_untouched_when_unchanged(self):
        post = make_post()
        old = make_dest()
        db = platform_db(post, ext=make_cargo_ext(), dests=[old])
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=db,
            post_id=101,
            owner=OWNER,
            draft=draft_matching(post, dests=[old], contact_name="李四"),
            now=NOW,
        )
        assert old.is_deleted == 0
        assert db.of_type(SysEcoPostDest) == []


class TestEditQuantity:
    @pytest.mark.asyncio
    async def test_cannot_shrink_below_what_others_already_took(self):
        post = make_post(total_quantity=20, remaining_quantity=12, deal_count=1)
        dests = [make_dest()]
        with pytest.raises(BizException) as e:
            await EcoPostManageService.edit(
                tenant_db=tenant_db(),
                platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
                post_id=101,
                owner=OWNER,
                draft=draft_matching(post, dests=dests, total_quantity=5),
                now=NOW,
            )
        assert "8台" in e.value.message

    @pytest.mark.asyncio
    async def test_growing_the_total_keeps_the_dealt_part_deducted(self):
        post = make_post(total_quantity=20, remaining_quantity=12, deal_count=1)
        dests = [make_dest()]
        draft = draft_matching(post, dests=dests, total_quantity=30)
        draft.remaining_quantity = 30
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft,
            now=NOW,
        )
        assert post.total_quantity == 30
        assert post.remaining_quantity == 22

    @pytest.mark.asyncio
    async def test_non_split_post_follows_the_draft(self):
        post = make_post(total_quantity=20, remaining_quantity=None)
        dests = [make_dest()]
        draft = draft_matching(post, dests=dests, total_quantity=25)
        draft.remaining_quantity = None
        await EcoPostManageService.edit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post, ext=make_cargo_ext(), dests=dests),
            post_id=101,
            owner=OWNER,
            draft=draft,
            now=NOW,
        )
        assert post.remaining_quantity is None


# ---------------------------------------------------------------------------
# 停止展示
# ---------------------------------------------------------------------------


class TestDelist:
    @pytest.mark.asyncio
    async def test_happy_path(self):
        post = make_post()
        db = platform_db(post)
        tdb = tenant_db()
        result = await EcoPostManageService.delist(
            tenant_db=tdb, platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert post.status == PostStatus.DELISTED
        assert post.delist_reason == DelistReason.BY_OWNER
        assert result.ref_synced is True
        assert tdb.rows[BizEcoPostRef][0].post_status == PostStatus.DELISTED
        trail = db.one_of(SysEcoPostAudit)
        assert trail.action == PostAuditAction.DELIST_BY_OWNER
        assert trail.to_status == PostStatus.DELISTED

    @pytest.mark.asyncio
    async def test_remark_is_stored_and_logged(self):
        post = make_post()
        db = platform_db(post)
        await EcoPostManageService.delist(
            tenant_db=tenant_db(),
            platform_db=db,
            post_id=101,
            owner=OWNER,
            remark="客户改期了",
            now=NOW,
        )
        assert post.delist_remark == "客户改期了"
        assert db.one_of(SysEcoPostAudit).reason == "客户改期了"

    @pytest.mark.asyncio
    async def test_blank_remark_becomes_null(self):
        post = make_post()
        await EcoPostManageService.delist(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            remark="   ",
            now=NOW,
        )
        assert post.delist_remark is None

    @pytest.mark.asyncio
    async def test_pending_and_talking_intents_are_invalidated(self):
        post = make_post(intent_count=2)
        pending = make_intent(IntentStatus.PENDING)
        talking = make_intent(IntentStatus.TALKING, no="YX202607250002", tenant="T003")
        db = platform_db(post, intents=[pending, talking], count=0)
        result = await EcoPostManageService.delist(
            tenant_db=tenant_db(), platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert pending.status == IntentStatus.INVALID
        assert talking.status == IntentStatus.INVALID
        assert pending.invalid_reason == IntentInvalidReason.POST_DELISTED
        assert len(result.invalidated_intents) == 2
        assert {i.initiator_tenant_code for i in result.invalidated_intents} == {
            "T002",
            "T003",
        }

    @pytest.mark.asyncio
    async def test_selected_intent_is_left_alone(self):
        """已选定的意向背后有成交单，作废它会让成交单失去来源"""
        post = make_post(status=PostStatus.LISTED, intent_count=1)
        selected = make_intent(IntentStatus.SELECTED)
        db = platform_db(post, intents=[], count=1)
        result = await EcoPostManageService.delist(
            tenant_db=tenant_db(), platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert selected.status == IntentStatus.SELECTED
        assert result.invalidated_intents == []
        assert post.intent_count == 1

    @pytest.mark.asyncio
    async def test_intent_count_is_recomputed(self):
        post = make_post(intent_count=99)
        db = platform_db(post, intents=[make_intent(IntentStatus.PENDING)], count=0)
        await EcoPostManageService.delist(
            tenant_db=tenant_db(), platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert post.intent_count == 0

    @pytest.mark.asyncio
    async def test_message_mentions_the_people_still_talking(self):
        post = make_post(intent_count=1)
        db = platform_db(post, intents=[make_intent(IntentStatus.TALKING)], count=0)
        result = await EcoPostManageService.delist(
            tenant_db=tenant_db(), platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert "1 家" in result.message

    @pytest.mark.asyncio
    async def test_already_delisted_is_idempotent(self):
        post = make_post(status=PostStatus.DELISTED, delist_reason=DelistReason.EXPIRED)
        db = platform_db(post)
        result = await EcoPostManageService.delist(
            tenant_db=tenant_db(), platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert "已经停止展示" in result.message
        # 幂等返回不能改写原有的下架原因
        assert post.delist_reason == DelistReason.EXPIRED
        assert db.of_type(SysEcoPostAudit) == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", [PostStatus.LOCKED, PostStatus.FULFILLING])
    async def test_cannot_delist_while_a_deal_is_running(self, status):
        post = make_post(status=status)
        with pytest.raises(BizException) as e:
            await EcoPostManageService.delist(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                now=NOW,
            )
        assert "我的合作" in e.value.message

    @pytest.mark.asyncio
    async def test_auditing_post_can_be_pulled_back(self):
        """源单联动可能在挂牌还排队时就判定信息失效"""
        post = make_post(status=PostStatus.AUDITING, audit_status=AuditStatus.PENDING)
        await EcoPostManageService.delist(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            now=NOW,
        )
        assert post.status == PostStatus.DELISTED

    @pytest.mark.asyncio
    async def test_mirror_failure_does_not_block(self):
        """角标写失败远好过「停止展示失败」但其实已经撤下来了"""
        post = make_post()
        result = await EcoPostManageService.delist(
            tenant_db=FailingTenantDb(rows={BizEcoPostRef: [make_ref()]}),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            now=NOW,
        )
        assert post.status == PostStatus.DELISTED
        assert result.ref_synced is False

    @pytest.mark.asyncio
    async def test_missing_mirror_row_is_reported_not_recreated(self):
        post = make_post()
        result = await EcoPostManageService.delist(
            tenant_db=tenant_db(with_ref=False),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            now=NOW,
        )
        assert result.ref_synced is False
        assert post.status == PostStatus.DELISTED


# ---------------------------------------------------------------------------
# 重新上架
# ---------------------------------------------------------------------------


def delisted_post(**overrides) -> SysEcoPost:
    """到期下架的挂牌，展示跨度 7 天、装车时间还没到"""
    fields = {
        "status": PostStatus.DELISTED,
        "delist_reason": DelistReason.EXPIRED,
        "audit_status": AuditStatus.APPROVED,
        "valid_from": NOW - timedelta(days=9),
        "valid_until": NOW - timedelta(days=2),
        "window_start": NOW + timedelta(days=2),
    }
    fields.update(overrides)
    return make_post(**fields)


class TestRelist:
    @pytest.mark.asyncio
    async def test_goes_back_to_the_audit_queue(self):
        post = delisted_post()
        db = platform_db(post)
        tdb = tenant_db()
        result = await EcoPostManageService.relist(
            tenant_db=tdb, platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert post.status == PostStatus.AUDITING
        assert post.audit_status == AuditStatus.PENDING
        assert post.delist_reason is None
        assert post.delist_remark is None
        assert result.require_reaudit is True
        assert tdb.rows[BizEcoPostRef][0].post_status == PostStatus.AUDITING
        assert db.one_of(SysEcoPostAudit).action == PostAuditAction.RELIST

    @pytest.mark.asyncio
    async def test_whitelist_gets_no_fast_path(self):
        """被下架过的正是这条内容本身，白名单信任的是租户历史表现"""
        post = delisted_post()
        await EcoPostManageService.relist(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=WHITELIST_OWNER,
            now=NOW,
        )
        assert post.status == PostStatus.AUDITING
        assert post.audit_status == AuditStatus.PENDING

    @pytest.mark.asyncio
    async def test_validity_is_reset_so_it_does_not_expire_on_arrival(self):
        post = delisted_post()
        await EcoPostManageService.relist(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            now=NOW,
        )
        assert post.valid_from == NOW
        assert post.valid_until > NOW

    @pytest.mark.asyncio
    async def test_original_span_is_reused_when_no_days_given(self):
        post = delisted_post()  # 原跨度 7 天
        await EcoPostManageService.relist(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            now=NOW,
        )
        assert post.valid_until == NOW + timedelta(days=7)

    @pytest.mark.asyncio
    async def test_explicit_days_win(self):
        post = delisted_post()
        await EcoPostManageService.relist(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            valid_days=15,
            now=NOW,
        )
        assert post.valid_until == NOW + timedelta(days=15)

    @pytest.mark.asyncio
    async def test_invalid_days_are_rejected(self):
        post = delisted_post()
        with pytest.raises(BizException) as e:
            await EcoPostManageService.relist(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                valid_days=9,
                now=NOW,
            )
        assert "展示天数" in e.value.message

    @pytest.mark.asyncio
    async def test_force_delist_history_follows_the_post_to_the_reviewer(self):
        """否则运营会把同一条违规内容当成新挂牌重新放行"""
        post = delisted_post(
            delist_reason=DelistReason.FORCED, delist_remark="夹带外部平台引流"
        )
        result = await EcoPostManageService.relist(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            now=NOW,
        )
        assert SuspiciousFlag.WAS_FORCE_DELISTED in result.suspicious_flags
        assert SuspiciousFlag.WAS_FORCE_DELISTED in (post.precheck_flags or [])

    @pytest.mark.asyncio
    async def test_expired_window_must_be_fixed_first(self):
        post = delisted_post(window_start=NOW - timedelta(days=1))
        with pytest.raises(BizException) as e:
            await EcoPostManageService.relist(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                now=NOW,
            )
        assert "已经过了" in e.value.message
        assert post.status == PostStatus.DELISTED

    @pytest.mark.asyncio
    async def test_sensitive_word_added_after_publish_is_caught(self):
        """词库是运营在线维护的，上次干净的文本这次可能已经命中新词"""
        post = delisted_post(title="代开发票 杭州→成都")
        with pytest.raises(BizException):
            await EcoPostManageService.relist(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                precheck=PrecheckInput(
                    sensitive_words=[
                        SensitiveWordRule(
                            word="代开发票",
                            category=SensitiveWordCategory.OTHER,
                            action=SensitiveWordAction.BLOCK,
                        )
                    ]
                ),
                now=NOW,
            )
        assert post.status == PostStatus.DELISTED

    @pytest.mark.asyncio
    async def test_already_auditing_is_idempotent(self):
        post = make_post(status=PostStatus.AUDITING, audit_status=AuditStatus.PENDING)
        db = platform_db(post)
        result = await EcoPostManageService.relist(
            tenant_db=tenant_db(), platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert "已经在审核中" in result.message
        assert db.of_type(SysEcoPostAudit) == []

    @pytest.mark.asyncio
    async def test_already_listed_says_so(self):
        post = make_post(status=PostStatus.LISTED)
        result = await EcoPostManageService.relist(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            now=NOW,
        )
        assert "正在展示中" in result.message

    @pytest.mark.asyncio
    async def test_finished_post_cannot_be_relisted(self):
        post = make_post(status=PostStatus.FINISHED)
        with pytest.raises(BizException) as e:
            await EcoPostManageService.relist(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                now=NOW,
            )
        assert "已完成" in e.value.message


# ---------------------------------------------------------------------------
# 提交审核
# ---------------------------------------------------------------------------


class TestSubmit:
    @pytest.mark.asyncio
    async def test_draft_enters_the_queue(self):
        post = make_post(
            status=PostStatus.DRAFT,
            audit_status=AuditStatus.NOT_SUBMITTED,
            listed_at=None,
        )
        db = platform_db(post)
        await EcoPostManageService.submit(
            tenant_db=tenant_db(), platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert post.status == PostStatus.AUDITING
        assert post.audit_status == AuditStatus.PENDING
        assert db.one_of(SysEcoPostAudit).action == PostAuditAction.SUBMIT

    @pytest.mark.asyncio
    async def test_draft_validity_is_reset_because_it_may_have_sat_for_days(self):
        post = make_post(
            status=PostStatus.DRAFT,
            valid_from=NOW - timedelta(days=20),
            valid_until=NOW - timedelta(days=13),
        )
        await EcoPostManageService.submit(
            tenant_db=tenant_db(),
            platform_db=platform_db(post),
            post_id=101,
            owner=OWNER,
            now=NOW,
        )
        assert post.valid_from == NOW
        assert post.valid_until == NOW + timedelta(days=7)

    @pytest.mark.asyncio
    async def test_whitelist_draft_goes_straight_to_the_hall(self):
        post = make_post(status=PostStatus.DRAFT, listed_at=None)
        db = platform_db(post)
        result = await EcoPostManageService.submit(
            tenant_db=tenant_db(),
            platform_db=db,
            post_id=101,
            owner=WHITELIST_OWNER,
            now=NOW,
        )
        assert post.status == PostStatus.LISTED
        assert post.audit_status == AuditStatus.WHITELIST_PASS
        assert post.listed_at == NOW
        assert "同行就能看到" in result.message
        assert db.one_of(SysEcoPostAudit).action == PostAuditAction.WHITELIST_PASS

    @pytest.mark.asyncio
    async def test_rejected_post_resubmits_without_a_fast_path(self):
        """驳回是人看过之后的判断，直通上架等于让用户自己决定意见有没有落实"""
        post = make_post(
            status=PostStatus.REJECTED,
            audit_status=AuditStatus.REJECTED,
            audit_reason="线路信息不清楚",
        )
        db = platform_db(post)
        await EcoPostManageService.submit(
            tenant_db=tenant_db(),
            platform_db=db,
            post_id=101,
            owner=WHITELIST_OWNER,
            now=NOW,
        )
        assert post.status == PostStatus.AUDITING
        assert post.audit_status == AuditStatus.PENDING
        assert post.audit_reason is None
        assert db.one_of(SysEcoPostAudit).action == PostAuditAction.RESUBMIT

    @pytest.mark.asyncio
    async def test_delisted_post_is_redirected_to_relist(self):
        post = delisted_post()
        with pytest.raises(BizException) as e:
            await EcoPostManageService.submit(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                now=NOW,
            )
        assert "重新上架" in e.value.message

    @pytest.mark.asyncio
    async def test_already_auditing_is_idempotent(self):
        post = make_post(status=PostStatus.AUDITING, audit_status=AuditStatus.PENDING)
        db = platform_db(post)
        result = await EcoPostManageService.submit(
            tenant_db=tenant_db(), platform_db=db, post_id=101, owner=OWNER, now=NOW
        )
        assert "已经在审核中" in result.message
        assert db.of_type(SysEcoPostAudit) == []

    @pytest.mark.asyncio
    async def test_listed_post_cannot_be_submitted_again(self):
        post = make_post(status=PostStatus.LISTED)
        with pytest.raises(BizException) as e:
            await EcoPostManageService.submit(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                now=NOW,
            )
        assert "展示中" in e.value.message

    @pytest.mark.asyncio
    async def test_blocked_content_stops_the_submit(self):
        post = make_post(status=PostStatus.DRAFT, title="加微信 vx88888888 聊")
        with pytest.raises(BizException) as e:
            await EcoPostManageService.submit(
                tenant_db=tenant_db(),
                platform_db=platform_db(post),
                post_id=101,
                owner=OWNER,
                precheck=PrecheckInput(),
                now=NOW,
            )
        assert "联系方式" in e.value.message
        assert post.status == PostStatus.DRAFT


# ---------------------------------------------------------------------------
# 延长展示
# ---------------------------------------------------------------------------


class TestExtend:
    @pytest.mark.asyncio
    async def test_happy_path(self):
        post = make_post(
            valid_from=NOW - timedelta(days=1), valid_until=NOW + timedelta(days=3)
        )
        db = platform_db(post)
        result = await EcoPostManageService.extend(
            platform_db=db, post_id=101, owner=OWNER, days=7, now=NOW
        )
        assert post.valid_until == NOW + timedelta(days=10)
        assert result.valid_until == post.valid_until
        assert db.one_of(SysEcoPostAudit).action == PostAuditAction.EXTEND

    @pytest.mark.asyncio
    async def test_expired_post_counts_from_now_not_from_the_stale_date(self):
        """从旧的失效时间起算会延完还是过期状态"""
        post = make_post(
            valid_from=NOW - timedelta(days=10), valid_until=NOW - timedelta(days=3)
        )
        await EcoPostManageService.extend(
            platform_db=platform_db(post), post_id=101, owner=OWNER, days=3, now=NOW
        )
        assert post.valid_until == NOW + timedelta(days=3)

    @pytest.mark.asyncio
    async def test_cap_is_enforced(self):
        post = make_post(
            valid_from=NOW - timedelta(days=28), valid_until=NOW + timedelta(days=1)
        )
        with pytest.raises(BizException) as e:
            await EcoPostManageService.extend(
                platform_db=platform_db(post), post_id=101, owner=OWNER, days=7, now=NOW
            )
        assert str(MAX_VALID_DAYS) in e.value.message
        assert "重新发布" in e.value.message

    @pytest.mark.asyncio
    async def test_long_term_cooperation_gets_a_longer_cap(self):
        post = make_post(
            cooperation_type=CooperationType.LONG_TERM,
            valid_from=NOW - timedelta(days=28),
            valid_until=NOW + timedelta(days=1),
        )
        await EcoPostManageService.extend(
            platform_db=platform_db(post), post_id=101, owner=OWNER, days=7, now=NOW
        )
        assert post.valid_until == NOW + timedelta(days=8)

    @pytest.mark.asyncio
    async def test_invalid_days_are_rejected_before_loading_the_post(self):
        db = platform_db(make_post())
        with pytest.raises(BizException) as e:
            await EcoPostManageService.extend(
                platform_db=db, post_id=101, owner=OWNER, days=9, now=NOW
            )
        assert "展示天数" in e.value.message

    @pytest.mark.asyncio
    async def test_delisted_post_is_pointed_at_relist(self):
        post = delisted_post()
        with pytest.raises(BizException) as e:
            await EcoPostManageService.extend(
                platform_db=platform_db(post), post_id=101, owner=OWNER, days=7, now=NOW
            )
        assert "重新上架" in e.value.message

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status", [PostStatus.AUDITING, PostStatus.LOCKED, PostStatus.FINISHED]
    )
    async def test_only_listed_posts_can_be_extended(self, status):
        post = make_post(status=status)
        with pytest.raises(BizException) as e:
            await EcoPostManageService.extend(
                platform_db=platform_db(post), post_id=101, owner=OWNER, days=7, now=NOW
            )
        assert "不能延长展示" in e.value.message

    @pytest.mark.asyncio
    async def test_status_is_not_changed(self):
        post = make_post()
        await EcoPostManageService.extend(
            platform_db=platform_db(post), post_id=101, owner=OWNER, days=3, now=NOW
        )
        assert post.status == PostStatus.LISTED
        assert post.audit_status == AuditStatus.APPROVED
