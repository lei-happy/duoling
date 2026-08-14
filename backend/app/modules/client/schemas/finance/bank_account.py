"""银行账户 Schemas"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.modules.client.services.finance.base.constants import (
    AccountUsageScope,
    BankAccountType,
)


class BankAccountListItem(BaseModel):
    id: int
    enterpriseId: int
    accountName: str
    accountNo: str
    accountNoMasked: Optional[str] = None
    bankName: Optional[str] = None
    bankBranch: Optional[str] = None
    accountType: int = 2
    accountTypeLabel: Optional[str] = None
    currency: str = "CNY"
    balance: float = 0
    usageScope: int = 1
    usageScopeLabel: Optional[str] = None
    isDefaultReceive: int = 0
    isDefaultPay: int = 0
    status: int = 1
    sortOrder: int = 0
    displayLabel: Optional[str] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None

    @classmethod
    def from_model(cls, m: Any) -> "BankAccountListItem":
        return cls(
            id=m.id,
            enterpriseId=m.enterprise_id,
            accountName=m.account_name,
            accountNo=m.account_no,
            accountNoMasked=m.account_no_masked,
            bankName=m.bank_name,
            bankBranch=m.bank_branch,
            accountType=int(m.account_type or 0),
            accountTypeLabel=BankAccountType.LABELS.get(int(m.account_type or 0)),
            currency=m.currency or "CNY",
            balance=float(m.balance or 0),
            usageScope=int(m.usage_scope or 0),
            usageScopeLabel=AccountUsageScope.LABELS.get(int(m.usage_scope or 0)),
            isDefaultReceive=int(m.is_default_receive or 0),
            isDefaultPay=int(m.is_default_pay or 0),
            status=int(m.status or 0),
            sortOrder=int(m.sort_order or 0),
            displayLabel=m.display_label,
            remark=m.remark,
            createdAt=m.created_at,
        )


class BankAccountOption(BaseModel):
    """下拉项（不带余额之外的冗余字段）"""

    id: int
    accountName: str
    accountNoMasked: Optional[str] = None
    bankName: Optional[str] = None
    displayLabel: Optional[str] = None
    balance: float = 0
    usageScope: int = 1
    isDefaultReceive: int = 0
    isDefaultPay: int = 0

    @classmethod
    def from_model(cls, m: Any) -> "BankAccountOption":
        return cls(
            id=m.id,
            accountName=m.account_name,
            accountNoMasked=m.account_no_masked,
            bankName=m.bank_name,
            displayLabel=m.display_label,
            balance=float(m.balance or 0),
            usageScope=int(m.usage_scope or 0),
            isDefaultReceive=int(m.is_default_receive or 0),
            isDefaultPay=int(m.is_default_pay or 0),
        )


class BankAccountCreateRequest(BaseModel):
    enterpriseId: int
    accountName: str = Field(min_length=1, max_length=100)
    accountNo: str = Field(min_length=1, max_length=50)
    bankName: Optional[str] = Field(default=None, max_length=100)
    bankBranch: Optional[str] = Field(default=None, max_length=100)
    accountType: int = Field(default=BankAccountType.GENERAL, ge=1, le=4)
    currency: str = Field(default="CNY", max_length=8)
    usageScope: int = Field(default=AccountUsageScope.BOTH, ge=1, le=3)
    balance: Optional[Decimal] = Field(default=None, description="建档时的账面余额")
    isDefaultReceive: int = Field(default=0, ge=0, le=1)
    isDefaultPay: int = Field(default=0, ge=0, le=1)
    sortOrder: int = 0
    remark: Optional[str] = Field(default=None, max_length=255)


class BankAccountUpdateRequest(BaseModel):
    accountName: Optional[str] = Field(default=None, max_length=100)
    accountNo: Optional[str] = Field(default=None, max_length=50)
    bankName: Optional[str] = Field(default=None, max_length=100)
    bankBranch: Optional[str] = Field(default=None, max_length=100)
    accountType: Optional[int] = Field(default=None, ge=1, le=4)
    currency: Optional[str] = Field(default=None, max_length=8)
    usageScope: Optional[int] = Field(default=None, ge=1, le=3)
    isDefaultReceive: Optional[int] = Field(default=None, ge=0, le=1)
    isDefaultPay: Optional[int] = Field(default=None, ge=0, le=1)
    status: Optional[int] = Field(default=None, ge=0, le=1)
    sortOrder: Optional[int] = None
    remark: Optional[str] = Field(default=None, max_length=255)


class BankAccountStatusRequest(BaseModel):
    status: int = Field(ge=0, le=1)


class BalanceCalibrateRequest(BaseModel):
    balance: Decimal = Field(description="银行实际余额")
    reason: str = Field(min_length=5, max_length=255)
