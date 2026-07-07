"""
成本政策表（租户库）

成本政策是费用规则的归属载体，类比收入侧运价合同 biz_freight_contract。
可按全局默认 / 指定承运商 / 指定司机 / 指定运力划定适用范围与生效期。
"""

from typing import Optional
from datetime import date

from sqlalchemy import String, SmallInteger, BigInteger, Integer, Date, Index, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class CostPolicy(TenantModelBase):
    """成本政策"""

    __tablename__ = "biz_cost_policy"
    __table_args__ = (
        Index("uk_cost_policy_no", "policy_no", unique=True),
        Index("idx_cost_policy_scope", "scope_type", "scope_id"),
        Index("idx_cost_policy_status_date", "status", "effective_date", "expiry_date"),
        Index("idx_cost_policy_carrier_type", "carrier_type"),
        {"comment": "成本政策表"},
    )
    __table_tier__ = "business"

    policy_no: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="政策编号（租户内唯一）"
    )
    policy_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="政策名称"
    )

    scope_type: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="适用范围类型 0-全局默认 1-指定承运商 2-指定司机 3-指定运力",
    )
    scope_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True,
        comment="适用范围对象ID（承运商/司机/运力ID，scope_type=0时为空）",
    )

    carrier_type: Mapped[Optional[int]] = mapped_column(
        SmallInteger, nullable=True,
        comment="适用承运类型 1-自有车 2-承运商 3-社会运力，空表示不限",
    )

    effective_date: Mapped[date] = mapped_column(
        Date, nullable=False, comment="生效日期"
    )
    expiry_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, comment="失效日期（空表示长期）"
    )

    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, server_default=text("0"),
        comment="状态 0-草稿 1-生效 2-已过期 3-已终止",
    )
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0"),
        comment="政策级人工优先级（越大越优先）",
    )
    version_no: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1"),
        comment="政策版本号",
    )

    remark: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="备注"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="更新人"
    )
