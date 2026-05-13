"""
运单批量导入 - 批次表 + 行明细表
"""

from typing import Optional

from sqlalchemy import (
    BigInteger,
    Index,
    Integer,
    JSON,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class WaybillImportBatch(TenantModelBase):
    """运单导入批次"""

    __tablename__ = "biz_waybill_import_batch"
    __table_args__ = (
        Index("idx_wib_status", "status"),
        Index("idx_wib_created_by", "created_by"),
        {"comment": "运单导入批次表"},
    )
    __table_tier__ = "business"

    file_name: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="原始文件名"
    )
    total_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="总行数（解析后）"
    )
    success_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="导入成功行数"
    )
    fail_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="校验失败行数"
    )
    calc_success_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="计算成功数"
    )
    calc_exception_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="计算异常数"
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending",
        server_default=text("'pending'"),
        comment="状态 pending/importing/imported/calculating/done/failed"
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, comment="批次级错误"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人ID"
    )


class WaybillImportRow(TenantModelBase):
    """运单导入行明细"""

    __tablename__ = "biz_waybill_import_row"
    __table_args__ = (
        Index("idx_wir_batch", "batch_id"),
        Index("idx_wir_validate", "validate_status"),
        {"comment": "运单导入行明细表"},
    )
    __table_tier__ = "business"

    batch_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="批次ID"
    )
    row_no: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="原 Excel 行号"
    )
    raw_data_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="原始行数据 JSON"
    )

    validate_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending",
        server_default=text("'pending'"),
        comment="校验状态 pending/success/failed"
    )
    validate_message: Mapped[Optional[str]] = mapped_column(
        String(1000), nullable=True, comment="校验信息"
    )

    waybill_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="生成的运单ID（成功后回填）"
    )
    calc_status: Mapped[Optional[str]] = mapped_column(
        String(32), nullable=True, comment="该行运单的最新计算状态"
    )
