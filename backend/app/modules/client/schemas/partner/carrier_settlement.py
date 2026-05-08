"""
承运商结算账户 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CarrierSettlementBase(BaseModel):
    """结算账户公共字段"""
    accountLabel: str = Field(description="账户标签（对公主账户/私户-司机张三 等）")
    accountType: int = Field(default=0, description="账户类型 0-对公 1-对私 2-其他")
    settlementType: int = Field(description="结算方式 0-月结 1-票结 2-预付 3-趟结")
    settlementPeriod: Optional[int] = Field(default=None, description="月结/趟结周期天数")
    settlementDay: Optional[int] = Field(default=None, description="月结结账日 1-28")
    bankName: Optional[str] = None
    bankBranch: Optional[str] = None
    bankAccount: Optional[str] = None
    bankAccountName: Optional[str] = None
    swiftCode: Optional[str] = None
    taxRate: Optional[float] = None
    applicableScope: Optional[str] = None
    isDefault: int = Field(default=0, description="是否默认 1-是 0-否")
    status: int = Field(default=1, description="状态 0-停用 1-正常")
    sortOrder: int = Field(default=0, description="排序")
    remark: Optional[str] = None


class CarrierSettlementCreate(CarrierSettlementBase):
    """创建结算账户"""
    pass


class CarrierSettlementUpdate(BaseModel):
    """更新结算账户（全字段可选）"""
    accountLabel: Optional[str] = None
    accountType: Optional[int] = None
    settlementType: Optional[int] = None
    settlementPeriod: Optional[int] = None
    settlementDay: Optional[int] = None
    bankName: Optional[str] = None
    bankBranch: Optional[str] = None
    bankAccount: Optional[str] = None
    bankAccountName: Optional[str] = None
    swiftCode: Optional[str] = None
    taxRate: Optional[float] = None
    applicableScope: Optional[str] = None
    isDefault: Optional[int] = None
    status: Optional[int] = None
    sortOrder: Optional[int] = None
    remark: Optional[str] = None


class CarrierSettlementOut(BaseModel):
    """结算账户输出"""
    id: int
    carrierId: int
    accountLabel: str
    accountType: int
    settlementType: int
    settlementPeriod: Optional[int] = None
    settlementDay: Optional[int] = None
    bankName: Optional[str] = None
    bankBranch: Optional[str] = None
    bankAccount: Optional[str] = None
    bankAccountName: Optional[str] = None
    swiftCode: Optional[str] = None
    taxRate: Optional[float] = None
    applicableScope: Optional[str] = None
    isDefault: int
    status: int
    sortOrder: int
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    @classmethod
    def from_model(cls, m) -> "CarrierSettlementOut":
        return cls(
            id=m.id,
            carrierId=m.carrier_id,
            accountLabel=m.account_label,
            accountType=m.account_type,
            settlementType=m.settlement_type,
            settlementPeriod=m.settlement_period,
            settlementDay=m.settlement_day,
            bankName=m.bank_name,
            bankBranch=m.bank_branch,
            bankAccount=m.bank_account,
            bankAccountName=m.bank_account_name,
            swiftCode=m.swift_code,
            taxRate=float(m.tax_rate) if m.tax_rate is not None else None,
            applicableScope=m.applicable_scope,
            isDefault=m.is_default,
            status=m.status,
            sortOrder=m.sort_order,
            remark=m.remark,
            createdAt=m.created_at,
        )
