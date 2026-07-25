"""服务平台 · 挂牌查询安全基线（纯逻辑，零 DB）测试

大厅查询的可见范围一旦退化，不会报错、不会 500，只会静默把别人屏蔽掉的挂牌
推到查看方眼前。这类回归必须由测试兜住，因此这里把查询编译成 SQL，
断言几条安全条件恒定存在。

「我发布的」用的是另一套边界——归属而非可见性。它同样要被钉死，而且要确认
两套条件没有互相串味：大厅查询不能丢屏蔽名单，「我发布的」不能把自己的草稿、
过期挂牌也过滤掉。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §3.1 与 §3.6
          doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §3
对应代码：backend/app/modules/client/services/ecosystem/post_query_service.py
"""

from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.dialects import mysql

from app.modules.client.services.ecosystem.post_query_service import (
    MY_POST_STATUS_GROUPS,
    SORT_OPTIONS,
    EcoPostQueryService,
    HallFilter,
    MyPostFilter,
    resolve_status_group,
)
from app.modules.console.models.ecosystem.constants import PostStatus, PostType
from app.modules.console.models.ecosystem.post import SysEcoPost

VIEWER = "2002"
OWNER = "1001"


def compile_hall(post_type: int = PostType.CARGO, flt: HallFilter = None) -> str:
    """把大厅查询编译成 MySQL 文本，便于对条件做断言。"""
    flt = flt or HallFilter()
    stmt = select(SysEcoPost)
    stmt = EcoPostQueryService._apply_visibility_scope(
        stmt,
        post_type=post_type,
        viewer_tenant_code=VIEWER,
        exclude_mine=flt.exclude_mine,
    )
    stmt = EcoPostQueryService._apply_filters(stmt, post_type, flt)
    stmt = EcoPostQueryService._apply_sort(stmt, flt.sort_by)
    return str(
        stmt.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True})
    )


class TestSecurityBaseline:
    """无论调用方传什么筛选条件，这些约束都必须在 SQL 里。"""

    def test_block_rule_always_applied(self):
        assert "sys_eco_block_rule" in compile_hall()

    def test_block_rule_direction_is_correct(self):
        """屏蔽方向不能写反：条件必须是「挂牌归属方屏蔽了查看方」。

        方向写反的 SQL 一样能跑、结果集一样非空，但语义完全相反。
        """
        sql = compile_hall()
        assert "sys_eco_block_rule.tenant_code = sys_eco_post.owner_tenant_code" in sql
        assert f"sys_eco_block_rule.blocked_tenant_code = '{VIEWER}'" in sql

    def test_post_level_block_applied(self):
        assert "json_contains(sys_eco_post.extra_block_tenants" in compile_hall()

    def test_hall_disabled_tenant_excluded(self):
        assert "hall_enabled = 0" in compile_hall()

    def test_only_listed_status(self):
        assert f"sys_eco_post.status = {PostStatus.LISTED}" in compile_hall()

    def test_expired_excluded(self):
        assert "sys_eco_post.valid_until >" in compile_hall()

    def test_soft_deleted_excluded(self):
        assert "sys_eco_post.is_deleted = 0" in compile_hall()

    @pytest.mark.parametrize("sort_by", list(SORT_OPTIONS) + ["garbage", None])
    def test_block_rule_survives_every_sort(self, sort_by):
        sql = compile_hall(flt=HallFilter(sort_by=sort_by))
        assert "sys_eco_block_rule" in sql

    @pytest.mark.parametrize("post_type", [PostType.CARGO, PostType.CAPACITY])
    def test_block_rule_in_both_halls(self, post_type):
        assert "sys_eco_block_rule" in compile_hall(post_type)

    def test_block_rule_survives_exclude_mine_off(self):
        """「包含我发布的」不能顺带关掉屏蔽名单。"""
        sql = compile_hall(flt=HallFilter(exclude_mine=False))
        assert "sys_eco_block_rule" in sql
        assert "owner_tenant_code !=" not in sql

    def test_exclude_mine_default_on(self):
        assert "owner_tenant_code !=" in compile_hall()


