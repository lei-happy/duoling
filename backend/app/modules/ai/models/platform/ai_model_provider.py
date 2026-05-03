"""
LLM Provider 配置（平台库）
"""

from typing import Optional
from sqlalchemy import String, SmallInteger, Text, JSON, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.modules.ai.models._base import AiPlatformBase


class AiModelProvider(AiPlatformBase):
    """LLM Provider 配置

    支持 OpenAI 兼容协议（通义千问 / DeepSeek / OpenAI / Azure OpenAI 等）。
    api_key 字段使用对称加密存储，读出时由 services 层解密。
    """

    __tablename__ = "ai_model_provider"
    __table_args__ = (
        Index("idx_ai_provider_status", "status"),
        {"comment": "AI 模型 Provider 配置表"},
    )

    code: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="Provider 编码（如 default/qwen/deepseek）"
    )
    name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="Provider 名称"
    )
    provider_type: Mapped[str] = mapped_column(
        String(32),
        default="openai_compat",
        comment="Provider 类型 openai_compat/openai/azure_openai",
    )
    base_url: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="API Base URL"
    )
    api_key_encrypted: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="API Key（对称加密后存储）"
    )
    model_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="默认模型名（如 qwen-plus / deepseek-chat）"
    )
    extra_params: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="附加参数（JSON）"
    )
    timeout_seconds: Mapped[int] = mapped_column(
        Integer, default=60, comment="单次请求超时（秒）"
    )
    is_default: Mapped[int] = mapped_column(
        SmallInteger, default=0, comment="是否为默认 Provider 0-否 1-是"
    )
    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, comment="状态 0-停用 1-启用"
    )
