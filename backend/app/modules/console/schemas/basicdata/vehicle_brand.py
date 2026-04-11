"""
Console 平台品牌 Schemas（字段名对齐前端 camelCase）
"""

from app.common.schemas.vehicle_brand import (
    VehicleBrandCreateBase as VehicleBrandCreate,
    VehicleBrandUpdateBase as VehicleBrandUpdate,
    VehicleBrandOutBase as VehicleBrandOut,
)

__all__ = ["VehicleBrandCreate", "VehicleBrandUpdate", "VehicleBrandOut"]