class TestViewerRequired:
    @pytest.mark.parametrize("bad", ["", None])
    async def test_empty_viewer_rejected(self, bad):
        """查看方为空必须直接报错，绝不能退化成「全部可见」。"""
        with pytest.raises(ValueError):
            await EcoPostQueryService.page_hall(
                None, post_type=PostType.CARGO, viewer_tenant_code=bad,
                flt=HallFilter(),
            )


class TestFilters:
    def test_full_cargo_filter_compiles(self):
        flt = HallFilter(
            keyword="杭州",
            from_province="浙江省",
            from_city="杭州市",
            to_provinces=["四川省", "重庆市"],
            to_city="成都市",
            window_start_from=datetime(2026, 7, 26),
            window_start_to=datetime(2026, 7, 30),
            quantity_min=2,
            quantity_max=20,
            truck_types=["1-8", "1-9"],
            slot_min=6,
            slot_max=12,
            cargo_category=1,
            price_type=1,
            only_verified=True,
            only_high_credit=True,
            sort_by="priceAsc",
        )
        sql = compile_hall(PostType.CARGO, flt)
        assert "sys_eco_cargo_post" in sql
        assert "license_verified = 1" in sql
        assert "complete_rate >= 90" in sql

    def test_full_capacity_filter_compiles(self):
        flt = HallFilter(truck_types=["1-8"], slot_min=6, slot_max=12, sort_by="active")
        sql = compile_hall(PostType.CAPACITY, flt)
        assert "sys_eco_capacity_post" in sql
        assert "sys_eco_capacity_post.truck_type IN" in sql

    def test_destination_uses_side_table_not_json(self):
        """目的地筛选必须走 sys_eco_post_dest，主表 JSON 方案用不上索引。"""
        sql = compile_hall(flt=HallFilter(to_provinces=["四川省"]))
        assert "sys_eco_post_dest" in sql

    def test_destination_falls_back_to_any_direction(self):
        """接受任意流向的运力，不应被目的地筛选漏掉。"""
        sql = compile_hall(flt=HallFilter(to_provinces=["四川省"]))
        assert "any_direction = 1" in sql

    def test_no_ext_join_when_not_needed(self):
        """不带扩展表条件时不应产生多余子查询。"""
        sql = compile_hall(PostType.CARGO, HallFilter(from_city="杭州市"))
        assert "sys_eco_cargo_post" not in sql

    def test_keyword_searches_expected_columns(self):
        sql = compile_hall(flt=HallFilter(keyword="杭州"))
        for col in ("title", "from_name", "to_name", "post_no"):
            assert f"sys_eco_post.{col} LIKE" in sql


class TestSort:
    def test_top_always_first(self):
        for key in SORT_OPTIONS:
            sql = compile_hall(flt=HallFilter(sort_by=key))
            order = sql.split("ORDER BY")[1]
            assert order.strip().startswith("sys_eco_post.is_top DESC"), key

    def test_unknown_sort_falls_back_to_latest(self):
        assert "listed_at DESC" in compile_hall(flt=HallFilter(sort_by="garbage"))

    @pytest.mark.parametrize("key", ["priceAsc", "priceDesc"])
    def test_negotiable_price_sinks_to_bottom(self, key):
        """面议（价格为空）在按价排序时排最后，否则一片 NULL 占住首屏。"""
        sql = compile_hall(flt=HallFilter(sort_by=key))
        assert "price_amount IS NULL ASC" in sql


# ---------------------------------------------------------------------------
# 「我发布的」：边界从可见性换成归属，两套条件不能互相串味
# ---------------------------------------------------------------------------


def compile_mine(flt: MyPostFilter = None) -> str:
    flt = flt or MyPostFilter()
    stmt = EcoPostQueryService._mine_scope(OWNER, flt)
    if flt.statuses:
        stmt = stmt.where(SysEcoPost.status.in_(flt.statuses))
    return str(
        stmt.compile(dialect=mysql.dialect(), compile_kwargs={"literal_binds": True})
    )


def mine_where(flt: MyPostFilter = None) -> str:
    """只取 WHERE 子句：断言「某条件不存在」时，SELECT 的列名会一路误命中"""
    return compile_mine(flt).split("WHERE", 1)[1]


