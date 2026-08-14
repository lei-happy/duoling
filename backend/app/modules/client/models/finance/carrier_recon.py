"""承运商对账单（租户库）

一段周期内某承运商名下「已交车且未付清」任务的事项确认书（文档 03 §3.2）。
与客户对账单同构，两处关键差异：

- **多了预付扣减**：任务在途时可能已通过任务级预付 / 补款付过一部分钱，纳入对账
  后必须扣掉，否则会重复支付。扣减额写快照（``prepaid_offset_amount``），预付单
  事后被撤销也不回灌——差额靠手工 ``adjust_amount`` 补，留痕比自动漂移安全。
- **净额是结算依据**：行 ``net_amount`` = 毛额 - 预付扣减；主表 ``planned_amount``
  存净额合计（结算单按它付钱），毛额另存 ``gross_amount_total`` 供对账页展示。

脏标记列与主表三个计数列的列名与客户侧完全一致，故一致性核对器可以共用同一套
实现（见 ``ConsistencyChecker`` 的 ``ReconBinding``）。
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

# 本表 doc_kind 常量（与 ReconKind.CARRIER、FinanceStateMachine 登记值一致）
CARRIER_RECON_DOC_KIND = "carrier_recon"


class CarrierRecon(FinanceDocBaseMixin, TenantModelBase):
    """承运商对账单主表"""

    __tablename__ = "biz_carrier_recon"
    __table_args__ = (
        Index("idx_carecon_carrier", "carrier_id", "status"),
        Index("idx_carecon_period", "period_start", "period_end"),
        Index("idx_carecon_status", "status"),
        Index("idx_carecon_enterprise", "enterprise_id"),
        Index("uk_carecon_period_dedup", "dedup_key", unique=True),
        {"comment": "承运商对账单主表"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=CARRIER_RECON_DOC_KIND,
        server_default=CARRIER_RECON_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 carrier_recon）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="收/付方向（应付固定 2-付款）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="状态 0-草稿 2-已确认 3-已结清 4-已撤销（对账类不走 1-待审批）",
    )

    # ===== 承运商与归属 =====
    carrier_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_carrier.id"
    )
    carrier_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="承运商名称（冗余）"
    )
    carrier_short_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="承运商简称（冗余）"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="成本归属经营主体ID（biz_business_entity.id），取自承运商档案",
    )
    settlement_account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="推荐结算账户（biz_carrier_settlement.id，写入时冻结）",
    )
    settlement_account_label: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="结算账户标签（冗余）"
    )
    settlement_type_snapshot: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="承运商主结算方式快照 0-月结 1-票结 2-预付 3-趟结",
    )

    # ===== 合计（冗余，供列表页免 join 桥接表） =====
    task_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联任务数"
    )
    total_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="计费数量合计（按行 quantity 求和）",
    )
    gross_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="毛额合计（含行调整额，未扣预付）",
    )
    prepaid_offset_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="任务级预付/补款已付金额合计（自动扣减项）",
    )
    adjust_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="行调整额合计（可负）；超过阈值需业务主管审批后才能确认",
    )
    applied_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已被结算单关联的金额合计（判断还能再关联多少）",
    )
    paid_amount_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="已付妥金额合计（关联结算单中已支付部分的应用金额之和）",
    )
    settle_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联结算单数量"
    )

    # ===== 承运商方确认 =====
    confirmed_by_carrier_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="承运商确认时间"
    )
    confirmed_by_carrier_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="承运商确认人姓名（自由文本）"
    )
    confirm_voucher_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="承运商回签凭证 URL"
    )
    carrier_contact_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="承运商对账联系人（冗余）"
    )
    carrier_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="承运商对账联系电话（冗余）"
    )

    # ===== 大额调整的业务主管审批（软门槛，文档 03 §3.5） =====
    adjust_approved_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="大额调整审批人 user_id"
    )
    adjust_approved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True,
        comment="大额调整审批时间；调整额再次变动会清空，需重新审批",
    )

    # ===== 一致性核对冗余计数（由 ConsistencyChecker 维护，列名与客户侧一致） =====
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
        comment="已强制放行差异条数（biz_recon_diff.status=3）",
    )

    # ===== 同承运商同周期唯一（条件唯一，同客户侧做法） =====
    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(80), nullable=True,
        comment="唯一键 carrier_id:period_start:period_end，"
                "仅非撤销且未删除时有值，撤销/软删置 NULL 释放占用",
    )

    @staticmethod
    def build_dedup_key(
        carrier_id: int,
        period_start: Optional[datetime],
        period_end: Optional[datetime],
    ) -> str:
        """构造同承运商同周期唯一键（周期为空时用 0 占位）。"""
        s = period_start.strftime("%Y%m%d") if period_start else "0"
        e = period_end.strftime("%Y%m%d") if period_end else "0"
        return f"{int(carrier_id)}:{s}:{e}"


class CarrierReconTaskLink(TenantModelBase):
    """承运商对账行（对账单 ↔ 任务单桥接，含预付扣减与快照）"""

    __tablename__ = "biz_carrier_recon_task_link"
    __table_args__ = (
        Index("idx_crtl_recon", "recon_id"),
        Index("idx_crtl_task", "task_id"),
        Index("idx_crtl_dirty", "recon_id", "recon_dirty"),
        Index("uk_crtl_dedup", "dedup_key", unique=True),
        {"comment": "承运商对账单-任务单桥接表（对账行）"},
    )
    __table_tier__ = "business"

    recon_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_carrier_recon.id"
    )
    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task.id"
    )
    task_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="任务单号（冗余）"
    )
    plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="车牌号（冗余，对账时承运商按车核对）"
    )

    # ===== 计费 =====
    billing_base: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="计费基础 1-按台 2-按吨 3-按趟 4-包车",
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default="0",
        comment="计费数量（按台=已交车台数 按趟/包车=1）",
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="单价（可手工覆盖）",
    )
    gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="行毛额 = quantity × unit_price + adjust_amount",
    )
    adjust_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="调整额（罚款、补价、油卡核销，可负）",
    )
    adjust_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="调整原因（有调整额时必填）"
    )
    prepaid_offset_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="任务级预付/补款已支付的扣减额（写入时快照，见文档 03 §3.6）",
    )
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="行净额 = gross_amount - prepaid_offset_amount（结算按此付款）",
    )

    # ===== 业务事实快照（写入时冻结，业务侧变更不回灌） =====
    carrier_cost_snapshot: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True,
        comment="写入时的 task.carrier_cost_amount 快照",
    )
    signed_quantity_snapshot: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="写入时已交车台数快照"
    )
    signed_at_snapshot: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="写入时任务实际到达时间快照"
    )
    locked_snapshot_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="快照冻结时间"
    )

    # ===== 脏标记（列名与客户侧一致，由核对器统一维护） =====
    recon_dirty: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否需重新核对 0-否 1-是（快照与业务事实已不一致）",
    )
    dirty_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="置脏原因"
    )
    dirty_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="置脏时间"
    )

    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键 recon_id:task_id，防重复挂接；移除行（软删）时置 NULL",
    )

    @staticmethod
    def build_dedup_key(recon_id: int, task_id: int) -> str:
        return f"{int(recon_id)}:{int(task_id)}"
