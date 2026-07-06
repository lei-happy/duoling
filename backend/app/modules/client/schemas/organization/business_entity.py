"""
经营主体 Schemas（字段名对齐前端 camelCase）
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field


class BusinessEntityCreate(BaseModel):
    model_config = {"extra": "ignore"}

    entityName: str = Field(..., description="主体名称（法人全称）")
    entityCode: Optional[str] = Field(default=None, description="主体编码（留空自动生成）")
    shortName: Optional[str] = None
    unifiedCreditCode: Optional[str] = None
    legalPerson: Optional[str] = None
    registeredAddress: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    bankName: Optional[str] = None
    bankAccount: Optional[str] = None
    invoiceTitle: Optional[str] = None
    invoiceTaxNo: Optional[str] = None
    sortOrder: int = 0
    remark: Optional[str] = None


class BusinessEntityUpdate(BaseModel):
    model_config = {"extra": "ignore"}

    entityName: Optional[str] = None
    shortName: Optional[str] = None
    unifiedCreditCode: Optional[str] = None
    legalPerson: Optional[str] = None
    registeredAddress: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    bankName: Optional[str] = None
    bankAccount: Optional[str] = None
    invoiceTitle: Optional[str] = None
    invoiceTaxNo: Optional[str] = None
    sortOrder: Optional[int] = None
    remark: Optional[str] = None


class BusinessEntityStatusUpdate(BaseModel):
    status: int = Field(..., description="1-正常 0-停用")


class BusinessEntityOut(BaseModel):
    id: int
    entityCode: str
    entityName: str
    shortName: Optional[str] = None
    unifiedCreditCode: Optional[str] = None
    legalPerson: Optional[str] = None
    registeredAddress: Optional[str] = None
    contactPerson: Optional[str] = None
    contactPhone: Optional[str] = None
    bankName: Optional[str] = None
    bankAccount: Optional[str] = None
    invoiceTitle: Optional[str] = None
    invoiceTaxNo: Optional[str] = None
    isDefault: int = 0
    status: int = 1
    sortOrder: int = 0
    remark: Optional[str] = None
    createdAt: Optional[str] = None

    @classmethod
    def from_model(cls, m) -> "BusinessEntityOut":
        return cls(
            id=m.id,
            entityCode=m.entity_code,
            entityName=m.entity_name,
            shortName=m.short_name,
            unifiedCreditCode=m.unified_credit_code,
            legalPerson=m.legal_person,
            registeredAddress=m.registered_address,
            contactPerson=m.contact_person,
            contactPhone=m.contact_phone,
            bankName=m.bank_name,
            bankAccount=m.bank_account,
            invoiceTitle=m.invoice_title,
            invoiceTaxNo=m.invoice_tax_no,
            isDefault=m.is_default,
            status=m.status,
            sortOrder=m.sort_order,
            remark=m.remark,
            createdAt=(
                m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None
            ),
        )


class BusinessEntityOption(BaseModel):
    """下拉选项（供各业务表单主体选择器）"""
    id: int
    entityName: str
    shortName: Optional[str] = None
    isDefault: int = 0

    @classmethod
    def from_model(cls, m) -> "BusinessEntityOption":
        return cls(
            id=m.id,
            entityName=m.entity_name,
            shortName=m.short_name,
            isDefault=m.is_default,
        )
