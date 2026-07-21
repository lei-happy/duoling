"""
内置条件评估器（条件引擎 v2）。

导入本模块即完成注册（@register 副作用）。新增条件类型只需在此追加一个
ConditionEvaluator 子类并 @register，无需改表 / 迁移 / 改匹配器。

评分口径：
  - region_route  → LINE_SCORE + DIR_SCORE（复用收入侧线路+方向层级，保证存量分数不变）
  - vehicle_brand → MODEL_SCORE["brand"]；vehicle_series → MODEL_SCORE["series"]
  - 其余通用条件 → cost_constants.CONDITION_SCORE 固定特异度权重
"""

from __future__ import annotations

from typing import Any, Optional

from app.modules.client.services.billing.conditions.base import (
    ConditionEvaluator,
    ConditionMatch,
    compare_scalar,
)
from app.modules.client.services.billing.conditions.registry import register
from app.modules.client.services.billing.cost_constants import CONDITION_SCORE
from app.modules.client.services.billing.freight_matcher import (
    DIR_SCORE,
    LINE_SCORE,
    MODEL_SCORE,
)


def _pick(node: dict, *keys: str) -> Any:
    """按多个候选键名取值（兼容 camelCase / snake_case）。"""
    for k in keys:
        if k in node and node.get(k) is not None:
            return node.get(k)
    return None


# ---------- 线路 / 车型（复用收入侧层级评分）----------


@register
class RegionRouteEvaluator(ConditionEvaluator):
    key = "region_route"
    label = "线路（起终点行政区）"
    value_type = "region_route"
    operators = ["match"]
    option_source = "region"

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        o = _pick(node, "originRegionId", "origin_region_id")
        d = _pick(node, "destinationRegionId", "destination_region_id")
        bidir = int(_pick(node, "bidirectional", "is_bidirectional") or 0)
        if o is None and d is None:
            return ConditionMatch()  # 空线路=不约束

        origin_chain = [
            (n.region_id, n.level_label)
            for n in (ctx.origin.chain if ctx.origin else [])
        ]
        dest_chain = [
            (n.region_id, n.level_label)
            for n in (ctx.destination.chain if ctx.destination else [])
        ]
        cache = getattr(ctx, "region_level_cache", None) or {}

        best = None
        for oid, ol in origin_chain:
            for did, dl in dest_chain:
                direction = None
                if o == oid and d == did:
                    direction = "forward"
                elif bidir == 1 and o == did and d == oid:
                    direction = "backward"
                if direction is None:
                    continue
                rule_o_level = cache.get(o, "custom")
                rule_d_level = cache.get(d, "custom")
                line_s = LINE_SCORE.get((rule_o_level, rule_d_level), 5_000)
                dir_s = DIR_SCORE.get(direction, 0)
                score = line_s + dir_s
                if best is None or score > best["score"]:
                    best = {
                        "score": score, "direction": direction,
                        "oid": oid, "did": did, "ol": ol, "dl": dl,
                        "line": line_s, "dir": dir_s,
                        "line_pair": f"{rule_o_level}->{rule_d_level}",
                    }
        if best is None:
            return None
        return ConditionMatch(
            score_delta=best["score"],
            facts={
                "line_matched": True,
                "direction": best["direction"],
                "matched_origin": best["oid"],
                "matched_destination": best["did"],
                "origin_level": best["ol"],
                "destination_level": best["dl"],
            },
            trace=[{
                "type": self.key, "direction": best["direction"],
                "line": best["line"], "dir": best["dir"],
                "line_pair": best["line_pair"],
            }],
        )


class _VehicleModelEvaluator(ConditionEvaluator):
    """车型层级评估器基类（品牌/车系）。"""

    attr = "brand_id"
    model_layer = "brand"
    operators = ["eq"]

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        value = _pick(node, "value", "brandId", "seriesId")
        if value is None:
            return ConditionMatch()  # 不限车型
        v = getattr(ctx, "current_vehicle", None)
        if v is None:
            return None
        actual = getattr(v, self.attr, None)
        if actual is not None and compare_scalar(actual, "eq", value):
            return ConditionMatch(
                score_delta=MODEL_SCORE.get(self.model_layer, 0),
                facts={"model_match_type": self.model_layer},
                trace=[{"type": self.key, "model_layer": self.model_layer,
                        "value": value}],
            )
        return None


