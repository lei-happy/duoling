"""服务平台 · 挂牌编辑分级测试

分档判错的两种后果不对称：

- **该完整重审的判成快速复审**：改了线路却留在大厅，同行按旧信息打过来白跑一趟。
  这是撮合平台最伤信任的一类错，必须逐字段钉死。
- **该快速复审的判成完整重审**：用户改个联系人要排两小时队，久了就不维护信息了。

另一类要防的是「判成改了其实没改」：表单提交的空串与库里的 NULL 是同一个意思，
判成改动会让每次保存都触发一次重审。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.4
对应代码：backend/app/modules/client/services/ecosystem/post_edit_policy.py
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal

import pytest

from app.modules.client.services.ecosystem.post_draft import DestDraft, PostDraft
from app.modules.client.services.ecosystem.post_edit_policy import (
    CAPACITY_EXT_FIELDS,
    CARGO_EXT_FIELDS,
    MAIN_FIELDS,
    EditDiff,
    ReauditTier,
    build_diff,
    diff_destinations,
    diff_ext,
    diff_main,
    normalize,
)
from app.modules.console.models.ecosystem.constants import PostType, PriceType

NOW = datetime(2026, 7, 25, 10, 0, 0)


class FakeRow:
    """够用的 ORM 行替身：只需要按名取属性"""

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    def __getattr__(self, _name):
        return None


def base_post(**overrides) -> FakeRow:
    row = FakeRow(
        post_type=PostType.CARGO,
        title="杭州→成都 20台 比亚迪",
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
        window_start=NOW,
        window_end=None,
        total_quantity=20,
        quantity_unit="台",
        price_type=PriceType.PER_UNIT,
        price_amount=Decimal("800.00"),
        price_include_tax=0,
        price_negotiable=1,
        cooperation_type=1,
        keep_listed_after_deal=0,
        contact_name="张三",
        contact_phone="13800138000",
        contact_backup=None,
        visibility_level=2,
        contact_visibility=3,
        apply_block_rule=1,
        extra_block_tenants=None,
    )
    for k, v in overrides.items():
        setattr(row, k, v)
    return row


def draft_matching(post: FakeRow, *, ext=None, dests=(), **overrides) -> PostDraft:
    """构造一份与挂牌完全一致的草稿，再按需覆盖，用来精确制造「只改了 X」"""
    draft = PostDraft(post_type=post.post_type)
    for name in MAIN_FIELDS:
        setattr(draft, name, getattr(post, name))
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


# ---------------------------------------------------------------------------
# 分级表本身
# ---------------------------------------------------------------------------


class TestFieldTables:
    def test_every_main_field_has_a_valid_tier(self):
        for name, rule in MAIN_FIELDS.items():
            assert rule.tier in (ReauditTier.FAST, ReauditTier.FULL), name
            assert rule.label, name

    @pytest.mark.parametrize("table", [CARGO_EXT_FIELDS, CAPACITY_EXT_FIELDS])
    def test_every_ext_field_has_a_valid_tier(self, table):
        for name, rule in table.items():
            assert rule.tier in (ReauditTier.FAST, ReauditTier.FULL), name
            assert rule.label, name

    def test_validity_fields_are_not_in_the_table(self):
        """有效期只能由「延长展示」改；混进编辑就等于给了无限续命的口子"""
        assert "valid_from" not in MAIN_FIELDS
        assert "valid_until" not in MAIN_FIELDS
        assert "valid_days" not in MAIN_FIELDS

    def test_derived_and_owned_fields_are_not_in_the_table(self):
        """这些字段不该由用户表单驱动，进表就会被编辑覆盖掉"""
        for name in (
            "status",
            "audit_status",
            "post_no",
            "owner_tenant_code",
            "remaining_quantity",
            "intent_count",
            "view_count",
            "is_top",
            "delist_reason",
        ):
            assert name not in MAIN_FIELDS, name

    @pytest.mark.parametrize(
        "name",
        [
            "from_province",
            "from_city",
            "to_province",
            "any_direction",
            "window_start",
            "total_quantity",
        ],
    )
    def test_deal_substance_fields_are_full_reaudit(self, name):
        """线路、时间、台数改了就是另一笔生意，必须先撤出大厅"""
        assert MAIN_FIELDS[name].tier == ReauditTier.FULL

    @pytest.mark.parametrize(
        "name",
        [
            "title",
            "price_amount",
            "contact_phone",
            "visibility_level",
            "extra_block_tenants",
        ],
    )
    def test_description_fields_are_fast_reaudit(self, name):
        assert MAIN_FIELDS[name].tier == ReauditTier.FAST

    def test_route_fields_share_one_label_so_the_trail_reads_cleanly(self):
        """五个 from_* 字段一起变时，流水该写「出发地」而不是罗列五个列名"""
        labels = {
            MAIN_FIELDS[n].label
            for n in (
                "from_province",
                "from_city",
                "from_district",
                "from_region_code",
                "from_name",
            )
        }
        assert labels == {"出发地"}

    def test_cargo_and_capacity_tables_do_not_overlap_on_semantics(self):
        """两张扩展表各自独立，同名字段的分级必须一致，否则同一改动两个大厅表现不同"""
        for name in set(CARGO_EXT_FIELDS) & set(CAPACITY_EXT_FIELDS):
            assert CARGO_EXT_FIELDS[name].tier == CAPACITY_EXT_FIELDS[name].tier, name


# ---------------------------------------------------------------------------
# 归一化
# ---------------------------------------------------------------------------


class TestNormalize:
    def test_blank_string_becomes_none(self):
        assert normalize("   ") is None

    def test_string_is_trimmed(self):
        assert normalize("  杭州  ") == "杭州"

    def test_empty_list_becomes_none(self):
        assert normalize([]) is None

    def test_list_is_preserved(self):
        assert normalize(["A", "B"]) == ["A", "B"]

    def test_tuple_becomes_list_for_comparability(self):
        assert normalize(("A",)) == ["A"]

    def test_zero_is_not_treated_as_empty(self):
        """0 是有意义的取值（如 any_direction=0），当成空值会漏判改动"""
        assert normalize(0) == 0

    def test_none_stays_none(self):
        assert normalize(None) is None


# ---------------------------------------------------------------------------
# 主表比对
# ---------------------------------------------------------------------------


class TestDiffMain:
    def test_identical_draft_yields_no_change(self):
        post = base_post()
        assert diff_main(post, draft_matching(post)) == []

    def test_empty_string_equals_null(self):
        """表单把没填的备用联系方式提成 ""，不该判成改动"""
        post = base_post(contact_backup=None)
        draft = draft_matching(post, contact_backup="")
        assert diff_main(post, draft) == []

    def test_whitespace_only_equals_null(self):
        post = base_post(contact_backup=None)
        assert diff_main(post, draft_matching(post, contact_backup="  ")) == []

    def test_decimal_and_int_of_equal_value_are_same(self):
        post = base_post(price_amount=Decimal("800.00"))
        assert diff_main(post, draft_matching(post, price_amount=800)) == []

    def test_price_change_is_fast(self):
        post = base_post()
        changed = diff_main(post, draft_matching(post, price_amount=Decimal("900")))
        assert [c.name for c in changed] == ["price_amount"]
        assert changed[0].tier == ReauditTier.FAST
        assert changed[0].label == "报价"

    def test_route_change_is_full(self):
        post = base_post()
        changed = diff_main(post, draft_matching(post, from_city="宁波市"))
        assert changed[0].tier == ReauditTier.FULL

    def test_clearing_a_field_counts_as_change(self):
        post = base_post(contact_backup="0571-88888888")
        changed = diff_main(post, draft_matching(post, contact_backup=None))
        assert [c.name for c in changed] == ["contact_backup"]
        assert changed[0].new is None

    def test_old_and_new_values_are_carried_for_the_trail(self):
        post = base_post()
        changed = diff_main(post, draft_matching(post, title="新标题"))
        assert changed[0].old == "杭州→成都 20台 比亚迪"
        assert changed[0].new == "新标题"

    def test_any_direction_flip_is_full(self):
        post = base_post(any_direction=0)
        changed = diff_main(post, draft_matching(post, any_direction=1))
        assert changed[0].tier == ReauditTier.FULL

    def test_block_list_change_is_fast(self):
        post = base_post(extra_block_tenants=None)
        changed = diff_main(post, draft_matching(post, extra_block_tenants=["T9"]))
        assert changed[0].tier == ReauditTier.FAST
        assert changed[0].label == "可见范围"


# ---------------------------------------------------------------------------
# 扩展表比对
# ---------------------------------------------------------------------------


class TestDiffExt:
    def test_none_draft_ext_yields_no_change(self):
        ext = FakeRow(other_requirements="需要带挂")
        assert diff_ext(PostType.CARGO, ext, None) == []

    def test_absent_key_is_left_untouched(self):
        """扩展表字段多且各 Builder 只填自己关心的，缺键当清空会误抹数据"""
        ext = FakeRow(other_requirements="需要带挂", cargo_category=1)
        changed = diff_ext(PostType.CARGO, ext, {"cargo_category": 1})
        assert changed == []

    def test_explicit_none_clears_and_counts_as_change(self):
        ext = FakeRow(other_requirements="需要带挂")
        changed = diff_ext(PostType.CARGO, ext, {"other_requirements": None})
        assert [c.name for c in changed] == ["other_requirements"]

    def test_cargo_goods_change_is_full(self):
        ext = FakeRow(cargo_category=1)
        changed = diff_ext(PostType.CARGO, ext, {"cargo_category": 2})
        assert changed[0].tier == ReauditTier.FULL
        assert changed[0].label == "货物信息"

    def test_cargo_remark_change_is_fast(self):
        ext = FakeRow(other_requirements="A")
        changed = diff_ext(PostType.CARGO, ext, {"other_requirements": "B"})
        assert changed[0].tier == ReauditTier.FAST

    def test_capacity_truck_change_is_full(self):
        ext = FakeRow(truck_type="8位板车")
        changed = diff_ext(PostType.CAPACITY, ext, {"truck_type": "6位板车"})
        assert changed[0].tier == ReauditTier.FULL
        assert changed[0].label == "车辆信息"

    def test_capacity_plate_change_is_full(self):
        """换车牌意味着换了车，不能悄悄留在大厅"""
        ext = FakeRow(plate_number="浙A12345")
        changed = diff_ext(PostType.CAPACITY, ext, {"plate_number": "浙A99999"})
        assert changed[0].tier == ReauditTier.FULL

    def test_capacity_driver_change_is_full(self):
        ext = FakeRow(driver_name="王大锤")
        changed = diff_ext(PostType.CAPACITY, ext, {"driver_name": "李小明"})
        assert changed[0].tier == ReauditTier.FULL

    def test_capacity_service_promise_change_is_fast(self):
        ext = FakeRow(service_promise="准时到达")
        changed = diff_ext(PostType.CAPACITY, ext, {"service_promise": "全程可查"})
        assert changed[0].tier == ReauditTier.FAST

    def test_unknown_field_falls_back_to_full(self):
        """新增列忘登记时，代价是多一次人工审核，而不是静默放行"""
        ext = FakeRow(brand_new_column="A")
        changed = diff_ext(PostType.CARGO, ext, {"brand_new_column": "B"})
        assert changed[0].tier == ReauditTier.FULL

    def test_missing_ext_row_treats_every_value_as_new(self):
        changed = diff_ext(PostType.CARGO, None, {"cargo_category": 2})
        assert [c.name for c in changed] == ["cargo_category"]

    def test_json_list_reorder_counts_as_change(self):
        ext = FakeRow(require_truck_types=["A", "B"])
        changed = diff_ext(PostType.CARGO, ext, {"require_truck_types": ["B", "A"]})
        assert len(changed) == 1


# ---------------------------------------------------------------------------
# 目的地比对
# ---------------------------------------------------------------------------


class TestDiffDestinations:
    def test_identical_yields_no_change(self):
        dests = [FakeRow(province="四川省", city="成都市", region_code=510100, sort_order=0)]
        post = base_post()
        assert diff_destinations(dests, draft_matching(post, dests=dests)) == []

    def test_added_destination_is_full(self):
        dests = [FakeRow(province="四川省", city="成都市", region_code=510100, sort_order=0)]
        draft = draft_matching(base_post(), dests=dests)
        draft.destinations.append(
            DestDraft(province="重庆市", city="重庆市", region_code=500100, sort_order=1)
        )
        changed = diff_destinations(dests, draft)
        assert [c.name for c in changed] == ["destinations"]
        assert changed[0].tier == ReauditTier.FULL

    def test_removed_destination_is_detected(self):
        dests = [
            FakeRow(province="四川省", city="成都市", region_code=510100, sort_order=0),
            FakeRow(province="重庆市", city="重庆市", region_code=500100, sort_order=1),
        ]
        draft = draft_matching(base_post(), dests=dests[:1])
        assert len(diff_destinations(dests, draft)) == 1

    def test_reorder_is_a_change_because_first_one_is_the_primary(self):
        dests = [
            FakeRow(province="四川省", city="成都市", region_code=510100, sort_order=0),
            FakeRow(province="重庆市", city="重庆市", region_code=500100, sort_order=1),
        ]
        draft = draft_matching(base_post(), dests=dests)
        draft.destinations[0].sort_order = 1
        draft.destinations[1].sort_order = 0
        assert len(diff_destinations(dests, draft)) == 1

    def test_destinations_without_province_are_ignored(self):
        """Builder 可能塞进空行，空行不该被当成一个目的地"""
        dests = [FakeRow(province="四川省", city="成都市", region_code=510100, sort_order=0)]
        draft = draft_matching(base_post(), dests=dests)
        draft.destinations.append(DestDraft(province="", city=None, sort_order=9))
        assert diff_destinations(dests, draft) == []

    def test_both_empty_yields_no_change(self):
        assert diff_destinations([], draft_matching(base_post())) == []


# ---------------------------------------------------------------------------
# 汇总
# ---------------------------------------------------------------------------


class TestEditDiff:
    def test_no_change_reports_fast_tier(self):
        diff = EditDiff()
        assert diff.has_changes is False
        assert diff.tier == ReauditTier.FAST
        assert diff.requires_full_reaudit is False

    def test_one_full_field_drags_the_whole_edit_to_full(self):
        post = base_post()
        diff = build_diff(
            post=post,
            ext=None,
            dests=[],
            draft=draft_matching(post, contact_name="李四", from_city="宁波市"),
        )
        assert diff.requires_full_reaudit is True

    def test_all_fast_stays_fast(self):
        post = base_post()
        diff = build_diff(
            post=post,
            ext=None,
            dests=[],
            draft=draft_matching(
                post, contact_name="李四", price_amount=Decimal("900")
            ),
        )
        assert diff.requires_full_reaudit is False

    def test_labels_are_deduped_in_first_seen_order(self):
        post = base_post()
        diff = build_diff(
            post=post,
            ext=None,
            dests=[],
            draft=draft_matching(
                post,
                price_amount=Decimal("900"),
                price_include_tax=1,
                contact_name="李四",
            ),
        )
        assert diff.labels == ["报价", "联系方式"]

    def test_build_diff_covers_main_ext_and_dests_together(self):
        post = base_post()
        dests = [FakeRow(province="四川省", city="成都市", region_code=510100, sort_order=0)]
        draft = draft_matching(post, dests=dests, ext={"other_requirements": "改了"})
        draft.title = "新标题"
        draft.destinations = [
            DestDraft(province="湖北省", city="武汉市", region_code=420100, sort_order=0)
        ]
        diff = build_diff(
            post=post, ext=FakeRow(other_requirements="原值"), dests=dests, draft=draft
        )
        names = set(diff.field_names)
        assert {"title", "other_requirements", "destinations"} <= names
        assert diff.requires_full_reaudit is True


class TestAuditPayload:
    """写进 ``sys_eco_post_audit.changed_fields`` 的结构

    只记字段名，审核员看不出「报价从 1200 改到 1180」还是「改到 120」，
    洽谈方的「对方更新了信息」通知也说不清改成了什么。
    """

    def test_no_change_yields_none(self):
        assert EditDiff().to_audit_payload() is None

    def test_payload_carries_old_and_new(self):
        post = base_post()
        diff = build_diff(
            post=post,
            ext=None,
            dests=[],
            draft=draft_matching(post, price_amount=Decimal("900.00")),
        )
        payload = diff.to_audit_payload()

        item = next(i for i in payload["items"] if i["field"] == "price_amount")
        assert item["old"] == "800.00"
        assert item["new"] == "900.00"
        assert item["label"] == "报价"

    def test_payload_carries_tier_and_labels(self):
        post = base_post()
        diff = build_diff(
            post=post, ext=None, dests=[], draft=draft_matching(post, from_city="宁波市")
        )
        payload = diff.to_audit_payload()

        assert payload["tier"] == ReauditTier.FULL
        assert payload["labels"] == ["出发地"]

    def test_datetime_is_formatted_not_serialized_raw(self):
        """``datetime`` 不是 JSON 原生类型，留着会在写库时炸在序列化上"""
        post = base_post()
        diff = build_diff(
            post=post,
            ext=None,
            dests=[],
            draft=draft_matching(post, window_start=datetime(2026, 8, 1, 9, 30)),
        )
        item = next(
            i for i in diff.to_audit_payload()["items"] if i["field"] == "window_start"
        )

        assert item["new"] == "2026-08-01 09:30"

    def test_none_stays_none(self):
        post = base_post(contact_backup="备用微信")
        diff = build_diff(
            post=post, ext=None, dests=[], draft=draft_matching(post, contact_backup=None)
        )
        item = next(
            i
            for i in diff.to_audit_payload()["items"]
            if i["field"] == "contact_backup"
        )

        assert item["old"] == "备用微信"
        assert item["new"] is None

    def test_list_values_are_joined(self):
        dests = [FakeRow(province="四川省", city="成都市", region_code=510100, sort_order=0)]
        post = base_post()
        draft = draft_matching(post, dests=dests)
        draft.destinations = [
            DestDraft(province="湖北省", city="武汉市", region_code=420100, sort_order=0)
        ]
        item = next(
            i
            for i in build_diff(post=post, ext=None, dests=dests, draft=draft)
            .to_audit_payload()["items"]
            if i["field"] == "destinations"
        )

        assert "四川省" in item["old"]
        assert "湖北省" in item["new"]

    def test_long_value_is_truncated(self):
        """流水是给人看的，不是给 JSON 列当仓库"""
        post = base_post()
        diff = build_diff(
            post=post, ext=None, dests=[], draft=draft_matching(post, title="标" * 300)
        )
        item = diff.to_audit_payload()["items"][0]

        assert len(item["new"]) <= 101

    def test_payload_is_json_serializable(self):
        post = base_post()
        diff = build_diff(
            post=post,
            ext=None,
            dests=[],
            draft=draft_matching(
                post,
                price_amount=Decimal("900"),
                window_start=datetime(2026, 8, 1, 9, 30),
                total_quantity=8,
            ),
        )
        assert json.loads(json.dumps(diff.to_audit_payload(), ensure_ascii=False))
