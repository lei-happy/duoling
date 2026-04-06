"""
租户端品牌 Schemas（字段名对齐前端 camelCase）
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class VehicleBrandCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    brandLogo: Optional[str] = None
    brandNameCn: str
    brandCountry: Optional[str] = None
    brandIntroduce: Optional[str] = None


class VehicleBrandUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    brandLogo: Optional[str] = None
    brandNameCn: Optional[str] = None
    brandCountry: Optional[str] = None
    brandIntroduce: Optional[str] = None


class VehicleBrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    brandId: int
    brandLogo: Optional[str] = None
    brandNameCn: str
    brandCountry: Optional[str] = None
    brandIntroduce: Optional[str] = None
    createTime: Optional[str] = None
    lastUpdateTime: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "VehicleBrandOut":
        return cls(
            brandId=m.brand_id,
            brandLogo=m.brand_logo,
            brandNameCn=m.brand_name_cn,
            brandCountry=m.brand_country,
            brandIntroduce=m.brand_introduce,
            createTime=m.create_time.isoformat(sep=" ", timespec="seconds")
            if m.create_time
            else None,
            lastUpdateTime=m.last_update_time.isoformat(sep=" ", timespec="seconds")
            if m.last_update_time
            else None,
        )
