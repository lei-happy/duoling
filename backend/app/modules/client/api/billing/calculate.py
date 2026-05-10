"""
企业端运费计算 API
"""

from typing import Optional
from datetime import date

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_tenant_db, get_current_user
from app.common.response import success
from app.modules.client.services.billing.billing_engine_service import BillingEngineService

router = APIRouter()


class FreightCalcRequest(BaseModel):
    customerId: int
    originCode: str
    destinationCode: str
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int = 1
    billingDate: Optional[date] = None


@router.post("")
async def calculate_freight(
    data: FreightCalcRequest,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    result = await BillingEngineService.calculate_freight(
        db,
        customer_id=data.customerId,
        origin_code=data.originCode,
        destination_code=data.destinationCode,
        vehicle_brand=data.vehicleBrand,
        vehicle_model=data.vehicleModel,
        quantity=data.quantity or 1,
        billing_date=data.billingDate,
    )
    if result:
        return success(data=result.model_dump())
    return success(data=None)
