"""服务平台 · 地区解析测试

发布挂牌时必须把租户库的 ``region_id`` 翻译成省/市/区 + 行政区划代码。
译错了不会报错，只会让挂牌在大厅里搜不到、或往平台库写入指向不存在地区的代码，
因此这里重点覆盖：链路向上回溯、层级归位、自定义地区、脏数据成环、批量查询次数。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/07.数据库设计.md §3.4
对应代码：backend/app/modules/client/services/ecosystem/region_resolver.py
"""

from __future__ import annotations

import pytest

from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.services.ecosystem.region_resolver import (
    EMPTY,
    RegionResolver,
    resolve_pair,
)


def region(
    id: int,
    code: str,
    name: str,
    level: int,
    parent_code: str = None,
    source: int = 0,
    is_deleted: int = 0,
) -> BizRegion:
    r = BizRegion(
        code=code, name=name, level=level, parent_code=parent_code, source=source
    )
    r.id = id
    r.is_deleted = is_deleted
    return r


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return list(self._rows)


class FakeRegionDb:
    """按真实编译出的 SQL 分发，这样查询构造本身也被测到。"""

    def __init__(self, regions):
        self.regions = list(regions)
        self.queries = []

    async def execute(self, stmt):
        compiled = stmt.compile()
        sql = str(compiled)
        params = compiled.params
        self.queries.append(sql)

        if "biz_region.id IN" in sql:
            wanted = set(params.get("id_1") or [])
            rows = [r for r in self.regions if r.id in wanted]
        elif "biz_region.code IN" in sql:
            wanted = set(params.get("code_1") or [])
            rows = [r for r in self.regions if r.code in wanted]
        else:  # pragma: no cover
            raise AssertionError(f"未预期的查询：{sql}")

        rows = [r for r in rows if int(r.is_deleted or 0) == 0]
        # ids_by_codes 只认系统地区，且只取 id/code 两列
        if "biz_region.source = " in sql:
            rows = [r for r in rows if int(r.source or 0) == params.get("source_1")]
        if "biz_region.name" not in sql.split("FROM")[0]:
            return FakeResult([(r.id, r.code) for r in rows])
        return FakeResult(rows)

    @property
    def query_count(self) -> int:
        return len(self.queries)


# 浙江省 → 杭州市 → 余杭区 → （自定义）某物流园
ZHEJIANG = region(1, "330000", "浙江省", 1)
HANGZHOU = region(2, "330100", "杭州市", 2, "330000")
YUHANG = region(3, "330110", "余杭区", 3, "330100")
CUSTOM_PARK = region(4, "C0001", "余杭综合物流园", 4, "330110", source=1)

# 四川省 → 成都市
SICHUAN = region(11, "510000", "四川省", 1)
CHENGDU = region(12, "510100", "成都市", 2, "510000")

FULL_TREE = [ZHEJIANG, HANGZHOU, YUHANG, CUSTOM_PARK, SICHUAN, CHENGDU]


class TestResolveChain:
    @pytest.mark.asyncio
    async def test_district_resolves_full_chain(self):
        db = FakeRegionDb(FULL_TREE)
        r = await RegionResolver.resolve(db, YUHANG.id)
        assert (r.province, r.city, r.district) == ("浙江省", "杭州市", "余杭区")
        assert r.region_code == 330110

    @pytest.mark.asyncio
    async def test_city_leaves_district_empty(self):
        db = FakeRegionDb(FULL_TREE)
        r = await RegionResolver.resolve(db, HANGZHOU.id)
        assert (r.province, r.city, r.district) == ("浙江省", "杭州市", None)
        assert r.region_code == 330100

    @pytest.mark.asyncio
    async def test_province_only(self):
        db = FakeRegionDb(FULL_TREE)
        r = await RegionResolver.resolve(db, ZHEJIANG.id)
        assert (r.province, r.city, r.district) == ("浙江省", None, None)
        assert r.region_code == 330000

    @pytest.mark.asyncio
    async def test_names_land_on_correct_level(self):
        """归位错了会让「杭州市」被当成省份写进大厅筛选条件。"""
        db = FakeRegionDb(FULL_TREE)
        r = await RegionResolver.resolve(db, CHENGDU.id)
        assert r.province == "四川省"
        assert r.city == "成都市"


