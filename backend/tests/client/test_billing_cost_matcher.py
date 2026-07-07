"""计费引擎 · 成本匹配算法辅助函数（纯逻辑，零 DB）测试

覆盖成本引擎的两个纯算法辅助：
  - ``CostMatcher._round``：舍入模式 0-分/1-四舍五入到元/2-向上取整
  - ``CostMatcher._tiered_amount``：阶梯累进计价

对应需求：项目文档/02.需求文档/02.企业端/05.计费引擎模块/成本引擎.md
对应代码：backend/app/modules/client/services/billing/cost_matcher.py
覆盖用例：TC-CLI-BILLING-071 ~ TC-CLI-BILLING-085
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.modules.client.services.billing.cost_matcher import CostMatcher


class TestRound:
    def test_default_two_decimals(self):
        assert CostMatcher._round(Decimal("10.005"), 0) == Decimal("10.01")
        assert CostMatcher._round(Decimal("10.004"), 0) == Decimal("10.00")

    def test_round_half_up_to_yuan(self):
        assert CostMatcher._round(Decimal("10.5"), 1) == Decimal("11")
        assert CostMatcher._round(Decimal("10.4"), 1) == Decimal("10")

    def test_ceiling_to_yuan(self):
        assert CostMatcher._round(Decimal("10.01"), 2) == Decimal("11")
        assert CostMatcher._round(Decimal("10.00"), 2) == Decimal("10")


class TestTieredAmount:
    def test_empty_tiers_is_zero(self):
        assert CostMatcher._tiered_amount(None, Decimal("10")) == Decimal("0")
        assert CostMatcher._tiered_amount([], Decimal("10")) == Decimal("0")

    def test_single_open_tier(self):
        tiers = [{"upTo": None, "unitPrice": 5}]
        assert CostMatcher._tiered_amount(tiers, Decimal("10")) == Decimal("50")

    def test_progressive_two_tiers(self):
        # 前 100 台 @5，超出 @4；120 台 = 100*5 + 20*4 = 580
        tiers = [{"upTo": 100, "unitPrice": 5}, {"upTo": None, "unitPrice": 4}]
        assert CostMatcher._tiered_amount(tiers, Decimal("120")) == Decimal("580")

    def test_within_first_tier(self):
        tiers = [{"upTo": 100, "unitPrice": 5}, {"upTo": None, "unitPrice": 4}]
        assert CostMatcher._tiered_amount(tiers, Decimal("30")) == Decimal("150")

    def test_exact_boundary(self):
        tiers = [{"upTo": 100, "unitPrice": 5}, {"upTo": None, "unitPrice": 4}]
        assert CostMatcher._tiered_amount(tiers, Decimal("100")) == Decimal("500")
