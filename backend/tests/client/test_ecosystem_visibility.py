"""服务平台 · 可见性内核（纯逻辑，零 DB）测试

可见性是本模块最容易出错、也最不能出错的部分：漏一个字段就是一次数据泄露。
因此这里对四个层级 + 发布方本人做穷举断言，而不是抽样。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §2
对应代码：backend/app/modules/client/services/ecosystem/visibility.py
          backend/app/modules/client/services/ecosystem/serializer.py
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.modules.client.services.ecosystem.serializer import EcoPostSerializer
from app.modules.client.services.ecosystem.visibility import (
    EcoViewerContext,
    ViewerLevel,
    brands_only,
    can_see_contact,
    can_see_full_plate,
    can_see_owner_full_name,
    coarse_day,
    mask_company_name,
    mask_plate,
    price_range,
    resolve_level,
)
from app.modules.console.models.ecosystem.constants import PostType, VisibilityLevel

OWNER_TENANT = "1001"
VIEWER_TENANT = "2002"
DRIVER_REAL_NAME = "王大锤"


def make_post(post_type: int = PostType.CARGO, **overrides):
    """构造一条「展示中」的挂牌，字段取值贴近真实发布结果。"""
    base = dict(
        id=10231,
        post_no="HY202607250012",
        post_type=post_type,
        title="杭州 → 成都 商品车 8 台",
        status=3,
        is_top=0,
        owner_tenant_code=OWNER_TENANT,
        owner_tenant_name="杭州顺行汽车物流有限公司",
        owner_masked_name="杭***公司",
        from_province="浙江省",
        from_city="杭州市",
        from_district="萧山区",
        from_name="杭州市萧山区宁围街道",
        from_region_code=330109,
        to_province="四川省",
        to_city="成都市",
        to_district="龙泉驿区",
        to_name="成都市龙泉驿区大面街道",
        any_direction=0,
        window_start=datetime(2026, 7, 27, 8, 30, 0),
        window_end=datetime(2026, 7, 28, 18, 0, 0),
        total_quantity=8,
        quantity_unit="台",
        remaining_quantity=8,
        price_type=1,
        price_amount=Decimal("12000.00"),
        price_negotiable=1,
        price_include_tax=0,
        cooperation_type=1,
        contact_name="张三",
        contact_phone="13812345678",
        contact_backup="微信同号",
        visibility_level=VisibilityLevel.CERTIFIED,
        contact_visibility=VisibilityLevel.NEGOTIATING,
        apply_block_rule=1,
        extra_block_tenants=["3003"],
        keep_listed_after_deal=0,
        view_count=42,
        intent_count=3,
        listed_at=datetime(2026, 7, 25, 10, 0, 0),
        valid_until=datetime(2026, 8, 1, 0, 0, 0),
        last_active_at=datetime(2026, 7, 25, 16, 0, 0),
        source_type=1,
        source_id=88,
        source_changed=0,
        source_changed_at=None,
        delist_reason=None,
        delist_remark=None,
        audit_status=2,
        audit_reason=None,
        audit_at=datetime(2026, 7, 25, 9, 50, 0),
        precheck_flags=["price_far_below_market"],
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def make_cargo(**overrides):
    base = dict(
        cargo_category=1,
        vehicle_condition=1,
        cargo_name=None,
        cargo_weight=None,
        cargo_volume=None,
        package_type=None,
        cargo_items=[
            {"brand": "吉利", "series": "星越L", "quantity": 5},
            {"brand": "比亚迪", "series": "宋PLUS", "quantity": 3},
        ],
        require_truck_types=["1-8"],
        require_slot_min=8,
        require_slot_max=None,
        allow_split=0,
        require_insurance=1,
        reference_mileage=Decimal("1850.5"),
        segment_count=1,
        time_negotiable=1,
        freq_desc="每周 3~5 车",
        via_points=[{"name": "武汉市"}],
        other_requirements="需要封闭板运输",
        settle_type=2,
        prepay_ratio=30,
        arrive_time=datetime(2026, 7, 30, 12, 0, 0),
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def make_capacity(**overrides):
    base = dict(
        post_granularity=1,
        truck_type="1-8 轿运车",
        slot_count=8,
        truck_length=Decimal("17.50"),
        rated_load=Decimal("20.00"),
        truck_quantity=1,
        plate_number="浙A88888",
        plate_masked=None,
        plate_public=0,
        has_trailer=1,
        trailer_plate_number="浙A99999挂",
        driver_name=DRIVER_REAL_NAME,
        driver_display="王师傅",
        driver_years=12,
        driver_order_count=340,
        departure_ready_at=datetime(2026, 7, 26, 9, 0, 0),
        pickup_radius=50,
        good_at_categories=["商品车"],
        can_invoice=1,
        invoice_type="增值税专用发票",
        has_insurance=1,
        service_promise="准时到达",
        settle_require=2,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def make_credit(**overrides):
    base = dict(
        deal_count=20,
        deal_completed_count=19,
        complete_rate=Decimal("95.00"),
        eval_count=15,
        avg_score=Decimal("4.80"),
        top_tags=["装车快", "沟通顺畅"],
        avg_respond_minutes=95,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


# 五种查看方上下文
def ctx_anonymous():
    return EcoViewerContext(viewer_tenant_code=VIEWER_TENANT, license_verified=False)


def ctx_certified():
    return EcoViewerContext(viewer_tenant_code=VIEWER_TENANT, license_verified=True)


def ctx_negotiating(post_id: int = 10231):
    return EcoViewerContext(
        viewer_tenant_code=VIEWER_TENANT,
        license_verified=True,
        negotiating_post_ids=frozenset({post_id}),
    )


def ctx_dealt(post_id: int = 10231):
    return EcoViewerContext(
        viewer_tenant_code=VIEWER_TENANT,
        license_verified=True,
        dealt_post_ids=frozenset({post_id}),
    )


def ctx_owner():
    return EcoViewerContext(viewer_tenant_code=OWNER_TENANT, license_verified=True)


class TestResolveLevel:
    def test_owner_wins_over_everything(self):
        """同租户即发布方，即使未认证也是 OWNER。"""
        viewer = EcoViewerContext(
            viewer_tenant_code=OWNER_TENANT, license_verified=False
        )
        assert resolve_level(make_post(), viewer) == ViewerLevel.OWNER

    def test_dealt_outranks_negotiating(self):
        viewer = EcoViewerContext(
            viewer_tenant_code=VIEWER_TENANT,
            license_verified=True,
            negotiating_post_ids=frozenset({10231}),
            dealt_post_ids=frozenset({10231}),
        )
        assert resolve_level(make_post(), viewer) == ViewerLevel.DEALT

    def test_unverified_is_anonymous(self):
        assert resolve_level(make_post(), ctx_anonymous()) == ViewerLevel.ANONYMOUS

    def test_verified_is_certified(self):
        assert resolve_level(make_post(), ctx_certified()) == ViewerLevel.CERTIFIED

    def test_level_is_per_post_not_global(self):
        """层级是「查看方 × 挂牌」的组合属性：对 A 是洽谈层，对 B 仍是认证层。"""
        viewer = ctx_negotiating(post_id=10231)
        post_a = make_post(id=10231)
        post_b = make_post(id=99999)
        assert resolve_level(post_a, viewer) == ViewerLevel.NEGOTIATING
        assert resolve_level(post_b, viewer) == ViewerLevel.CERTIFIED

    def test_negotiating_on_other_post_does_not_leak(self):
        """在别的挂牌上洽谈，不能提升本挂牌的层级。"""
        viewer = ctx_negotiating(post_id=55555)
        assert resolve_level(make_post(id=10231), viewer) == ViewerLevel.CERTIFIED


class TestOwnerFullName:
    def test_default_hidden_from_anonymous(self):
        """默认 visibility_level=2，匿名层看不到企业全称。"""
        post = make_post(visibility_level=VisibilityLevel.CERTIFIED)
        assert can_see_owner_full_name(post, ViewerLevel.ANONYMOUS) is False
        assert can_see_owner_full_name(post, ViewerLevel.CERTIFIED) is True

    def test_publisher_may_open_to_anonymous(self):
        post = make_post(visibility_level=VisibilityLevel.ANONYMOUS)
        assert can_see_owner_full_name(post, ViewerLevel.ANONYMOUS) is True

    def test_missing_config_falls_back_to_certified(self):
        """配置缺失时按认证层要求，不能因数据缺失而放宽。"""
        post = make_post(visibility_level=None)
        assert can_see_owner_full_name(post, ViewerLevel.ANONYMOUS) is False
        assert can_see_owner_full_name(post, ViewerLevel.CERTIFIED) is True


class TestContactVisibility:
    def test_anonymous_never_sees_contact(self):
        for cv in (
            VisibilityLevel.ANONYMOUS,
            VisibilityLevel.CERTIFIED,
            VisibilityLevel.NEGOTIATING,
        ):
            post = make_post(contact_visibility=cv)
            assert can_see_contact(post, ViewerLevel.ANONYMOUS) is False, cv

    def test_certified_visible_when_configured(self):
        post = make_post(contact_visibility=VisibilityLevel.CERTIFIED)
        assert can_see_contact(post, ViewerLevel.CERTIFIED) is True

    def test_certified_hidden_when_negotiating_required(self):
        post = make_post(contact_visibility=VisibilityLevel.NEGOTIATING)
        assert can_see_contact(post, ViewerLevel.CERTIFIED) is False
        assert can_see_contact(post, ViewerLevel.NEGOTIATING) is True

    def test_dealt_and_owner_always_see(self):
        post = make_post(contact_visibility=VisibilityLevel.NEGOTIATING)
        assert can_see_contact(post, ViewerLevel.DEALT) is True
        assert can_see_contact(post, ViewerLevel.OWNER) is True


class TestPlateVisibility:
    def test_anonymous_sees_nothing(self):
        cap = make_capacity(plate_public=1)
        assert can_see_full_plate(cap, ViewerLevel.ANONYMOUS) is False

    def test_certified_only_when_public(self):
        assert can_see_full_plate(make_capacity(plate_public=0), ViewerLevel.CERTIFIED) is False
        assert can_see_full_plate(make_capacity(plate_public=1), ViewerLevel.CERTIFIED) is True

    def test_negotiating_always(self):
        cap = make_capacity(plate_public=0)
        assert can_see_full_plate(cap, ViewerLevel.NEGOTIATING) is True
        assert can_see_full_plate(cap, ViewerLevel.OWNER) is True


class TestMaskHelpers:
    def test_mask_plate(self):
        assert mask_plate("浙A88888") == "浙A·**·88"

    def test_mask_plate_strips_separators(self):
        assert mask_plate("浙A·88888") == "浙A·**·88"

    def test_mask_plate_short_input_not_leaked(self):
        assert mask_plate("浙A88") == "浙***"

    def test_mask_plate_none(self):
        assert mask_plate(None) is None
        assert mask_plate("") is None

    def test_coarse_day_drops_time(self):
        assert coarse_day(datetime(2026, 7, 27, 8, 30)) == "2026-07-27"

    @pytest.mark.parametrize(
        "amount,expected",
        [
            (Decimal("12000"), "1万~1.5万"),
            (Decimal("8500"), "8000~9000"),
            (Decimal("500"), "0~1000"),
        ],
    )
    def test_price_range_buckets(self, amount, expected):
        assert price_range(amount) == expected

    def test_price_range_none_and_zero(self):
        assert price_range(None) is None
        assert price_range(Decimal("0")) is None

    def test_price_range_never_reveals_exact(self):
        """区间不能等于原始报价字符串。"""
        assert price_range(Decimal("12000")) != "12000"

    def test_brands_only_drops_series_and_quantity(self):
        out = brands_only(
            [{"brand": "吉利", "series": "星越L", "quantity": 5}]
        )
        assert out == [{"brand": "吉利"}]

    def test_brands_only_dedupes(self):
        out = brands_only(
            [{"brand": "吉利", "series": "A"}, {"brand": "吉利", "series": "B"}]
        )
        assert out == [{"brand": "吉利"}]

    def test_brands_only_empty(self):
        assert brands_only(None) is None
        assert brands_only([]) is None


class TestCargoSerialization:
    def _ser(self, viewer, **kw):
        return EcoPostSerializer.serialize(
            make_post(PostType.CARGO),
            viewer,
            cargo=make_cargo(),
            credit=make_credit(),
            detail=True,
            **kw,
        )

    def test_anonymous_gets_coarse_view(self):
        data = self._ser(ctx_anonymous())
        # 省市可见，区县与详细地名不可见
        assert data["fromProvince"] == "浙江省"
        assert data["fromCity"] == "杭州市"
        assert data["fromDistrict"] is None
        assert data["fromName"] is None
        assert data["toName"] is None
        # 时间降精度到日
        assert data["windowStart"] == "2026-07-27"
        # 价格只给区间
        assert data["priceAmount"] is None
        assert data["priceRange"] == "1万~1.5万"
        # 企业全称与联系方式不可见
        assert data["ownerTenantName"] is None
        assert data["ownerMaskedName"] == "杭***公司"
        assert data["contactPhone"] is None
        assert data["contactLocked"] is True
        # 统计与结算细节不可见
        assert data["viewCount"] is None
        assert data["intentCount"] is None
        assert data["otherRequirements"] is None
        assert data["settleType"] is None
        # 商品车明细只到品牌
        assert data["cargoItems"] == [{"brand": "吉利"}, {"brand": "比亚迪"}]

    def test_certified_gets_detail_but_no_contact(self):
        data = self._ser(ctx_certified())
        assert data["fromDistrict"] == "萧山区"
        assert data["fromName"] == "杭州市萧山区宁围街道"
        assert data["windowStart"] == "2026-07-27 08:30:00"
        assert data["priceAmount"] == "12000.00"
        assert data["priceRange"] is None
        assert data["ownerTenantName"] == "杭州顺行汽车物流有限公司"
        assert data["viewCount"] == 42
        assert data["otherRequirements"] == "需要封闭板运输"
        assert data["settleType"] == 2
        assert data["cargoItems"][0]["series"] == "星越L"
        # 本挂牌要求洽谈层才给联系方式
        assert data["contactPhone"] is None
        assert data["contactLocked"] is True

    def test_negotiating_unlocks_contact(self):
        data = self._ser(ctx_negotiating())
        assert data["contactName"] == "张三"
        assert data["contactPhone"] == "13812345678"
        assert data["contactBackup"] == "微信同号"
        assert data["contactLocked"] is False

    def test_dealt_sees_contact(self):
        data = self._ser(ctx_dealt())
        assert data["contactPhone"] == "13812345678"

    def test_owner_sees_private_block(self):
        data = self._ser(ctx_owner(), viewer_stats={"weeklyViewerCount": 12})
        assert data["isMine"] is True
        assert data["sourceType"] == 1
        assert data["sourceId"] == 88
        assert data["applyBlockRule"] == 1
        assert data["extraBlockTenants"] == ["3003"]
        assert data["viewerStats"] == {"weeklyViewerCount": 12}
        assert data["auditStatus"] == 2
        assert data["precheckFlags"] == ["price_far_below_market"]

    def test_plate_public_only_for_owner(self):
        """「是否公开车牌」的勾选状态只给发布方

        他自己总能看到完整车牌，编辑弹层只看 plateNumber 有没有值，
        会把这个勾选一律回填成「已公开」。
        """
        capacity = make_capacity(plate_public=0)
        post = make_post(post_type=2)
        owner = EcoPostSerializer.serialize(
            post, ctx_owner(), capacity=capacity, detail=True
        )
        assert owner["platePublic"] == 0
        other = EcoPostSerializer.serialize(
            post, ctx_negotiating(), capacity=capacity, detail=True
        )
        assert "platePublic" not in other

    def test_owner_gets_region_codes_for_edit(self):
        """编辑弹层要靠区划代码把地区翻回租户库 ID，才能回填选中项"""
        dest = SimpleNamespace(province="四川省", city="成都市", region_code=510100)
        data = EcoPostSerializer.serialize(
            make_post(),
            ctx_owner(),
            cargo=make_cargo(),
            destinations=[dest],
            detail=True,
        )
        assert data["fromRegionCode"] == 330109
        assert data["destinations"][0]["regionCode"] == 510100

    @pytest.mark.parametrize(
        "ctx_factory",
        [ctx_anonymous, ctx_certified, ctx_negotiating, ctx_dealt],
    )
    def test_non_owner_never_sees_owner_private(self, ctx_factory):
        """源单信息、屏蔽配置、审核详情、热度反馈只属于发布方。"""
        data = self._ser(ctx_factory(), viewer_stats={"weeklyViewerCount": 12})
        for key in (
            "sourceType",
            "sourceId",
            "sourceChanged",
            "applyBlockRule",
            "extraBlockTenants",
            "viewerStats",
            "auditStatus",
            "auditReason",
            "precheckFlags",
            "fromRegionCode",
        ):
            assert key not in data, f"{key} 泄露给了非发布方"

    @pytest.mark.parametrize(
        "ctx_factory",
        [ctx_anonymous, ctx_certified, ctx_negotiating, ctx_dealt],
    )
    def test_non_owner_destinations_carry_no_code(self, ctx_factory):
        """目的地只给省市名：区划代码是发布方回填编辑表单用的"""
        dest = SimpleNamespace(province="四川省", city="成都市", region_code=510100)
        data = EcoPostSerializer.serialize(
            make_post(),
            ctx_factory(),
            cargo=make_cargo(),
            destinations=[dest],
            detail=True,
        )
        assert data["destinations"] == [{"province": "四川省", "city": "成都市"}]

    def test_card_view_omits_contact_entirely(self):
        """列表卡片不带联系方式字段，避免整页数据里夹带手机号。"""
        data = EcoPostSerializer.serialize(
            make_post(), ctx_negotiating(), cargo=make_cargo(), detail=False
        )
        assert "contactPhone" not in data
        assert "contactName" not in data


class TestCapacitySerialization:
    def _ser(self, viewer, capacity=None):
        return EcoPostSerializer.serialize(
            make_post(PostType.CAPACITY),
            viewer,
            capacity=capacity or make_capacity(),
            credit=make_credit(),
            detail=True,
        )

    def test_anonymous_sees_no_plate_or_driver(self):
        data = self._ser(ctx_anonymous())
        assert data["plateNumber"] is None
        assert data["plateMasked"] is None
        assert data["trailerPlateNumber"] is None
        assert data["driverDisplay"] is None
        assert data["driverYears"] is None
        assert data["departureReadyAt"] is None
        # 车型能力对所有层级可见，否则大厅无法筛选
        assert data["truckType"] == "1-8 轿运车"
        assert data["slotCount"] == 8
        assert data["canInvoice"] == 1

    def test_certified_sees_masked_plate(self):
        data = self._ser(ctx_certified())
        assert data["plateNumber"] is None
        assert data["plateMasked"] == "浙A·**·88"
        # 挂车牌以「挂」结尾，取末两位即 "9挂"；打码函数对所有车牌一视同仁，
        # 不为挂车特例化——单一规则比多一个分支更不容易出错
        assert data["trailerPlateNumber"] == "浙A·**·9挂"
        assert data["driverDisplay"] == "王师傅"
        assert data["driverYears"] == 12

    def test_certified_sees_full_plate_when_public(self):
        data = self._ser(ctx_certified(), capacity=make_capacity(plate_public=1))
        assert data["plateNumber"] == "浙A88888"

    def test_negotiating_sees_full_plate(self):
        data = self._ser(ctx_negotiating())
        assert data["plateNumber"] == "浙A88888"
        assert data["trailerPlateNumber"] == "浙A99999挂"

    @pytest.mark.parametrize(
        "ctx_factory",
        [ctx_anonymous, ctx_certified, ctx_negotiating, ctx_dealt, ctx_owner],
    )
    def test_driver_real_name_never_returned(self, ctx_factory):
        """司机真实姓名在任何层级、包括发布方本人视角都不出现。

        这是 08.接口契约.md §2.4 的硬约束：对外只给 driverDisplay，
        真实姓名只在成交后由承运方在履约节点主动提供。
        """
        data = self._ser(ctx_factory())
        assert "driverName" not in data
        assert DRIVER_REAL_NAME not in _flatten(data)


class TestCreditDisplay:
    def test_enough_samples_shows_numbers(self):
        data = EcoPostSerializer.serialize(
            make_post(), ctx_certified(), cargo=make_cargo(), credit=make_credit()
        )
        credit = data["credit"]
        assert credit["isNewcomer"] is False
        assert credit["completeRate"] == 95.0
        assert credit["avgScore"] == 4.8
        assert credit["topTags"] == ["装车快", "沟通顺畅"]

    def test_insufficient_deals_hides_complete_rate(self):
        """成交样本不足时不给完成率：2 单 1 失败会显示 50%，误伤新用户。"""
        data = EcoPostSerializer.serialize(
            make_post(),
            ctx_certified(),
            cargo=make_cargo(),
            credit=make_credit(
                deal_count=2, deal_completed_count=1, complete_rate=Decimal("50.00")
            ),
        )
        assert data["credit"]["completeRate"] is None

    def test_insufficient_evals_hides_score(self):
        data = EcoPostSerializer.serialize(
            make_post(),
            ctx_certified(),
            cargo=make_cargo(),
            credit=make_credit(eval_count=2, avg_score=Decimal("3.00")),
        )
        assert data["credit"]["avgScore"] is None
        assert data["credit"]["topTags"] is None

    def test_brand_new_tenant_marked_newcomer(self):
        data = EcoPostSerializer.serialize(
            make_post(),
            ctx_certified(),
            cargo=make_cargo(),
            credit=make_credit(
                deal_count=0,
                deal_completed_count=0,
                complete_rate=None,
                eval_count=0,
                avg_score=None,
                top_tags=None,
            ),
        )
        assert data["credit"]["isNewcomer"] is True

    def test_missing_credit_row_is_newcomer(self):
        """信誉表懒加载，首次访问时可能还没有记录。"""
        data = EcoPostSerializer.serialize(
            make_post(), ctx_certified(), cargo=make_cargo(), credit=None
        )
        assert data["credit"]["isNewcomer"] is True
        assert data["credit"]["completeRate"] is None


class TestMaskCompanyName:
    """脱敏名出现在每张大厅卡片上：既要认不出是哪一家，又要能判断大概是哪儿的、做什么的。"""

    def test_typical_logistics_company(self):
        assert mask_company_name("杭州速达物流有限公司") == "杭州**物流"

    def test_keeps_industry_keyword(self):
        assert mask_company_name("上海鼎昌盛世供应链管理有限公司") == "上海**供应链"
        assert mask_company_name("成都长风顺达运输有限责任公司") == "成都**运输"

    def test_longest_industry_word_wins(self):
        """「供应链」不能被「链」之类的短词抢先命中。"""
        assert "供应链" in mask_company_name("广州某某某某供应链有限公司")

    def test_no_industry_word_falls_back_to_head_and_tail(self):
        masked = mask_company_name("杭州鼎昌盛世置业有限公司")
        assert masked.startswith("杭州")
        assert "**" in masked

    def test_short_name_still_gets_masked(self):
        """名字太短也不能原样输出，否则等于没脱敏。"""
        for name in ("速达物流", "速达物流有限公司"):
            masked = mask_company_name(name)
            assert masked != name
            assert "*" in masked

    def test_two_character_name(self):
        assert mask_company_name("速达") == "速*"

    def test_empty_input(self):
        assert mask_company_name(None) == ""
        assert mask_company_name("") == ""

    def test_result_fits_column_width(self):
        """owner_masked_name 是 varchar(100)。"""
        assert len(mask_company_name("某" * 300 + "物流有限公司")) <= 100

    def test_whitespace_normalized(self):
        assert mask_company_name("  杭州速达物流有限公司  ") == "杭州**物流"


def _flatten(obj) -> str:
    """把序列化结果拍平成字符串，用于「某个敏感值绝不出现」的兜底断言。"""
    return repr(obj)
