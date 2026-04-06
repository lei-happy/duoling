"""
Console 平台经销商 Schemas
"""

from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict


class DealerCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    dealerName: str
    dealerType: str
    mainBrand: str
    province: str
    city: str
    addressDetail: str
    longitude: Optional[Union[Decimal, float]] = None
    latitude: Optional[Union[Decimal, float]] = None


class DealerUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    dealerName: Optional[str] = None
    dealerType: Optional[str] = None
    mainBrand: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    addressDetail: Optional[str] = None
    longitude: Optional[Union[Decimal, float]] = None
    latitude: Optional[Union[Decimal, float]] = None


class DealerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    dealerId: int
    dealerName: str
    dealerType: str
    mainBrand: str
    province: str
    city: str
    addressDetail: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "DealerOut":
        return cls(
            dealerId=int(m.dealer_id),
            dealerName=m.dealer_name,
            dealerType=m.dealer_type,
            mainBrand=m.main_brand,
            province=m.province,
            city=m.city,
            addressDetail=m.address_detail,
            longitude=float(m.longitude) if m.longitude is not None else None,
            latitude=float(m.latitude) if m.latitude is not None else None,
            createdAt=m.created_at.isoformat(sep=" ", timespec="seconds")
            if m.created_at
            else None,
            updatedAt=m.updated_at.isoformat(sep=" ", timespec="seconds")
            if m.updated_at
            else None,
        )
