"""
驾驶员运营属性表（租户库）

与 biz_driver 1:1 关联，存储车队归属、驾驶员类型、运营状态等业务属性。
"""

from typing import Optional, Any
from sqlalchemy import String, SmallInteger, BigInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class DriverOperation(TenantModelBase):
    """驾驶员运营属性"""
    __tablename__ = "biz_driver_operation"
    __table_args__ = {"comment": "驾驶员运营属性表"}
    __table_tier__ = "business"

    driver_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, comment="关联驾驶员ID"
    )
    department_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="所属车队/部门ID"
    )
    driver_type: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="自有驾驶员类型（数据字典 dictDataCode）"
    )
    settlement_mode: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="结算模式 1-承包制 2-统一管理各费用 3-计件提成",
    )
    resident_areas: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="常驻区域，存储省市代码数组"
    )
    common_routes: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="常跑线路（文本描述）"
    )
    operation_status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="运营状态 1-可接单 2-忙碌 3-休假 4-停运"
    )
