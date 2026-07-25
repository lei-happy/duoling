"""服务平台屏蔽名单（平台库）

「我不希望哪些企业看到我的挂牌」。屏蔽对被屏蔽方**静默**——它看不到自己被
屏蔽，也看不到对方的挂牌，不会收到任何提示。

``idx_eco_block_blocked`` 的字段顺序是为可见性过滤器服务的：查询「当前查看方
被哪些租户屏蔽了」时以 ``blocked_tenant_code`` 为条件。这个索引方向容易建反，
建反后 SQL 仍能跑通、结果集也非空，但语义完全相反且不报错，是典型静默 bug。
"""

from typing import Optional

from sqlalchemy import BigInteger, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.console.models.common.base import PlatformModelBase


class SysEcoBlockRule(PlatformModelBase):
    """服务平台屏蔽名单"""

    __tablename__ = "sys_eco_block_rule"
    __table_args__ = (
        UniqueConstraint("tenant_code", "blocked_tenant_code", name="uk_eco_block"),
        # 可见性过滤：以被屏蔽方（即查看方）为查询入口
        Index("idx_eco_block_blocked", "blocked_tenant_code", "tenant_code"),
        {"comment": "服务平台屏蔽名单"},
    )

    tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="设置方租户"
    )
    blocked_tenant_code: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="被屏蔽方租户"
    )
    blocked_tenant_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, comment="被屏蔽方企业名（快照）"
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="备注（仅设置方可见）"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="操作人 user_id"
    )
