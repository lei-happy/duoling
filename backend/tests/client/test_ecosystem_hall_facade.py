"""服务平台 · 大厅读接口装配层测试

本模块守四条底线：

1. **列表页必须带查看方上下文**：漏了它所有卡片退化到匿名层，已经解锁的联系方式
   又被藏起来，用户会以为系统坏了。
2. **「我发布的」混排后顺序不能乱**：两个大厅的扩展表要分组装载，分组之后必须
   按分页原始顺序还原，否则用户每次翻页看到的排序都不一样。
3. **浏览统计失败不能影响看详情**：统计是给发布方看热度的，为它把一次正常查看
   变成报错不划算。
4. **发布方看自己的挂牌不计浏览量**：自己刷十遍就有十个浏览的数据毫无意义，
   还会让热度反馈变成噪声。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/05.前端交互与UX设计.md §7.3
对应代码：backend/app/modules/client/services/ecosystem/hall_facade.py
"""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from typing import Any, Dict, List

import pytest

from app.common.exceptions import BizException
from app.modules.client.services.ecosystem import hall_facade as facade_mod
from app.modules.client.services.ecosystem.hall_facade import EcoHallFacade
from app.modules.client.services.ecosystem.post_query_service import (
    HallFilter,
    MyPostFilter,
)
from app.modules.client.services.ecosystem.visibility import EcoViewerContext
from app.modules.console.models.ecosystem.constants import PostStatus, PostType

NOW = datetime(2026, 7, 25, 10, 0, 0)
OWNER = "hz001"
VIEWER = "sh002"


class FakeDb:
    """只负责记录执行过的语句；facade 的取数一律通过打桩替换"""

    def __init__(self):
        self.statements: List[Any] = []

    async def execute(self, stmt):
        self.statements.append(stmt)
        raise AssertionError("本用例不应真的落到 DB，请检查打桩")


def make_post(post_id: int, post_type: int = PostType.CARGO, **kwargs):
    defaults = dict(
        id=post_id,
        post_no=f"HY2026072500{post_id:02d}",
        post_type=post_type,
        owner_tenant_code=OWNER,
        status=PostStatus.LISTED,
        view_count=3,
        intent_count=1,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


@pytest.fixture
def stub_pipeline(monkeypatch):
    """把「批量装载 + 查看方上下文 + 序列化」三步替换成可观测的桩

    返回一个 dict，用例可以从里面读到每一步实际被怎么调用的。
    """
    calls: Dict[str, Any] = {"viewer_post_ids": None, "serialized": []}

    async def _load_related(db, posts, post_type):
        calls.setdefault("load_related", []).append(
            (tuple(p.id for p in posts), post_type)
        )
        return {"ext": {}, "dests": {}, "credits": {}}

    async def _build_viewer(db, tenant_code, post_ids, **kwargs):
        calls["viewer_post_ids"] = list(post_ids)
        calls["viewer_tenant_code"] = tenant_code
        return EcoViewerContext(viewer_tenant_code=tenant_code, license_verified=True)

    def _serialize(post, viewer, **kwargs):
        calls["serialized"].append((post.id, kwargs.get("detail")))
        return {"id": post.id, "postNo": post.post_no, "postType": post.post_type}

    monkeypatch.setattr(
        facade_mod.EcoPostQueryService, "load_related", staticmethod(_load_related)
    )
    monkeypatch.setattr(
        facade_mod.EcoViewerContextBuilder,
        "build_for_posts",
        staticmethod(_build_viewer),
    )
    monkeypatch.setattr(
        facade_mod.EcoPostSerializer, "serialize", staticmethod(_serialize)
    )
    return calls


# ---------------------------------------------------------------------------
# 大厅列表
# ---------------------------------------------------------------------------


class TestPageHall:
    @pytest.mark.asyncio
    async def test_pipeline_is_complete(self, monkeypatch, stub_pipeline):
        posts = [make_post(1), make_post(2)]

        async def _page(db, *, post_type, viewer_tenant_code, flt):
            return posts, 17

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "page_hall", staticmethod(_page)
        )

        data = await EcoHallFacade.page_hall(
            FakeDb(),
            post_type=PostType.CARGO,
            viewer_tenant_code=VIEWER,
            flt=HallFilter(page=2, page_size=20),
        )

        assert data["total"] == 17
        assert data["count"] == 17
        assert data["page"] == 2
        assert data["pageSize"] == 20
        assert [r["id"] for r in data["list"]] == [1, 2]
        # 整页一次算出洽谈关系，而不是每条卡片查一遍
        assert stub_pipeline["viewer_post_ids"] == [1, 2]
        assert stub_pipeline["viewer_tenant_code"] == VIEWER
        # 列表是卡片视图，不带联系方式与发布方私有字段
        assert stub_pipeline["serialized"] == [(1, False), (2, False)]

    @pytest.mark.asyncio
    async def test_empty_page_skips_extra_queries(self, monkeypatch, stub_pipeline):
        async def _page(db, *, post_type, viewer_tenant_code, flt):
            return [], 0

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "page_hall", staticmethod(_page)
        )

        data = await EcoHallFacade.page_hall(
            FakeDb(),
            post_type=PostType.CARGO,
            viewer_tenant_code=VIEWER,
            flt=HallFilter(),
        )

        assert data["list"] == []
        assert data["total"] == 0
        assert "load_related" not in stub_pipeline


