"""
运单服务（租户库）
"""

import random
from typing import Optional
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.schemas.waybill.waybill import (
    WaybillCreate, WaybillUpdate, WaybillStatusUpdate, WaybillOut,
)
from app.modules.client.services.system_config_service import SystemConfigService
from app.modules.client.services.billing.billing_engine_service import BillingEngineService


class WaybillService:

    @staticmethod
    def _generate_waybill_no() -> str:
        now = datetime.now()
        return f"YD{now.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

    @staticmethod
    async def page_waybills(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        status: Optional[int] = None,
        freight_source: Optional[int] = None,
    ) -> dict:
        base = select(Waybill).where(Waybill.is_deleted == 0)

        if keyword:
            base = base.where(
                (Waybill.waybill_no.contains(keyword)) |
                (Waybill.customer_name.contains(keyword)) |
                (Waybill.dealer_name.contains(keyword))
            )
        if customer_id is not None:
            base = base.where(Waybill.customer_id == customer_id)
        if status is not None:
            base = base.where(Waybill.status == status)
        if freight_source is not None:
            base = base.where(Waybill.freight_source == freight_source)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Waybill.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [WaybillOut.from_model(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_waybill(db: AsyncSession, waybill_id: int) -> Waybill:
        result = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = result.scalar_one_or_none()
        if not waybill:
            raise BizException("运单不存在")
        return waybill

    @staticmethod
    async def create_waybill(
        db: AsyncSession, data: WaybillCreate, current_user_id: int
    ) -> Waybill:
        waybill_no = data.waybillNo or WaybillService._generate_waybill_no()

        freight_amount = None
        freight_source = None
        contract_id = None
        rate_id = None

        calc_mode = await SystemConfigService.get_by_key(db, "waybill.freight_calc_mode")
        if not calc_mode:
            calc_mode = "manual_only"

        if calc_mode in ("auto_required", "auto_preferred"):
            if data.customerId and data.originCode and data.destinationCode:
                calc_result = await BillingEngineService.calculate_freight(
                    db,
                    customer_id=data.customerId,
                    origin_code=data.originCode,
                    destination_code=data.destinationCode,
                    vehicle_brand=data.vehicleBrand,
                    vehicle_model=data.vehicleModel,
                    quantity=data.quantity or 1,
                )
                if calc_result:
                    freight_amount = calc_result.totalAmount
                    freight_source = 0
                    contract_id = calc_result.contractId
                    rate_id = calc_result.rateId
                elif calc_mode == "auto_required":
                    raise BizException("未匹配到运价，无法创建运单")

        if freight_amount is None:
            if data.freightAmount is not None:
                freight_amount = Decimal(str(data.freightAmount))
            freight_source = 1

        waybill = Waybill(
            waybill_no=waybill_no,
            customer_id=data.customerId,
            customer_name=data.customerName,
            origin=data.origin,
            origin_code=data.originCode,
            destination=data.destination,
            destination_code=data.destinationCode,
            vehicle_brand=data.vehicleBrand,
            vehicle_model=data.vehicleModel,
            quantity=data.quantity or 1,
            plan_issue_time=data.planIssueTime,
            required_load_time=data.requiredLoadTime,
            required_deliver_time=data.requiredDeliverTime,
            dealer_name=data.dealerName,
            dealer_contact=data.dealerContact,
            dealer_phone=data.dealerPhone,
            dealer_address=data.dealerAddress,
            freight_amount=freight_amount,
            freight_source=freight_source,
            contract_id=contract_id,
            rate_id=rate_id,
            remark=data.remark,
            status=0,
            created_by=current_user_id,
        )
        db.add(waybill)
        await db.flush()
        await db.refresh(waybill)
        return waybill

    @staticmethod
    async def update_waybill(
        db: AsyncSession, waybill_id: int, data: WaybillUpdate
    ) -> Waybill:
        result = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = result.scalar_one_or_none()
        if not waybill:
            raise BizException("运单不存在")

        field_map = {
            "customerId": "customer_id",
            "customerName": "customer_name",
            "origin": "origin",
            "originCode": "origin_code",
            "destination": "destination",
            "destinationCode": "destination_code",
            "vehicleBrand": "vehicle_brand",
            "vehicleModel": "vehicle_model",
            "quantity": "quantity",
            "planIssueTime": "plan_issue_time",
            "requiredLoadTime": "required_load_time",
            "requiredDeliverTime": "required_deliver_time",
            "dealerName": "dealer_name",
            "dealerContact": "dealer_contact",
            "dealerPhone": "dealer_phone",
            "dealerAddress": "dealer_address",
            "freightAmount": "freight_amount",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(waybill, model_field, val)

        await db.flush()
        await db.refresh(waybill)
        return waybill

    @staticmethod
    async def update_status(
        db: AsyncSession, waybill_id: int, data: WaybillStatusUpdate
    ) -> Waybill:
        result = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = result.scalar_one_or_none()
        if not waybill:
            raise BizException("运单不存在")

        waybill.status = data.status
        await db.flush()
        await db.refresh(waybill)
        return waybill

    @staticmethod
    async def delete_waybill(db: AsyncSession, waybill_id: int) -> None:
        result = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id,
                Waybill.is_deleted == 0,
            )
        )
        waybill = result.scalar_one_or_none()
        if not waybill:
            raise BizException("运单不存在")
        if waybill.status not in (0, 6):
            raise BizException("只有待处理或已取消的运单可以删除")
        waybill.is_deleted = 1
        await db.flush()
