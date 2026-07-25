"""服务平台 · 挂牌下架时的意向收口测试

发布方主动停止展示、平台强制下架、到期自动下架、源单失效下架——四条路径共用
这一份逻辑。守两条底线：

1. **待响应与洽谈中的意向必须失效**：挂牌不在了还挂着「待响应」，
   就是让同行白等，且没有任何解释。
2. **已选定的意向不能动**：背后有成交单在跑，作废意向会让成交单指向一条
   无效意向，履约、评价、纠纷追溯全部失去来源。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §3.6
对应代码：backend/app/modules/console/services/ecosystem/intent_lifecycle.py
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

import pytest

from app.modules.console.models.ecosystem.constants import (
    IntentInvalidReason,
    IntentStatus,
    PostType,
)
from app.modules.console.models.ecosystem.intent import SysEcoIntent
from app.modules.console.services.ecosystem.intent_lifecycle import (
    INVALIDATABLE,
    invalidate_active_intents,
    recount_active_intents,
)

NOW = datetime(2026, 7, 25, 10, 0, 0)
TENANT = "T001"


class FakeResult:
    def __init__(self, rows=(), scalar=None):
        self._rows = list(rows)
        self._scalar = scalar

    def scalars(self):
        return self

    def all(self):
        return list(self._rows)

    def scalar(self):
        return self._scalar


class FakePost:
    def __init__(self, intent_count: int = 0):
        self.id = 1
        self.post_no = "HY202607250001"
        self.intent_count = intent_count


class FakeDb:
    """按查询形态分发：取意向返回行，聚合查询返回计数"""

    def __init__(self, intents: Optional[List[SysEcoIntent]] = None, count: int = 0):
        self.intents = list(intents or [])
        self.count = count
        self.flush_count = 0
        self.queries = 0

    async def execute(self, stmt):
        self.queries += 1
        try:
            has_entity = any(
                d.get("entity") is not None for d in stmt.column_descriptions
            )
        except Exception:  # pragma: no cover
            has_entity = False
        if has_entity:
            return FakeResult(self.intents)
        return FakeResult(scalar=self.count)

    async def flush(self):
        self.flush_count += 1


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


class TestInvalidatableStatuses:
    def test_only_pending_and_talking(self):
        assert INVALIDATABLE == (IntentStatus.PENDING, IntentStatus.TALKING)

    def test_selected_is_not_invalidatable(self):
        """这一条挂了，成交单会指向一条无效意向"""
        assert IntentStatus.SELECTED not in INVALIDATABLE


class TestInvalidate:
    @pytest.mark.asyncio
    async def test_marks_rows_invalid_with_reason(self):
        rows = [
            make_intent(1, IntentStatus.PENDING),
            make_intent(2, IntentStatus.TALKING, tenant="T600"),
        ]
        db = FakeDb(intents=rows)
        post = FakePost(intent_count=2)

        result = await invalidate_active_intents(db, post=post, now=NOW)

        assert all(r.status == IntentStatus.INVALID for r in rows)
        assert all(
            r.invalid_reason == IntentInvalidReason.POST_DELISTED for r in rows
        )
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_returns_initiator_for_notification(self):
        """上层要拿这份数据给同行发「这条信息已撤下」的通知"""
        rows = [make_intent(1, IntentStatus.PENDING, tenant="T600")]
        db = FakeDb(intents=rows)

        result = await invalidate_active_intents(db, post=FakePost(), now=NOW)

        assert result[0].intent_id == 1
        assert result[0].intent_no == "YX202607250001"
        assert result[0].initiator_tenant_code == "T600"

    @pytest.mark.asyncio
    async def test_reason_is_caller_supplied(self):
        """同一段代码服务下架、过期、被他人成交三种场景，原因不能写死"""
        rows = [make_intent(1, IntentStatus.PENDING)]
        db = FakeDb(intents=rows)

        await invalidate_active_intents(
            db, post=FakePost(), reason=IntentInvalidReason.POST_EXPIRED, now=NOW
        )

        assert rows[0].invalid_reason == IntentInvalidReason.POST_EXPIRED

    @pytest.mark.asyncio
    async def test_intent_count_is_recomputed_not_decremented(self):
        """冗余计数本来就可能漂移，每次下架正好是一个免费的纠偏点"""
        db = FakeDb(intents=[make_intent(1, IntentStatus.PENDING)], count=1)
        post = FakePost(intent_count=99)

        await invalidate_active_intents(db, post=post, now=NOW)

        assert post.intent_count == 1

    @pytest.mark.asyncio
    async def test_no_active_intent_is_a_no_op(self):
        db = FakeDb(intents=[], count=0)
        post = FakePost(intent_count=3)

        result = await invalidate_active_intents(db, post=post, now=NOW)

        assert result == []
        # 计数照样纠偏
        assert post.intent_count == 0

    @pytest.mark.asyncio
    async def test_flushes_before_recount(self):
        """不 flush 就重算，数出来的还是改动前的旧值"""
        db = FakeDb(intents=[make_intent(1, IntentStatus.PENDING)], count=0)

        await invalidate_active_intents(db, post=FakePost(), now=NOW)

        assert db.flush_count >= 1


class TestRecount:
    @pytest.mark.asyncio
    async def test_returns_int(self):
        db = FakeDb(count=7)
        assert await recount_active_intents(db, FakePost()) == 7

    @pytest.mark.asyncio
    async def test_null_count_degrades_to_zero(self):
        db = FakeDb(count=None)
        assert await recount_active_intents(db, FakePost()) == 0
