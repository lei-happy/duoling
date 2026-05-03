"""
OpenAI 兼容协议 LLM Provider

支持：通义千问（DashScope OpenAI 兼容模式）/ DeepSeek / OpenAI / Azure OpenAI 等。
"""

from __future__ import annotations

import json
from typing import AsyncIterator, Optional

from loguru import logger

from app.modules.ai.llm.base import (
    ChatChunk,
    ChatMessage,
    LLMProvider,
    ToolCall,
    ToolDefinition,
)


class OpenAICompatProvider(LLMProvider):
    """走 OpenAI 兼容 /chat/completions 协议的 Provider"""

    def __init__(
        self,
        code: str,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = 60,
        extra_params: Optional[dict] = None,
    ) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as e:
            raise RuntimeError(
                "未安装 openai 包，请执行 `pip install openai>=1.50.0`"
            ) from e

        self.code = code
        self.model = model
        self.extra_params = extra_params or {}

        client_kwargs: dict = {"api_key": api_key, "timeout": timeout}
        if base_url:
            client_kwargs["base_url"] = base_url
        self._client = AsyncOpenAI(**client_kwargs)

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        tools: Optional[list[ToolDefinition]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> AsyncIterator[ChatChunk]:
        request_kwargs: dict = {
            "model": kwargs.get("model") or self.model,
            "messages": [m.to_openai() for m in messages],
            "stream": True,
        }
        # 仅当 Provider 显式开启 include_usage 时才发 stream_options：
        # Kimi/Moonshot、Doubao 等厂商目前不支持该参数，默认带上会被 400 拒绝。
        # 在 ai_model_provider.extra_params 中可手动配置 {"include_usage": true} 启用。
        if self.extra_params.get("include_usage"):
            request_kwargs["stream_options"] = {"include_usage": True}
        if tools:
            request_kwargs["tools"] = [t.to_openai() for t in tools]
            request_kwargs["tool_choice"] = kwargs.get("tool_choice", "auto")

        # temperature：支持 Provider 级强制覆盖（fixed_temperature），
        # 用于 OpenAI o1 / Kimi K2.5/K2.6 这种只允许 temperature=1 的 thinking 模型
        fixed_temp = self.extra_params.get("fixed_temperature")
        if fixed_temp is not None:
            try:
                request_kwargs["temperature"] = float(fixed_temp)
            except (TypeError, ValueError):
                pass
        elif temperature is not None:
            request_kwargs["temperature"] = temperature

        if max_tokens is not None:
            request_kwargs["max_tokens"] = max_tokens

        # extra_params 中的其他键透传（控制开关不透传）
        _control_keys = {
            "include_usage",
            "fixed_temperature",
            "omit_params",
            "disable_tools",
        }
        for k, v in self.extra_params.items():
            if k in _control_keys:
                continue
            request_kwargs.setdefault(k, v)

        # disable_tools：某些模型不支持 tool_calls，可在 Provider 层关闭
        if self.extra_params.get("disable_tools"):
            request_kwargs.pop("tools", None)
            request_kwargs.pop("tool_choice", None)

        # omit_params：列出要从最终请求中剔除的字段（如 ["temperature","max_tokens"]）
        omit = self.extra_params.get("omit_params") or []
        if isinstance(omit, list):
            for k in omit:
                request_kwargs.pop(k, None)

        # 工具调用 delta 拼装缓冲：index -> {id, name, arguments}
        tool_buffer: dict[int, dict] = {}

        logger.info(
            f"[LLM] {self.code} model={request_kwargs['model']} "
            f"msgs={len(messages)} tools={len(tools or [])}"
        )
        try:
            stream = await self._client.chat.completions.create(**request_kwargs)
        except Exception as e:
            logger.exception(f"[LLM] 调用失败 provider={self.code}: {e!r}")
            raise

        async for chunk in stream:
            # 用量回报（部分实现仅在最后一个 chunk 给）
            if getattr(chunk, "usage", None):
                yield ChatChunk(
                    type="usage",
                    prompt_tokens=getattr(chunk.usage, "prompt_tokens", 0) or 0,
                    completion_tokens=getattr(chunk.usage, "completion_tokens", 0) or 0,
                )

            choices = getattr(chunk, "choices", None) or []
            for choice in choices:
                delta = getattr(choice, "delta", None)
                finish_reason = getattr(choice, "finish_reason", None)

                if delta is None:
                    if finish_reason:
                        # 推送已拼装好的 tool_calls
                        for idx in sorted(tool_buffer.keys()):
                            tc_data = tool_buffer[idx]
                            yield ChatChunk(
                                type="tool_call_done",
                                tool_call=ToolCall(
                                    id=tc_data.get("id") or f"call_{idx}",
                                    name=tc_data.get("name") or "",
                                    arguments=tc_data.get("arguments") or "{}",
                                ),
                            )
                        tool_buffer.clear()
                        yield ChatChunk(type="finish", finish_reason=finish_reason)
                    continue

                content = getattr(delta, "content", None)
                if content:
                    yield ChatChunk(type="delta", text=content)

                tool_calls = getattr(delta, "tool_calls", None) or []
                for tc in tool_calls:
                    idx = getattr(tc, "index", 0) or 0
                    buf = tool_buffer.setdefault(
                        idx, {"id": None, "name": None, "arguments": ""}
                    )
                    if getattr(tc, "id", None):
                        buf["id"] = tc.id
                    fn = getattr(tc, "function", None)
                    if fn is not None:
                        if getattr(fn, "name", None):
                            buf["name"] = fn.name
                        if getattr(fn, "arguments", None):
                            buf["arguments"] += fn.arguments

                if finish_reason:
                    for idx in sorted(tool_buffer.keys()):
                        tc_data = tool_buffer[idx]
                        yield ChatChunk(
                            type="tool_call_done",
                            tool_call=ToolCall(
                                id=tc_data.get("id") or f"call_{idx}",
                                name=tc_data.get("name") or "",
                                arguments=tc_data.get("arguments") or "{}",
                            ),
                        )
                    tool_buffer.clear()
                    yield ChatChunk(type="finish", finish_reason=finish_reason)

    async def close(self) -> None:
        try:
            await self._client.close()
        except Exception:
            pass


def safe_json_loads(s: str) -> dict:
    """安全解析 LLM 返回的 JSON 参数（容错空串/单引号等）"""
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        try:
            return json.loads(s.replace("'", '"'))
        except Exception:
            logger.warning(f"[LLM] 工具参数 JSON 解析失败: {s!r}")
            return {}
