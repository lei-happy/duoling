"""
任务预警阈值规则表（租户库）

预警阈值采用三层模型，本表承载后两层：

1. 规则类型内置默认值 —— 代码常量（``alert_rule_catalog``），永不为空，开箱可用
2. **租户默认阈值** —— 本表中所有 scope 列为空的记录，一个 rule_code 至多一条
3. **维度覆盖规则** —— 本表中带 scope 限定的记录，命中最特化的一条

维度用独立列而不是 ``conditions_json`` 条件树：预警阈值是运营人员日常自助
维护的对象，配置门槛必须低于计费规则。需要更复杂组合时再考虑升级。

与计费规则的一个刻意分叉：同分冲突时本表**不抛异常**，按
``rule_version`` → ``id`` 兜底选取并继续出警。预警漏报的代价远大于误报，
不能因为配置写重了就整片不报警。
"""

from datetime import date
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Date,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase

# ---- 时间基准：由 plan_enabled / required_enabled 派生，保留兼容读写 ----
TIME_BASIS_PLAN = 0      # 只看内部计划时间
TIME_BASIS_REQUIRED = 1  # 只看客户要求时间
TIME_BASIS_EARLIEST = 2  # 两路都开，谁先碰到阈值听谁的

TIME_BASIS_LABELS: dict[int, str] = {
    TIME_BASIS_PLAN: "内部计划时间",
    TIME_BASIS_REQUIRED: "客户要求时间",
    TIME_BASIS_EARLIEST: "两路都看",
}


def clocks_from_time_basis(time_basis: int) -> tuple[int, int]:
    """time_basis → (plan_enabled, required_enabled)。"""
    if time_basis == TIME_BASIS_PLAN:
        return 1, 0
    if time_basis == TIME_BASIS_REQUIRED:
        return 0, 1
    return 1, 1


def time_basis_from_clocks(plan_enabled: int, required_enabled: int) -> int:
    """(plan_enabled, required_enabled) → time_basis。"""
    if plan_enabled and required_enabled:
        return TIME_BASIS_EARLIEST
    if required_enabled:
        return TIME_BASIS_REQUIRED
    return TIME_BASIS_PLAN

RULE_STATUS_DISABLED = 0
RULE_STATUS_ENABLED = 1


class TaskAlertRule(TenantModelBase):
    """任务预警阈值规则"""

    __tablename__ = "biz_task_alert_rule"
    __table_args__ = (
        Index("idx_tar_code_status", "rule_code", "status"),
        Index("idx_tar_customer", "customer_id"),
        {"comment": "任务预警阈值规则表"},
    )
    __table_tier__ = "business"

    rule_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="规则码，见 alert_rule_catalog"
    )
    rule_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="规则名称（便于列表识别，空则取类型名）"
    )
    stage: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="限定阶段（仅 STAGE_STAGNANT 需要逐阶段配置；其余规则码阶段已隐含，留空）",
    )

    # ===== 适用范围（全空 = 租户默认阈值）=====
    customer_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="客户 ID（任务任一挂接运单命中即生效）"
    )
    customer_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="客户类型 0-主机厂 1-贸易商 2-经销商 3-个人 4-其他",
    )
    origin_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="出发地行政区 ID（支持向上匹配）"
    )
    destination_region_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="目的地行政区 ID（支持向上匹配）"
    )
    distance_min: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="里程下限（公里，含）"
    )
    distance_max: Mapped[Optional[float]] = mapped_column(
        Numeric(10, 2), nullable=True, comment="里程上限（公里，不含）"
    )
    brand_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="商品车品牌 ID"
    )
    series_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="商品车车系 ID"
    )
    carrier_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True, comment="承运方式 1-自有车 2-承运商 3-社会运力"
    )

    # ===== 阈值 =====
    time_basis: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=TIME_BASIS_EARLIEST,
        server_default=text("2"),
        comment="时间基准（派生）0-只看内部 1-只看客户 2-两路都看",
    )
    plan_enabled: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="是否启用内部计划时间这一路 0-关 1-开",
    )
    required_enabled: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="是否启用客户要求时间这一路 0-关 1-开",
    )
    anchor_offset_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True,
        comment="锚点允许时长（分钟）：DEPART/DELIVER 类以「实际装车/到达时间 + 本值」为应完成时间",
    )
    warn_ahead_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="相对内部计划：提前多少分钟进入「关注」"
    )
    critical_after_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="相对内部计划：超时多少分钟升「严重」"
    )
    warn_ahead_required_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="相对客户要求：提前多少分钟进入「关注」"
    )
    critical_after_required_minutes: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="相对客户要求：超时多少分钟升「严重」"
    )
    stagnant_hours: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, comment="阶段滞留阈值（小时，仅 STAGE_STAGNANT 使用）"
    )

    # ===== 治理 =====
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="人工优先级，直接累加到特异度得分",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=RULE_STATUS_ENABLED,
        server_default=text("1"), comment="状态 0-停用 1-启用",
    )
    effective_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="生效日期（空=立即生效）"
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="失效日期（空=长期有效）"
    )
    rule_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="规则版本号（每次编辑 +1，同分冲突时的 tie-break 依据）",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )

    def has_scope(self) -> bool:
        """是否为带维度限定的覆盖规则（否则即租户默认阈值）。"""
        return any(
            v is not None
            for v in (
                self.customer_id,
                self.customer_type,
                self.origin_region_id,
                self.destination_region_id,
                self.distance_min,
                self.distance_max,
                self.brand_id,
                self.series_id,
                self.carrier_type,
            )
        )
