"""
成本引擎常量：费用类型、计价方式、异常类型、评分权重

费用类型采用字典驱动定位，这里内置系统默认项；租户可通过数据字典 cost_fee_type 扩展。
"""

from __future__ import annotations


COST_ENGINE_VERSION = "cost-v2.0.0"


# ---- 计价方式 ----
PM_PER_VEHICLE = "per_vehicle"
PM_PER_KM = "per_km"
PM_PER_TRIP = "per_trip"
PM_PER_TON_KM = "per_ton_km"
PM_FIXED = "fixed"
PM_PERCENTAGE = "percentage"
PM_TIERED = "tiered"

PRICING_METHODS = [
    {"value": PM_PER_VEHICLE, "label": "每台", "qtyDimension": "vehicle"},
    {"value": PM_PER_KM, "label": "每公里", "qtyDimension": "km"},
    {"value": PM_PER_TRIP, "label": "每趟固定", "qtyDimension": "trip"},
    {"value": PM_PER_TON_KM, "label": "每吨公里", "qtyDimension": "ton"},
    {"value": PM_FIXED, "label": "固定/包车", "qtyDimension": None},
    {"value": PM_PERCENTAGE, "label": "按比例", "qtyDimension": None},
    {"value": PM_TIERED, "label": "阶梯", "qtyDimension": "vehicle"},
]

# 依赖计价数量（台数）的方式：金额随台数变化，需要按车型分组累加
QTY_METHODS = {PM_PER_VEHICLE, PM_PER_TON_KM, PM_TIERED}
# 依赖里程的方式
KM_METHODS = {PM_PER_KM, PM_PER_TON_KM}


# ---- 费用类型（内置默认，字典 cost_fee_type 可扩展）----
# payee_type: 1-司机 2-承运商 3-社会运力
# directionDefault: 成本恒为付款（应付）=2，随 cost-meta 下发供前端新增规则预填
# pricingMethodDefault: 按费用性质给出建议计价方式，用户可改
_DIR_PAY = 2
FEE_TYPES = [
    {"code": "driver_freight", "name": "司机运费", "isRequired": True, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_PER_VEHICLE, "directionDefault": _DIR_PAY},
    {"code": "car_wash", "name": "洗车费", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_PER_VEHICLE, "directionDefault": _DIR_PAY},
    {"code": "loading", "name": "装车费", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_PER_VEHICLE, "directionDefault": _DIR_PAY},
    {"code": "unloading", "name": "卸车费", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_PER_VEHICLE, "directionDefault": _DIR_PAY},
    {"code": "highway", "name": "高速/路桥费", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_FIXED, "directionDefault": _DIR_PAY},
    {"code": "fuel_subsidy", "name": "油补", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_PER_KM, "directionDefault": _DIR_PAY},
    {"code": "waiting", "name": "等待费", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_FIXED, "directionDefault": _DIR_PAY},
    {"code": "detour", "name": "超里程费", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_PER_KM, "directionDefault": _DIR_PAY},
    {"code": "night", "name": "夜间费", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_FIXED, "directionDefault": _DIR_PAY},
    {"code": "carrier_freight", "name": "承运商运费", "isRequired": False, "payeeTypeDefault": 2,
     "pricingMethodDefault": PM_PER_VEHICLE, "directionDefault": _DIR_PAY},
    {"code": "other", "name": "其他费用", "isRequired": False, "payeeTypeDefault": 1,
     "pricingMethodDefault": PM_FIXED, "directionDefault": _DIR_PAY},
]

FEE_TYPE_MAP = {ft["code"]: ft for ft in FEE_TYPES}


def fee_type_name(code: str) -> str:
    ft = FEE_TYPE_MAP.get(code)
    return ft["name"] if ft else code


def fee_type_is_required(code: str) -> bool:
    ft = FEE_TYPE_MAP.get(code)
    return bool(ft["isRequired"]) if ft else False


# ---- 评分权重（承运范围分替换收入侧客户分）----
# scope_type: 0-全局默认 1-承运商 2-司机 3-运力
SCOPE_SCORE = {
    2: 40_000,   # 指定司机
    3: 35_000,   # 指定运力
    1: 30_000,   # 指定承运商
    0: 10_000,   # 全局默认
}

# ---- 通用条件特异度评分（条件引擎 v2）----
# region_route 复用 LINE_SCORE+DIR_SCORE、vehicle_brand/series 复用 MODEL_SCORE，
# 数值口径与收入侧一致；以下为通用等值/区间/包含类条件的固定特异度权重。
# 量级低于线路(万级)与车型(千级)分，避免通用条件盖过线路/车型的层级语义。
CONDITION_SCORE = {
    "carrier": 6_500,        # 指定承运商（强特异）
    "capacity": 6_000,       # 指定运力
    "capacity_group": 5_800,  # 指定运力分组（弱于单条运力、强于单个司机属性）
    "driver": 5_500,         # 指定司机
    "dispatch_route": 4_500,  # 调令起终点
    "text_contains": 4_000,  # 地名包含
    "mileage_range": 3_500,  # 里程区间
    "quantity_range": 3_000,  # 台数区间
    "vehicle_attr": 2_500,   # 运输车辆属性
    "driver_attr": 2_500,    # 司机属性
    "carrier_type": 1_500,   # 承运方式
    "enterprise": 1_000,     # 经营主体
}


# ---- 异常类型 ----
ERR_POLICY_NOT_FOUND = "POLICY_NOT_FOUND"
ERR_RULE_NOT_FOUND = "RULE_NOT_FOUND"
ERR_RULE_CONFLICT = "RULE_CONFLICT"
ERR_DISTANCE_NOT_FOUND = "DISTANCE_NOT_FOUND"
ERR_AREA_NOT_RECOGNIZED = "AREA_NOT_RECOGNIZED"
ERR_INVALID_QTY = "INVALID_QTY"
ERR_CARRIER_RESOURCE_MISSING = "CARRIER_RESOURCE_MISSING"
ERR_TASK_LOCKED = "TASK_LOCKED"


# ---- 承运成本类型映射（回填 task.carrier_cost_type）----
# 1-包车 2-按台 3-按吨公里 4-其他
def carrier_cost_type_of(pricing_method: str) -> int:
    if pricing_method in (PM_FIXED,):
        return 1
    if pricing_method in (PM_PER_VEHICLE, PM_TIERED):
        return 2
    if pricing_method == PM_PER_TON_KM:
        return 3
    return 4
