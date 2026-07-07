"""驾驶员财务服务测试（只读，硬过滤 payee_id）

分两层：
1. 纯逻辑：``_to_float`` 空值容错；
2. 集成：连租户库 ``1001``，新建司机在无任何费用单时列表/汇总应为空/零，
   越权访问不存在的费用单被拒；资金账户懒加载余额为 0。

对应需求：项目文档/02.需求文档/03.移动端/02.驾驶员H5端/03.财务与收入查询.md
覆盖用例：TC-DRV-FIN-001/002/003/004/005/006
"""

from decimal import Decimal

import pytest

from app.common.exceptions import BizException
from app.modules.driver.services.driver_finance_service import (
    DriverFinanceService,
    _to_float,
)


# =====================================================================
# 1) 纯逻辑：_to_float
# =====================================================================
class TestToFloat:
    def test_none_is_zero(self):
        assert _to_float(None) == 0.0

    def test_decimal_cast(self):
        assert _to_float(Decimal("12.34")) == pytest.approx(12.34)


# =====================================================================
# 2) 集成（真实租户库，事务回滚）
# =====================================================================
class TestFinanceIntegration:
    async def test_list_docs_empty(self, driver_ctx):
        session, ctx = driver_ctx
        items, total = await DriverFinanceService.list_my_docs(session, ctx)
        assert total == 0
        assert items == []

    async def test_summary_zero(self, driver_ctx):
        session, ctx = driver_ctx
        summary = await DriverFinanceService.summary(session, ctx)
        assert summary.totalIncome == 0
        assert summary.prepaidAmount == 0
        assert summary.settledAmount == 0
        assert summary.byMonth == []

    async def test_invalid_year_month_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        with pytest.raises(BizException):
            await DriverFinanceService.list_my_docs(
                session, ctx, year_month="2026/07"
            )

    async def test_get_unknown_doc_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        with pytest.raises(BizException):
            await DriverFinanceService.get_doc(session, ctx, 999_000_111)

    async def test_list_accounts_empty(self, driver_ctx):
        session, ctx = driver_ctx
        accounts = await DriverFinanceService.list_my_accounts(session, ctx)
        assert accounts == []

    async def test_fund_account_lazy_zero(self, driver_ctx):
        session, ctx = driver_ctx
        acc = await DriverFinanceService.get_my_fund_account(session, ctx)
        assert Decimal(str(acc["balance"])) == Decimal("0.00")
