"""
Console 平台车系 Schemas
"""

from decimal import Decimal
from typing import Optional, Union

from pydantic import BaseModel, ConfigDict


class VehicleSeriesCreate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    brandId: int
    price: Optional[str] = None
    seriesImage: Optional[str] = None
    seriesName: str
    energyType: Optional[str] = None
    lengthMm: Optional[int] = None
    widthMm: Optional[int] = None
    heightMm: Optional[int] = None
    wheelbaseMm: Optional[int] = None
    frontTrackMm: Optional[int] = None
    rearTrackMm: Optional[int] = None
    approachAngle: Optional[Union[Decimal, float]] = None
    departureAngle: Optional[Union[Decimal, float]] = None
    curbWeightKg: Optional[int] = None


class VehicleSeriesUpdate(BaseModel):
    model_config = ConfigDict(extra="ignore")

    price: Optional[str] = None
    seriesImage: Optional[str] = None
    seriesName: Optional[str] = None
    energyType: Optional[str] = None
    lengthMm: Optional[int] = None
    widthMm: Optional[int] = None
    heightMm: Optional[int] = None
    wheelbaseMm: Optional[int] = None
    frontTrackMm: Optional[int] = None
    rearTrackMm: Optional[int] = None
    approachAngle: Optional[Union[Decimal, float]] = None
    departureAngle: Optional[Union[Decimal, float]] = None
    curbWeightKg: Optional[int] = None


class VehicleSeriesOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    seriesId: int
    brandId: int
    price: Optional[str] = None
    seriesImage: Optional[str] = None
    seriesName: str
    energyType: Optional[str] = None
    lengthMm: Optional[int] = None
    widthMm: Optional[int] = None
    heightMm: Optional[int] = None
    wheelbaseMm: Optional[int] = None
    frontTrackMm: Optional[int] = None
    rearTrackMm: Optional[int] = None
    approachAngle: Optional[float] = None
    departureAngle: Optional[float] = None
    curbWeightKg: Optional[int] = None
    createTime: Optional[str] = None
    lastUpdateTime: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "VehicleSeriesOut":
        return cls(
            seriesId=m.series_id,
            brandId=m.brand_id,
            price=m.price,
            seriesImage=m.series_image,
            seriesName=m.series_name,
            energyType=m.energy_type,
            lengthMm=m.length_mm,
            widthMm=m.width_mm,
            heightMm=m.height_mm,
            wheelbaseMm=m.wheelbase_mm,
            frontTrackMm=m.front_track_mm,
            rearTrackMm=m.rear_track_mm,
            approachAngle=float(m.approach_angle) if m.approach_angle is not None else None,
            departureAngle=float(m.departure_angle) if m.departure_angle is not None else None,
            curbWeightKg=m.curb_weight_kg,
            createTime=m.create_time.isoformat(sep=" ", timespec="seconds")
            if m.create_time
            else None,
            lastUpdateTime=m.last_update_time.isoformat(sep=" ", timespec="seconds")
            if m.last_update_time
            else None,
        )
