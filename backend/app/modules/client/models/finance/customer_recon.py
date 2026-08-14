"""
客户对账单（租户库）

一段时间内某客户名下所有「待结算运单」的事项确认书：主表记周期与合计，桥接表
逐行记运单的计费基础、数量、单价与金额（文档 02 §3.2）。

设计要点：

- **快照不漂移**：行上的 ``freight_amount_snapshot`` / ``signed_quantity_snapshot``
  是写入时的业务事实。业务侧后续变更只置脏（``recon_dirty``）并留差异，不回灌
  改金额——否则对账单会在客户签字后自己变数。
- **同客户同周期至多一张非撤销对账单**：MySQL 无部分唯一索引，故用 ``dedup_key``
  冗余列 + 唯一索引，撤销 / 软删时置 NULL 释放占用（同 ``biz_recon_diff`` 的做法）。
- **金额列不与基类重复**：应收合计直接用基类 ``planned_amount``，不再另立
  ``total_planned_amount``；已关联与已收妥另立 ``applied_amount_total`` /
  ``received_amount_total``，两者语义不同（关联 ≠ 收到），见 §3.5「部分确认/分批结清」。
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    BigInteger, DateTime, Index, Integer, Numeric, SmallInteger, String, Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase
from app.modules.client.models.finance.finance_doc_base import FinanceDocBaseMixin

# 本表 doc_kind 常量（与 ReconKind.CUSTOMER、FinanceStateMachine 登记值一致）
CUSTOMER_RECON_DOC_KIND = "customer_recon"


class CustomerRecon(FinanceDocBaseMixin, TenantModelBase):
    """客户对账单主表"""

    __tablename__ = "biz_customer_recon"
    __table_args__ = (
        Index("idx_crecon_customer", "customer_id", "status"),
        Index("idx_crecon_period", "period_start", "period_end"),
        Index("idx_crecon_status", "status"),
        Index("idx_crecon_enterprise", "enterprise_id"),
        Index("uk_crecon_period_dedup", "dedup_key", unique=True),
        {"comment": "客户对账单主表"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=CUSTOMER_RECON_DOC_KIND,
        server_default=CUSTOMER_RECON_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 customer_recon）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="收/付方向（应收固定 1-收款）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿 2-已确认 3-已结清 4-已撤销（对账类不走 1-待审批）",
    )

    # ===== 客户与归属 =====
    customer_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer.id"
    )
    customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户名称（冗余）"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="收入归属经营主体ID（biz_business_entity.id），取自客户档案默认主体",
    )
    settlement_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="结算方式 0-月结 1-票结 2-预付（写入时从客户档案冻结）",
    )

    # ===== 合计（冗余，供列表页免 join 桥接表） =====
    waybill_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联运单数"
    )
    total_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="计费数量合计（按行 quantity 求和）",
    )
    adjust_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="行调整额合计（可负）；超过阈值需业务主管审批后才能确认",
    )
    applied_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已被结算单关联的金额合计（判断还能再关联多少）",
    )
    received_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已收妥金额合计（关联结算单中已收款部分的应用金额之和）",
    )
    settle_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联结算单数量"
    )

    # ===== 客户方确认 =====
    confirmed_by_customer_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="客户方确认时间"
    )
    confirmed_by_customer_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="客户方确认人姓名（自由文本）"
    )
    confirm_voucher_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="客户回签凭证 URL（PDF/图片）"
    )
    customer_contact_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="客户对账联系人（冗余）"
    )
    customer_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="客户对账联系电话（冗余）"
    )

    # ===== 大额调整的业务主管审批（软门槛，文档 02 §3.6） =====
    adjust_approved_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="大额调整审批人 user_id"
    )
    adjust_approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="大额调整审批时间；调整额再次变动会清空，需重新审批",
    )

    # ===== 一致性核对冗余计数（由 ConsistencyChecker 维护） =====
    dirty_line_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
        comment="脏行数（快照与业务事实不一致的行），>0 时列表高亮",
    )
    diff_open_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
        comment="未处置差异条数（biz_recon_diff.status=0）",
    )
    diff_forced_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0",
        comment="已强制放行差异条数（biz_recon_diff.status=3），>0 显示带未决差异徽章",
    )

    # ===== 同客户同周期唯一（条件唯一，见模块 docstring） =====
    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(80), nullable=True,
        comment="唯一键 customer_id:period_start:period_end，"
                "仅非撤销且未删除时有值，撤销/软删置 NULL 释放占用",
    )

    @staticmethod
    def build_dedup_key(
        customer_id: int,
        period_start: Optional[datetime],
        period_end: Optional[datetime],
    ) -> str:
        """构造同客户同周期唯一键（周期为空时用 0 占位）。"""
        s = period_start.strftime("%Y%m%d") if period_start else "0"
        e = period_end.strftime("%Y%m%d") if period_end else "0"
        return f"{int(customer_id)}:{s}:{e}"


class CustomerReconWaybillLink(TenantModelBase):
    """客户对账行（对账单 ↔ 运单桥接，含计费基础与快照）"""

    __tablename__ = "biz_customer_recon_waybill_link"
    __table_args__ = (
        Index("idx_crwl_recon", "recon_id"),
        Index("idx_crwl_waybill", "waybill_id"),
        Index("idx_crwl_dirty", "recon_id", "recon_dirty"),
        Index("uk_crwl_dedup", "dedup_key", unique=True),
        {"comment": "客户对账单-运单桥接表（对账行）"},
    )
    __table_tier__ = "business"

    recon_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_customer_recon.id"
    )
    waybill_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_waybill.id"
    )
    waybill_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="运单号（冗余）"
    )

    # ===== 计费 =====
    billing_base: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="计费基础 1-按台 2-按吨 3-按趟 4-固定金额",
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default="0",
        comment="计费数量（按台=已交车台数 按吨=吨数 按趟=1）",
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="单价（合同冻结，可手工覆盖）",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="行金额 = quantity × unit_price + adjust_amount",
    )
    adjust_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="调整额（差异、罚款、补价，可负）",
    )
    adjust_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="调整原因（有调整额时必填）"
    )

    # ===== 业务事实快照（写入时冻结，业务侧变更不回灌） =====
    freight_amount_snapshot: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="写入时的 waybill.freight_amount 快照"
    )
    signed_quantity_snapshot: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="写入时的已交车台数聚合快照"
    )
    locked_snapshot_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="快照冻结时间"
    )

    # ===== 脏标记（由 ConsistencyChecker 写，见文档 09 §3.2） =====
    recon_dirty: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否需重新核对 0-否 1-是（快照与业务事实已不一致）",
    )
    dirty_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="置脏原因（如「签收台数由 8 变为 7」）"
    )
    dirty_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="置脏时间"
    )

    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键 recon_id:waybill_id，防重复挂接；移除行（软删）时置 NULL",
    )

    @staticmethod
    def build_dedup_key(recon_id: int, waybill_id: int) -> str:
        return f"{int(recon_id)}:{int(waybill_id)}"
