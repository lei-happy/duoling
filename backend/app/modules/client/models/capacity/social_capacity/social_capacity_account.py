"""
社会运力 - 结算账户表（租户库）

与 biz_social_capacity 1:N 关联，一条社会运力可拥有多个结算账户。
同 social_capacity_id 内最多 1 条 is_default=1，应用层 + 索引双重保障。
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class SocialCapacityAccount(TenantModelBase):
    """社会运力结算账户"""

    __tablename__ = "biz_social_capacity_account"
    __table_args__ = (
        Index(
            "idx_account_social_capacity",
            "social_capacity_id",
            "is_default",
            "status",
        ),
        {"comment": "社会运力结算账户表"},
    )
    __table_tier__ = "business"

    social_capacity_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="关联 biz_social_capacity.id"
    )
    account_type: Mapped[int] = mapped_column(
        SmallInteger,
        nullable=False,
        comment="账户类型 1-银行卡 2-支付宝 3-微信 4-其他",
    )
    account_label: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True, comment="账户标签（主账户 / 油卡专用 等）"
    )
    account_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="户名"
    )
    account_no: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="账号 / 手机号"
    )
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开户行（仅银行卡）"
    )
    bank_branch: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开户支行（仅银行卡）"
    )
    holder_id_card: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, comment="持卡人身份证号（配偶卡 / 第三方代收场景）"
    )

    is_default: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        server_default="0",
        nullable=False,
        comment="是否默认 0-否 1-是；同社会运力内最多 1 条",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        server_default="1",
        nullable=False,
        comment="状态 0-停用 1-正常",
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )
