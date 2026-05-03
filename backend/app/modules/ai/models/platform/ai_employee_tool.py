"""
数字员工 ↔ 工具 多对多绑定（平台库）
"""

from typing import Optional
from sqlalchemy import BigInteger, SmallInteger, String, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiPlatformBase


class AiEmployeeTool(AiPlatformBase):
    """数字员工与工具的绑定关系"""

    __tablename__ = "ai_employee_tool"
    __table_args__ = (
        UniqueConstraint("employee_id", "tool_id", name="uk_ai_emp_tool"),
        Index("idx_ai_et_emp", "employee_id"),
        Index("idx_ai_et_tool", "tool_id"),
        {"comment": "数字员工-工具绑定表"},
    )

    employee_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="数字员工ID"
    )
    tool_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, comment="工具ID"
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="工具排序"
    )
    enabled: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="是否启用 0-禁用 1-启用"
    )
    custom_description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="自定义描述（覆盖默认描述，便于角色化提示）",
    )
