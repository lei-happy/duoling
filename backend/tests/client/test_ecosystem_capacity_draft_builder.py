"""服务平台 · 运力档案 → 运力草稿测试

重点覆盖两件事：

1. **证照过期硬拦截**（03 §2.1）。把一台证照过期的车推给同行，一旦路上出事，
   平台的责任说不清。这是运力大厅特有、也是必须做的校验。
2. **司机与车牌隐私**（03 §4.2、08 §2.4）。司机姓名只露姓氏、手机号不落平台库、
   车牌默认打码。这几条一旦退化，平台就成了同行互挖司机的名录。

对应代码：backend/app/modules/client/services/ecosystem/capacity_draft_builder.py
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.driver.driver_license import (
    DriverLicense,
)
from app.modules.client.models.capacity.self_capacity.trailer_ext import TrailerExt
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.services.ecosystem.capacity_draft_builder import (
    CapacityDraftBuilder,
    CapacityPublishForm,
    CapacitySource,
    driver_display,
)
from app.modules.client.services.ecosystem.region_resolver import ResolvedRegion
from app.modules.console.models.ecosystem.constants import (
    PostGranularity,
    PostType,
    SourceType,
)

NOW = datetime(2026, 7, 25, 10, 0, 0)
TODAY = NOW.date()

CHENGDU = ResolvedRegion(province="四川省", city="成都市", region_code=510100)
ZHEJIANG = ResolvedRegion(province="浙江省", region_code=330000)
JIANGSU = ResolvedRegion(province="江苏省", region_code=320000)

DRIVER_REAL_NAME = "王大锤"
DRIVER_PHONE = "13800138000"
PLATE = "川A88888"


def make_capacity(**overrides) -> Capacity:
    c = Capacity(
        driver_id=3,
        driver_name=DRIVER_REAL_NAME,
        driver_phone=DRIVER_PHONE,
        vehicle_id=7,
        plate_number=PLATE,
        status=1,
        operation_status=1,
    )
    c.id = 555
    c.is_deleted = 0
    for k, v in overrides.items():
        setattr(c, k, v)
    return c


def make_source(**overrides) -> CapacitySource:
    vehicle = Vehicle(plate_number=PLATE, trailer_id=11, status=1)
    vehicle.id = 7
    vehicle_ext = VehicleExt(
        vehicle_id=7,
        vehicle_type="板车",
        load_capacity=30.0,
        inspection_expire=date(2027, 1, 1),
        transport_license_expire=date(2027, 1, 1),
    )
    trailer_ext = TrailerExt(trailer_id=11, parking_spots=8, length=17.5, load_capacity=35.0)
    driver_license = DriverLicense(
        driver_id=3,
        license_expire=date(2027, 6, 1),
        qualification_expire=date(2027, 6, 1),
    )
    source = CapacitySource(
        capacity=make_capacity(),
        vehicle=vehicle,
        vehicle_ext=vehicle_ext,
        trailer_ext=trailer_ext,
        driver_license=driver_license,
        origin=CHENGDU,
        destinations=[ZHEJIANG],
    )
    for k, v in overrides.items():
        setattr(source, k, v)
    return source


def make_form(**overrides) -> CapacityPublishForm:
    form = CapacityPublishForm(
        from_region_id=12,
        to_region_ids=[1],
        contact_name="李四",
        contact_phone="13900139000",
        window_start=NOW + timedelta(days=1),
        valid_days=7,
    )
    for k, v in overrides.items():
        setattr(form, k, v)
    return form


def flatten(draft) -> str:
    return repr(draft)


class TestLicenseExpiry:
    """证照过期是硬拦截，不是标红提醒。"""

    def test_expired_inspection_blocks(self):
        source = make_source()
        source.vehicle_ext.inspection_expire = date(2026, 1, 1)
        with pytest.raises(BizException) as e:
            CapacityDraftBuilder.assert_publishable(source, make_form(), now=NOW)
        assert "车辆年检" in str(e.value)

    def test_expired_transport_license_blocks(self):
        source = make_source()
        source.vehicle_ext.transport_license_expire = date(2026, 1, 1)
        with pytest.raises(BizException) as e:
            CapacityDraftBuilder.assert_publishable(source, make_form(), now=NOW)
        assert "道路运输证" in str(e.value)

    def test_expired_driver_license_blocks(self):
        source = make_source()
        source.driver_license.license_expire = date(2026, 1, 1)
        with pytest.raises(BizException) as e:
            CapacityDraftBuilder.assert_publishable(source, make_form(), now=NOW)
        assert "驾驶证" in str(e.value)

    def test_expired_qualification_blocks(self):
        source = make_source()
        source.driver_license.qualification_expire = date(2026, 1, 1)
        with pytest.raises(BizException) as e:
            CapacityDraftBuilder.assert_publishable(source, make_form(), now=NOW)
        assert "从业资格证" in str(e.value)

    def test_all_expired_are_listed_together(self):
        """一次说清全部问题，别让用户改一个再被拦一次。"""
        source = make_source()
        source.vehicle_ext.inspection_expire = date(2026, 1, 1)
        source.driver_license.license_expire = date(2026, 1, 1)
        expired = CapacityDraftBuilder.expired_licenses(source, today=TODAY)
        assert set(expired) == {"车辆年检", "司机驾驶证"}

    def test_expiring_today_is_still_valid(self):
        """当天到期仍可上路，按「早于今天」判定。"""
        source = make_source()
        source.vehicle_ext.inspection_expire = TODAY
        assert CapacityDraftBuilder.expired_licenses(source, today=TODAY) == []

    def test_missing_expiry_is_not_treated_as_expired(self):
        """大量存量档案没录全效期，拦掉等于劝退用户。"""
        source = make_source()
        source.vehicle_ext.inspection_expire = None
        source.driver_license.qualification_expire = None
        assert CapacityDraftBuilder.expired_licenses(source, today=TODAY) == []

    def test_missing_license_row_does_not_crash(self):
        source = make_source(driver_license=None, vehicle_ext=None)
        assert CapacityDraftBuilder.expired_licenses(source, today=TODAY) == []

    def test_insurance_expiry_is_not_a_hard_block(self):
        """保险影响理赔而非上路合法性，各家投保节奏差异大，硬拦会误伤正常运力。"""
        source = make_source()
        source.vehicle_ext.insurance_expire = date(2026, 1, 1)
        assert CapacityDraftBuilder.expired_licenses(source, today=TODAY) == []
        CapacityDraftBuilder.assert_publishable(source, make_form(), now=NOW)

    def test_insurance_expiry_is_flagged_for_review(self):
        """不拦不等于当作不存在：出事时保险最影响追偿，必须让审核员看见。"""
        source = make_source()
        source.vehicle_ext.insurance_expire = date(2026, 1, 1)
        assert CapacityDraftBuilder.soft_expired_licenses(source, today=TODAY) == [
            "车辆保险"
        ]

    def test_valid_insurance_is_not_flagged(self):
        source = make_source()
        source.vehicle_ext.insurance_expire = date(2027, 1, 1)
        assert CapacityDraftBuilder.soft_expired_licenses(source, today=TODAY) == []

    def test_soft_flag_is_carried_into_the_draft(self):
        source = make_source()
        source.vehicle_ext.insurance_expire = date(2026, 1, 1)
        draft = CapacityDraftBuilder.to_draft(source, make_form())
        assert draft.soft_expired_licenses == ["车辆保险"]


class TestBindingAndOperationStatus:
    def test_unbound_capacity_rejected(self):
        with pytest.raises(BizException) as e:
            CapacityDraftBuilder.assert_bindable(make_capacity(status=0))
        assert "绑定" in str(e.value)

    def test_busy_capacity_names_its_state(self):
        """告诉用户车在忙什么，他才知道要不要改状态还是换台车。"""
        for status, label in ((2, "运输中"), (3, "休假"), (4, "停运"), (5, "维修保养")):
            with pytest.raises(BizException) as e:
                CapacityDraftBuilder.assert_bindable(
                    make_capacity(operation_status=status)
                )
            assert label in str(e.value)

    def test_available_capacity_passes(self):
        CapacityDraftBuilder.assert_bindable(make_capacity())


class TestRouteAndSchedule:
    def test_missing_origin_rejected(self):
        """运力档案没有实时位置，位置是找车方的第一决策依据，必须填。"""
        source = make_source(origin=ResolvedRegion())
        with pytest.raises(BizException) as e:
            CapacityDraftBuilder.assert_publishable(source, make_form(), now=NOW)
        assert "所在地" in str(e.value)

    def test_no_direction_and_not_any_rejected(self):
        source = make_source(destinations=[])
        with pytest.raises(BizException) as e:
            CapacityDraftBuilder.assert_publishable(source, make_form(), now=NOW)
        assert "任意流向" in str(e.value)

    def test_any_direction_needs_no_destination(self):
        source = make_source(destinations=[])
        CapacityDraftBuilder.assert_publishable(
            source, make_form(any_direction=1), now=NOW
        )

    def test_missing_window_start_rejected(self):
        with pytest.raises(BizException):
            CapacityDraftBuilder.assert_publishable(
                make_source(), make_form(window_start=None), now=NOW
            )

    def test_inverted_window_rejected(self):
        form = make_form(
            window_start=NOW + timedelta(days=5), window_end=NOW + timedelta(days=1)
        )
        with pytest.raises(BizException):
            CapacityDraftBuilder.assert_publishable(make_source(), form, now=NOW)

    def test_open_ended_window_allowed(self):
        """长期可用时结束时间为空是正常业务场景。"""
        CapacityDraftBuilder.assert_publishable(
            make_source(), make_form(window_end=None), now=NOW
        )


class TestPrivacy:
    def test_driver_phone_never_reaches_platform(self):
        """司机手机号不落平台库，需要时回租户库读。"""
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert DRIVER_PHONE not in flatten(draft)

    def test_driver_display_only_shows_surname(self):
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["driver_display"] == "王师傅"

    def test_driver_real_name_is_stored_but_separate(self):
        """原值留库供成交后与运营核查，序列化层负责不对外返回。"""
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["driver_name"] == DRIVER_REAL_NAME

    def test_plate_is_masked_for_display(self):
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["plate_masked"] == "川A·**·88"
        assert draft.ext["plate_number"] == PLATE

    def test_compound_surname_kept_intact(self):
        source = make_source()
        source.capacity.driver_name = "欧阳锋"
        draft = CapacityDraftBuilder.to_draft(source, make_form())
        assert draft.ext["driver_display"] == "欧阳师傅"

    def test_driver_display_handles_blank(self):
        assert driver_display(None) is None
        assert driver_display("  ") is None


class TestVehicleSpec:
    def test_slot_count_comes_from_trailer(self):
        """板位在挂车上，牵引车本身没有板位。"""
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["slot_count"] == 8
        assert draft.total_quantity == 8

    def test_slot_count_falls_back_to_manual_input(self):
        """挂车档案没录板位时允许手填（03 §2.2）。"""
        source = make_source(trailer_ext=None)
        draft = CapacityDraftBuilder.to_draft(source, make_form(slot_count=6))
        assert draft.ext["slot_count"] == 6

    def test_truck_length_from_trailer(self):
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["truck_length"] == Decimal("17.5")

    def test_rated_load_prefers_trailer(self):
        """带挂时载重以挂车为准，用牵引车的值会低报运力。"""
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["rated_load"] == Decimal("35.0")

    def test_rated_load_falls_back_to_vehicle(self):
        source = make_source(trailer_ext=None)
        draft = CapacityDraftBuilder.to_draft(source, make_form())
        assert draft.ext["rated_load"] == Decimal("30.0")

    def test_has_trailer_flag(self):
        assert CapacityDraftBuilder.to_draft(make_source(), make_form()).ext[
            "has_trailer"
        ] == 1

    def test_truck_type_defaults_when_unknown(self):
        """车型是非空字段，取不到时给「其他」而不是让库报错。"""
        source = make_source(vehicle_ext=None, trailer_ext=None)
        draft = CapacityDraftBuilder.to_draft(source, make_form())
        assert draft.ext["truck_type"] == "其他"

    def test_truck_type_uses_dict_label(self):
        """车型要存中文名：字典项在租户自己库里，别家看不到 ``heavy_truck`` 的含义"""
        source = make_source(truck_type_label="重型牵引车")
        source.vehicle_ext.vehicle_type = "heavy_truck"
        draft = CapacityDraftBuilder.to_draft(source, make_form())
        assert draft.ext["truck_type"] == "重型牵引车"
        assert "重型牵引车" in draft.title

    def test_truck_type_falls_back_to_code(self):
        """字典里查不到时退回编码：比统一写成「其他」多留一点信息"""
        source = make_source()
        source.vehicle_ext.vehicle_type = "heavy_truck"
        draft = CapacityDraftBuilder.to_draft(source, make_form())
        assert draft.ext["truck_type"] == "heavy_truck"

    def test_granularity_is_specific_vehicle(self):
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.ext["post_granularity"] == PostGranularity.SPECIFIC
        assert draft.ext["truck_quantity"] == 1


class TestDraftShape:
    def test_source_points_back_at_capacity(self):
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.post_type == PostType.CAPACITY
        assert draft.source_type == SourceType.REF_CAPACITY
        assert draft.source_id == 555

    def test_origin_from_form_resolved_region(self):
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert (draft.from_province, draft.from_city) == ("四川省", "成都市")
        assert draft.from_region_code == 510100

    def test_destinations_keep_their_order(self):
        """流向顺序表达优先级，第一条是主目的地。"""
        source = make_source(destinations=[ZHEJIANG, JIANGSU])
        draft = CapacityDraftBuilder.to_draft(source, make_form())
        assert [d.province for d in draft.destinations] == ["浙江省", "江苏省"]
        assert [d.sort_order for d in draft.destinations] == [0, 1]
        assert draft.to_province == "浙江省"

    def test_any_direction_clears_destination_columns(self):
        source = make_source(destinations=[])
        draft = CapacityDraftBuilder.to_draft(source, make_form(any_direction=1))
        assert draft.any_direction == 1
        assert draft.to_province is None
        assert draft.destinations == []

    def test_auto_title_leads_with_route(self):
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert draft.title == "成都→浙江 8位板车 可载8台"

    def test_user_title_wins(self):
        draft = CapacityDraftBuilder.to_draft(
            make_source(), make_form(title="成都空车找货")
        )
        assert draft.title == "成都空车找货"

    def test_keep_listed_after_deal_is_carried(self):
        """长期运力挂牌成交后继续展示，是运力与货源最重要的机制差异。"""
        draft = CapacityDraftBuilder.to_draft(
            make_source(), make_form(keep_listed_after_deal=1)
        )
        assert draft.keep_listed_after_deal == 1


class TestGuardTexts:
    def test_service_promise_is_scanned(self):
        draft = CapacityDraftBuilder.to_draft(
            make_source(), make_form(service_promise="准时到位，破损包赔")
        )
        assert draft.guard_texts["服务承诺"] == "准时到位，破损包赔"

    def test_only_user_written_fields_scanned(self):
        draft = CapacityDraftBuilder.to_draft(make_source(), make_form())
        assert set(draft.guard_texts) <= {"标题", "服务承诺"}