@register
class VehicleBrandEvaluator(_VehicleModelEvaluator):
    key = "vehicle_brand"
    label = "商品车品牌"
    value_type = "brand"
    option_source = "vehicle_brand"
    attr = "brand_id"
    model_layer = "brand"


@register
class VehicleSeriesEvaluator(_VehicleModelEvaluator):
    key = "vehicle_series"
    label = "商品车车系"
    value_type = "series"
    option_source = "vehicle_series"
    attr = "series_id"
    model_layer = "series"


# ---------- 文本包含（任务 / 调令 起终点名称）----------


@register
class TextContainsEvaluator(ConditionEvaluator):
    key = "text_contains"
    label = "地点名称包含"
    value_type = "text"
    operators = ["contains", "eq", "in"]
    fields = [
        {"value": "origin_name", "label": "任务出发地"},
        {"value": "destination_name", "label": "任务目的地"},
        {"value": "dispatch_from", "label": "调令出发地"},
        {"value": "dispatch_to", "label": "调令目的地"},
    ]

    @staticmethod
    def _texts(ctx: Any, field: str) -> list[str]:
        if field == "origin_name":
            return [ctx.origin.region_name] if ctx.origin else []
        if field == "destination_name":
            return [ctx.destination.region_name] if ctx.destination else []
        orders = getattr(ctx, "dispatch_orders", None) or []
        if field == "dispatch_from":
            return [o.from_location for o in orders]
        if field == "dispatch_to":
            return [o.to_location for o in orders]
        return []

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        field = _pick(node, "field") or "origin_name"
        value = _pick(node, "value")
        op = _pick(node, "op") or "contains"
        if value is None:
            return ConditionMatch()
        texts = [t for t in self._texts(ctx, field) if t]
        if any(compare_scalar(t, op, value) for t in texts):
            return ConditionMatch(
                score_delta=CONDITION_SCORE["text_contains"],
                trace=[{"type": self.key, "field": field, "op": op, "value": value}],
            )
        return None


# ---------- 数值区间（里程 / 台数）----------


class _RangeEvaluator(ConditionEvaluator):
    value_type = "number_range"
    operators = ["between", "gte", "lte", "eq"]
    score_key = ""

    def _actual(self, ctx: Any) -> Optional[Any]:
        raise NotImplementedError

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        value = _pick(node, "value")
        op = _pick(node, "op") or "between"
        if value is None:
            return ConditionMatch()
        actual = self._actual(ctx)
        if actual is None:
            return None
        if compare_scalar(actual, op, value):
            return ConditionMatch(
                score_delta=CONDITION_SCORE[self.score_key],
                trace=[{"type": self.key, "op": op, "value": value,
                        "actual": float(actual)}],
            )
        return None


@register
class MileageRangeEvaluator(_RangeEvaluator):
    key = "mileage_range"
    label = "里程区间(公里)"
    score_key = "mileage_range"

    def _actual(self, ctx: Any):
        if ctx.distance_km is not None:
            return ctx.distance_km
        orders = getattr(ctx, "dispatch_orders", None) or []
        total = None
        for o in orders:
            if o.mileage is not None:
                total = (total or 0) + float(o.mileage)
        return total


@register
class QuantityRangeEvaluator(_RangeEvaluator):
    key = "quantity_range"
    label = "台数区间"
    score_key = "quantity_range"

    def _actual(self, ctx: Any):
        return ctx.total_quantity


# ---------- 属性条件（运输车辆 / 司机）----------


