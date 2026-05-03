"""
数字员工角色定义（平台库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiPlatformBase


class AiEmployee(AiPlatformBase):
    """数字员工角色

    平台预置 + 运营端可视化扩展。一个数字员工对应一种岗位职责
    （如录单员、数据分析员、档案管理员），绑定若干工具构成能力闭环。
    """

    __tablename__ = "ai_employee"
    __table_args__ = (
        Index("idx_ai_emp_status", "status"),
        Index("idx_ai_emp_feature", "feature_code"),
        {"comment": "数字员工角色定义表"},
    )

    code: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="员工编码（全局唯一）"
    )
    name: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="员工名称（如：录单员小智）"
    )
    employee_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="custom",
        comment="员工类型 form_recorder/data_analyst/archivist/custom",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="员工简介（用户侧可见）"
    )
    avatar: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="头像 URL 或预置 icon code"
    )
    system_prompt: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="系统提示词（可引用 ai_prompt_template）"
    )
    welcome_message: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True, comment="欢迎语，新会话首条 assistant 消息"
    )
    suggested_questions: Mapped[Optional[list]] = mapped_column(
        JSON, nullable=True, comment="建议提问列表（JSON 数组）"
    )
    model_config_json: Mapped[Optional[dict]] = mapped_column(
        "model_config",
        JSON,
        nullable=True,
        comment=(
            "模型相关配置 {provider_code, model, temperature, max_tokens, "
            "max_tool_loops, context_window}"
        ),
    )
    feature_code: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="关联产品功能编码（用于版本控制；为空则随 ai_assistant 总开关）",
    )
    sort_order: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="排序号"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-启用"
    )
