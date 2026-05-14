"""
运单 Schemas
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


def waybill_brand_model_key(brand: Optional[str], model: Optional[str]) -> str:
    """品牌+车型 → 与 biz 车系表匹配用的键（均为 strip 后原文）。"""
    b = (brand or "").strip()
    m = (model or "").strip()
    return f"{b}\x1f{m}"


class WaybillCargoLineIn(BaseModel):
    """货物明细入参（创建/整单替换）"""

    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int = Field(1, ge=1)
    sortOrder: int = Field(0, ge=0)

    @field_validator("vehicleBrand", "vehicleModel", mode="before")
    @classmethod
    def strip_opt(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None


class WaybillCargoOut(BaseModel):
    id: int
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int
    sortOrder: int
    seriesImage: Optional[str] = Field(
        default=None,
        description="车系图（biz_vehicle_series.series_image，与品牌+车型匹配）",
    )

    model_config = {"from_attributes": True}

    @classmethod
    def from_cargo(cls, c, series_image: Optional[str] = None) -> "WaybillCargoOut":
        return cls(
            id=c.id,
            vehicleBrand=c.vehicle_brand,
            vehicleModel=c.vehicle_model,
            quantity=c.quantity,
            sortOrder=c.sort_order,
            seriesImage=series_image,
        )


class WaybillCreate(BaseModel):
    waybillNo: Optional[str] = None
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    origin: Optional[str] = None
    originCode: Optional[str] = None
    originRegionId: Optional[int] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    destinationRegionId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: Optional[int] = 1
    cargoes: list[WaybillCargoLineIn] = Field(default_factory=list)
    planIssueTime: Optional[datetime] = None
    requiredLoadTime: Optional[datetime] = None
    requiredDeliverTime: Optional[datetime] = None
    dealerName: Optional[str] = None
    dealerContact: Optional[str] = None
    dealerPhone: Optional[str] = None
    dealerAddress: Optional[str] = None
    freightAmount: Optional[float] = None
    remark: Optional[str] = None

    @model_validator(mode="after")
    def ensure_cargoes_or_legacy(self):
        if self.cargoes:
            return self
        # 兼容旧客户端：无 cargoes 时用顶层品牌/车型生成一行
        brand = (self.vehicleBrand or "").strip() or None
        model = (self.vehicleModel or "").strip() or None
        qty = self.quantity if self.quantity is not None else 1
        if brand or model or qty:
            self.cargoes = [
                WaybillCargoLineIn(
                    vehicleBrand=brand,
                    vehicleModel=model,
                    quantity=max(1, int(qty)),
                    sortOrder=0,
                )
            ]
        return self


class WaybillUpdate(BaseModel):
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    origin: Optional[str] = None
    originCode: Optional[str] = None
    originRegionId: Optional[int] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    destinationRegionId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: Optional[int] = None
    cargoes: Optional[list[WaybillCargoLineIn]] = None
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


def _cargo_summary_from_lines(cargo_models: list) -> str:
    """用于列表展示的摘要文案"""
    if not cargo_models:
        return ""
    rows = sorted(cargo_models, key=lambda x: (x.sort_order, x.id))
    parts: list[str] = []
    for r in rows:
        brand = (r.vehicle_brand or "").strip()
        model = (r.vehicle_model or "").strip()
        mid = "/".join(x for x in (brand, model) if x) or "—"
        parts.append(f"{mid}×{r.quantity}")
    return "；".join(parts)


class WaybillOut(BaseModel):
    id: int
    waybillNo: str
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    origin: Optional[str] = None
    originCode: Optional[str] = None
    originRegionId: Optional[int] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    destinationRegionId: Optional[int] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int
    cargoes: list[WaybillCargoOut] = Field(default_factory=list)
    cargoSummary: Optional[str] = None
    primarySeriesImage: Optional[str] = Field(
        default=None,
        description="首条货物或主档品牌/车型对应的车系图",
    )
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
    calcStatus: Optional[str] = None
    isLocked: Optional[int] = None
    waybillVersion: Optional[int] = None
    lastCalcAt: Optional[datetime] = None
    lastResultId: Optional[int] = None
    remark: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(
        cls,
        m,
        cargoes: Optional[list] = None,
        *,
        series_image_lookup: Optional[dict[str, Optional[str]]] = None,
        redact_freight_amount: bool = False,
    ) -> "WaybillOut":
        cargo_list = cargoes or []
        cargo_out: list[WaybillCargoOut] = []
        for c in cargo_list:
            key = waybill_brand_model_key(c.vehicle_brand, c.vehicle_model)
            img = (
                series_image_lookup.get(key)
                if series_image_lookup is not None
                else None
            )
            cargo_out.append(WaybillCargoOut.from_cargo(c, img))
        summary = _cargo_summary_from_lines(cargo_list) or None
        primary_series_image: Optional[str] = None
        for co in cargo_out:
            if co.seriesImage:
                primary_series_image = co.seriesImage
                break
        if primary_series_image is None and series_image_lookup is not None:
            primary_series_image = series_image_lookup.get(
                waybill_brand_model_key(m.vehicle_brand, m.vehicle_model)
            )
        freight_amount: Optional[float] = (
            float(m.freight_amount) if m.freight_amount is not None else None
        )
        if redact_freight_amount:
            freight_amount = None
        return cls(
            id=m.id,
            waybillNo=m.waybill_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            origin=m.origin,
            originCode=m.origin_code,
            originRegionId=getattr(m, "origin_region_id", None),
            destination=m.destination,
            destinationCode=m.destination_code,
            destinationRegionId=getattr(m, "destination_region_id", None),
            vehicleBrand=m.vehicle_brand,
            vehicleModel=m.vehicle_model,
            quantity=m.quantity,
            cargoes=cargo_out,
            cargoSummary=summary,
            primarySeriesImage=primary_series_image,
            planIssueTime=m.plan_issue_time,
            requiredLoadTime=m.required_load_time,
            requiredDeliverTime=m.required_deliver_time,
            dealerName=m.dealer_name,
            dealerContact=m.dealer_contact,
            dealerPhone=m.dealer_phone,
            dealerAddress=m.dealer_address,
            freightAmount=freight_amount,
            freightSource=m.freight_source,
            contractId=m.contract_id,
            rateId=m.rate_id,
            status=m.status,
            calcStatus=getattr(m, "calc_status", None),
            isLocked=getattr(m, "is_locked", None),
            waybillVersion=getattr(m, "waybill_version", None),
            lastCalcAt=getattr(m, "last_calc_at", None),
            lastResultId=getattr(m, "last_result_id", None),
            remark=m.remark,
            createdBy=m.created_by,
            createdAt=m.created_at,
        )
