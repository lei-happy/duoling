"""
驾驶员资质信息 Schemas
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class DriverLicenseOut(BaseModel):
    """资质信息响应"""
    id: int
    driverId: int
    licenseType: Optional[str] = None
    licenseNo: Optional[str] = None
    licenseExpire: Optional[date] = None
    qualificationNo: Optional[str] = None
    qualificationExpire: Optional[date] = None
    licensePhoto: Optional[str] = None
    qualificationPhoto: Optional[str] = None
    idCardFrontPhoto: Optional[str] = None
    idCardBackPhoto: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "DriverLicenseOut":
        return cls(
            id=m.id,
            driverId=m.driver_id,
            licenseType=m.license_type,
            licenseNo=m.license_no,
            licenseExpire=m.license_expire,
            qualificationNo=m.qualification_no,
            qualificationExpire=m.qualification_expire,
            licensePhoto=m.license_photo,
            qualificationPhoto=m.qualification_photo,
            idCardFrontPhoto=m.id_card_front_photo,
            idCardBackPhoto=m.id_card_back_photo,
            createdAt=m.created_at,
        )
