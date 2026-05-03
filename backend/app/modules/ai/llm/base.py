"""
LLM Provider 抽象接口与统一数据结构

走 OpenAI 兼容协议：messages + tools + 流式 chunk + tool_calls。
具体实现见 openai_compat.py。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator, Optional


@dataclass
class ToolDefinition:
    """工具定义（提供给 LLM 的 function 协议条目）"""

    name: str
    description: str
    parameters: dict  # JSON Schema

    def to_openai(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description or "",
                "parameters": self.parameters or {"type": "object", "properties": {}},
            },
        }


@dataclass
class ToolCall:
    """LLM 返回的工具调用请求"""

    id: str
    name: str
    arguments: str  # JSON 字符串（按 OpenAI 协议）

    def to_openai(self) -> dict:
        return {
            "id": self.id,
            "type": "function",
            "function": {"name": self.name, "arguments": self.arguments or "{}"},
        }


@dataclass
class ChatMessage:
    """对话消息（统一结构）"""

    role: str  # system/user/assistant/tool
    content: Optional[str] = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: Optional[str] = None
    name: Optional[str] = None  # 工具消息时为工具名

    def to_openai(self) -> dict:
        msg: dict[str, Any] = {"role": self.role}
        if self.content is not None:
            msg["content"] = self.content
        if self.tool_calls:
            msg["tool_calls"] = [tc.to_openai() for tc in self.tool_calls]
        if self.tool_call_id:
            msg["tool_call_id"] = self.tool_call_id
        if self.name:
            msg["name"] = self.name
        return msg


@dataclass
class ChatChunk:
    """流式 chunk（SSE delta）

    type 取值：
    - delta             : 普通文本 delta
    - tool_call_delta   : 工具调用 delta（参数边推边来）
    - tool_call_done    : 单次工具调用拼装完毕
    - finish            : 一轮 LLM 输出结束（带 finish_reason）
    - usage             : 用量回报
    """

    type: str
    text: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    finish_reason: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMProvider(ABC):
    """LLM Provider 抽象基类"""

    code: str = "default"
    model: str = ""

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[ChatMessage],
        tools: Optional[list[ToolDefinition]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[ChatChunk]:
        """流式对话；产出 ChatChunk"""
        if False:  # pragma: no cover
            yield  # 仅用于让类型识别为 async generator

    async def close(self) -> None:
        """资源清理（HTTP client）"""
