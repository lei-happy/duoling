"""
财务单据审计事件表（租户库）

``biz_finance_doc_event`` 是财务领域内的"事实流水"，与通用 ``operation_log`` 互补：
- ``operation_log`` 记录跨模块通用操作日志；
- 本表记录每一次财务单据的状态/支付/撤销/锁定动作，对账时直接读这张表。

设计要点：
- **append-only**：不允许更新或删除事件；任何"删错单据"通过反向事件冲销。
- **冗余足够**：操作人姓名、金额、关联快照都冗余在事件里，单据软删除后仍可定位。
"""

from decimal import Decimal
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON, BigInteger, DateTime, Index, Numeric, SmallInteger, String, func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class FinanceDocEvent(TenantModelBase):
    """财务单据审计事件（append-only 事实流）"""

    __tablename__ = "biz_finance_doc_event"
    __table_args__ = (
        Index("idx_fde_doc_kind_id", "doc_kind", "doc_id"),
        Index("idx_fde_event_time", "event_time"),
        {"comment": "财务单据审计事件表"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="单据大类（同 FinanceDocBaseMixin.doc_kind）",
    )
    doc_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="单据 ID"
    )
    event_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="事件类型 1-创建 2-提交 3-审批通过 4-审批拒绝 5-退回草稿 "
                "6-支付 7-撤销支付 8-撤销 9-强制撤销 10-核销 11-锁定 12-解锁 "
                "13-开票 14-作废 15-红冲",
    )
    from_status: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="变更前状态"
    )
    to_status: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="变更后状态"
    )
    direction: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="收/付方向 1-收 2-付"
    )
    occurred_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2), nullable=True,
        comment="该事件涉及金额（撤销/红冲填负数）",
    )
    operator_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人 user_id"
    )
    operator_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="操作人姓名（冗余）"
    )
    reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="原因"
    )
    payload_snapshot: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="关键字段快照（金额/关联范围等）"
    )
    event_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="事件时间"
    )
