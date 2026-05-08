"""
承运商主体档案 Schemas
"""

from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel, Field

from app.modules.client.schemas.partner.carrier_settlement import (
    CarrierSettlementCreate, CarrierSettlementOut,
)


class CarrierBase(BaseModel):
    """承运商公共字段"""
    carrierCode: Optional[str] = None
    carrierName: str = Field(description="承运商全称")
    shortName: Optional[str] = None
    carrierType: int = Field(default=0, description="0-公司车队 1-个体司机/小车队 2-其他")
    creditCode: Optional[str] = None
    idCardNo: Optional[str] = None
    legalPerson: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: str = Field(description="联系电话（互联激活关键字段）")
    contactEmail: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    cooperationStartDate: Optional[date] = None
    status: int = Field(default=1, description="0-停用 1-正常 2-黑名单")
    remark: Optional[str] = None


class CarrierCreate(CarrierBase):
    """创建承运商（可附带多个结算账户一次性写入）"""
    settlements: Optional[List[CarrierSettlementCreate]] = Field(
        default=None,
        description="同时创建的结算账户数组（可选）",
    )


class CarrierUpdate(BaseModel):
    """更新承运商主体（不动结算账户）"""
    carrierCode: Optional[str] = None
    carrierName: Optional[str] = None
    shortName: Optional[str] = None
    carrierType: Optional[int] = None
    creditCode: Optional[str] = None
    idCardNo: Optional[str] = None
    legalPerson: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    contactEmail: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    cooperationStartDate: Optional[date] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class CarrierOut(BaseModel):
    """承运商详情输出"""
    id: int
    carrierCode: Optional[str] = None
    carrierName: str
    shortName: Optional[str] = None
    carrierType: int
    creditCode: Optional[str] = None
    idCardNo: Optional[str] = None
    legalPerson: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: str
    contactEmail: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    cooperationStartDate: Optional[date] = None
    status: int
    linkedTenantCode: Optional[str] = None
    inviteStatus: int
    invitedAt: Optional[datetime] = None
    activatedAt: Optional[datetime] = None
    ratingScore: Optional[float] = None
    ratingLevel: Optional[int] = None
    lastEvaluatedAt: Optional[datetime] = None
    remark: Optional[str] = None
    createdAt: datetime
    settlements: Optional[List[CarrierSettlementOut]] = None
    defaultSettlement: Optional[CarrierSettlementOut] = None

    @classmethod
    def from_model(
        cls,
        m,
        settlements: Optional[List] = None,
        default_settlement=None,
    ) -> "CarrierOut":
        return cls(
            id=m.id,
            carrierCode=m.carrier_code,
            carrierName=m.carrier_name,
            shortName=m.short_name,
            carrierType=m.carrier_type,
            creditCode=m.credit_code,
            idCardNo=m.id_card_no,
            legalPerson=m.legal_person,
            contactPerson=m.contact_person,
            contactPhone=m.contact_phone,
            contactEmail=m.contact_email,
            province=m.province,
            city=m.city,
            district=m.district,
            address=m.address,
            cooperationStartDate=m.cooperation_start_date,
            status=m.status,
            linkedTenantCode=m.linked_tenant_code,
            inviteStatus=m.invite_status,
            invitedAt=m.invited_at,
            activatedAt=m.activated_at,
            ratingScore=float(m.rating_score) if m.rating_score is not None else None,
            ratingLevel=m.rating_level,
            lastEvaluatedAt=m.last_evaluated_at,
            remark=m.remark,
            createdAt=m.created_at,
            settlements=(
                [CarrierSettlementOut.from_model(s) for s in settlements]
                if settlements is not None else None
            ),
            defaultSettlement=(
                CarrierSettlementOut.from_model(default_settlement)
                if default_settlement is not None else None
            ),
        )


class CarrierListItemOut(BaseModel):
    """列表行输出（含默认结算摘要）"""
    id: int
    carrierCode: Optional[str] = None
    carrierName: str
    shortName: Optional[str] = None
    carrierType: int
    contactPerson: Optional[str] = None
    contactPhone: str
    status: int
    linkedTenantCode: Optional[str] = None
    inviteStatus: int
    createdAt: datetime
    defaultSettlementType: Optional[int] = Field(
        default=None, description="默认结算账户的结算方式"
    )
    defaultSettlementLabel: Optional[str] = Field(
        default=None, description="默认结算账户标签"
    )
    defaultBankAccountName: Optional[str] = Field(
        default=None, description="默认收款户名"
    )

    @classmethod
    def from_model(cls, m, default_settlement=None) -> "CarrierListItemOut":
        return cls(
            id=m.id,
            carrierCode=m.carrier_code,
            carrierName=m.carrier_name,
            shortName=m.short_name,
            carrierType=m.carrier_type,
            contactPerson=m.contact_person,
            contactPhone=m.contact_phone,
            status=m.status,
            linkedTenantCode=m.linked_tenant_code,
            inviteStatus=m.invite_status,
            createdAt=m.created_at,
            defaultSettlementType=(
                default_settlement.settlement_type if default_settlement else None
            ),
            defaultSettlementLabel=(
                default_settlement.account_label if default_settlement else None
            ),
            defaultBankAccountName=(
                default_settlement.bank_account_name if default_settlement else None
            ),
        )


class CarrierSelectItem(BaseModel):
    """承运商选择器返回项"""
    id: int
    carrierCode: Optional[str] = None
    carrierName: str
    shortName: Optional[str] = None
    carrierType: int
    linked: bool
    linkedTenantCode: Optional[str] = None
    defaultSettlement: Optional[CarrierSettlementOut] = None