class TestCustomRegion:
    """企业自定义地区（source=1）的 code 是租户自己编的，不能写进平台库。"""

    @pytest.mark.asyncio
    async def test_custom_leaf_still_resolves_standard_ancestors(self):
        db = FakeRegionDb(FULL_TREE)
        r = await RegionResolver.resolve(db, CUSTOM_PARK.id)
        assert (r.province, r.city, r.district) == ("浙江省", "杭州市", "余杭区")

    @pytest.mark.asyncio
    async def test_custom_leaf_code_not_used(self):
        """自定义层不是标准层级，代码要落到最深的标准祖先上。"""
        db = FakeRegionDb(FULL_TREE)
        r = await RegionResolver.resolve(db, CUSTOM_PARK.id)
        assert r.region_code == 330110

    @pytest.mark.asyncio
    async def test_custom_standard_level_falls_back_to_coarser_code(self):
        """租户自建了一个 level=2 的「市」，其 code 指不到 sys_regions。

        此时退到省级代码：粗一级但真实有效，比留空更有用，也比写悬空引用安全。
        代价是 region_code 的精度可能低于 city——已在 ResolvedRegion 上标注。
        """
        custom_city = region(20, "C0100", "某自定义市", 2, "330000", source=1)
        db = FakeRegionDb([ZHEJIANG, custom_city])
        r = await RegionResolver.resolve(db, custom_city.id)
        assert r.city == "某自定义市"
        assert r.province == "浙江省"
        assert r.region_code == 330000

    @pytest.mark.asyncio
    async def test_non_numeric_code_falls_back_to_coarser_code(self):
        weird = region(21, "ABCDEF", "怪数据市", 2, "330000", source=0)
        db = FakeRegionDb([ZHEJIANG, weird])
        r = await RegionResolver.resolve(db, weird.id)
        assert r.city == "怪数据市"
        assert r.region_code == 330000

    @pytest.mark.asyncio
    async def test_no_standard_ancestor_leaves_code_empty(self):
        """整条链都是自定义地区时只能留空，绝不能编一个代码出来。"""
        custom_prov = region(22, "CP01", "自定义省", 1, source=1)
        custom_city = region(23, "CC01", "自定义市", 2, "CP01", source=1)
        db = FakeRegionDb([custom_prov, custom_city])
        r = await RegionResolver.resolve(db, custom_city.id)
        assert r.province == "自定义省"
        assert r.region_code is None


class TestBrokenData:
    @pytest.mark.asyncio
    async def test_missing_id_returns_empty(self):
        db = FakeRegionDb(FULL_TREE)
        assert await RegionResolver.resolve(db, 99999) == EMPTY

    @pytest.mark.asyncio
    async def test_none_id_short_circuits_without_query(self):
        db = FakeRegionDb(FULL_TREE)
        assert await RegionResolver.resolve(db, None) == EMPTY
        assert db.query_count == 0

    @pytest.mark.asyncio
    async def test_deleted_region_is_ignored(self):
        gone = region(30, "330200", "宁波市", 2, "330000", is_deleted=1)
        db = FakeRegionDb([ZHEJIANG, gone])
        assert await RegionResolver.resolve(db, gone.id) == EMPTY

    @pytest.mark.asyncio
    async def test_broken_parent_chain_keeps_what_it_found(self):
        """父级缺失时不该整条失败——能拿到市就先用市。"""
        orphan = region(31, "440300", "深圳市", 2, "440000")
        db = FakeRegionDb([orphan])
        r = await RegionResolver.resolve(db, orphan.id)
        assert r.city == "深圳市"
        assert r.province is None

    @pytest.mark.asyncio
    async def test_self_referencing_parent_does_not_hang(self):
        """parent_code 指回自己是脏数据，必须熔断而不是死循环。"""
        loop = region(32, "330000", "环形省", 1, "330000")
        db = FakeRegionDb([loop])
        r = await RegionResolver.resolve(db, loop.id)
        assert r.province == "环形省"

    @pytest.mark.asyncio
    async def test_two_node_cycle_does_not_hang(self):
        a = region(33, "A", "甲", 2, "B")
        b = region(34, "B", "乙", 1, "A")
        db = FakeRegionDb([a, b])
        r = await RegionResolver.resolve(db, a.id)
        assert r.city == "甲"
        assert r.province == "乙"


class TestUsability:
    """省份是硬要求：解析不出省份的挂牌进了大厅也搜不到。"""

    @pytest.mark.asyncio
    async def test_province_resolved_is_usable(self):
        db = FakeRegionDb(FULL_TREE)
        assert (await RegionResolver.resolve(db, YUHANG.id)).is_usable

    @pytest.mark.asyncio
    async def test_no_province_is_not_usable(self):
        orphan = region(40, "440300", "深圳市", 2, "440000")
        db = FakeRegionDb([orphan])
        assert not (await RegionResolver.resolve(db, orphan.id)).is_usable

    @pytest.mark.asyncio
    async def test_empty_is_not_usable(self):
        assert not EMPTY.is_usable

    @pytest.mark.asyncio
    async def test_display_concatenates_available_levels(self):
        db = FakeRegionDb(FULL_TREE)
        assert (await RegionResolver.resolve(db, YUHANG.id)).display == "浙江省杭州市余杭区"
        assert (await RegionResolver.resolve(db, HANGZHOU.id)).display == "浙江省杭州市"


class TestBatching:
    """批量解析不能退化成 N+1，否则发布列表页会把租户库压出来。"""

    @pytest.mark.asyncio
    async def test_query_count_is_bounded_by_depth_not_input_size(self):
        db = FakeRegionDb(FULL_TREE)
        ids = [YUHANG.id, CHENGDU.id, HANGZHOU.id, CUSTOM_PARK.id, ZHEJIANG.id]
        resolved = await RegionResolver.resolve_many(db, ids)
        assert len(resolved) == 5
        # 1 次按 id + 每层 1 次按 code，与传入数量无关
        assert db.query_count <= 4

    @pytest.mark.asyncio
    async def test_batch_results_are_keyed_by_region_id(self):
        db = FakeRegionDb(FULL_TREE)
        resolved = await RegionResolver.resolve_many(db, [YUHANG.id, CHENGDU.id])
        assert resolved[YUHANG.id].city == "杭州市"
        assert resolved[CHENGDU.id].city == "成都市"

    @pytest.mark.asyncio
    async def test_empty_input_makes_no_query(self):
        db = FakeRegionDb(FULL_TREE)
        assert await RegionResolver.resolve_many(db, [None, 0]) == {}
        assert db.query_count == 0

    @pytest.mark.asyncio
    async def test_duplicate_ids_are_deduped(self):
        db = FakeRegionDb(FULL_TREE)
        resolved = await RegionResolver.resolve_many(db, [YUHANG.id] * 10)
        assert len(resolved) == 1


class TestResolvePair:
    @pytest.mark.asyncio
    async def test_pair_resolved_in_one_pass(self):
        db = FakeRegionDb(FULL_TREE)
        origin, dest = await resolve_pair(db, HANGZHOU.id, CHENGDU.id)
        assert origin.city == "杭州市"
        assert dest.city == "成都市"
        assert db.query_count <= 3

    @pytest.mark.asyncio
    async def test_pair_with_missing_destination(self):
        """运力「任意流向」没有终点，这是正常业务场景，不能报错。"""
        db = FakeRegionDb(FULL_TREE)
        origin, dest = await resolve_pair(db, HANGZHOU.id, None)
        assert origin.city == "杭州市"
        assert dest == EMPTY

    @pytest.mark.asyncio
    async def test_pair_both_empty(self):
        db = FakeRegionDb(FULL_TREE)
        origin, dest = await resolve_pair(db, None, None)
        assert (origin, dest) == (EMPTY, EMPTY)
        assert db.query_count == 0


class TestIdsByCodes:
    """反向解析：编辑运力挂牌时要把区划代码翻回租户库 ID 才能回填选中项。"""

    @pytest.mark.asyncio
    async def test_codes_mapped_in_one_query(self):
        db = FakeRegionDb(FULL_TREE)
        mapping = await RegionResolver.ids_by_codes(db, [330100, 510100])
        assert mapping == {330100: HANGZHOU.id, 510100: CHENGDU.id}
        assert db.query_count == 1

    @pytest.mark.asyncio
    async def test_custom_region_not_reversed(self):
        """自定义地区的 code 是租户自己编的，反查会撞上同名代码"""
        db = FakeRegionDb([*FULL_TREE, region(90, "330101", "自建园区", 4, source=1)])
        assert await RegionResolver.ids_by_codes(db, [330101]) == {}

    @pytest.mark.asyncio
    async def test_unknown_code_absent(self):
        """地区被删过就翻不回来，调用方按缺失处理，不能报错"""
        db = FakeRegionDb(FULL_TREE)
        assert await RegionResolver.ids_by_codes(db, [999999]) == {}

    @pytest.mark.asyncio
    async def test_deleted_region_absent(self):
        db = FakeRegionDb([region(50, "440100", "广州市", 2, is_deleted=1)])
        assert await RegionResolver.ids_by_codes(db, [440100]) == {}

    @pytest.mark.asyncio
    async def test_empty_input_skips_query(self):
        db = FakeRegionDb(FULL_TREE)
        assert await RegionResolver.ids_by_codes(db, [None, 0]) == {}
        assert db.query_count == 0
