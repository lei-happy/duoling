"""工作台与洞察 · 利润总览（经营驾驶舱）测试

两层：
  1. 纯逻辑：毛利率 / 环比 / 归一化辅助函数
  2. 集成冒烟：真实租户库上跑 KPI / 趋势 / 承运结构 / 成本构成 / 客户排行
     聚合 SQL（事务回滚不落库），校验可执行且返回结构正确（不校验具体数值）。

对应需求：项目文档/02.需求文档/02.企业端/10.数据洞察/利润总览.md
对应接口：/api/client/insight/cockpit/profit/**
对应代码：backend/app/modules/client/services/insight/profit_service.py
覆盖用例：TC-CLI-PROFIT-001 ~ TC-CLI-PROFIT-020
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest

from app.modules.client.services.insight.profit_service import (
    ProfitService,
    _coerce_dt,
    _safe_growth_rate,
    _safe_margin,
    _to_float,
)


# =====================================================================
# 1) 纯逻辑辅助
# =====================================================================
class TestProfitHelpers:
    def test_to_float(self):
        assert _to_float(None) == 0.0
        assert _to_float(Decimal("12.34")) == 12.34
        assert _to_float(5) == 5.0

    def test_safe_margin(self):
        assert _safe_margin(100.0, 60.0) == pytest.approx(0.4)
        assert _safe_margin(0.0, 10.0) is None  # 收入为 0 → None

    def test_safe_growth_rate(self):
        assert _safe_growth_rate(120.0, 100.0) == pytest.approx(0.2)
        assert _safe_growth_rate(10.0, 0.0) is None  # 上期为 0 → None

    def test_coerce_dt_from_date(self):
        d = date(2026, 7, 7)
        assert _coerce_dt(d) == datetime(2026, 7, 7, 0, 0, 0)

    def test_coerce_dt_passthrough(self):
        dt = datetime(2026, 7, 7, 8, 30)
        assert _coerce_dt(dt) is dt

    def test_coerce_dt_type_error(self):
        with pytest.raises(TypeError):
            _coerce_dt("2026-07-07")

    def test_week_monday_start(self):
        # 2026-07-07 是周二，周一应为 07-06
        wm = ProfitService._week_monday_start(date(2026, 7, 7))
        assert wm == datetime(2026, 7, 6, 0, 0, 0)


# =====================================================================
# 2) 集成冒烟（真实 SQL 可执行，结构正确）
# =====================================================================
class TestProfitAggregationSmoke:
    async def test_kpi_summary_shape(self, tenant_session):
        now = datetime.now()
        res = await ProfitService.kpi_summary(
            tenant_session, now - timedelta(days=30), now
        )
        assert {"revenue", "cost", "grossProfit", "grossMargin",
                "costCoverageRate"} <= set(res)
        assert "todayValue" in res["revenue"]
        assert isinstance(res["revenue"]["trend30d"], list)
        assert len(res["revenue"]["trend30d"]) == 30

    async def test_trend_runs(self, tenant_session):
        now = datetime.now()
        rows = await ProfitService.trend(
            tenant_session, now - timedelta(days=7), now, granularity="day"
        )
        assert isinstance(rows, list)
        for r in rows:
            assert {"date", "revenue", "cost", "grossProfit", "grossMargin"} <= set(r)

    async def test_carrier_structure_runs(self, tenant_session):
        now = datetime.now()
        rows = await ProfitService.carrier_structure(
            tenant_session, now - timedelta(days=30), now
        )
        assert isinstance(rows, list)
        for r in rows:
            assert {"carrierType", "label", "revenue", "cost"} <= set(r)

    async def test_cost_structure_runs(self, tenant_session):
        now = datetime.now()
        rows = await ProfitService.cost_structure(
            tenant_session, now - timedelta(days=30), now
        )
        assert isinstance(rows, list)

    async def test_customer_rank_runs(self, tenant_session):
        now = datetime.now()
        rows = await ProfitService.customer_rank(
            tenant_session, now - timedelta(days=30), now, limit=5, sort_by="profit"
        )
        assert isinstance(rows, list)
        assert len(rows) <= 5
