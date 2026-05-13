"""
计费引擎服务（对外门面）

历史上 BillingEngineService 提供按 (customer_id + 出发/目的地编码 + 品牌+车型 + 数量)
的硬过滤计算入口；本次升级保留该入口供试算/AI 工具继续使用，但底层全部
替换为新的 FreightCalcService + FreightMatcher（综合评分 + 留痕）。

核心入口：
  - calculate_freight   : 单条货物试算（保持旧签名，用于 /billing/calculate）
  - preview_for_waybill : 整单试算（试算模式 dry_run，用于编辑表单批量试算）
  - calculate_and_persist: 正式计算（写 result，刷新 waybill）
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.services.billing.freight_calc_service import (
    FreightCalcService,
    WaybillCalcSummary,
)


class FreightResult(BaseModel):
    """与旧 schema 兼容的单条计算结果（供前端 /billing/calculate 沿用）"""

    unitPrice: Decimal
    billingMode: int = 0
    distanceKm: Optional[Decimal] = None
    totalAmount: Decimal
    contractId: int
    contractNo: str
    rateId: int
    matchLevel: str
    priceType: int = 0


class BillingEngineService:

    @staticmethod
    async def calculate_freight(
        db: AsyncSession,
        customer_id: int,
        origin_code: str,
        destination_code: str,
        vehicle_brand: Optional[str] = None,
        vehicle_model: Optional[str] = None,
        quantity: int = 1,
        billing_date: Optional[date] = None,
    ) -> Optional[FreightResult]:
        """单条货物的试算入口（旧 API 兼容）

        组装一个临时 Waybill + WaybillCargo 调用新引擎，返回首条命中明细。
        """
        if billing_date is None:
            billing_date = date.today()

        # 临时对象（不持久化）
        waybill = Waybill(
            id=0,
            waybill_no="__preview__",
            customer_id=customer_id,
            origin_code=origin_code,
            destination_code=destination_code,
            origin=None,
            destination=None,
        )
        cargo = WaybillCargo(
            id=0,
            waybill_id=0,
            sort_order=0,
            vehicle_brand=vehicle_brand,
            vehicle_model=vehicle_model,
            quantity=max(int(quantity or 1), 1),
        )

        summary: WaybillCalcSummary = await FreightCalcService.preview_for_waybill(
            db, waybill, [cargo], billing_date,
        )

        first = next(
            (r for r in summary.cargo_results if r.calc_status == "success"),
            None,
        )
        if not first or not first.matched_rule or not first.matched_contract:
            return None

        return FreightResult(
            unitPrice=first.matched_rule.unit_price,
            billingMode=first.matched_rule.billing_mode,
            distanceKm=first.matched_rule.distance_km,
            totalAmount=first.amount,
            contractId=first.matched_contract.id,
            contractNo=first.matched_contract.contract_no,
            rateId=first.matched_rule.id,
            matchLevel=first.model_match_type or "general",
            priceType=first.matched_rule.price_type,
        )