class TestMineSecurityBaseline:
    def test_owner_condition_is_always_present(self):
        """缺了它「我发布的」就是「所有人发布的」，而这个错误不会报错"""
        assert f"sys_eco_post.owner_tenant_code = '{OWNER}'" in compile_mine()

    def test_soft_deleted_excluded(self):
        assert "sys_eco_post.is_deleted = 0" in compile_mine()

    @pytest.mark.parametrize("bad", ["", None])
    async def test_empty_owner_rejected(self, bad):
        with pytest.raises(ValueError):
            await EcoPostQueryService.page_mine(
                None, owner_tenant_code=bad, flt=MyPostFilter()
            )

    @pytest.mark.parametrize("bad", ["", None])
    async def test_empty_owner_rejected_on_counts(self, bad):
        with pytest.raises(ValueError):
            await EcoPostQueryService.count_mine_by_status(
                None, owner_tenant_code=bad
            )

    def test_owner_condition_survives_every_filter(self):
        flt = MyPostFilter(
            post_type=PostType.CAPACITY,
            statuses=[PostStatus.LISTED, PostStatus.DELISTED],
            keyword="杭州",
        )
        assert f"owner_tenant_code = '{OWNER}'" in compile_mine(flt)


class TestMineScope:
    def test_no_status_filter_by_default(self):
        """草稿、驳回、已下架都要能看到，否则用户没有入口去处理它们"""
        assert "sys_eco_post.status" not in mine_where()

    def test_no_validity_filter(self):
        """已过期但还是「展示中」的挂牌必须出现，用户要靠它点「延长展示」"""
        assert "valid_until" not in mine_where()

    def test_visibility_scope_is_not_applied(self):
        """屏蔽名单、大厅开关都是对外的限制，看自己的东西不适用"""
        where = mine_where()
        assert "sys_eco_block_rule" not in where
        assert "hall_enabled" not in where
        assert "extra_block_tenants" not in where

    def test_status_filter_when_given(self):
        sql = compile_mine(MyPostFilter(statuses=[PostStatus.LOCKED, PostStatus.FULFILLING]))
        assert f"sys_eco_post.status IN ({PostStatus.LOCKED}, {PostStatus.FULFILLING})" in sql

    def test_post_type_filter(self):
        sql = compile_mine(MyPostFilter(post_type=PostType.CAPACITY))
        assert f"sys_eco_post.post_type = {PostType.CAPACITY}" in sql

    def test_keyword_searches_expected_columns(self):
        sql = compile_mine(MyPostFilter(keyword="成都"))
        for col in ("title", "post_no", "from_name", "to_name"):
            assert f"sys_eco_post.{col} LIKE" in sql


class TestDetailLoaders:
    """详情取数：列表搜不到的挂牌，拼 ID 也必须拿不到

    挂牌 ID 是自增的。详情页只按 ID 查、不施加可见范围，等于把整个大厅的私有
    内容变成了可遍历接口——而这个洞在界面上完全看不出来。
    """

    class _Db:
        def __init__(self):
            self.stmt = None

        async def execute(self, stmt):
            self.stmt = stmt
            return self

        def scalars(self):
            return self

        def first(self):
            return None

        def sql(self) -> str:
            return str(
                self.stmt.compile(
                    dialect=mysql.dialect(), compile_kwargs={"literal_binds": True}
                )
            )

    async def _hall_sql(self) -> str:
        db = self._Db()
        await EcoPostQueryService.get_hall_post(
            db, post_id=888, viewer_tenant_code=VIEWER
        )
        return db.sql()

    async def test_hall_detail_keeps_block_rule(self):
        sql = await self._hall_sql()
        assert "sys_eco_block_rule" in sql
        assert f"sys_eco_block_rule.blocked_tenant_code = '{VIEWER}'" in sql

    async def test_hall_detail_keeps_status_and_validity(self):
        sql = await self._hall_sql()
        assert f"sys_eco_post.status = {PostStatus.LISTED}" in sql
        assert "sys_eco_post.valid_until >" in sql

    async def test_hall_detail_keeps_hall_switch(self):
        assert "hall_enabled = 0" in await self._hall_sql()

    async def test_hall_detail_is_not_limited_to_one_hall(self):
        """详情按 ID 取单条，不该限定大厅类型——限定了就得靠调用方传对，
        传错的表现是「明明能看到的挂牌，点进去说不存在」"""
        where = (await self._hall_sql()).split("WHERE", 1)[1]
        assert "sys_eco_post.post_type" not in where

    async def test_hall_detail_does_not_exclude_own_post(self):
        """发布方从自己的分享链接点进来要能看到"""
        assert "owner_tenant_code !=" not in await self._hall_sql()

    @pytest.mark.parametrize("bad", ["", None])
    async def test_hall_detail_rejects_empty_viewer(self, bad):
        with pytest.raises(ValueError):
            await EcoPostQueryService.get_hall_post(
                None, post_id=1, viewer_tenant_code=bad
            )

    async def test_own_detail_scopes_by_owner_only(self):
        db = self._Db()
        await EcoPostQueryService.get_own_post(
            db, post_id=888, owner_tenant_code=OWNER
        )
        sql = db.sql()
        where = sql.split("WHERE", 1)[1]

        assert f"sys_eco_post.owner_tenant_code = '{OWNER}'" in where
        # 自己的草稿 / 已过期挂牌都要能打开，否则没有入口去处理它们
        assert "sys_eco_post.status" not in where
        assert "valid_until" not in where

    @pytest.mark.parametrize("bad", ["", None])
    async def test_own_detail_rejects_empty_owner(self, bad):
        with pytest.raises(ValueError):
            await EcoPostQueryService.get_own_post(
                None, post_id=1, owner_tenant_code=bad
            )


