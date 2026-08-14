"""企业银行账户（租户库）

**不继承** ``FinanceDocBaseMixin``——账户是主数据，不是单据：没有状态机、没有
审批、没有 doc_no。

取代文档 02 §4.5 的临时字典方案（`tenant_bank_account`）：字典存不了余额、存不了
经营主体归属、无法做收支流水归集（文档 10 §三）。

``balance`` 是**账面值不是银行真实余额**，只作出纳参考与超额提示依据；与银行实际
余额的差（手续费、利息、未入账）不追求自动对平，靠「余额校准」动作定期对齐。
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Integer, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.client.models.base import TenantModelBase


class BankAccount(TenantModelBase):
    """企业银行账户（主数据）"""

    __tablename__ = "biz_bank_account"
    __table_args__ = (
        Index("idx_bank_acct_entity", "enterprise_id", "status"),
        # 同一账号不重复建；软删后置 NULL 允许重建（同 dedup_key 套路）
        Index("uk_bank_acct_no", "dedup_key", unique=True),
        {"comment": "企业银行账户表（收付款账户主数据）"},
    )
    __table_tier__ = "business"

    enterprise_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False,
        comment="所属经营主体ID（biz_business_entity.id）",
    )
    account_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="账户名称（户名）"
    )
    account_no: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="银行账号"
    )
    bank_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="开户行全称"
    )
    bank_branch: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="支行"
    )
    account_type: Mapped[int] = mapped_column(
        SmallInteger, default=2, server_default="2",
        comment="账户类型 1-基本户 2-一般户 3-专用户 4-其他",
    )
    currency: Mapped[str] = mapped_column(
        String(8), default="CNY", server_default="CNY", comment="币种"
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(16, 2), default=0, server_default="0",
        comment="账面余额（由收付动作维护，非银行真实余额）",
    )
    usage_scope: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1",
        comment="用途 1-收付通用 2-仅收款 3-仅付款",
    )
    is_default_receive: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否该主体默认收款账户 0-否 1-是",
    )
    is_default_pay: Mapped[int] = mapped_column(
        SmallInteger, default=0, server_default="0",
        comment="是否该主体默认付款账户 0-否 1-是",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, server_default="1", comment="状态 0-停用 1-正常"
    )
    sort_order: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", comment="下拉排序"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注"
    )

    dedup_key: Mapped[Optional[str]] = mapped_column(
        String(60), nullable=True,
        comment="唯一键（账号），防同账号重复建档；软删时置 NULL 允许重建",
    )

    @staticmethod
    def build_dedup_key(account_no: str) -> str:
        return (account_no or "").strip()

    @property
    def account_no_masked(self) -> str:
        """账号脱敏：只留后四位，列表与下拉都用这个"""
        no = (self.account_no or "").strip()
        return f"****{no[-4:]}" if len(no) > 4 else no

    @property
    def display_label(self) -> str:
        """下拉与冗余快照统一用这个标签，避免各处拼法不一致"""
        parts = [p for p in (self.bank_name, self.account_no_masked) if p]
        return " ".join(parts) or self.account_name or ""
