"""服务平台 · 挂牌标题生成测试

标题是大厅卡片主视觉 + 关键词搜索的主要命中字段，且长度受 varchar(120) 硬约束。
生成规则跑偏不会报错，只会让大厅列表变得难读、搜索命中率下降。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/02.货源大厅设计.md §3
          doc/02.需求文档/02.企业端/13.服务平台/03.运力大厅设计.md §3.1
对应代码：backend/app/modules/client/services/ecosystem/title_builder.py
"""

from __future__ import annotations

from app.modules.client.services.ecosystem.title_builder import (
    MAX_TITLE_LENGTH,
    build_capacity_title,
    build_cargo_title,
    main_brand,
    place_label,
    short_place,
)


class TestShortPlace:
    def test_strips_city_suffix(self):
        assert short_place("杭州市") == "杭州"

    def test_strips_province_suffix(self):
        assert short_place("浙江省") == "浙江"

    def test_autonomous_regions_use_common_short_names(self):
        assert short_place("内蒙古自治区") == "内蒙古"
        assert short_place("广西壮族自治区") == "广西"
        assert short_place("新疆维吾尔自治区") == "新疆"
        assert short_place("西藏自治区") == "西藏"
        assert short_place("宁夏回族自治区") == "宁夏"

    def test_municipalities(self):
        assert short_place("北京市") == "北京"
        assert short_place("重庆市") == "重庆"

    def test_short_names_are_not_over_stripped(self):
        """「市」本身、两字地名不能被削成一个字。"""
        assert short_place("市") == "市"
        assert short_place("亳州") == "亳州"

    def test_district_suffix(self):
        assert short_place("余杭区") == "余杭"

    def test_empty_and_none(self):
        assert short_place(None) is None
        assert short_place("") is None
        assert short_place("   ") is None


class TestPlaceLabel:
    def test_prefers_city(self):
        assert place_label("浙江省", "杭州市", "余杭区") == "杭州"

    def test_falls_back_to_district_then_province(self):
        assert place_label("浙江省", None, "余杭区") == "余杭"
        assert place_label("浙江省", None, None) == "浙江"

    def test_unknown_when_nothing_available(self):
        assert place_label(None, None, None) == "待确认"


class TestMainBrand:
    def test_single_brand(self):
        assert main_brand(["比亚迪"]) == "比亚迪"

    def test_multiple_brands_are_summarized(self):
        """多品牌必须标出来，否则看板的人会按单一品牌误判车型需求。"""
        assert main_brand(["比亚迪", "吉利", "长安"]) == "比亚迪等3个品牌"

    def test_duplicates_collapse_to_single(self):
        assert main_brand(["比亚迪", "比亚迪", " 比亚迪 "]) == "比亚迪"

    def test_blank_entries_ignored(self):
        assert main_brand([None, "", "  ", "吉利"]) == "吉利"

    def test_empty_returns_none(self):
        assert main_brand([]) is None
        assert main_brand(None) is None


class TestCargoTitle:
    def test_standard_shape(self):
        title = build_cargo_title(
            from_province="浙江省",
            from_city="杭州市",
            to_province="四川省",
            to_city="成都市",
            total_quantity=20,
            brands=["比亚迪"],
        )
        assert title == "杭州→成都 20台 比亚迪"

    def test_general_cargo_uses_cargo_name(self):
        title = build_cargo_title(
            from_city="杭州市",
            to_city="成都市",
            total_quantity=30,
            quantity_unit="吨",
            cargo_name="钢材",
        )
        assert title == "杭州→成都 30吨 钢材"

    def test_brand_wins_over_cargo_name(self):
        """商品车是主业务，有品牌就不该退回普货货名。"""
        title = build_cargo_title(
            from_city="杭州市", to_city="成都市", brands=["吉利"], cargo_name="钢材"
        )
        assert "吉利" in title
        assert "钢材" not in title

    def test_route_alone_is_valid(self):
        assert build_cargo_title(from_city="杭州市", to_city="成都市") == "杭州→成都"

    def test_missing_destination_is_marked_not_faked(self):
        title = build_cargo_title(from_city="杭州市", total_quantity=5)
        assert title == "杭州→待确认 5台"

    def test_zero_quantity_omitted(self):
        """0 台是无意义信息，不如不写。"""
        title = build_cargo_title(from_city="杭州市", to_city="成都市", total_quantity=0)
        assert title == "杭州→成都"


class TestCapacityTitle:
    def test_route_comes_first(self):
        """找车方先看位置与流向，车辆参数是次要过滤条件（03 §3.1）。"""
        title = build_capacity_title(
            from_city="成都市",
            to_province="浙江省",
            truck_type_name="板车",
            slot_count=8,
            total_quantity=8,
        )
        assert title.startswith("成都→浙江")
        assert title == "成都→浙江 8位板车 可载8台"

    def test_any_direction(self):
        title = build_capacity_title(
            from_city="成都市", any_direction=True, slot_count=8, truck_type_name="板车"
        )
        assert title == "成都→不限流向 8位板车"

    def test_any_direction_overrides_stale_destination(self):
        """勾了任意流向就以它为准，不能同时显示一个具体流向自相矛盾。"""
        title = build_capacity_title(
            from_city="成都市", to_city="杭州市", any_direction=True
        )
        assert title == "成都→不限流向"

    def test_no_direction_and_not_any_is_marked_pending(self):
        """既没勾任意流向又没填流向，如实写「流向待定」而不是伪装成有线路。"""
        assert build_capacity_title(from_city="成都市") == "成都→流向待定"

    def test_slot_without_truck_type(self):
        title = build_capacity_title(
            from_city="成都市", any_direction=True, slot_count=6
        )
        assert title == "成都→不限流向 6位"

    def test_truck_type_without_slot(self):
        title = build_capacity_title(
            from_city="成都市", any_direction=True, truck_type_name="高栏车"
        )
        assert title == "成都→不限流向 高栏车"


class TestLengthGuard:
    def test_long_title_is_clamped_not_rejected(self):
        """超长必须截断：报错发生在发布最后一步，用户已经填完整个表单了。"""
        title = build_cargo_title(
            from_city="某个特别长的地名" * 5,
            to_city="另一个特别长的地名" * 5,
            total_quantity=99,
            brands=[f"品牌{i}" for i in range(20)],
        )
        assert len(title) <= MAX_TITLE_LENGTH

    def test_clamped_title_is_marked_with_ellipsis(self):
        title = build_cargo_title(
            from_city="长" * 200, to_city="短", total_quantity=1
        )
        assert title.endswith("…")
        assert len(title) == MAX_TITLE_LENGTH

    def test_normal_title_untouched(self):
        title = build_cargo_title(from_city="杭州市", to_city="成都市")
        assert not title.endswith("…")

    def test_whitespace_is_normalized(self):
        title = build_cargo_title(
            from_city="杭州市", to_city="成都市", cargo_name="  钢  材  "
        )
        assert "  " not in title
