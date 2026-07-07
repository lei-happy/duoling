"""
成本计算异常表（业务结果维度，区别于 task 的工作流维度）

异常类型枚举：
  - POLICY_NOT_FOUND          该任务无任何生效成本政策
  - RULE_NOT_FOUND            某必算费用类型未匹配到规则
  - RULE_CONFLICT             某费用类型匹配到多条同分规则
  - DISTANCE_NOT_FOUND        per_km/per_ton_km 缺里程
  - AREA_NOT_RECOGNIZED       起点/终点无法标准化
  - INVALID_QTY               台数为空或 <= 0（per_vehicle 时）
  - CARRIER_RESOURCE_MISSING  缺承运资源（无法确定收款方）
  - TASK_LOCKED               任务已锁定，跳过自动重算
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    JSON,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CostCalcException(TenantModelBase):
    """成本计算异常"""

    __tablename__ = "biz_cost_calc_exception"
    __table_args__ = (
        Index("idx_cce_status", "status"),
        Index("idx_cce_task", "task_id"),
        Index("idx_cce_type", "exception_type"),
        {"comment": "成本计算异常表"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="任务ID"
    )
    fee_type: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="费用类型（整任务级异常时为空）"
    )

    exception_type: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="异常类型"
    )
    exception_message: Mapped[str] = mapped_column(
        String(1000), nullable=False, comment="异常描述"
    )
    context_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="上下文JSON（触发来源/匹配轨迹）"
    )

    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending",
        server_default=text("'pending'"),
        comment="处理状态 pending/processed/ignored",
    )
    processed_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="处理人"
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="处理时间"
    )
    process_remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="处理备注"
    )
