"""
运单表（租户库）
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import String, SmallInteger, BigInteger, DateTime, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class Waybill(TenantModelBase):
    """运单"""
    __tablename__ = "biz_waybill"
    __table_args__ = {"comment": "运单表"}
    __table_tier__ = "business"

    waybill_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="运单号"
    )
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="客户ID"
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户名称"
    )
    origin: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="出发地"
    )
    origin_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="出发地编码"
    )
    destination: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="目的地"
    )
    destination_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="目的地编码"
    )
    vehicle_brand: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="车辆品牌"
    )
    vehicle_model: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="车型"
    )
    quantity: Mapped[int] = mapped_column(
        Integer, default=1, comment="数量"
    )
    plan_issue_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划下发时间"
    )
    required_load_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="要求装车时间"
    )
    required_deliver_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="要求送达时间"
    )
    dealer_name: Mapped[Optional[str]] = mapped_column(
        String(200), nullable=True, comment="经销商名称"
    )
    dealer_contact: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="经销商联系人"
    )
    dealer_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="经销商电话"
    )
    dealer_address: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="经销商地址"
    )
    freight_amount: Mapped[Optional[str]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="运费金额"
    )
    freight_source: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="运费来源 0-自动计算 1-手动填写"
    )
    contract_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="合同ID"
    )
    rate_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="运价ID"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0,
        comment="状态 0-待确认 1-已确认 2-已调度 3-运输中 4-已送达 5-已完成 6-已取消"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人ID"
    )
