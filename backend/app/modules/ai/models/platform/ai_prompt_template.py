"""
提示词模板（平台库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiPlatformBase


class AiPromptTemplate(AiPlatformBase):
    """提示词模板

    便于不重启发版即可调整数字员工 system prompt / 场景化提示。
    通过 {{variable}} 占位符在装配阶段渲染上下文。
    """

    __tablename__ = "ai_prompt_template"
    __table_args__ = (
        Index("idx_ai_prompt_scene", "scene"),
        {"comment": "提示词模板表"},
    )

    code: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="模板编码（全局唯一）"
    )
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="模板名称"
    )
    scene: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="role",
        comment="场景 system/role/scenario",
    )
    content: Mapped[str] = mapped_column(
        Text, nullable=False, comment="模板内容（支持 {{variable}} 占位）"
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="模板说明"
    )
    version: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="版本号（每次修改 +1）"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-启用"
    )
