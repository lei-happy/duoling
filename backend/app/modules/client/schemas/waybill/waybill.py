"""
运单 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class WaybillCreate(BaseModel):
    waybillNo: Optional[str] = None
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    origin: Optional[str] = None
    originCode: Optional[str] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: Optional[int] = 1
    planIssueTime: Optional[datetime] = None
    requiredLoadTime: Optional[datetime] = None
    requiredDeliverTime: Optional[datetime] = None
    dealerName: Optional[str] = None
    dealerContact: Optional[str] = None
    dealerPhone: Optional[str] = None
    dealerAddress: Optional[str] = None
    freightAmount: Optional[float] = None
    remark: Optional[str] = None


class WaybillUpdate(BaseModel):
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    origin: Optional[str] = None
    originCode: Optional[str] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: Optional[int] = None
    planIssueTime: Optional[datetime] = None
    requiredLoadTime: Optional[datetime] = None
    requiredDeliverTime: Optional[datetime] = None
    dealerName: Optional[str] = None
    dealerContact: Optional[str] = None
    dealerPhone: Optional[str] = None
    dealerAddress: Optional[str] = None
    freightAmount: Optional[float] = None
    remark: Optional[str] = None


class WaybillStatusUpdate(BaseModel):
    status: int


class WaybillOut(BaseModel):
    id: int
    waybillNo: str
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    origin: Optional[str] = None
    originCode: Optional[str] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int
    planIssueTime: Optional[datetime] = None
    requiredLoadTime: Optional[datetime] = None
    requiredDeliverTime: Optional[datetime] = None
    dealerName: Optional[str] = None
    dealerContact: Optional[str] = None
    dealerPhone: Optional[str] = None
    dealerAddress: Optional[str] = None
    freightAmount: Optional[float] = None
    freightSource: Optional[int] = None
    contractId: Optional[int] = None
    rateId: Optional[int] = None
    status: int
    remark: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "WaybillOut":
        return cls(
            id=m.id,
            waybillNo=m.waybill_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            origin=m.origin,
            originCode=m.origin_code,
            destination=m.destination,
            destinationCode=m.destination_code,
            vehicleBrand=m.vehicle_brand,
            vehicleModel=m.vehicle_model,
            quantity=m.quantity,
            planIssueTime=m.plan_issue_time,
            requiredLoadTime=m.required_load_time,
            requiredDeliverTime=m.required_deliver_time,
            dealerName=m.dealer_name,
            dealerContact=m.dealer_contact,
            dealerPhone=m.dealer_phone,
            dealerAddress=m.dealer_address,
            freightAmount=float(m.freight_amount) if m.freight_amount is not None else None,
            freightSource=m.freight_source,
            contractId=m.contract_id,
            rateId=m.rate_id,
            status=m.status,
            remark=m.remark,
            createdBy=m.created_by,
            createdAt=m.created_at,
        )
