"""
司机管理 Schemas
"""

from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel


class DriverCreate(BaseModel):
    userId: Optional[int] = None
    name: str
    phone: str
    idCard: Optional[str] = None
    gender: Optional[int] = None
    licenseType: Optional[str] = None
    licenseNo: Optional[str] = None
    licenseExpire: Optional[date] = None
    qualificationNo: Optional[str] = None
    qualificationExpire: Optional[date] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    avatar: Optional[str] = None
    remark: Optional[str] = None


class DriverUpdate(BaseModel):
    userId: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    idCard: Optional[str] = None
    gender: Optional[int] = None
    licenseType: Optional[str] = None
    licenseNo: Optional[str] = None
    licenseExpire: Optional[date] = None
    qualificationNo: Optional[str] = None
    qualificationExpire: Optional[date] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    avatar: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class DriverOut(BaseModel):
    id: int
    userId: Optional[int] = None
    name: str
    phone: str
    idCard: Optional[str] = None
    gender: Optional[int] = None
    licenseType: Optional[str] = None
    licenseNo: Optional[str] = None
    licenseExpire: Optional[date] = None
    qualificationNo: Optional[str] = None
    qualificationExpire: Optional[date] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    avatar: Optional[str] = None
    status: int
    remark: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "DriverOut":
        return cls(
            id=m.id,
            userId=m.user_id,
            name=m.name,
            phone=m.phone,
            idCard=m.id_card,
            gender=m.gender,
            licenseType=m.license_type,
            licenseNo=m.license_no,
            licenseExpire=m.license_expire,
            qualificationNo=m.qualification_no,
            qualificationExpire=m.qualification_expire,
            emergencyContact=m.emergency_contact,
            emergencyPhone=m.emergency_phone,
            avatar=m.avatar,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
        )
