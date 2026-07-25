"""服务平台 · 任务单 → 货源草稿测试

两类风险，都必须由测试兜住：

1. **商业机密外泄**：客户名称、内部单号、内部成本、VIN、详细地址一旦写进平台库，
   就是跨租户可见，事后删也补不回泄露。这类字段要逐个断言「绝不出现」。
2. **前置校验退化**：已派车、已锁定、装车时间已过的任务被挂到大厅，
   同行联系过来才发现车早就安排好了，一次就把信任耗掉。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/02.货源大厅设计.md §2.1、§2.2
对应代码：backend/app/modules/client/services/ecosystem/cargo_draft_builder.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.common.exceptions import BizException
from app.modules.client.models.task.task import Task
from app.modules.client.services.ecosystem.cargo_draft_builder import (
    MAX_CARGO_ITEMS,
    CargoDraftBuilder,
    CargoItem,
    CargoPublishForm,
    CargoSource,
)
from app.modules.client.services.ecosystem.region_resolver import ResolvedRegion
from app.modules.console.models.ecosystem.constants import (
    CargoCategory,
    PostType,
    PriceType,
    SourceType,
)

NOW = datetime(2026, 7, 25, 10, 0, 0)

HANGZHOU = ResolvedRegion(
    province="浙江省", city="杭州市", district="余杭区", region_code=330110
)
CHENGDU = ResolvedRegion(province="四川省", city="成都市", region_code=510100)

# 这些值绝不允许出现在草稿的任何角落
SECRET_CUSTOMER = "一汽大众销售有限公司"
SECRET_DEALER = "成都锦江4S店"
SECRET_TASK_NO = "T202607250001"
SECRET_WAYBILL_NO = "JH20260725120000"
SECRET_COST = Decimal("18888.88")


def make_task(**overrides) -> Task:
    task = Task(
        task_no=SECRET_TASK_NO,
        status=0,
        origin="杭州市余杭区科技大道 123 号中转仓",
        origin_region_id=3,
        destination="成都市锦江区某某路 88 号",
        destination_region_id=12,
        segment_count=2,
        total_quantity=20,
        planned_load_time=NOW + timedelta(days=1),
        planned_arrive_time=NOW + timedelta(days=4),
        carrier_cost_amount=SECRET_COST,
        carrier_cost_type=2,
        is_locked=0,
    )
    task.id = 777
    task.is_deleted = 0
    for k, v in overrides.items():
        setattr(task, k, v)
    return task


def make_source(task: Task = None, items=None) -> CargoSource:
    return CargoSource(
        task=task or make_task(),
        origin=HANGZHOU,
        destination=CHENGDU,
        items=items
        if items is not None
        else [
            CargoItem(brand="比亚迪", series="汉EV", quantity=12),
            CargoItem(brand="吉利", series="星越L", quantity=8),
        ],
    )


def make_form(**overrides) -> CargoPublishForm:
    form = CargoPublishForm(
        contact_name="张三",
        contact_phone="13800138000",
        valid_days=7,
        price_type=PriceType.PER_UNIT,
        price_amount=Decimal("800.00"),
    )
    for k, v in overrides.items():
        setattr(form, k, v)
    return form


def flatten(draft) -> str:
    """把草稿拍平成字符串，用于「某个敏感值绝不出现」的兜底断言。"""
    return repr(draft)


class TestSecretsNeverLeak:
    """02 §2.2 明确列出的「绝不进入平台库」字段。"""

    def test_customer_name_absent(self):
        source = make_source()
        source.task.carrier_name = SECRET_CUSTOMER
        draft = CargoDraftBuilder.to_draft(source, make_form())
        assert SECRET_CUSTOMER not in flatten(draft)

    def test_internal_task_no_absent(self):
        """内部单号会暴露业务量，且对同行毫无用处。"""
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert SECRET_TASK_NO not in flatten(draft)

    def test_internal_cost_absent(self):
        """内部成本等于利润空间，带出去等于把底价交给同行。"""
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert "18888" not in flatten(draft)

    def test_price_comes_from_form_not_from_task_cost(self):
        draft = CargoDraftBuilder.to_draft(
            make_source(), make_form(price_amount=Decimal("800.00"))
        )
        assert draft.price_amount == Decimal("800.00")

    def test_detailed_address_absent(self):
        """task.origin 是自由文本，很可能写着门牌号，只能带到区县级。"""
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        blob = flatten(draft)
        assert "科技大道" not in blob
        assert "123 号" not in blob
        assert "中转仓" not in blob

    def test_place_names_are_built_from_regions(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert draft.from_name == "浙江省杭州市余杭区"
        assert draft.to_name == "四川省成都市"

    def test_cargo_items_only_carry_brand_series_quantity(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        for item in draft.ext["cargo_items"]:
            assert set(item) == {"brand", "series", "quantity"}


class TestPrechecks:
    """文案要与前端按钮置灰时一致：用户可能绕过置灰直接调接口。"""

    def test_dispatched_task_rejected(self):
        with pytest.raises(BizException) as e:
            CargoDraftBuilder.assert_publishable(make_task(status=1), now=NOW)
        assert "还没派车" in str(e.value)

    def test_task_with_capacity_rejected(self):
        with pytest.raises(BizException) as e:
            CargoDraftBuilder.assert_publishable(make_task(capacity_id=5), now=NOW)
        assert "承运方" in str(e.value)

    def test_task_with_carrier_rejected(self):
        with pytest.raises(BizException):
            CargoDraftBuilder.assert_publishable(make_task(carrier_id=9), now=NOW)

    def test_locked_task_rejected(self):
        with pytest.raises(BizException) as e:
            CargoDraftBuilder.assert_publishable(make_task(is_locked=1), now=NOW)
        assert "结算" in str(e.value)

    def test_missing_route_rejected(self):
        with pytest.raises(BizException):
            CargoDraftBuilder.assert_publishable(make_task(destination=""), now=NOW)

    def test_past_load_time_rejected(self):
        task = make_task(planned_load_time=NOW - timedelta(hours=1))
        with pytest.raises(BizException) as e:
            CargoDraftBuilder.assert_publishable(task, now=NOW)
        assert "装车时间已过" in str(e.value)

    def test_missing_load_time_rejected(self):
        with pytest.raises(BizException):
            CargoDraftBuilder.assert_publishable(
                make_task(planned_load_time=None), now=NOW
            )

    def test_valid_task_passes(self):
        CargoDraftBuilder.assert_publishable(make_task(), now=NOW)


class TestFieldMapping:
    def test_source_points_back_at_the_task(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert draft.source_type == SourceType.REF_TASK
        assert draft.source_id == 777
        assert draft.post_type == PostType.CARGO

    def test_route_and_window_from_task(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert (draft.from_province, draft.from_city) == ("浙江省", "杭州市")
        assert draft.window_start == NOW + timedelta(days=1)
        assert draft.window_end == NOW + timedelta(days=4)

    def test_region_codes_are_carried(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert draft.from_region_code == 330110
        assert draft.to_region_code == 510100

    def test_destination_row_is_written_for_cargo(self):
        """货源也写目的地行，这样大厅筛选对两个大厅同构。"""
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert len(draft.destinations) == 1
        assert draft.destinations[0].province == "四川省"

    def test_segment_count_from_task(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["segment_count"] == 2

    def test_arrive_time_lands_on_extension(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["arrive_time"] == NOW + timedelta(days=4)

    def test_cargo_category_is_vehicle(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["cargo_category"] == CargoCategory.VEHICLE

    def test_quantity_falls_back_to_item_sum(self):
        """总台数冗余字段可能为 0（历史数据），此时用明细求和兜住。"""
        draft = CargoDraftBuilder.to_draft(
            make_source(task=make_task(total_quantity=0)), make_form()
        )
        assert draft.total_quantity == 20


class TestSplitAndRemaining:
    def test_split_enabled_tracks_remaining(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form(allow_split=1))
        assert draft.remaining_quantity == 20

    def test_split_disabled_leaves_remaining_empty(self):
        """不分批时留空表示整单承接，填上会让人误以为可以部分接。"""
        draft = CargoDraftBuilder.to_draft(make_source(), make_form(allow_split=0))
        assert draft.remaining_quantity is None


class TestTitle:
    def test_auto_title_follows_spec(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert draft.title == "杭州→成都 20台 比亚迪等2个品牌"

    def test_user_title_wins(self):
        draft = CargoDraftBuilder.to_draft(
            make_source(), make_form(title="急运一批商品车")
        )
        assert draft.title == "急运一批商品车"

    def test_blank_user_title_falls_back_to_auto(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form(title="   "))
        assert draft.title.startswith("杭州→成都")


class TestGuardTexts:
    """只扫用户可写的字段：扫系统生成的内容只会白白增加误拦风险。"""

    def test_title_is_scanned(self):
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert "标题" in draft.guard_texts

    def test_other_requirements_is_scanned(self):
        draft = CargoDraftBuilder.to_draft(
            make_source(), make_form(other_requirements="需要封闭箱车")
        )
        assert draft.guard_texts["其他要求"] == "需要封闭箱车"

    def test_blank_requirements_not_scanned(self):
        draft = CargoDraftBuilder.to_draft(
            make_source(), make_form(other_requirements="   ")
        )
        assert "其他要求" not in draft.guard_texts

    def test_place_names_not_scanned(self):
        """地名是系统拼的，不可能夹带联系方式。"""
        draft = CargoDraftBuilder.to_draft(make_source(), make_form())
        assert set(draft.guard_texts) <= {"标题", "其他要求", "货量频次"}


class TestItemAggregation:
    def test_same_brand_series_merges(self):
        items = CargoDraftBuilder._aggregate(
            [("比亚迪", "汉EV", 3), ("比亚迪", "汉EV", 5), ("吉利", "星越L", 2)]
        )
        assert len(items) == 2
        merged = next(i for i in items if i.series == "汉EV")
        assert merged.quantity == 8

    def test_sorted_by_quantity_desc(self):
        """卡片只展示前几条，应该先给最有代表性的。"""
        items = CargoDraftBuilder._aggregate(
            [("A", "a", 1), ("B", "b", 9), ("C", "c", 5)]
        )
        assert [i.brand for i in items] == ["B", "C", "A"]

    def test_blank_brand_normalized_to_none(self):
        items = CargoDraftBuilder._aggregate([("  ", "", 4)])
        assert items[0].brand is None
        assert items[0].series is None

    def test_zero_quantity_dropped(self):
        assert CargoDraftBuilder._aggregate([("A", "a", 0)]) == []

    def test_item_count_is_capped(self):
        """品牌车系组合过多时截断，避免 JSON 撑到几百条拖慢列表查询。"""
        rows = [(f"品牌{i}", f"车系{i}", i + 1) for i in range(MAX_CARGO_ITEMS + 15)]
        assert len(CargoDraftBuilder._aggregate(rows)) == MAX_CARGO_ITEMS

    def test_no_items_leaves_json_empty(self):
        """普货任务可能没有商品车明细，此处不能写成空数组糊弄。"""
        draft = CargoDraftBuilder.to_draft(make_source(items=[]), make_form())
        assert draft.ext["cargo_items"] is None
