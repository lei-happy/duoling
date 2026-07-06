"""驾驶员资金账户联动编排器

任务级费用单支付 / 撤销支付时，联动写入驾驶员资金账户流水：

- 预付单（``doc_type=1`` 且 ``payee_type=1`` 司机）已支付
  → 自动写「预付登记」流水（``delta<0``，司机占用公司预付资金）；
- 撤销该预付单支付（撤销支付 / 强制撤销）
  → 自动写「冲正」流水（``delta>0``）。

结算单 / 补款单为即时对价（收付相抵），不改往来账，留给财务或下次任务手工核销，
避免与实际现金流重复计账。所有写入幂等（按 ``related_finance_doc_id`` 去重）。
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.services.capacity.self_capacity.driver.driver_fund_account_service import (
    DriverFundAccountService,
)
from app.modules.client.services.finance.base.constants import DocType, PayeeType


class DriverFundOrchestrator:
    """费用单 ↔ 驾驶员资金账户 联动"""

    @staticmethod
    def _is_driver_prepay(doc) -> bool:
        return (
            int(getattr(doc, "doc_type", 0) or 0) == DocType.PREPAY
            and int(getattr(doc, "payee_type", 0) or 0) == PayeeType.DRIVER
            and getattr(doc, "payee_id", None) is not None
        )

    @staticmethod
    async def on_finance_doc_paid(
        db: AsyncSession,
        doc,
        operator_id: Optional[int] = None,
    ) -> None:
        """费用单支付成功后回调。仅司机预付单触发预付登记。"""
        if not DriverFundOrchestrator._is_driver_prepay(doc):
            return
        amount = getattr(doc, "actual_amount", None)
        if amount is None:
            return
        await DriverFundAccountService.system_register_prepay(
            db,
            driver_id=int(doc.payee_id),
            amount=Decimal(str(amount)),
            # 经营主体：费用单继承任务归属，账户按 (driver_id, enterprise_id) 记账；
            # 为空时由账户服务归一到租户默认主体。
            enterprise_id=int(getattr(doc, "enterprise_id", 0)) or None,
            task_id=int(getattr(doc, "task_id", 0)) or None,
            finance_doc_id=int(doc.id),
            operator_id=operator_id,
            doc_no=getattr(doc, "doc_no", None),
        )

    @staticmethod
    async def on_finance_doc_payment_reversed(
        db: AsyncSession,
        doc,
        operator_id: Optional[int] = None,
    ) -> None:
        """撤销支付 / 强制撤销后回调。冲正之前的预付登记。"""
        if not DriverFundOrchestrator._is_driver_prepay(doc):
            return
        await DriverFundAccountService.system_reverse_prepay(
            db,
            finance_doc_id=int(doc.id),
            operator_id=operator_id,
            doc_no=getattr(doc, "doc_no", None),
        )