@register
class VehicleAttrEvaluator(ConditionEvaluator):
    key = "vehicle_attr"
    label = "运输车辆属性"
    value_type = "attr"
    operators = ["eq", "ne", "in", "gte", "lte", "between"]
    fields = [
        {"value": "plate_category", "label": "车牌类型"},
        {"value": "vehicle_type", "label": "车辆类型"},
        {"value": "load_capacity", "label": "核定载重(吨)"},
        {"value": "volume_capacity", "label": "核定容积(m³)"},
        {"value": "status", "label": "车辆状态"},
    ]

    @staticmethod
    def _attrs(ctx: Any) -> dict:
        attrs: dict = {}
        veh = getattr(ctx, "transport_vehicle", None)
        if veh is not None:
            attrs.update({
                "plate_category": getattr(veh, "plate_category", None),
                "status": getattr(veh, "status", None),
                "plate_number": getattr(veh, "plate_number", None),
                "enterprise_id": getattr(veh, "enterprise_id", None),
            })
        ext = getattr(ctx, "vehicle_ext", None)
        if ext is not None:
            attrs.update({
                "vehicle_type": getattr(ext, "vehicle_type", None),
                "load_capacity": getattr(ext, "load_capacity", None),
                "volume_capacity": getattr(ext, "volume_capacity", None),
            })
        return attrs

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        field = _pick(node, "field")
        value = _pick(node, "value")
        op = _pick(node, "op") or "eq"
        if not field or value is None:
            return ConditionMatch()
        attrs = self._attrs(ctx)
        actual = attrs.get(field)
        if actual is None:
            return None
        if compare_scalar(actual, op, value):
            return ConditionMatch(
                score_delta=CONDITION_SCORE["vehicle_attr"],
                trace=[{"type": self.key, "field": field, "op": op, "value": value}],
            )
        return None


@register
class DriverAttrEvaluator(ConditionEvaluator):
    key = "driver_attr"
    label = "司机属性"
    value_type = "attr"
    operators = ["eq", "ne", "in"]
    fields = [
        {"value": "settlement_mode", "label": "结算模式"},
        {"value": "driver_type", "label": "司机类型"},
        {"value": "department_id", "label": "所属车队"},
        {"value": "operation_status", "label": "运营状态"},
        {"value": "status", "label": "人事状态"},
    ]

    @staticmethod
    def _attrs(ctx: Any) -> dict:
        attrs: dict = {}
        drv = getattr(ctx, "driver", None)
        if drv is not None:
            attrs.update({
                "driver_id": getattr(drv, "id", None),
                "status": getattr(drv, "status", None),
                "enterprise_id": getattr(drv, "enterprise_id", None),
            })
        op = getattr(ctx, "driver_operation", None)
        if op is not None:
            attrs.update({
                "settlement_mode": getattr(op, "settlement_mode", None),
                "driver_type": getattr(op, "driver_type", None),
                "department_id": getattr(op, "department_id", None),
                "operation_status": getattr(op, "operation_status", None),
            })
        return attrs

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        field = _pick(node, "field")
        value = _pick(node, "value")
        op = _pick(node, "op") or "eq"
        if not field or value is None:
            return ConditionMatch()
        attrs = self._attrs(ctx)
        actual = attrs.get(field)
        if actual is None:
            return None
        if compare_scalar(actual, op, value):
            return ConditionMatch(
                score_delta=CONDITION_SCORE["driver_attr"],
                trace=[{"type": self.key, "field": field, "op": op, "value": value}],
            )
        return None


# ---------- 承运 / 主体（等值命中）----------


class _ScalarEqEvaluator(ConditionEvaluator):
    """通用等值命中：value 与 ctx 某属性相等。"""

    ctx_attr = ""
    score_key = ""
    operators = ["eq", "in"]

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        value = _pick(node, "value")
        op = _pick(node, "op") or "eq"
        if value is None:
            return ConditionMatch()
        actual = getattr(ctx, self.ctx_attr, None)
        if actual is None:
            return None
        if compare_scalar(actual, op, value):
            return ConditionMatch(
                score_delta=CONDITION_SCORE[self.score_key],
                trace=[{"type": self.key, "op": op, "value": value}],
            )
        return None


