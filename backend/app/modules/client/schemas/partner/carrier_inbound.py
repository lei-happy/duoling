"""
合作客户（反向视角）Schemas
B 视角：本租户作为承运商被哪些 A 公司纳入了合作关系。
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


class CarrierInboundLinkOut(BaseModel):
    """合作客户列表项（B 视角）"""
    id: int = Field(description="sys_carrier_link.id")
    sourceTenantCode: str = Field(description="A 公司租户编码")
    sourceTenantName: Optional[str] = Field(
        default=None, description="A 公司企业名称（来自 sys_tenant，实时）"
    )
    sourceTenantShortName: Optional[str] = None
    sourceContactPerson: Optional[str] = None
    sourceContactPhone: Optional[str] = None
    sourceProvince: Optional[str] = None
    sourceCity: Optional[str] = None
    sourceAddress: Optional[str] = None

    sourceCarrierId: int = Field(
        description="A 端 biz_carrier.id（用于跨端追溯）"
    )
    sourceCarrierName: str = Field(
        description="A 端登记的本企业名称（即对方为我们设定的'承运商名'）"
    )

    cooperationStart: Optional[date] = Field(
        default=None, description="合作起始日"
    )
    linkStatus: int = Field(
        description="1-激活 2-A 端已删除 3-B 端已退出"
    )
    createdAt: datetime
