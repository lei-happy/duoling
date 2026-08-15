"""能源风控规则（租户库）"""

from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import JSON, Numeric, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class EnergyRule(TenantModelBase):
    """能源风控规则（阈值可配）"""

    __tablename__ = "biz_energy_rule"
    __table_args__ = (
        {"comment": "能源风控规则表"},
    )
    __table_tier__ = "business"

    rule_code: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="规则编码 OVER_TANK/REPEAT_FILL/..."
    )
    rule_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="规则名称"
    )
    energy_type: Mapped[Optional[str]] = mapped_column(
        String(16), nullable=True, comment="适用能源类型，空表示全部"
    )
    threshold_value: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 4), nullable=True, comment="主阈值（容量倍数/分钟/偏离比例）"
    )
    extra_config_json: Mapped[Optional[Any]] = mapped_column(
        JSON, nullable=True, comment="扩展配置"
    )
    risk_level: Mapped[str] = mapped_column(
        String(16), nullable=False, default="MEDIUM",
        server_default=text("'MEDIUM'"),
        comment="风险等级 LOW/MEDIUM/HIGH",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=1, server_default=text("1"),
        comment="状态 0-停用 1-启用",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
