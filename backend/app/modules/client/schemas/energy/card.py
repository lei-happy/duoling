from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EnergyCardCreate(BaseModel):
    accountId: int
    cardNo: str
    externalCardId: Optional[str] = None
    cardType: Optional[str] = None
    energyType: Optional[str] = None
    remark: Optional[str] = None


class EnergyCardUpdate(BaseModel):
    cardType: Optional[str] = None
    energyType: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class EnergyCardOut(BaseModel):
    id: int
    accountId: int
    accountName: Optional[str] = None
    cardNo: str
    externalCardId: Optional[str] = None
    cardType: Optional[str] = None
    energyType: Optional[str] = None
    status: int
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    remark: Optional[str] = None
    vehicleId: Optional[int] = None
    driverId: Optional[int] = None
    createdAt: datetime

    @classmethod
    def from_model(cls, m, *, account_name: Optional[str] = None,
                   vehicle_id: Optional[int] = None,
                   driver_id: Optional[int] = None) -> "EnergyCardOut":
        return cls(
            id=m.id,
            accountId=m.account_id,
            accountName=account_name,
            cardNo=m.card_no,
            externalCardId=m.external_card_id,
            cardType=m.card_type,
            energyType=m.energy_type,
            status=m.status,
            validFrom=m.valid_from,
            validTo=m.valid_to,
            remark=m.remark,
            vehicleId=vehicle_id,
            driverId=driver_id,
            createdAt=m.created_at,
        )


class EnergyCardBindIn(BaseModel):
    vehicleId: Optional[int] = None
    driverId: Optional[int] = None
    startTime: Optional[datetime] = None
