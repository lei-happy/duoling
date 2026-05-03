"""
工具元数据（平台库）

工具实现存在于代码（@register_tool），表里只记元数据用于：
1) Console 端展示与启停；
2) 数字员工 ↔ 工具绑定的外键载体；
3) 与代码注册表对账（启动时 upsert）。
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiPlatformBase


class AiTool(AiPlatformBase):
    """AI 工具元数据"""

    __tablename__ = "ai_tool"
    __table_args__ = (
        Index("idx_ai_tool_category", "category"),
        Index("idx_ai_tool_status", "status"),
        {"comment": "AI 工具元数据表"},
    )

    code: Mapped[str] = mapped_column(
        String(128),
        unique=True,
        nullable=False,
        comment="工具编码（全局唯一，与 @register_tool 装饰器 code 一致）",
    )
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="工具名称（人类可读）"
    )
    category: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment="工具分类 waybill/vehicle/customer/file/...",
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="工具描述（提供给 LLM 的 function description）"
    )
    params_schema: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="工具入参 JSON Schema（OpenAI function 协议用）",
    )
    required_permission: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        comment="需要的菜单权限码（对应 sys_menu.menu_code，如 biz:waybill:list）",
    )
    risk_level: Mapped[str] = mapped_column(
        String(16),
        default="low",
        comment="风险等级 low/medium/high",
    )
    confirm_required: Mapped[int] = mapped_column(
        SmallInteger,
        default=0,
        comment="是否需要用户在前端确认后再执行 0-否 1-是",
    )
    is_builtin: Mapped[int] = mapped_column(
        SmallInteger,
        default=1,
        comment="是否代码内置 1-是（@register_tool 反射）0-否（远期 DB 自定义）",
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-启用"
    )