# ---------------------------------------------------------------------------
# 我发布的
# ---------------------------------------------------------------------------


class TestPageMine:
    @pytest.mark.asyncio
    async def test_mixed_types_keep_paging_order(self, monkeypatch, stub_pipeline):
        """货源与运力交替出现时，分组装载后必须还原成原顺序"""
        posts = [
            make_post(11, PostType.CARGO),
            make_post(12, PostType.CAPACITY),
            make_post(13, PostType.CARGO),
            make_post(14, PostType.CAPACITY),
        ]

        async def _page(db, *, owner_tenant_code, flt):
            return posts, 4

        async def _counts(db, *, owner_tenant_code, flt=None):
            return {"listed": 4}

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "page_mine", staticmethod(_page)
        )
        monkeypatch.setattr(
            facade_mod.EcoPostQueryService,
            "count_mine_by_status",
            staticmethod(_counts),
        )

        data = await EcoHallFacade.page_mine(
            FakeDb(), owner_tenant_code=OWNER, flt=MyPostFilter()
        )

        assert [r["id"] for r in data["list"]] == [11, 12, 13, 14]
        assert data["statusCounts"] == {"listed": 4}
        # 两个类型各装载一次，不是每条一次
        assert stub_pipeline["load_related"] == [
            ((11, 13), PostType.CARGO),
            ((12, 14), PostType.CAPACITY),
        ]

    @pytest.mark.asyncio
    async def test_counts_can_be_skipped(self, monkeypatch, stub_pipeline):
        async def _page(db, *, owner_tenant_code, flt):
            return [], 0

        def _counts(*args, **kwargs):
            raise AssertionError("with_counts=False 时不该查角标")

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "page_mine", staticmethod(_page)
        )
        monkeypatch.setattr(
            facade_mod.EcoPostQueryService,
            "count_mine_by_status",
            staticmethod(_counts),
        )

        data = await EcoHallFacade.page_mine(
            FakeDb(), owner_tenant_code=OWNER, flt=MyPostFilter(), with_counts=False
        )
        assert "statusCounts" not in data


# ---------------------------------------------------------------------------
# 详情
# ---------------------------------------------------------------------------


class TestHallDetail:
    @pytest.mark.asyncio
    async def test_missing_post_says_it_is_gone(self, monkeypatch):
        async def _get(db, *, post_id, viewer_tenant_code):
            return None

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "get_hall_post", staticmethod(_get)
        )

        with pytest.raises(BizException) as exc:
            await EcoHallFacade.hall_detail(
                FakeDb(), post_id=9, viewer_tenant_code=VIEWER
            )
        # 文案不能是「挂牌不存在」：绝大多数情况是被下架或已成交
        assert "不在大厅" in str(exc.value.message)

    @pytest.mark.asyncio
    async def test_records_view_for_other_tenant(self, monkeypatch, stub_pipeline):
        post = make_post(21)
        recorded: List[str] = []

        async def _get(db, *, post_id, viewer_tenant_code):
            return post

        async def _record(db, *, post, viewer_tenant_code, now):
            recorded.append(viewer_tenant_code)

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "get_hall_post", staticmethod(_get)
        )
        monkeypatch.setattr(
            EcoHallFacade, "_record_view", staticmethod(_record)
        )

        data = await EcoHallFacade.hall_detail(
            FakeDb(), post_id=21, viewer_tenant_code=VIEWER, now=NOW
        )

        assert recorded == [VIEWER]
        assert stub_pipeline["serialized"] == [(21, True)]
        assert data["id"] == 21

    @pytest.mark.asyncio
    async def test_owner_view_is_not_counted(self, monkeypatch, stub_pipeline):
        """自己刷十遍就有十个浏览，热度反馈会变成噪声"""
        post = make_post(22)

        async def _get(db, *, post_id, viewer_tenant_code):
            return post

        async def _record(db, **kwargs):
            raise AssertionError("发布方查看自己的挂牌不该计入浏览")

        async def _stats(db, *, post, now=None):
            return {"viewerTenantCount": 5}

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "get_hall_post", staticmethod(_get)
        )
        monkeypatch.setattr(EcoHallFacade, "_record_view", staticmethod(_record))
        monkeypatch.setattr(EcoHallFacade, "viewer_stats", staticmethod(_stats))

        await EcoHallFacade.hall_detail(
            FakeDb(), post_id=22, viewer_tenant_code=OWNER, now=NOW
        )
        assert stub_pipeline["serialized"] == [(22, True)]


