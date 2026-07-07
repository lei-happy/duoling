"""
成本-财务对接适配层

把成本引擎的任务成本明细提供给财务侧（司机工资单 / 任务级结算单 / 承运商对账），
仅做取数与映射，不代替财务单据流程（弱联动、可解释）。
"""

from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.task_cost_result import (
    TaskCostResult,
    TaskCostResultItem,
)
from app.modules.client.services.billing.cost_constants import (
    PM_PER_TON_KM,
    PM_PER_TRIP,
    PM_PER_VEHICLE,
)


# billing_base 映射（供工资单任务提成行）
def _billing_base_of(pricing_method: str) -> str:
    if pricing_method == PM_PER_VEHICLE:
        return "vehicle"
    if pricing_method == PM_PER_TON_KM:
        return "ton"
    if pricing_method == PM_PER_TRIP:
        return "trip"
    return "amount"


class CostFinanceAdapter:

    @staticmethod
    async def get_active_result(
        db: AsyncSession, task_id: int
    ) -> Optional[TaskCostResult]:
        r = await db.execute(
            select(TaskCostResult).where(
                TaskCostResult.task_id == task_id,
                TaskCostResult.is_active == 1,
                TaskCostResult.is_deleted == 0,
            ).order_by(TaskCostResult.id.desc()).limit(1)
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def get_result_items(
        db: AsyncSession, result_id: int
    ) -> list[TaskCostResultItem]:
        r = await db.execute(
            select(TaskCostResultItem).where(
                TaskCostResultItem.result_id == result_id,
                TaskCostResultItem.is_deleted == 0,
                TaskCostResultItem.calc_status == "success",
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def get_driver_commission(
        db: AsyncSession, task_id: int
    ) -> Optional[dict]:
        """司机工资单任务提成行取数：fee_type='driver_freight' 明细。"""
        result = await CostFinanceAdapter.get_active_result(db, task_id)
        if not result:
            return None
        items = await CostFinanceAdapter.get_result_items(db, result.id)
        driver_item = next(
            (it for it in items if it.fee_type == "driver_freight"), None
        )
        if not driver_item:
            return None
        return {
            "taskId": task_id,
            "unitPrice": float(driver_item.unit_price) if driver_item.unit_price is not None else None,
            "quantity": float(driver_item.quantity) if driver_item.quantity is not None else None,
            "commissionAmount": float(driver_item.amount),
            "billingBase": _billing_base_of(driver_item.pricing_method),
            "matchedRuleId": driver_item.matched_rule_id,
        }

    @staticmethod
    async def get_task_cost_items(
        db: AsyncSession, task_id: int
    ) -> list[dict]:
        """任务级结算单 / 承运商对账取数：逐项费用明细。"""
        result = await CostFinanceAdapter.get_active_result(db, task_id)
        if not result:
            return []
        items = await CostFinanceAdapter.get_result_items(db, result.id)
        out = []
        for it in items:
            out.append({
                "feeType": it.fee_type,
                "feeName": it.fee_name,
                "direction": it.direction,
                "payeeType": it.payee_type,
                "pricingMethod": it.pricing_method,
                "amount": float(it.amount),
            })
        return out

    @staticmethod
    async def get_total_cost(db: AsyncSession, task_id: int) -> Decimal:
        result = await CostFinanceAdapter.get_active_result(db, task_id)
        return result.total_cost_amount if result else Decimal("0")
