"""
社会运力池 Schema - 结算账户

一条社会运力可拥有多个结算账户，同 social_capacity_id 内最多 1 条 isDefault=1。
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class SocialCapacityAccountCreate(BaseModel):
    """创建结算账户"""

    accountType: int
    accountLabel: Optional[str] = None
    accountName: str
    accountNo: str
    bankName: Optional[str] = None
    bankBranch: Optional[str] = None
    holderIdCard: Optional[str] = None
    isDefault: Optional[int] = 0
    status: Optional[int] = 1
    remark: Optional[str] = None


class SocialCapacityAccountUpdate(BaseModel):
    """更新结算账户"""

    accountType: Optional[int] = None
    accountLabel: Optional[str] = None
    accountName: Optional[str] = None
    accountNo: Optional[str] = None
    bankName: Optional[str] = None
    bankBranch: Optional[str] = None
    holderIdCard: Optional[str] = None
    isDefault: Optional[int] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class SocialCapacityAccountOut(BaseModel):
    """结算账户响应"""

    id: int
    socialCapacityId: int
    accountType: int
    accountLabel: Optional[str] = None
    accountName: str
    accountNo: str
    bankName: Optional[str] = None
    bankBranch: Optional[str] = None
    holderIdCard: Optional[str] = None
    isDefault: int
    status: int
    remark: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_model(cls, m) -> "SocialCapacityAccountOut":
        return cls(
            id=m.id,
            socialCapacityId=m.social_capacity_id,
            accountType=m.account_type,
            accountLabel=m.account_label,
            accountName=m.account_name,
            accountNo=m.account_no,
            bankName=m.bank_name,
            bankBranch=m.bank_branch,
            holderIdCard=m.holder_id_card,
            isDefault=m.is_default,
            status=m.status,
            remark=m.remark,
            createdAt=m.created_at,
            updatedAt=m.updated_at,
        )
