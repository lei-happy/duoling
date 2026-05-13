"""
运价合同表（租户库）
"""

from typing import Optional
from datetime import date
from sqlalchemy import String, SmallInteger, BigInteger, Integer, Date, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FreightContract(TenantModelBase):
    """运价合同"""
    __tablename__ = "biz_freight_contract"
    __table_args__ = {"comment": "运价合同表"}
    __table_tier__ = "business"

    contract_no: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, comment="合同编号"
    )
    contract_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="合同名称"
    )
    customer_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="客户ID"
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户名称"
    )
    effective_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="生效日期"
    )
    expiry_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="到期日期"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="状态 0-草稿 1-生效 2-已终止"
    )
    contract_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="合同版本号"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