@register
class CarrierEvaluator(_ScalarEqEvaluator):
    key = "carrier"
    label = "指定承运商"
    value_type = "carrier"
    option_source = "carrier"
    ctx_attr = "carrier_id"
    score_key = "carrier"


@register
class CarrierTypeEvaluator(_ScalarEqEvaluator):
    key = "carrier_type"
    label = "承运方式"
    value_type = "enum"
    ctx_attr = "carrier_type"
    score_key = "carrier_type"


@register
class CapacityEvaluator(_ScalarEqEvaluator):
    key = "capacity"
    label = "指定运力"
    value_type = "capacity"
    option_source = "capacity"
    ctx_attr = "capacity_id"
    score_key = "capacity"


@register
class DriverEvaluator(_ScalarEqEvaluator):
    key = "driver"
    label = "指定司机"
    value_type = "driver"
    option_source = "driver"
    ctx_attr = "driver_id"
    score_key = "driver"


@register
class CapacityGroupEvaluator(ConditionEvaluator):
    """指定运力分组：判断当前运力(司机)是否在某分组集合内。

    命中依赖 ctx.capacity_group_ids（编排层按当前 driver_id 预加载的启用分组ID集合）。
    op=eq 时命中「属于该分组」；op=in 时命中「属于给定任一分组」。
    """
    key = "capacity_group"
    label = "指定运力分组"
    value_type = "capacity_group"
    option_source = "capacity_group"
    operators = ["eq", "in"]

    @staticmethod
    def _to_int(v: Any) -> Optional[int]:
        try:
            return int(v)
        except (TypeError, ValueError):
            return None

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        value = _pick(node, "value")
        op = _pick(node, "op") or "eq"
        if value is None:
            return ConditionMatch()  # 未指定分组=不约束
        group_ids = getattr(ctx, "capacity_group_ids", None) or set()
        if not group_ids:
            return None

        if op == "in":
            raw = value if isinstance(value, (list, tuple, set)) else [value]
            targets = {i for i in (self._to_int(v) for v in raw) if i is not None}
            hit_id = next((g for g in targets if g in group_ids), None)
        else:
            target = self._to_int(value)
            hit_id = target if (target is not None and target in group_ids) else None

        if hit_id is None:
            return None
        return ConditionMatch(
            score_delta=CONDITION_SCORE["capacity_group"],
            facts={"capacity_group_matched": hit_id},
            trace=[{"type": self.key, "op": op, "value": value,
                    "matched_group": hit_id}],
        )


@register
class EnterpriseEvaluator(_ScalarEqEvaluator):
    key = "enterprise"
    label = "经营主体"
    value_type = "enterprise"
    option_source = "business_entity"
    ctx_attr = "enterprise_id"
    score_key = "enterprise"


# ---------- 调令线路（起终点行政区 / 名称包含）----------


@register
class DispatchRouteEvaluator(ConditionEvaluator):
    key = "dispatch_route"
    label = "调令起终点"
    value_type = "attr"
    operators = ["eq", "contains"]
    fields = [
        {"value": "from_region_id", "label": "调令出发行政区"},
        {"value": "to_region_id", "label": "调令目的行政区"},
        {"value": "from_location", "label": "调令出发地名称"},
        {"value": "to_location", "label": "调令目的地名称"},
    ]

    def evaluate(self, node: dict, ctx: Any) -> Optional[ConditionMatch]:
        field = _pick(node, "field") or "from_region_id"
        value = _pick(node, "value")
        op = _pick(node, "op") or ("contains" if field.endswith("location") else "eq")
        if value is None:
            return ConditionMatch()
        orders = getattr(ctx, "dispatch_orders", None) or []
        for o in orders:
            actual = getattr(o, field, None)
            if actual is not None and compare_scalar(actual, op, value):
                return ConditionMatch(
                    score_delta=CONDITION_SCORE["dispatch_route"],
                    trace=[{"type": self.key, "field": field, "op": op,
                            "value": value}],
                )
        return None