class TestStatusGroups:
    def test_every_status_appears_in_exactly_one_group(self):
        """漏了某个状态，那些挂牌就在「我发布的」里彻底看不见了"""
        grouped = [s for statuses in MY_POST_STATUS_GROUPS.values() for s in statuses]
        assert sorted(grouped) == sorted(
            [
                PostStatus.DRAFT,
                PostStatus.AUDITING,
                PostStatus.REJECTED,
                PostStatus.LISTED,
                PostStatus.LOCKED,
                PostStatus.FULFILLING,
                PostStatus.FINISHED,
                PostStatus.DELISTED,
                PostStatus.CANCELLED,
            ]
        )

    def test_no_status_is_double_counted(self):
        grouped = [s for statuses in MY_POST_STATUS_GROUPS.values() for s in statuses]
        assert len(grouped) == len(set(grouped))

    def test_contract_keys_are_all_present(self):
        """键名是给前端 Tab 用的，改名等于前端角标全部归零（08 §3.6）"""
        assert {
            "draft",
            "auditing",
            "rejected",
            "listed",
            "dealing",
            "finished",
            "delisted",
        } <= set(MY_POST_STATUS_GROUPS)

    def test_dealing_merges_locked_and_fulfilling(self):
        assert MY_POST_STATUS_GROUPS["dealing"] == (
            PostStatus.LOCKED,
            PostStatus.FULFILLING,
        )

    def test_resolve_known_group(self):
        assert resolve_status_group("listed") == [PostStatus.LISTED]

    @pytest.mark.parametrize("key", ["", None, "garbage"])
    def test_unknown_group_means_no_status_filter(self, key):
        """未知 Tab 键退化成「不按状态过滤」，比返回空列表更不容易让人以为没数据"""
        assert resolve_status_group(key) == []


class TestCountByStatus:
    class _Result:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class _Db:
        def __init__(self, rows):
            self.rows = rows

        async def execute(self, _stmt):
            return TestCountByStatus._Result(self.rows)

    async def test_groups_are_summed(self):
        db = self._Db(
            [
                (PostStatus.LISTED, 12),
                (PostStatus.LOCKED, 2),
                (PostStatus.FULFILLING, 3),
                (PostStatus.DRAFT, 1),
            ]
        )
        counts = await EcoPostQueryService.count_mine_by_status(
            db, owner_tenant_code=OWNER
        )
        assert counts["listed"] == 12
        assert counts["dealing"] == 5
        assert counts["draft"] == 1

    async def test_absent_statuses_report_zero(self):
        """角标不能是空值，前端拿 undefined 会渲染成「NaN」"""
        counts = await EcoPostQueryService.count_mine_by_status(
            self._Db([]), owner_tenant_code=OWNER
        )
        assert set(counts) == set(MY_POST_STATUS_GROUPS)
        assert all(v == 0 for v in counts.values())
