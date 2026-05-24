"""驾驶员个人资料 Schemas"""

from typing import Optional

from pydantic import BaseModel, Field


class DriverProfileOut(BaseModel):
    """驾驶员个人资料"""

    id: int
    driverCode: str
    name: str
    phone: str
    gender: Optional[int] = 0
    avatar: Optional[str] = None
    idCard: Optional[str] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    homeAddress: Optional[str] = None
    status: int = 1
    remark: Optional[str] = None


class DriverProfileUpdate(BaseModel):
    """驾驶员可自助修改的字段（受限白名单）"""

    emergencyContact: Optional[str] = Field(default=None, max_length=50)
    emergencyPhone: Optional[str] = Field(default=None, max_length=20)
    homeAddress: Optional[str] = Field(default=None, max_length=255)
    avatar: Optional[str] = Field(default=None, max_length=255)
