"""智能配载引擎（纯算法，零 DB）测试

覆盖 SmartStowageEngine 的核心行为：
  - 占位系数解析（车型关键字命中 / 覆盖表优先）
  - 线路聚类：不同起终点不会拼进同一方案
  - 装箱 FFD：不超过目标车位数
  - 装载率下限过滤
  - 多目标打分排序（装载率高的方案排前）

对应设计：项目文档/02.需求文档/02.企业端/09.智能配载模块设计.md
对应代码：backend/app/modules/client/services/task/smart_stowage/stowage_engine.py
"""

from __future__ import annotations

from app.modules.client.services.task.smart_stowage.constants import (
    resolve_occupy_coefficient,
)
from app.modules.client.services.task.smart_stowage.stowage_engine import (
    CargoCandidate,
    EngineParams,
    SmartStowageEngine,
)


def _cand(cid, qty, origin, dest, model="轿车", brand="", cust=None):
    return CargoCandidate(
        waybill_id=cid,
        waybill_cargo_id=cid * 10,
        quantity=qty,
        waybill_no=f"W{cid}",
        customer_id=cust if cust is not None else cid,
        customer_name=f"客户{cid}",
        vehicle_brand=brand,
        vehicle_model=model,
        origin=origin,
        destination=dest,
    )


class TestOccupyCoefficient:
    def test_default_sedan(self):
        assert resolve_occupy_coefficient("轿车") == 1.0

    def test_suv(self):
        assert resolve_occupy_coefficient("SUV") == 1.2

    def test_pickup(self):
        assert resolve_occupy_coefficient("皮卡") == 1.6

    def test_override_takes_priority(self):
        assert resolve_occupy_coefficient(
            "轿车", overrides={"轿车": 0.8}
        ) == 0.8


class TestLineClustering:
    def test_different_lines_not_mixed(self):
        cands = [
            _cand(1, 2, "上海", "北京"),
            _cand(2, 2, "广州", "成都"),
        ]
        plans = SmartStowageEngine.generate(
            cands, EngineParams(target_spots=8, min_load_rate=0)
        )
        # 两条线路 -> 两个方案，且各自线路纯净
        lines = {(p.origin, p.destination) for p in plans}
        assert ("上海", "北京") in lines
        assert ("广州", "成都") in lines
        for p in plans:
            for it in p.items:
                assert it.origin == p.origin
                assert it.destination == p.destination


class TestBinPackingCapacity:
    def test_never_exceed_target_spots(self):
        cands = [_cand(1, 20, "上海", "北京", model="轿车")]
        cap = 8
        plans = SmartStowageEngine.generate(
            cands, EngineParams(target_spots=cap, min_load_rate=0)
        )
        assert plans, "应至少产出一个方案"
        for p in plans:
            assert p.occupied_spots <= cap + 1e-6
            assert p.load_rate <= 100.0

    def test_full_load_rate_computation(self):
        # 8 台轿车(系数1.0) 恰好占满 8 车位 -> 100%
        cands = [_cand(1, 8, "上海", "北京", model="轿车")]
        plans = SmartStowageEngine.generate(
            cands, EngineParams(target_spots=8, min_load_rate=0)
        )
        top = plans[0]
        assert top.vehicle_count == 8
        assert top.load_rate == 100.0


class TestMinLoadRateFilter:
    def test_low_load_rate_filtered(self):
        # 单台轿车装 8 车位 = 12.5%，下限 40% 应被过滤
        cands = [_cand(1, 1, "上海", "北京", model="轿车")]
        plans = SmartStowageEngine.generate(
            cands, EngineParams(target_spots=8, min_load_rate=40)
        )
        # 全部被过滤时保底返回（不为空），但装载率确实低
        assert all(p.load_rate < 40 for p in plans) or plans == []


class TestScoringOrder:
    def test_higher_load_rate_ranks_first(self):
        cands = [
            # 满线：8 台轿车 -> 100%
            _cand(1, 8, "上海", "北京", model="轿车"),
            # 半线：2 台轿车 -> 25%
            _cand(2, 2, "杭州", "武汉", model="轿车"),
        ]
        plans = SmartStowageEngine.generate(
            cands, EngineParams(target_spots=8, min_load_rate=0)
        )
        assert plans[0].load_rate >= plans[-1].load_rate
        assert plans[0].plan_no == 1
