"""自有司机工资单（租户库）

一段周期内某司机的薪资发放总单（文档 04 §3.2）。三张表分工：

- ``biz_driver_payroll``：主表，存周期、薪资模型、五个金额合计与发放账户；
- ``biz_driver_payroll_task_link``：任务提成行，按签收台数 × 单价聚合；
- ``biz_driver_payroll_item``：工资项，底薪 / 补贴 / 扣款 / 抵账各占一行。

金额口径（钉死，避免各处口算出不同结果）：

    gross_amount = total_base_amount + total_commission_amount
    net_amount   = gross_amount - total_deduction_amount - total_prepaid_offset_amount

``total_prepaid_offset_amount`` 是本周期已通过任务级预付 / 补款付给该司机的钱，写
入时快照；预付单事后撤销不回灌，差额靠手工工资项补回（事实快照原则，同承运商侧）。

工资单与承运商对账不同，**不接一致性核对器**：司机侧没有「跟对方核对台数」的动作，
业务侧改动通过 ``task.is_payroll_bound`` 软锁直接拦住，不需要差异台账。
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

DRIVER_PAYROLL_DOC_KIND = "driver_payroll"


class DriverPayroll(FinanceDocBaseMixin, TenantModelBase):
    """司机工资单主表"""

    __tablename__ = "biz_driver_payroll"
    __table_args__ = (
        Index("idx_dpay_driver_status", "driver_id", "status"),
        Index("idx_dpay_period", "period_start", "period_end"),
        Index("idx_dpay_status", "status"),
        Index("idx_dpay_enterprise", "enterprise_id"),
        Index("uk_dpay_period_dedup", "dedup_key", unique=True),
        {"comment": "自有司机工资单主表"},
    )
    __table_tier__ = "business"

    doc_kind: Mapped[str] = mapped_column(
        String(30),
        default=DRIVER_PAYROLL_DOC_KIND,
        server_default=DRIVER_PAYROLL_DOC_KIND,
        nullable=False,
        comment="单据大类（固定 driver_payroll）",
    )
    direction: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="收/付方向（应付固定 2-付款）",
    )

    # ===== 司机与归属 =====
    driver_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_driver.id"
    )
    driver_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="司机姓名（冗余）"
    )
    driver_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="司机手机号（冗余）"
    )
    enterprise_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="人力成本归属经营主体ID"
    )

    # ===== 薪资模型与周期 =====
    payroll_model: Mapped[int] = mapped_column(
        SmallInteger, default=3, server_default="3",
        comment="薪资模型 1-月薪固定 2-计件提成 3-混合（底薪+提成）",
    )
    period_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="发放周期 1-月薪 2-周薪 3-趟薪",
    )

    # ===== 合计（冗余，列表页与工资条直接取） =====
    task_count: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="关联任务数"
    )
    total_signed_quantity: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="已交车总台数"
    )
    total_commission_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="任务提成合计（来自任务提成行）",
    )
    total_base_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="底薪与补贴合计（工资项 category=1 应发项，不含提成汇总项）",
    )
    total_deduction_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="扣减与抵账合计（工资项 category=2/3）",
    )
    total_prepaid_offset_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="本周期已发放的任务级预付/补款合计（扣减项，写入时快照）",
    )
    gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="应发合计 = total_base_amount + total_commission_amount",
    )
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=0, server_default="0",
        comment="实发合计 = 应发 - 扣减 - 预付抵扣（可为负，下期结转）",
    )

    # ===== 发放账户 =====
    account_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="发薪账户（biz_driver_account.id）"
    )
    account_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="账户类型快照 1-银行卡 2-油气款 3-积分",
    )
    account_name_snapshot: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="账户名快照"
    )
    account_no_masked: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="账户号脱敏快照"
    )
    payslip_pdf_url: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="工资条 PDF URL（远期自动生成）"
    )

    # ===== 同司机同周期唯一（条件唯一，同对账类做法） =====
    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(80), nullable=True,
        comment="唯一键 driver_id:period_start:period_end，"
                "撤销/软删置 NULL 释放占用",
    )

    @staticmethod
    def build_dedup_key(
        driver_id: int,
        period_start: Optional[datetime],
        period_end: Optional[datetime],
    ) -> str:
        s = period_start.strftime("%Y%m%d") if period_start else "0"
        e = period_end.strftime("%Y%m%d") if period_end else "0"
        return f"{int(driver_id)}:{s}:{e}"


class DriverPayrollTaskLink(TenantModelBase):
    """任务提成行（工资单 ↔ 任务单桥接）"""

    __tablename__ = "biz_driver_payroll_task_link"
    __table_args__ = (
        Index("idx_dptl_payroll", "payroll_id"),
        Index("idx_dptl_task", "task_id"),
        Index("uk_dptl_dedup", "dedup_key", unique=True),
        {"comment": "司机工资单-任务单桥接表（任务提成行）"},
    )
    __table_tier__ = "business"

    payroll_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_driver_payroll.id"
    )
    task_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_task.id"
    )
    task_no: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="任务单号（冗余）"
    )
    plate_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="车牌号（冗余）"
    )
    signed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="交车时间快照（工资条按此排序）"
    )

    billing_base: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="计件基础 1-按台 2-按吨 3-按趟",
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default="0",
        comment="计件数量（按台=已交车台数）",
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0", comment="计件单价"
    )
    commission_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="该任务提成 = quantity × unit_price + adjust_amount",
    )
    adjust_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="调整额（绩效折扣、罚款，可负）",
    )
    adjust_reason: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="调整原因（有调整额时必填）"
    )

    signed_quantity_snapshot: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="写入时已交车台数快照"
    )
    locked_snapshot_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True, comment="快照冻结时间"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键 payroll_id:task_id，防重复挂接；移除行时置 NULL",
    )

    @staticmethod
    def build_dedup_key(payroll_id: int, task_id: int) -> str:
        return f"{int(payroll_id)}:{int(task_id)}"


class DriverPayrollItem(TenantModelBase):
    """工资项明细（底薪 / 补贴 / 扣款 / 抵账）"""

    __tablename__ = "biz_driver_payroll_item"
    __table_args__ = (
        Index("idx_dpi_payroll", "payroll_id", "category"),
        {"comment": "司机工资单工资项明细表"},
    )
    __table_tier__ = "business"

    payroll_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_driver_payroll.id"
    )
    item_type: Mapped[str] = mapped_column(
        String(30), nullable=False,
        comment="工资项编码 base_salary/attendance/commission_total/oil_subsidy/"
                "meal_subsidy/safety_award/fine/social_insurance/oil_card_offset/"
                "other_deduction/other_addition",
    )
    item_name: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="工资项名称（冗余，工资条直接展示）"
    )
    category: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="分类 1-应发项（加项） 2-扣减项 3-抵账项",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=0, server_default="0",
        comment="项目金额（一律填正数，加减由 category 决定）",
    )
    formula: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True,
        comment="计算说明（如「出勤 22 天 × 150 元/天」），工资条展示用",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="排序"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
