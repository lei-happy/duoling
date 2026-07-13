"""智能配载引擎常量与默认配置"""

from __future__ import annotations

# ---- 生成任务状态 ----
TASK_PENDING = "pending"
TASK_RUNNING = "running"
TASK_SUCCESS = "success"
TASK_FAILED = "failed"

# ---- 默认板车车位数（未指定 targetSpots 时兜底）----
DEFAULT_TARGET_SPOTS = 8

# ---- 产出方案数上限 ----
DEFAULT_MAX_PLANS = 20

# ---- 候选拉取上限（喂给算法的最大候选行数）----
DEFAULT_CANDIDATE_LIMIT = 500

# ---- 装载率下限：低于该值的方案不产出（避免推荐半空车）----
DEFAULT_MIN_LOAD_RATE = 40.0

# ---- 多目标打分权重 ----
DEFAULT_WEIGHTS = {
    "load_rate": 0.7,       # 装载率
    "aggregation": 0.2,     # 线路聚合度（台数）
    "concentration": 0.1,   # 客户集中度
}

# ---- 默认占位系数表（按车型关键字命中，越靠前优先）----
# 商品车按车型折算占用板车车位：轿车≈1，SUV/MPV≈1.2，皮卡/大型≈1.6
DEFAULT_OCCUPY_COEFFICIENTS: list[tuple[tuple[str, ...], float]] = [
    (("皮卡", "轻卡", "卡车", "大型", "越野"), 1.6),
    (("suv", "mpv", "商务", "七座", "7座"), 1.2),
]
DEFAULT_OCCUPY_COEFFICIENT = 1.0


def resolve_occupy_coefficient(
    vehicle_model: str | None,
    vehicle_brand: str | None = None,
    overrides: dict[str, float] | None = None,
) -> float:
    """按车型/品牌关键字解析占位系数。

    overrides: 用户传入的 { 关键字: 系数 } 覆盖表（优先于默认表）。
    """
    text = f"{vehicle_brand or ''}{vehicle_model or ''}".lower()
    if overrides:
        for kw, coef in overrides.items():
            if kw and kw.lower() in text:
                return float(coef)
    for keywords, coef in DEFAULT_OCCUPY_COEFFICIENTS:
        for kw in keywords:
            if kw.lower() in text:
                return coef
    return DEFAULT_OCCUPY_COEFFICIENT
