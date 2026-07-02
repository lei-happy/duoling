"""
财务单据通用字段集（mixin 风格，不映射表）

所有具体财务单据表通过多重继承本 mixin 复用通用字段集，例如：

    class CarrierRecon(FinanceDocBaseMixin, TenantModelBase):
        __tablename__ = "biz_carrier_recon"
        ...  # 仅声明领域特有字段

本 mixin 本身不继承 Base、不声明 ``__tablename__``，因此不会被映射成表，
只提供列声明供子类继承（SQLAlchemy 2.0 declarative mixin 语义）。

说明：现有 ``biz_task_finance_doc`` 出于向后兼容不直接继承本 mixin，
而是通过 ALTER 渐进补齐同名字段（见文档 05）；两者字段语义保持一致。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Numeric, SmallInteger, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column


class FinanceDocBaseMixin:
    """财务单据通用字段集

    通用状态码（见文档 01 §2.2）：
        0-草稿 1-待审批 2-已审批 3-已支付/已收款/已开票
        4-已撤销 5-已核销/已结清 6-部分核销/部分支付 9-已作废
    不同子单据只使用其中的部分状态码。
    """

    # ===== 单据标识 =====
    doc_no: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, comment="单据编号（系统生成，租户内唯一）"
    )
    doc_kind: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="单据大类（冗余）：task_finance / carrier_recon / carrier_settle / "
                "driver_payroll / customer_recon / customer_settle / customer_invoice",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="通用状态 0-草稿 1-待审批 2-已审批 3-已支付/已收款/已开票 "
                "4-已撤销 5-已核销/已结清 6-部分核销/部分支付 9-已作废",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="收/付方向 1-收款（应收） 2-付款（应付）",
    )
    currency: Mapped[str] = mapped_column(
        String(8), default="CNY", server_default="CNY", comment="币种"
    )

    # ===== 金额 =====
    planned_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, comment="计划金额（>= 0）"
    )
    actual_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(14, 2), nullable=True, comment="实际金额（支付/收款后填）"
    )

    # ===== 周期（对账类必填，单据类可空） =====
    period_start: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="周期起"
    )
    period_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="周期止"
    )

    # ===== 流程操作人与时间 =====
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人 user_id"
    )
    submitted_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="提交审批人 user_id"
    )
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="提交审批时间"
    )
    reviewed_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="审批人 user_id"
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="审批时间"
    )
    paid_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="付款/收款操作人 user_id"
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="付款/收款时间"
    )

    # ===== 支付 =====
    pay_method: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="支付方式（应付）/ 收款方式（应收）",
    )
    pay_voucher_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="凭证图片 URL"
    )

    # ===== 撤销 =====
    cancelled_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="撤销操作人 user_id"
    )
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="撤销时间"
    )
    cancel_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="撤销原因（撤销必填）"
    )

    # ===== 锁定 =====
    is_locked: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否锁定（终态后置 1）",
    )
    locked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="锁定时间"
    )
    locked_by_doc_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="锁定来源单据 ID（被哪个上游单据锁定）"
    )

    # ===== 远期能力预留 =====
    approval_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="远期审批中心单号"
    )
    idempotency_key: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="幂等键（远期写库唯一索引）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )
