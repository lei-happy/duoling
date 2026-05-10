"""
运单 Schemas
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator


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

    model_config = {"from_attributes": True}

    @classmethod
    def from_cargo(cls, c) -> "WaybillCargoOut":
        return cls(
            id=c.id,
            vehicleBrand=c.vehicle_brand,
            vehicleModel=c.vehicle_model,
            quantity=c.quantity,
            sortOrder=c.sort_order,
        )


class WaybillCreate(BaseModel):
    waybillNo: Optional[str] = None
    customerId: Optional[int] = None
    customerName: Optional[str] = None
    origin: Optional[str] = None
    originCode: Optional[str] = None
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
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
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
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
    destination: Optional[str] = None
    destinationCode: Optional[str] = None
    vehicleBrand: Optional[str] = None
    vehicleModel: Optional[str] = None
    quantity: int
    cargoes: list[WaybillCargoOut] = Field(default_factory=list)
    cargoSummary: Optional[str] = None
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
    remark: Optional[str] = None
    createdBy: Optional[int] = None
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m, cargoes: Optional[list] = None) -> "WaybillOut":
        cargo_list = cargoes or []
        cargo_out = [WaybillCargoOut.from_cargo(c) for c in cargo_list]
        summary = _cargo_summary_from_lines(cargo_list) or None
        return cls(
            id=m.id,
            waybillNo=m.waybill_no,
            customerId=m.customer_id,
            customerName=m.customer_name,
            origin=m.origin,
            originCode=m.origin_code,
            destination=m.destination,
            destinationCode=m.destination_code,
            vehicleBrand=m.vehicle_brand,
            vehicleModel=m.vehicle_model,
            quantity=m.quantity,
            cargoes=cargo_out,
            cargoSummary=summary,
            planIssueTime=m.plan_issue_time,
            requiredLoadTime=m.required_load_time,
            requiredDeliverTime=m.required_deliver_time,
            dealerName=m.dealer_name,
            dealerContact=m.dealer_contact,
            dealerPhone=m.dealer_phone,
            dealerAddress=m.dealer_address,
            freightAmount=float(m.freight_amount)
            if m.freight_amount is not None
            else None,
            freightSource=m.freight_source,
            contractId=m.contract_id,
            rateId=m.rate_id,
            status=m.status,
            remark=m.remark,
            createdBy=m.created_by,
            createdAt=m.created_at,
        )
