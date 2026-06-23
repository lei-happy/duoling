"""
运单表（租户库）
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import String, SmallInteger, BigInteger, DateTime, Integer, Text, Numeric, text
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
    origin_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="出发地行政区ID（biz_region.id）"
    )
    destination: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="目的地"
    )
    destination_code: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="目的地编码"
    )
    destination_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="目的地行政区ID（biz_region.id）"
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
        comment=(
            "状态 0-待确认 1-待调度 2-调度中 3-运输中 4-待签收 "
            "5-已签收 6-已回单 7-已关闭"
        )
    )
    receipt_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="回单确认时间（签收底单返还货主）"
    )
    calc_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending",
        server_default=text("'pending'"),
        comment="计算状态 pending/calculating/calculated/exception/locked"
    )
    is_locked: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="是否锁定 0-否 1-是（已结算/已开票后置1，禁止自动重算）"
    )
    waybill_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="运单版本号（计费敏感字段每变更1次+1）"
    )
    last_calc_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="最近一次正式计算时间"
    )
    last_result_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="最近一次计算结果主表ID（biz_waybill_freight_result.id）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人ID"
    )
