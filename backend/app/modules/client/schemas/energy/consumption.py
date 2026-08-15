from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel


class EnergyConsumptionCreate(BaseModel):
    accountId: Optional[int] = None
    cardId: Optional[int] = None
    cardNo: Optional[str] = None
    supplierId: Optional[int] = None
    stationId: Optional[int] = None
    stationName: Optional[str] = None
    vehicleId: Optional[int] = None
    plateNumber: Optional[str] = None
    driverId: Optional[int] = None
    energyType: str = "OIL"
    energyProductId: Optional[int] = None
    productName: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    unitPrice: Optional[Decimal] = None
    amount: Decimal
    mileage: Optional[Decimal] = None
    odometer: Optional[Decimal] = None
    consumptionTime: datetime
    sourceChannel: int = 3
    isLedgerAffecting: int = 1
    remark: Optional[str] = None


class EnergyConsumptionOut(BaseModel):
    id: int
    consumptionNo: str
    supplierId: Optional[int] = None
    stationName: Optional[str] = None
    accountId: Optional[int] = None
    cardNo: Optional[str] = None
    plateNumber: Optional[str] = None
    driverName: Optional[str] = None
    taskId: Optional[int] = None
    energyType: str
    productName: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    unitPrice: Optional[Decimal] = None
    amount: Decimal
    mileage: Optional[Decimal] = None
    consumptionTime: datetime
    sourceChannel: int
    isLedgerAffecting: int
    matchStatus: str
    reconStatus: Optional[str] = None
    exceptionStatus: Optional[str] = None
    remark: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "EnergyConsumptionOut":
        return cls(
            id=m.id,
            consumptionNo=m.consumption_no,
            supplierId=m.supplier_id,
            stationName=m.station_name,
            accountId=m.account_id,
            cardNo=m.card_no,
            plateNumber=m.plate_number,
            driverName=m.driver_name,
            taskId=m.task_id,
            energyType=m.energy_type,
            productName=m.product_name,
            quantity=m.quantity,
            unit=m.unit,
            unitPrice=m.unit_price,
            amount=m.amount,
            mileage=m.mileage,
            consumptionTime=m.consumption_time,
            sourceChannel=m.source_channel,
            isLedgerAffecting=m.is_ledger_affecting,
            matchStatus=m.match_status,
            reconStatus=m.recon_status,
            exceptionStatus=m.exception_status,
            remark=m.remark,
        )


class EnergyConsumptionAssignIn(BaseModel):
    vehicleId: Optional[int] = None
    driverId: Optional[int] = None
    taskId: Optional[int] = None
    accountId: Optional[int] = None
    cardId: Optional[int] = None
