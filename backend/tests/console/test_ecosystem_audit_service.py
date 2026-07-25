"""服务平台 · 运营审核动作测试

本模块守五条底线：

1. **只有待审队列里的挂牌能被裁决**：``status`` 与 ``audit_status`` 都要判，
   否则已被强制下架的挂牌会被「通过」重新推回大厅。
2. **驳回不动洽谈，强制下架才动**：驳回是「改改再来」，挂牌还在租户手里；
   强制下架是处置，待响应与洽谈中的意向必须收口，已选定的不能动。
3. **批量通过逐条独立**：一条失败不牵连其余，且失败原因要说清是哪一条。
4. **抽检结论必须落库**：即使挂牌撤不下来（有成交在跑），结论与白名单处置
   一样都不能少，否则免审就成了一条无人把守的通道。
5. **审核通过不能上架即过期**：排了一夜的挂牌有效期已过，必须平移。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2
          doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §4.1 §5
对应代码：backend/app/modules/console/services/ecosystem/audit_service.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

import pytest

from app.common.exceptions import BizException
from app.modules.console.models.ecosystem.constants import (
    MAX_BATCH_APPROVE,
    MAX_VALID_DAYS,
    MAX_VALID_DAYS_LONG_TERM,
    AuditStatus,
    CooperationType,
    DelistReason,
    IntentInvalidReason,
    IntentStatus,
    OperatorType,
    PostAuditAction,
    PostRejectReason,
    PostStatus,
    PostType,
    PriceType,
)
from app.modules.console.models.ecosystem.intent import SysEcoIntent
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.post_audit import SysEcoPostAudit
from app.modules.console.models.ecosystem.tenant_credit import SysEcoTenantCredit
from app.modules.console.services.ecosystem.audit_query_service import OpsContext
from app.modules.console.services.ecosystem.audit_service import (
    REJECT_TEMPLATES,
    EcoAuditService,
)

NOW = datetime(2026, 7, 25, 10, 0, 0)
TENANT = "T001"
OPS = OpsContext(user_id=90, user_name="运营小李")


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
            self.db.rollbacks += 1
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

    def one(self):
        return self._rows[0] if self._rows else (0,)

    def scalar(self):
        return self._scalar


def _entity_of(stmt):
    try:
        for desc in stmt.column_descriptions:
            entity = desc.get("entity")
            if entity is not None:
                return entity
    except Exception:  # pragma: no cover
        return None
    return None


def _is_whole_entity(stmt) -> bool:
    """整实体 select 与列 select 要分开：后者返回元组行"""
    try:
        descs = stmt.column_descriptions
        return len(descs) == 1 and descs[0].get("expr") is descs[0].get("entity")
    except Exception:  # pragma: no cover
        return False


def _param_id(stmt) -> Optional[int]:
    try:
        return stmt.compile().params.get("id_1")
    except Exception:  # pragma: no cover
        return None


class FakeDb:
    """按实体分发的 Session 替身"""

    def __init__(
        self,
        rows: Optional[Dict[type, List]] = None,
        posts: Optional[List[SysEcoPost]] = None,
        count: int = 0,
    ):
        self.rows: Dict[type, List] = dict(rows or {})
        if posts:
            self.rows[SysEcoPost] = list(posts)
        self.count = count
        self.added: List = []
        self.flush_count = 0
        self.savepoints = 0
        self.rollbacks = 0
        self._next_id = 7000

    async def execute(self, stmt):
        entity = _entity_of(stmt)
        if entity is None:
            return FakeResult(scalar=self.count)
        pool = self.rows.get(entity, [])
        if entity is SysEcoPost and not _is_whole_entity(stmt):
            # _load_post_nos 取的是 (id, post_no) 元组
            return FakeResult([(p.id, p.post_no) for p in pool])
        if entity is SysEcoPost:
            wanted = _param_id(stmt)
            if wanted is not None:
                pool = [p for p in pool if int(p.id) == int(wanted)]
        return FakeResult(pool)

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

    def trails(self) -> List[SysEcoPostAudit]:
        return self.of_type(SysEcoPostAudit)

    def one_trail(self) -> SysEcoPostAudit:
        rows = self.trails()
        assert len(rows) == 1, f"期望恰好 1 条流水，实际 {len(rows)}"
        return rows[0]


class FakeTenantSession:
    """租户库 Session 替身，只用于验证角标回写被调用过"""

    def __init__(self, refs=()):
        self.refs = list(refs)
        self.flush_count = 0

    async def execute(self, stmt):
        return FakeResult(self.refs)

    async def flush(self):
        self.flush_count += 1

    def begin_nested(self):
        return FakeNested(self)


@pytest.fixture
def no_mirror(monkeypatch):
    """默认屏蔽跨库回写：本模块验的是平台库的审核结论，不是同步机制

    返回一个记录列表，需要断言「有没有回写」的用例可以直接看它。
    """
    calls: List[tuple] = []

    async def fake_mirror(post, status, now):
        calls.append((post.post_no, int(status)))
        return True

    monkeypatch.setattr(EcoAuditService, "_mirror", staticmethod(fake_mirror))
    return calls


@pytest.fixture
def no_whitelist(monkeypatch):
    """默认屏蔽白名单联动，单独的用例再放开"""
    calls: List[tuple] = []

    async def fake_revoke(db, post, *, reason, now):
        calls.append((post.owner_tenant_code, reason))
        return True

    monkeypatch.setattr(
        EcoAuditService, "_revoke_whitelist", staticmethod(fake_revoke)
    )
    return calls


# ---------------------------------------------------------------------------
# 数据构造
# ---------------------------------------------------------------------------


def make_post(post_id: int = 1, **overrides) -> SysEcoPost:
    fields = dict(
        id=post_id,
        post_no=f"HY2026072500{post_id:02d}",
        post_type=PostType.CARGO,
        owner_tenant_code=TENANT,
        owner_tenant_name="杭州速达物流有限公司",
        owner_masked_name="杭州**物流",
        publisher_user_id=1,
        publisher_name="张三",
        title="杭州→成都 20台 比亚迪",
        status=PostStatus.AUDITING,
        audit_status=AuditStatus.PENDING,
        submitted_at=NOW - timedelta(hours=1),
        valid_from=NOW - timedelta(hours=1),
        valid_until=NOW + timedelta(days=7),
        from_province="浙江省",
        from_city="杭州市",
        window_start=NOW + timedelta(days=1),
        total_quantity=20,
        quantity_unit="台",
        remaining_quantity=20,
        price_type=PriceType.PER_UNIT,
        price_amount=Decimal("800.00"),
        cooperation_type=CooperationType.ONCE,
        contact_name="张三",
        contact_phone="13800000000",
        intent_count=0,
        is_deleted=0,
        listed_at=None,
        audit_reason=None,
        delist_reason=None,
        delist_remark=None,
    )
    fields.update(overrides)
    return SysEcoPost(**fields)


def make_intent(intent_id: int, status: int, tenant: str = "T500") -> SysEcoIntent:
    return SysEcoIntent(
        id=intent_id,
        intent_no=f"YX2026072500{intent_id:02d}",
        post_id=1,
        post_type=PostType.CARGO,
        owner_tenant_code=TENANT,
        initiator_tenant_code=tenant,
        initiator_tenant_name="成都某某物流",
        contact_name="李四",
        contact_phone="13900000000",
        status=status,
        is_deleted=0,
    )


# ---------------------------------------------------------------------------
# 通过
# ---------------------------------------------------------------------------


class TestApprove:
    @pytest.mark.asyncio
    async def test_pending_post_goes_live(self, no_mirror):
        post = make_post()
        db = FakeDb(posts=[post])

        result = await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        assert post.status == PostStatus.LISTED
        assert post.audit_status == AuditStatus.APPROVED
        assert post.audit_at == NOW
        assert post.audit_by == OPS.user_id
        assert post.listed_at == NOW
        assert result.changed is True
        assert "货源大厅" in result.message

    @pytest.mark.asyncio
    async def test_stale_reject_reason_is_cleared(self, no_mirror):
        """通过了还挂着上一轮的驳回原因，租户会以为又被驳了"""
        post = make_post(audit_reason="上次说了信息不全")
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        assert post.audit_reason is None

    @pytest.mark.asyncio
    async def test_first_listed_at_is_kept(self, no_mirror):
        """曾经上过架的挂牌重审通过，首次上架时间不该被改写"""
        first = NOW - timedelta(days=3)
        post = make_post(listed_at=first)
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        assert post.listed_at == first

    @pytest.mark.asyncio
    async def test_expired_validity_is_reslotted(self, no_mirror):
        """排了一夜有效期已过：通过后必须平移，否则上架即过期"""
        post = make_post(
            valid_from=NOW - timedelta(days=9), valid_until=NOW - timedelta(days=2)
        )
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        # 保留原来的 7 天跨度，而不是重新给一份，避免变成绕开展示上限的路径
        assert post.valid_from == NOW
        assert post.valid_until == NOW + timedelta(days=7)

    @pytest.mark.asyncio
    async def test_valid_validity_is_untouched(self, no_mirror):
        """没过期就不动：审核不该顺手给挂牌续命"""
        post = make_post()
        original_from, original_until = post.valid_from, post.valid_until
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        assert (post.valid_from, post.valid_until) == (original_from, original_until)

    @pytest.mark.asyncio
    async def test_reslot_respects_max_days(self, no_mirror):
        post = make_post(
            valid_from=NOW - timedelta(days=200), valid_until=NOW - timedelta(days=1)
        )
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        assert post.valid_until == NOW + timedelta(days=MAX_VALID_DAYS)

    @pytest.mark.asyncio
    async def test_reslot_respects_long_term_max(self, no_mirror):
        post = make_post(
            cooperation_type=CooperationType.LONG_TERM,
            valid_from=NOW - timedelta(days=200),
            valid_until=NOW - timedelta(days=1),
        )
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        assert post.valid_until == NOW + timedelta(days=MAX_VALID_DAYS_LONG_TERM)

    @pytest.mark.asyncio
    async def test_writes_ops_trail(self, no_mirror):
        post = make_post()
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        trail = db.one_trail()
        assert trail.action == PostAuditAction.APPROVE
        assert trail.from_status == PostStatus.AUDITING
        assert trail.to_status == PostStatus.LISTED
        assert trail.operator_type == OperatorType.PLATFORM_OPS
        assert trail.operator_id == OPS.user_id
        # 运营不属于任何租户，按租户统计处置次数要 JOIN 挂牌表
        assert trail.operator_tenant_code is None

    @pytest.mark.asyncio
    async def test_remark_lands_in_trail(self, no_mirror):
        post = make_post()
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, operator=OPS, remark="有源单且一致", now=NOW)

        assert db.one_trail().reason == "有源单且一致"

    @pytest.mark.asyncio
    async def test_mirrors_status_to_tenant_db(self):
        """通过后要回写租户库角标，否则租户在任务单列表上还看到「审核中」"""
        calls: List[tuple] = []

        async def fake_mirror(post, status, now):
            calls.append((post.post_no, int(status)))
            return True

        import app.modules.console.services.ecosystem.audit_service as mod

        original = mod.EcoAuditService._mirror
        mod.EcoAuditService._mirror = staticmethod(fake_mirror)
        try:
            post = make_post()
            db = FakeDb(posts=[post])
            result = await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)
        finally:
            mod.EcoAuditService._mirror = original

        assert calls == [(post.post_no, PostStatus.LISTED)]
        assert result.ref_synced is True

    @pytest.mark.asyncio
    async def test_already_listed_is_idempotent(self, no_mirror):
        post = make_post(status=PostStatus.LISTED, audit_status=AuditStatus.APPROVED)
        db = FakeDb(posts=[post])

        result = await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        assert result.changed is False
        assert db.trails() == []

    @pytest.mark.asyncio
    async def test_delisted_post_cannot_be_approved(self, no_mirror):
        """否则审核员点一下通过，就把已处置的挂牌重新推回大厅"""
        post = make_post(
            status=PostStatus.DELISTED, audit_status=AuditStatus.PENDING
        )
        db = FakeDb(posts=[post])

        with pytest.raises(BizException, match="不在待审核队列"):
            await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

    @pytest.mark.asyncio
    async def test_draft_cannot_be_approved(self, no_mirror):
        post = make_post(
            status=PostStatus.DRAFT, audit_status=AuditStatus.NOT_SUBMITTED
        )
        db = FakeDb(posts=[post])

        with pytest.raises(BizException):
            await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

    @pytest.mark.asyncio
    async def test_audit_status_mismatch_is_rejected(self, no_mirror):
        """状态待审核但审核状态已是通过：说明另一个审核员刚处理过"""
        post = make_post(audit_status=AuditStatus.APPROVED)
        db = FakeDb(posts=[post])

        with pytest.raises(BizException):
            await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

    @pytest.mark.asyncio
    async def test_missing_post_says_it_may_be_deleted(self, no_mirror):
        db = FakeDb(posts=[])

        with pytest.raises(BizException, match="没找到这条挂牌"):
            await EcoAuditService.approve(db, 999, operator=OPS, now=NOW)

    @pytest.mark.asyncio
    async def test_works_without_operator(self, no_mirror):
        """系统触发的通过（如自动化规则）不带操作人，不能因此报错"""
        post = make_post()
        db = FakeDb(posts=[post])

        await EcoAuditService.approve(db, 1, now=NOW)

        assert post.audit_by is None


# ---------------------------------------------------------------------------
# 驳回
# ---------------------------------------------------------------------------


class TestReject:
    @pytest.mark.asyncio
    async def test_reject_with_custom_reason(self, no_mirror):
        post = make_post()
        db = FakeDb(posts=[post])

        result = await EcoAuditService.reject(
            db,
            1,
            reason_code=PostRejectReason.CONTACT_VIOLATION,
            reason="「其他要求」里写了手机号，删掉后重新提交",
            operator=OPS,
            now=NOW,
        )

        assert post.status == PostStatus.REJECTED
        assert post.audit_status == AuditStatus.REJECTED
        assert post.audit_reason == "「其他要求」里写了手机号，删掉后重新提交"
        assert post.audit_at == NOW
        assert result.changed is True

    @pytest.mark.asyncio
    async def test_blank_reason_falls_back_to_template(self, no_mirror):
        """没写补充说明就套模板，而不是把「信息不真实」四个字甩给租户"""
        post = make_post()
        db = FakeDb(posts=[post])

        await EcoAuditService.reject(
            db, 1, reason_code=PostRejectReason.UNTRUE, operator=OPS, now=NOW
        )

        assert post.audit_reason == REJECT_TEMPLATES[PostRejectReason.UNTRUE]

    @pytest.mark.asyncio
    async def test_whitespace_reason_is_treated_as_blank(self, no_mirror):
        post = make_post()
        db = FakeDb(posts=[post])

        await EcoAuditService.reject(
            db,
            1,
            reason_code=PostRejectReason.INCOMPLETE,
            reason="   ",
            operator=OPS,
            now=NOW,
        )

        assert post.audit_reason == REJECT_TEMPLATES[PostRejectReason.INCOMPLETE]

    @pytest.mark.asyncio
    async def test_other_reason_requires_explanation(self, no_mirror):
        """「其他」没有模板，必须自己写，否则租户拿到一句没有下一步的话"""
        post = make_post()
        db = FakeDb(posts=[post])

        with pytest.raises(BizException, match="请补充一句说明"):
            await EcoAuditService.reject(
                db, 1, reason_code=PostRejectReason.OTHER, operator=OPS, now=NOW
            )

    @pytest.mark.asyncio
    async def test_other_reason_with_text_is_accepted(self, no_mirror):
        post = make_post()
        db = FakeDb(posts=[post])

        await EcoAuditService.reject(
            db,
            1,
            reason_code=PostRejectReason.OTHER,
            reason="这条线路目前暂停开放",
            operator=OPS,
            now=NOW,
        )

        assert post.audit_reason == "这条线路目前暂停开放"

    @pytest.mark.asyncio
    async def test_unknown_reason_code_is_rejected(self, no_mirror):
        """原因编码是审核质量统计的唯一依据，不能收自由取值"""
        post = make_post()
        db = FakeDb(posts=[post])

        with pytest.raises(BizException, match="请选择一个驳回原因"):
            await EcoAuditService.reject(
                db, 1, reason_code=77, reason="随便", operator=OPS, now=NOW
            )

    @pytest.mark.asyncio
    async def test_reason_code_lands_in_trail(self, no_mirror):
        post = make_post()
        db = FakeDb(posts=[post])

        await EcoAuditService.reject(
            db, 1, reason_code=PostRejectReason.PRICE_ABNORMAL, operator=OPS, now=NOW
        )

        trail = db.one_trail()
        assert trail.action == PostAuditAction.REJECT
        assert trail.reason_code == PostRejectReason.PRICE_ABNORMAL
        assert trail.to_status == PostStatus.REJECTED

    @pytest.mark.asyncio
    async def test_reject_does_not_touch_intents(self, no_mirror):
        """驳回是「改改再来」，不该把正在洽谈的同行单方面踢掉"""
        post = make_post()
        talking = make_intent(1, IntentStatus.TALKING)
        db = FakeDb(posts=[post], rows={SysEcoIntent: [talking]})

        await EcoAuditService.reject(
            db, 1, reason_code=PostRejectReason.INCOMPLETE, operator=OPS, now=NOW
        )

        assert talking.status == IntentStatus.TALKING

    @pytest.mark.asyncio
    async def test_long_reason_is_truncated_for_storage(self, no_mirror):
        post = make_post()
        db = FakeDb(posts=[post])

        await EcoAuditService.reject(
            db,
            1,
            reason_code=PostRejectReason.OTHER,
            reason="很长的说明" * 100,
            operator=OPS,
            now=NOW,
        )

        assert len(post.audit_reason) <= 255

    @pytest.mark.asyncio
    async def test_already_rejected_is_idempotent(self, no_mirror):
        post = make_post(
            status=PostStatus.REJECTED, audit_status=AuditStatus.REJECTED
        )
        db = FakeDb(posts=[post])

        result = await EcoAuditService.reject(
            db, 1, reason_code=PostRejectReason.INCOMPLETE, operator=OPS, now=NOW
        )

        assert result.changed is False
        assert db.trails() == []

    @pytest.mark.asyncio
    async def test_listed_post_cannot_be_rejected(self, no_mirror):
        post = make_post(status=PostStatus.LISTED, audit_status=AuditStatus.APPROVED)
        db = FakeDb(posts=[post])

        with pytest.raises(BizException, match="不在待审核队列"):
            await EcoAuditService.reject(
                db, 1, reason_code=PostRejectReason.INCOMPLETE, operator=OPS, now=NOW
            )


# ---------------------------------------------------------------------------
# 批量通过
# ---------------------------------------------------------------------------


class TestBatchApprove:
    @pytest.mark.asyncio
    async def test_all_pass(self, no_mirror):
        posts = [make_post(i) for i in (1, 2, 3)]
        db = FakeDb(posts=posts)

        result = await EcoAuditService.batch_approve(
            db, [1, 2, 3], operator=OPS, now=NOW
        )

        assert result.success_count == 3
        assert result.failed == []
        assert all(p.status == PostStatus.LISTED for p in posts)
        assert "已通过 3 条" in result.message

    @pytest.mark.asyncio
    async def test_one_failure_does_not_block_others(self, no_mirror):
        """08 §5：逐条独立事务，部分成功也要落地"""
        ok1, bad, ok2 = make_post(1), make_post(2), make_post(3)
        bad.status = PostStatus.DELISTED
        db = FakeDb(posts=[ok1, bad, ok2])

        result = await EcoAuditService.batch_approve(
            db, [1, 2, 3], operator=OPS, now=NOW
        )

        assert result.success_count == 2
        assert ok1.status == PostStatus.LISTED
        assert ok2.status == PostStatus.LISTED
        assert len(result.failed) == 1
        assert result.failed[0].post_id == 2

    @pytest.mark.asyncio
    async def test_failed_item_carries_post_no(self, no_mirror):
        """运营认的是挂牌编号，只给主键 ID 等于没告诉他是哪一条"""
        bad = make_post(2, status=PostStatus.DELISTED)
        db = FakeDb(posts=[bad])

        result = await EcoAuditService.batch_approve(db, [2], operator=OPS, now=NOW)

        assert result.failed[0].post_no == bad.post_no
        assert "不在待审核队列" in result.failed[0].message

    @pytest.mark.asyncio
    async def test_each_item_gets_its_own_savepoint(self, no_mirror):
        posts = [make_post(i) for i in (1, 2)]
        db = FakeDb(posts=posts)

        await EcoAuditService.batch_approve(db, [1, 2], operator=OPS, now=NOW)

        assert db.savepoints == 2

    @pytest.mark.asyncio
    async def test_failed_item_rolls_back_only_itself(self, no_mirror):
        bad = make_post(1, status=PostStatus.DELISTED)
        good = make_post(2)
        db = FakeDb(posts=[bad, good])

        await EcoAuditService.batch_approve(db, [1, 2], operator=OPS, now=NOW)

        assert db.rollbacks == 1
        assert good.status == PostStatus.LISTED

    @pytest.mark.asyncio
    async def test_duplicate_ids_are_processed_once(self, no_mirror):
        post = make_post(1)
        db = FakeDb(posts=[post])

        result = await EcoAuditService.batch_approve(
            db, [1, 1, 1], operator=OPS, now=NOW
        )

        assert result.success_count == 1

    @pytest.mark.asyncio
    async def test_empty_selection_is_rejected(self, no_mirror):
        db = FakeDb(posts=[])

        with pytest.raises(BizException, match="请先勾选"):
            await EcoAuditService.batch_approve(db, [], operator=OPS, now=NOW)

    @pytest.mark.asyncio
    async def test_oversized_batch_is_rejected(self, no_mirror):
        """不设上限会让长事务锁住待审队列，且失败难定位"""
        db = FakeDb(posts=[])

        with pytest.raises(BizException, match=str(MAX_BATCH_APPROVE)):
            await EcoAuditService.batch_approve(
                db, list(range(1, MAX_BATCH_APPROVE + 2)), operator=OPS, now=NOW
            )

    @pytest.mark.asyncio
    async def test_all_failed_message_is_honest(self, no_mirror):
        db = FakeDb(posts=[make_post(1, status=PostStatus.DELISTED)])

        result = await EcoAuditService.batch_approve(db, [1], operator=OPS, now=NOW)

        assert result.success_count == 0
        assert "都没能通过" in result.message

    @pytest.mark.asyncio
    async def test_partial_message_reports_both_sides(self, no_mirror):
        db = FakeDb(posts=[make_post(1), make_post(2, status=PostStatus.DELISTED)])

        result = await EcoAuditService.batch_approve(db, [1, 2], operator=OPS, now=NOW)

        assert "已通过 1 条" in result.message
        assert "1 条没能处理" in result.message


# ---------------------------------------------------------------------------
# 强制下架
# ---------------------------------------------------------------------------


class TestForceDelist:
    @pytest.mark.asyncio
    async def test_listed_post_is_pulled(self, no_mirror, no_whitelist):
        post = make_post(status=PostStatus.LISTED, audit_status=AuditStatus.APPROVED)
        db = FakeDb(posts=[post])

        result = await EcoAuditService.force_delist(
            db, 1, reason="信息核实不实", operator=OPS, now=NOW
        )

        assert post.status == PostStatus.DELISTED
        assert post.delist_reason == DelistReason.FORCED
        assert post.delist_remark == "信息核实不实"
        assert result.changed is True

    @pytest.mark.asyncio
    async def test_audit_status_becomes_rejected(self, no_mirror, no_whitelist):
        """留在「通过」上，租户端看不到任何审核结论，抽检队列也清不掉"""
        post = make_post(
            status=PostStatus.LISTED, audit_status=AuditStatus.WHITELIST_PASS
        )
        db = FakeDb(posts=[post])

        await EcoAuditService.force_delist(
            db, 1, reason="联系方式违规", operator=OPS, now=NOW
        )

        assert post.audit_status == AuditStatus.REJECTED
        assert post.audit_reason == "联系方式违规"

    @pytest.mark.asyncio
    async def test_pending_and_talking_intents_are_invalidated(
        self, no_mirror, no_whitelist
    ):
        post = make_post(status=PostStatus.LISTED)
        pending = make_intent(1, IntentStatus.PENDING)
        talking = make_intent(2, IntentStatus.TALKING, tenant="T600")
        db = FakeDb(posts=[post], rows={SysEcoIntent: [pending, talking]})

        result = await EcoAuditService.force_delist(
            db, 1, reason="信息虚假", operator=OPS, now=NOW
        )

        assert pending.status == IntentStatus.INVALID
        assert talking.status == IntentStatus.INVALID
        assert pending.invalid_reason == IntentInvalidReason.POST_DELISTED
        assert len(result.invalidated_intents) == 2
        assert "2 家正在洽谈" in result.message

    @pytest.mark.asyncio
    async def test_selected_intent_is_left_alone(self, no_mirror, no_whitelist):
        """已选定的意向背后有成交单，作废它会让成交单失去来源"""
        post = make_post(status=PostStatus.LISTED)
        selected = make_intent(3, IntentStatus.SELECTED)
        db = FakeDb(posts=[post], rows={SysEcoIntent: []})

        await EcoAuditService.force_delist(
            db, 1, reason="信息虚假", operator=OPS, now=NOW
        )

        assert selected.status == IntentStatus.SELECTED

    @pytest.mark.asyncio
    async def test_intent_count_is_recomputed(self, no_mirror, no_whitelist):
        post = make_post(status=PostStatus.LISTED, intent_count=9)
        db = FakeDb(posts=[post], rows={SysEcoIntent: []}, count=0)

        await EcoAuditService.force_delist(
            db, 1, reason="信息虚假", operator=OPS, now=NOW
        )

        assert post.intent_count == 0

    @pytest.mark.asyncio
    async def test_whitelist_is_revoked_by_default(self, no_mirror, no_whitelist):
        """强制下架是已确认的违规，与「这家的内容不用看也放心」不能同时成立"""
        post = make_post(status=PostStatus.LISTED)
        db = FakeDb(posts=[post])

        result = await EcoAuditService.force_delist(
            db, 1, reason="信息虚假", operator=OPS, now=NOW
        )

        assert no_whitelist == [(TENANT, "信息虚假")]
        assert result.whitelist_revoked is True

    @pytest.mark.asyncio
    async def test_whitelist_can_be_kept_by_caller(self, no_mirror, no_whitelist):
        """举报处置等已经单独处理过白名单的调用方传 False，避免重复处置"""
        post = make_post(status=PostStatus.LISTED)
        db = FakeDb(posts=[post])

        result = await EcoAuditService.force_delist(
            db,
            1,
            reason="举报成立",
            operator=OPS,
            revoke_whitelist=False,
            now=NOW,
        )

        assert no_whitelist == []
        assert result.whitelist_revoked is False

    @pytest.mark.asyncio
    async def test_whitelist_failure_does_not_roll_back_delist(self, monkeypatch):
        """下架已经生效了，为白名单没摘掉把它回滚等于让违规内容继续挂着"""

        async def boom(db, tenant_code, *, reason, now=None):
            raise RuntimeError("credit table locked")

        monkeypatch.setattr(EcoAuditService, "_mirror", staticmethod(_ok_mirror))
        import app.modules.console.services.ecosystem.audit_service as mod

        monkeypatch.setattr(mod.EcoWhitelistService, "revoke", staticmethod(boom))

        post = make_post(status=PostStatus.LISTED)
        db = FakeDb(posts=[post])
        result = await EcoAuditService.force_delist(
            db, 1, reason="信息虚假", operator=OPS, now=NOW
        )

        assert post.status == PostStatus.DELISTED
        assert result.whitelist_revoked is False

    @pytest.mark.asyncio
    async def test_blank_reason_is_rejected(self, no_mirror, no_whitelist):
        """强制下架的原因会原样展示给租户，不能是空的"""
        db = FakeDb(posts=[make_post(status=PostStatus.LISTED)])

        with pytest.raises(BizException, match="请填写强制下架的原因"):
            await EcoAuditService.force_delist(
                db, 1, reason="  ", operator=OPS, now=NOW
            )

    @pytest.mark.asyncio
    async def test_auditing_post_can_be_force_delisted(self, no_mirror, no_whitelist):
        """还在队列里就发现是恶意内容，不用先通过再下架"""
        post = make_post(status=PostStatus.AUDITING)
        db = FakeDb(posts=[post])

        await EcoAuditService.force_delist(
            db, 1, reason="恶意刷屏", operator=OPS, now=NOW
        )

        assert post.status == PostStatus.DELISTED

    @pytest.mark.asyncio
    async def test_locked_post_cannot_be_force_delisted(self, no_mirror, no_whitelist):
        """会留下一张找不到来源的成交单，运营该走成交单终止流程"""
        post = make_post(status=PostStatus.LOCKED, audit_status=AuditStatus.APPROVED)
        db = FakeDb(posts=[post])

        with pytest.raises(BizException, match="成交单"):
            await EcoAuditService.force_delist(
                db, 1, reason="信息虚假", operator=OPS, now=NOW
            )

    @pytest.mark.asyncio
    async def test_fulfilling_post_cannot_be_force_delisted(
        self, no_mirror, no_whitelist
    ):
        post = make_post(
            status=PostStatus.FULFILLING, audit_status=AuditStatus.APPROVED
        )
        db = FakeDb(posts=[post])

        with pytest.raises(BizException):
            await EcoAuditService.force_delist(
                db, 1, reason="信息虚假", operator=OPS, now=NOW
            )

    @pytest.mark.asyncio
    async def test_already_delisted_is_idempotent(self, no_mirror, no_whitelist):
        post = make_post(status=PostStatus.DELISTED)
        db = FakeDb(posts=[post])

        result = await EcoAuditService.force_delist(
            db, 1, reason="信息虚假", operator=OPS, now=NOW
        )

        assert result.changed is False
        assert db.trails() == []

    @pytest.mark.asyncio
    async def test_trail_records_forced_action(self, no_mirror, no_whitelist):
        post = make_post(status=PostStatus.LISTED)
        db = FakeDb(posts=[post])

        await EcoAuditService.force_delist(
            db,
            1,
            reason="信息虚假",
            reason_code=PostRejectReason.UNTRUE,
            operator=OPS,
            now=NOW,
        )

        trail = db.one_trail()
        assert trail.action == PostAuditAction.DELIST_FORCED
        assert trail.reason_code == PostRejectReason.UNTRUE
        assert trail.to_status == PostStatus.DELISTED


# ---------------------------------------------------------------------------
# 抽检
# ---------------------------------------------------------------------------


class TestSpotCheck:
    @pytest.mark.asyncio
    async def test_pass_only_changes_audit_status(self, no_mirror):
        """挂牌本来就在大厅里，抽检通过是「确认可以继续挂」，不是重新上架"""
        post = make_post(
            status=PostStatus.LISTED,
            audit_status=AuditStatus.WHITELIST_PASS,
            listed_at=NOW - timedelta(hours=5),
        )
        db = FakeDb(posts=[post])

        await EcoAuditService.spot_check_pass(db, 1, operator=OPS, now=NOW)

        assert post.status == PostStatus.LISTED
        assert post.audit_status == AuditStatus.SPOT_CHECKED
        assert post.audit_at == NOW

    @pytest.mark.asyncio
    async def test_pass_writes_trail(self, no_mirror):
        post = make_post(
            status=PostStatus.LISTED, audit_status=AuditStatus.WHITELIST_PASS
        )
        db = FakeDb(posts=[post])

        await EcoAuditService.spot_check_pass(db, 1, operator=OPS, now=NOW)

        trail = db.one_trail()
        assert trail.action == PostAuditAction.SPOT_CHECK_PASS
        assert trail.from_status == trail.to_status == PostStatus.LISTED

    @pytest.mark.asyncio
    async def test_manual_approved_post_is_not_spot_checkable(self, no_mirror):
        """人工审核通过的挂牌已经被人看过了，不该再占抽检队列"""
        post = make_post(status=PostStatus.LISTED, audit_status=AuditStatus.APPROVED)
        db = FakeDb(posts=[post])

        with pytest.raises(BizException, match="不用抽检"):
            await EcoAuditService.spot_check_pass(db, 1, operator=OPS, now=NOW)

    @pytest.mark.asyncio
    async def test_already_spot_checked_says_so(self, no_mirror):
        post = make_post(
            status=PostStatus.LISTED, audit_status=AuditStatus.SPOT_CHECKED
        )
        db = FakeDb(posts=[post])

        with pytest.raises(BizException, match="已经抽检过"):
            await EcoAuditService.spot_check_pass(db, 1, operator=OPS, now=NOW)

    @pytest.mark.asyncio
    async def test_fail_delists_and_revokes_whitelist(self, no_mirror, no_whitelist):
        post = make_post(
            status=PostStatus.LISTED, audit_status=AuditStatus.WHITELIST_PASS
        )
        db = FakeDb(posts=[post])

        result = await EcoAuditService.spot_check_fail(
            db, 1, reason="线路和实际不符", operator=OPS, now=NOW
        )

        assert post.status == PostStatus.DELISTED
        assert post.delist_reason == DelistReason.FORCED
        assert result.whitelist_revoked is True
        assert "移出免审白名单" in result.message

    @pytest.mark.asyncio
    async def test_fail_trail_uses_spot_check_action(self, no_mirror, no_whitelist):
        """流水要能区分「抽检不通过」与普通强制下架，否则统计抽检问题率无从下手"""
        post = make_post(
            status=PostStatus.LISTED, audit_status=AuditStatus.WHITELIST_PASS
        )
        db = FakeDb(posts=[post])

        await EcoAuditService.spot_check_fail(
            db, 1, reason="线路和实际不符", operator=OPS, now=NOW
        )

        assert db.one_trail().action == PostAuditAction.SPOT_CHECK_FAIL

    @pytest.mark.asyncio
    async def test_fail_records_conclusion_even_when_deal_is_running(
        self, no_mirror, no_whitelist
    ):
        """撤不下来也要留痕并摘白名单，否则免审成了无人把守的通道"""
        post = make_post(
            status=PostStatus.FULFILLING, audit_status=AuditStatus.WHITELIST_PASS
        )
        db = FakeDb(posts=[post])

        result = await EcoAuditService.spot_check_fail(
            db, 1, reason="车辆证照过期", operator=OPS, now=NOW
        )

        assert post.status == PostStatus.FULFILLING
        assert post.audit_status == AuditStatus.REJECTED
        assert post.audit_reason == "车辆证照过期"
        assert result.whitelist_revoked is True
        assert db.one_trail().action == PostAuditAction.SPOT_CHECK_FAIL
        assert "成交单" in result.message

    @pytest.mark.asyncio
    async def test_fail_requires_reason(self, no_mirror, no_whitelist):
        db = FakeDb(
            posts=[
                make_post(
                    status=PostStatus.LISTED, audit_status=AuditStatus.WHITELIST_PASS
                )
            ]
        )

        with pytest.raises(BizException, match="请填写抽检不通过的原因"):
            await EcoAuditService.spot_check_fail(
                db, 1, reason="", operator=OPS, now=NOW
            )

    @pytest.mark.asyncio
    async def test_fail_rejects_non_whitelist_post(self, no_mirror, no_whitelist):
        post = make_post(status=PostStatus.LISTED, audit_status=AuditStatus.APPROVED)
        db = FakeDb(posts=[post])

        with pytest.raises(BizException, match="不用抽检"):
            await EcoAuditService.spot_check_fail(
                db, 1, reason="信息不符", operator=OPS, now=NOW
            )


# ---------------------------------------------------------------------------
# 跨库回写
# ---------------------------------------------------------------------------


async def _ok_mirror(post, status, now):
    return True


class TestMirror:
    @pytest.mark.asyncio
    async def test_mirror_uses_owner_tenant_session(self, monkeypatch):
        """运营端没有租户库 Session，按挂牌归属临时开一个"""
        opened: List[str] = []
        session = FakeTenantSession()

        async def fake_get(tenant_code):
            opened.append(tenant_code)
            yield session

        import app.modules.console.services.ecosystem.audit_service as mod

        monkeypatch.setattr(mod.db_manager, "get_tenant_session", fake_get)

        async def fake_mirror_ref(tenant_db, *, post_id, post_no, status, now=None):
            return True

        monkeypatch.setattr(mod, "mirror_post_status", fake_mirror_ref)

        post = make_post(status=PostStatus.LISTED)
        assert await EcoAuditService._mirror(post, PostStatus.LISTED, NOW) is True
        assert opened == [TENANT]

    @pytest.mark.asyncio
    async def test_mirror_failure_is_swallowed(self, monkeypatch):
        """角标短时不准，比「审核失败」但挂牌其实已经上架了要好得多"""

        async def boom(tenant_code):
            raise RuntimeError("tenant db unreachable")
            yield  # pragma: no cover

        import app.modules.console.services.ecosystem.audit_service as mod

        monkeypatch.setattr(mod.db_manager, "get_tenant_session", boom)

        post = make_post(status=PostStatus.LISTED)
        assert await EcoAuditService._mirror(post, PostStatus.LISTED, NOW) is False

    @pytest.mark.asyncio
    async def test_mirror_failure_does_not_block_approve(self, monkeypatch):
        async def boom(tenant_code):
            raise RuntimeError("tenant db unreachable")
            yield  # pragma: no cover

        import app.modules.console.services.ecosystem.audit_service as mod

        monkeypatch.setattr(mod.db_manager, "get_tenant_session", boom)

        post = make_post()
        db = FakeDb(posts=[post])
        result = await EcoAuditService.approve(db, 1, operator=OPS, now=NOW)

        assert post.status == PostStatus.LISTED
        assert result.ref_synced is False

    @pytest.mark.asyncio
    async def test_missing_tenant_code_returns_false(self):
        post = make_post()
        post.owner_tenant_code = ""
        assert await EcoAuditService._mirror(post, PostStatus.LISTED, NOW) is False
