"""打款批次与批次明细（租户库）

批次**不是应付单据**，它是「一次银行付款动作」的执行记录（文档 10 §二）：应付义务
已经在承运商结算单 / 司机工资单 / 任务费用单上表达过，批次只负责「这 N 笔已审批的
钱，从某个账户一次性付出去」，金额是明细求和的结果而非独立录入。

明细用弱关联 ``(doc_kind, doc_id)`` 指向三种不同的应付单据表，不用强外键。

``dedup_key`` 承载「同一单据不被两个批次重复付」：``exec_status != 2`` 时写
``doc_kind:doc_id``，失败或移出批次时置 NULL，失败笔可重新入批。
"""

from decimal import Decimal
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, Date, DateTime, Index, Integer, Numeric, SmallInteger, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase
from app.modules.client.models.finance.finance_doc_base import FinanceDocBaseMixin

PAYMENT_BATCH_DOC_KIND = "payment_batch"


class PaymentBatch(FinanceDocBaseMixin, TenantModelBase):
    """打款批次（一次付款动作的载体）"""

    __tablename__ = "biz_payment_batch"
    __table_args__ = (
        Index("idx_pbatch_plan", "status", "plan_pay_date"),
        Index("idx_pbatch_account", "bank_account_id"),
        {"comment": "打款批次表（批量付款执行记录）"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=PAYMENT_BATCH_DOC_KIND,
        server_default=PAYMENT_BATCH_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 payment_batch）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="收/付方向（付款固定 2）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿 1-待审批 2-已审批 3-已执行 6-部分失败 4-已撤销",
    )

    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="付款经营主体ID"
    )
    bank_account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="付款账户ID（biz_bank_account.id）"
    )
    bank_account_label: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="付款账户标签（冗余展示）"
    )

    item_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="总笔数"
    )
    success_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="成功笔数"
    )
    fail_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="失败笔数"
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 2), default=0, server_default="0",
        comment="计划付款总额（= Σ 明细，与基类 planned_amount 同值，报表用语义列）",
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 2), default=0, server_default="0",
        comment="实际付出总额（= Σ 成功笔）",
    )
    plan_pay_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="计划付款日"
    )
    exec_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="执行开始时间"
    )
    exec_finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="执行结束时间"
    )
    exec_mode: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="执行方式 1-人工登记结果 2-银企直连（远期）",
    )


class PaymentBatchItem(TenantModelBase):
    """打款批次明细（每笔对应一张被打包的应付单据）"""

    __tablename__ = "biz_payment_batch_item"
    __table_args__ = (
        Index("idx_pbi_batch", "batch_id", "exec_status"),
        Index("idx_pbi_doc", "doc_kind", "doc_id"),
        Index("uk_pbi_dedup", "dedup_key", unique=True),
        {"comment": "打款批次明细表"},
    )
    __table_tier__ = "business"

    batch_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_payment_batch.id"
    )
    doc_kind: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="被付单据大类 task_finance / carrier_settle / driver_payroll",
    )
    doc_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="被付单据ID"
    )
    doc_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="被付单号（冗余）"
    )

    # ===== 收款方（冗余冻结：付款是历史事实，事后改账号不应影响已付记录） =====
    payee_type: Mapped[int] = mapped_column(
        SmallInteger, default=3, server_default="3",
        comment="收款方类型 1-司机 2-承运商 3-其他",
    )
    payee_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="收款方ID"
    )
    payee_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="收款方名称（冗余冻结）"
    )
    payee_bank_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="收款方开户行（冗余冻结）"
    )
    payee_bank_account: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="收款方账号（冗余冻结）"
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0", comment="本笔金额"
    )
    pay_method: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="支付方式（默认继承批次，可单笔改）",
    )
    exec_status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="执行状态 0-待执行 1-成功 2-失败",
    )
    fail_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="失败原因"
    )
    bank_serial_no: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, comment="银行流水号"
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="本笔实付时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键 doc_kind:doc_id，防同一单据被两个批次重复付；"
                "失败或移出批次时置 NULL，允许重新入批",
    )

    @staticmethod
    def build_dedup_key(doc_kind: str, doc_id: int) -> str:
        return f"{doc_kind}:{int(doc_id)}"
