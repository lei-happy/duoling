"""
任务单财务费用单（租户库）

一个任务单可挂多张：预付单（1）/ 补款单（2）/ 结算单（3）。
收款人 = (payee_type + payee_id)：自有车=司机，承运商=承运商，其他=自由文本。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Numeric, SmallInteger, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class TaskFinanceDoc(TenantModelBase):
    """任务单财务费用单"""

    __tablename__ = "biz_task_finance_doc"
    __table_args__ = (
        Index("idx_tfd_task_id", "task_id"),
        Index("idx_tfd_doc_type", "doc_type"),
        Index("idx_tfd_status", "status"),
        Index("idx_tfd_payee", "payee_type", "payee_id"),
        {"comment": "任务单财务费用单"},
    )
    __table_tier__ = "business"

    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task.id"
    )
    doc_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="单据编号（系统生成）"
    )
    doc_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, comment="单据类型 1-预付单 2-补款单 3-结算单"
    )
    is_final: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否最终结算单（仅 doc_type=3 可为 1）",
    )

    # ===== 收款对象 =====
    payee_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False,
        comment="收款人类型 1-司机 2-承运商 3-其他",
    )
    payee_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="收款人 ID（driver_id 或 carrier_id）"
    )
    payee_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="收款人名称（冗余）"
    )
    payee_account_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="账户类型 0-未指定 1-driver_account 2-carrier_settlement 3-自由文本",
    )
    payee_account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="账户 ID（driver_account.id 或 carrier_settlement.id）",
    )
    payee_bank_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开户行（冗余）"
    )
    payee_bank_account_masked: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="银行账号脱敏（冗余）"
    )

    # ===== 金额 =====
    planned_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, comment="计划金额"
    )
    actual_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="实际支付金额（支付后填）"
    )
    currency: Mapped[str] = mapped_column(
        String(8), default="CNY", server_default="CNY", comment="币种"
    )

    # ===== 支付 =====
    pay_method: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="支付方式 1-银行转账 2-油卡 3-油气款 4-现金 5-微信 6-支付宝",
    )
    planned_pay_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="计划支付时间"
    )
    actual_pay_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="实际支付时间"
    )
    pay_voucher_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="支付凭证图片 URL"
    )

    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿 1-待审批 2-已审批 3-已支付 4-已撤销",
    )

    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人 user_id"
    )
    reviewed_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="审批人 user_id"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="审批时间"
    )
    paid_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="付款操作人 user_id"
    )
    approval_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="关联审批单（远期对接审批中心）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
