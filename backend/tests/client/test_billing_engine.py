"""计费引擎 · 运费匹配算法 & 成本常量（纯逻辑，零 DB）测试

覆盖：
  - ``FreightMatcher._calc_amount``：每台 / 每公里 / 整单 / min_amount 兜底
  - ``FreightMatcher._model_match_type``：车系 / 品牌 / 通用 / 不匹配
  - ``FreightMatcher._direction_for``：正向 / 反向（双向开关）/ 未命中
  - ``FreightMatcher.match_one_cargo``：命中 / 台数非法 / 区域不识别 /
    无规则 / 同分冲突
  - ``cost_constants``：费用类型映射、承运成本类型映射、评分权重排序

对应需求：doc/02.需求文档/02.企业端/05.计费引擎模块/**
对应代码：backend/app/modules/client/services/billing/freight_matcher.py
          backend/app/modules/client/services/billing/cost_constants.py
覆盖用例：TC-CLI-BILLING-041 ~ TC-CLI-BILLING-070
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.modules.client.services.billing import cost_constants as CC
from app.modules.client.services.billing.freight_matcher import (
    CUSTOMER_SCORE,
    FreightMatcher,
)
from app.modules.client.services.billing.freight_matcher import (
    CargoInput,
    WaybillContext,
)
from app.modules.client.services.billing.standardize_service import (
    RegionNode,
    RegionResolution,
    VehicleResolution,
)


# ---- 轻量假 rule / contract（只暴露算法读取的属性）----
def _rule(**kw):
    base = dict(
        id=1, contract_id=100, unit_price=Decimal("500"), billing_mode=0,
        distance_km=None, min_amount=None, series_id=None, brand_id=None,
        is_bidirectional=0, origin_region_id=1, destination_region_id=2,
        price_type=0, rule_version=1, priority=0,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _contract(cid=100):
    return SimpleNamespace(id=cid)


def _region(region_id, level_label="district", name="测试区"):
    node = RegionNode(region_id=region_id, code=str(region_id), name=name,
                      level=3, level_label=level_label)
    return RegionResolution(
        region_id=region_id, region_code=str(region_id), region_name=name,
        level=3, matched_by="id_input", chain=[node],
    )


def _vehicle(brand_id=None, series_id=None, matched_by="ids_input"):
    return VehicleResolution(
        brand_id=brand_id, series_id=series_id,
        brand_name="牌", series_name="系", matched_by=matched_by,
    )


# =====================================================================
# _calc_amount
# =====================================================================
class TestCalcAmount:
    def test_per_vehicle(self):
        amt = FreightMatcher._calc_amount(
            _rule(billing_mode=0, unit_price=Decimal("500")), 3
        )
        assert amt == Decimal("1500")

    def test_per_km(self):
        amt = FreightMatcher._calc_amount(
            _rule(billing_mode=1, unit_price=Decimal("2"),
                  distance_km=Decimal("100")), 2
        )
        assert amt == Decimal("400")

    def test_whole_order_ignores_quantity(self):
        amt = FreightMatcher._calc_amount(
            _rule(billing_mode=2, unit_price=Decimal("888")), 5
        )
        assert amt == Decimal("888")

    def test_min_amount_floor(self):
        amt = FreightMatcher._calc_amount(
            _rule(billing_mode=0, unit_price=Decimal("100"),
                  min_amount=Decimal("500")), 1
        )
        assert amt == Decimal("500")

    def test_min_amount_not_triggered(self):
        amt = FreightMatcher._calc_amount(
            _rule(billing_mode=0, unit_price=Decimal("100"),
                  min_amount=Decimal("50")), 2
        )
        assert amt == Decimal("200")


# =====================================================================
# _model_match_type
# =====================================================================
class TestModelMatchType:
    def test_series_hit(self):
        r = _rule(series_id=7)
        assert FreightMatcher._model_match_type(r, _vehicle(series_id=7)) == "series"

    def test_series_miss(self):
        r = _rule(series_id=7)
        assert FreightMatcher._model_match_type(r, _vehicle(series_id=8)) is None

    def test_brand_hit(self):
        r = _rule(brand_id=3)
        assert FreightMatcher._model_match_type(r, _vehicle(brand_id=3)) == "brand"

    def test_general(self):
        r = _rule()
        assert FreightMatcher._model_match_type(r, _vehicle()) == "general"


# =====================================================================
# _direction_for
# =====================================================================
class TestDirectionFor:
    def test_forward(self):
        r = _rule(origin_region_id=10, destination_region_id=20)
        assert FreightMatcher._direction_for(r, 10, 20) == "forward"

    def test_backward_only_when_bidirectional(self):
        r = _rule(origin_region_id=10, destination_region_id=20, is_bidirectional=1)
        assert FreightMatcher._direction_for(r, 20, 10) == "backward"

    def test_backward_blocked_without_flag(self):
        r = _rule(origin_region_id=10, destination_region_id=20, is_bidirectional=0)
        assert FreightMatcher._direction_for(r, 20, 10) is None

    def test_no_match(self):
        r = _rule(origin_region_id=10, destination_region_id=20)
        assert FreightMatcher._direction_for(r, 99, 88) is None


# =====================================================================
# match_one_cargo 端到端
# =====================================================================
def _ctx(oid=310115, did=110105):
    return WaybillContext(
        customer_id=1, transport_date=date(2026, 7, 7),
        origin=_region(oid), destination=_region(did),
    )


class TestMatchOneCargo:
    def _cache(self, oid=310115, did=110105):
        return {oid: "district", did: "district"}

    def test_hit_forward(self):
        ctx = _ctx()
        cargo = CargoInput(waybill_cargo_id=1, quantity=2, vehicle=_vehicle())
        rule = _rule(origin_region_id=310115, destination_region_id=110105,
                     unit_price=Decimal("500"), billing_mode=0)
        res = FreightMatcher.match_one_cargo(
            ctx, cargo, [rule], {100: _contract()}, self._cache(),
        )
        assert res.calc_status == "success"
        assert res.matched_rule is rule
        assert res.direction == "forward"
        assert res.amount == Decimal("1000")
        assert res.score == CUSTOMER_SCORE + 30_000 + 1_000 + 500 + 200 + 1

    def test_invalid_quantity(self):
        ctx = _ctx()
        cargo = CargoInput(waybill_cargo_id=1, quantity=0, vehicle=_vehicle())
        res = FreightMatcher.match_one_cargo(
            ctx, cargo, [_rule()], {100: _contract()}, self._cache(),
        )
        assert res.error_type == "INVALID_QTY"

    def test_area_not_recognized(self):
        ctx = WaybillContext(
            customer_id=1, transport_date=date(2026, 7, 7),
            origin=RegionResolution(None, None, None, None, "unresolved", []),
            destination=_region(110105),
        )
        cargo = CargoInput(waybill_cargo_id=1, quantity=1, vehicle=_vehicle())
        res = FreightMatcher.match_one_cargo(
            ctx, cargo, [_rule()], {100: _contract()}, self._cache(),
        )
        assert res.error_type == "AREA_NOT_RECOGNIZED"

    def test_rule_not_found(self):
        ctx = _ctx()
        cargo = CargoInput(waybill_cargo_id=1, quantity=1, vehicle=_vehicle())
        # 线路完全不匹配的规则
        rule = _rule(origin_region_id=999, destination_region_id=888)
        res = FreightMatcher.match_one_cargo(
            ctx, cargo, [rule], {100: _contract()}, self._cache(),
        )
        assert res.error_type == "RULE_NOT_FOUND"

    def test_rule_conflict_same_score(self):
        ctx = _ctx()
        cargo = CargoInput(waybill_cargo_id=1, quantity=1, vehicle=_vehicle())
        r1 = _rule(id=1, origin_region_id=310115, destination_region_id=110105)
        r2 = _rule(id=2, origin_region_id=310115, destination_region_id=110105)
        res = FreightMatcher.match_one_cargo(
            ctx, cargo, [r1, r2], {100: _contract()}, self._cache(),
        )
        assert res.error_type == "RULE_CONFLICT"

    def test_higher_priority_wins_no_conflict(self):
        ctx = _ctx()
        cargo = CargoInput(waybill_cargo_id=1, quantity=1, vehicle=_vehicle())
        r1 = _rule(id=1, origin_region_id=310115, destination_region_id=110105,
                   priority=0)
        r2 = _rule(id=2, origin_region_id=310115, destination_region_id=110105,
                   priority=100)
        res = FreightMatcher.match_one_cargo(
            ctx, cargo, [r1, r2], {100: _contract()}, self._cache(),
        )
        assert res.calc_status == "success"
        assert res.matched_rule is r2


# =====================================================================
# cost_constants
# =====================================================================
class TestCostConstants:
    def test_fee_type_name_and_required(self):
        assert CC.fee_type_name("driver_freight") == "司机运费"
        assert CC.fee_type_name("unknown_code") == "unknown_code"
        assert CC.fee_type_is_required("driver_freight") is True
        assert CC.fee_type_is_required("car_wash") is False
        assert CC.fee_type_is_required("unknown_code") is False

    @pytest.mark.parametrize("pm,expected", [
        (CC.PM_FIXED, 1),
        (CC.PM_PER_VEHICLE, 2),
        (CC.PM_TIERED, 2),
        (CC.PM_PER_TON_KM, 3),
        (CC.PM_PER_KM, 4),
        (CC.PM_PERCENTAGE, 4),
    ])
    def test_carrier_cost_type_of(self, pm, expected):
        assert CC.carrier_cost_type_of(pm) == expected

    def test_scope_score_ordering(self):
        # 指定司机 > 指定运力 > 指定承运商 > 全局默认
        assert CC.SCOPE_SCORE[2] > CC.SCOPE_SCORE[3] > CC.SCOPE_SCORE[1] > CC.SCOPE_SCORE[0]

    def test_condition_score_ordering(self):
        # 承运商 > 运力 > 司机 > 调令线路 > ... > 经营主体
        cs = CC.CONDITION_SCORE
        assert cs["carrier"] > cs["capacity"] > cs["driver"] > cs["dispatch_route"]
        assert cs["dispatch_route"] > cs["text_contains"] > cs["mileage_range"]
        assert cs["enterprise"] == min(cs.values())

    def test_qty_and_km_method_sets(self):
        assert CC.PM_PER_VEHICLE in CC.QTY_METHODS
        assert CC.PM_PER_TON_KM in CC.QTY_METHODS and CC.PM_PER_TON_KM in CC.KM_METHODS
        assert CC.PM_FIXED not in CC.QTY_METHODS