class TestMineDetail:
    @pytest.mark.asyncio
    async def test_missing_own_post(self, monkeypatch):
        async def _get(db, *, post_id, owner_tenant_code):
            return None

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "get_own_post", staticmethod(_get)
        )

        with pytest.raises(BizException):
            await EcoHallFacade.mine_detail(
                FakeDb(), post_id=9, owner_tenant_code=OWNER
            )

    @pytest.mark.asyncio
    async def test_carries_viewer_stats(self, monkeypatch, stub_pipeline):
        post = make_post(31)
        stats = {"viewerTenantCount": 12, "days": 7}

        async def _get(db, *, post_id, owner_tenant_code):
            return post

        async def _stats(db, *, post, now=None):
            return stats

        monkeypatch.setattr(
            facade_mod.EcoPostQueryService, "get_own_post", staticmethod(_get)
        )
        monkeypatch.setattr(EcoHallFacade, "viewer_stats", staticmethod(_stats))

        captured: Dict[str, Any] = {}

        def _serialize(post_arg, viewer, **kwargs):
            captured.update(kwargs)
            return {"id": post_arg.id}

        monkeypatch.setattr(
            facade_mod.EcoPostSerializer, "serialize", staticmethod(_serialize)
        )

        await EcoHallFacade.mine_detail(
            FakeDb(), post_id=31, owner_tenant_code=OWNER
        )
        assert captured["viewer_stats"] == stats
        assert captured["detail"] is True


# ---------------------------------------------------------------------------
# 浏览统计
# ---------------------------------------------------------------------------


class TestRecordView:
    @pytest.mark.asyncio
    async def test_upsert_is_one_statement(self):
        class Db:
            def __init__(self):
                self.count = 0

            async def execute(self, stmt):
                self.count += 1
                self.sql = str(stmt.compile(compile_kwargs={"literal_binds": True}))

        db = Db()
        post = make_post(41, view_count=3)
        await EcoHallFacade._record_view(
            db, post=post, viewer_tenant_code=VIEWER, now=NOW
        )

        assert db.count == 1
        assert "ON DUPLICATE KEY UPDATE" in db.sql
        # 主表的 view_count 是列表页展示的数，与明细表一起加
        assert post.view_count == 4

    @pytest.mark.asyncio
    async def test_failure_is_swallowed(self):
        class Db:
            async def execute(self, stmt):
                raise RuntimeError("锁等待超时")

        post = make_post(42, view_count=1)
        # 不抛异常：为一次浏览统计把详情查看变成报错不划算
        await EcoHallFacade._record_view(
            Db(), post=post, viewer_tenant_code=VIEWER, now=NOW
        )
        assert post.view_count == 1


class TestViewerStats:
    @pytest.mark.asyncio
    async def test_aggregates_distinct_tenants(self):
        class Result:
            def __init__(self, rows):
                self._rows = rows

            def first(self):
                return self._rows[0] if self._rows else None

            def all(self):
                return list(self._rows)

        class Db:
            def __init__(self):
                self.calls = 0

            async def execute(self, stmt):
                self.calls += 1
                if self.calls == 1:
                    return Result([(6, 19)])
                return Result([("浙江省", 4), ("江苏省", 2)])

        post = make_post(51, intent_count=2)
        data = await EcoHallFacade.viewer_stats(Db(), post=post, now=NOW)

        assert data["viewerTenantCount"] == 6
        assert data["viewCount"] == 19
        assert data["intentCount"] == 2
        assert data["days"] == facade_mod.VIEWER_STATS_DAYS
        assert data["topProvinces"][0] == {"province": "浙江省", "tenantCount": 4}

    @pytest.mark.asyncio
    async def test_no_views_yet(self):
        class Result:
            def first(self):
                return None

            def all(self):
                return []

        class Db:
            async def execute(self, stmt):
                return Result()

        data = await EcoHallFacade.viewer_stats(Db(), post=make_post(52), now=NOW)
        # 没人看过时给 0 而不是 None：前端拿 None 会渲染成「NaN 家同行看过」
        assert data["viewerTenantCount"] == 0
        assert data["viewCount"] == 0
        assert data["topProvinces"] == []
