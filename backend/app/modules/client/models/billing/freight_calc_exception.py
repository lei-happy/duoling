"""
运费计算异常表（业务结果维度，区别于 task 的工作流维度）

异常类型枚举：
  - AREA_NOT_RECOGNIZED       出发地或目的地无法标准化
  - SERIES_NOT_RECOGNIZED     车型/品牌无法标准化
  - CONTRACT_NOT_FOUND        客户无有效合同
  - RULE_NOT_FOUND            未匹配到有效运价规则
  - RULE_CONFLICT             多条同分规则冲突
  - INVALID_QTY               台数为空或非正
  - WAYBILL_LOCKED            运单已锁定不允许重算
  - IMPORT_VALIDATE_FAILED    导入数据校验失败
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


class FreightCalcException(TenantModelBase):
    """运费计算异常"""

    __tablename__ = "biz_freight_calc_exception"
    __table_args__ = (
        Index("idx_fce_status", "status"),
        Index("idx_fce_waybill", "waybill_id"),
        Index("idx_fce_type", "exception_type"),
        Index("idx_fce_batch", "batch_id"),
        {"comment": "运费计算异常表"},
    )
    __table_tier__ = "business"

    waybill_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="运单ID（导入校验异常可能为空）"
    )
    waybill_cargo_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="运单货物明细ID"
    )
    batch_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="批量导入批次ID（来自导入流程）"
    )
    import_row_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="批量导入行ID"
    )

    exception_type: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="异常类型枚举"
    )
    exception_message: Mapped[str] = mapped_column(
        String(1000), nullable=False, comment="异常描述"
    )
    context_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="异常上下文（货物名/线路/客户/匹配候选等）"
    )

    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending",
        server_default=text("'pending'"),
        comment="处理状态 pending/processed/ignored"
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
