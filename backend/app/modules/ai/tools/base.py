"""
工具基础类型定义

ToolContext  : 工具运行时上下文（含 tenant Session、当前用户、当前会话）
ToolResult   : 工具执行结果（统一返回结构）
ToolSpec     : 工具规约（与 LLM function 协议、ai_tool 表对齐）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Optional, Type, TYPE_CHECKING

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenData

if TYPE_CHECKING:
    from app.modules.ai.models.tenant.biz_ai_session import BizAiSession


@dataclass
class ToolContext:
    """工具运行时上下文（每次调用注入）"""

    db: AsyncSession  # 当前租户库 Session
    platform_db: AsyncSession  # 平台库 Session
    user: TokenData  # 当前登录用户
    tenant_code: str
    session: Optional["BizAiSession"] = None  # 当前 AI 会话
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    """工具执行结果"""

    success: bool = True
    data: Any = None
    message: str = ""
    error: Optional[str] = None

    def to_llm_payload(self) -> dict:
        """转成给 LLM 的 tool message content"""
        if self.success:
            return {"ok": True, "data": self.data, "message": self.message}
        return {"ok": False, "error": self.error or self.message}


# 工具实现函数签名: (ctx, **kwargs) -> Awaitable[ToolResult|dict|Any]
ToolHandler = Callable[..., Awaitable[Any]]


@dataclass
class ToolSpec:
    """工具规约（注册表条目）"""

    code: str
    name: str
    category: str
    description: str
    params_schema: Type[BaseModel]
    handler: ToolHandler
    required_permission: Optional[str] = None
    risk_level: str = "low"  # low / medium / high
    confirm_required: bool = False

    def json_schema(self) -> dict:
        """从 Pydantic schema 转 JSON Schema（OpenAI function 协议用）"""
        try:
            schema = self.params_schema.model_json_schema()
        except Exception:
            schema = {"type": "object", "properties": {}}
        # OpenAI function 协议要求至少有 type=object
        schema.setdefault("type", "object")
        schema.pop("title", None)
        # 递归清理 title 字段（部分 LLM 不识别）
        _strip_titles(schema)
        return schema


def _strip_titles(node: Any) -> None:
    if isinstance(node, dict):
        node.pop("title", None)
        for v in node.values():
            _strip_titles(v)
    elif isinstance(node, list):
        for v in node:
            _strip_titles(v)


class EmptyParams(BaseModel):
    """无参数工具的占位 schema"""
