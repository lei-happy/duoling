"""
会话编排器（Orchestrator）

负责：
1) 装配 system / role / scenario 三段 Prompt
2) 加载历史消息 → 调 LLM → 边推 SSE 边累积 assistant 文本
3) 当 LLM 返回 tool_calls 时：
   - 经 PermissionGuard 校验
   - 高风险动作：写 pending_confirm 日志，向前端推 confirm.required 事件并暂停（返回流末尾）
   - 普通工具：进程内直调 → 结果作为 tool 消息加入对话 → 进入下一轮 LLM
4) 落库 biz_ai_message + 更新 biz_ai_session 计数
"""

from __future__ import annotations

import json
import time
import uuid
from typing import AsyncIterator, Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException, PermissionException
from app.modules.ai.engine.context import ContextManager
from app.modules.ai.engine.prompt_builder import PromptBuilder
from app.modules.ai.engine.runtime_context import EngineContext
from app.modules.ai.engine.streaming import sse_pack
from app.modules.ai.llm.base import ChatChunk, ChatMessage, ToolCall, ToolDefinition
from app.modules.ai.llm.openai_compat import safe_json_loads
from app.modules.ai.models.platform.ai_employee_tool import AiEmployeeTool
from app.modules.ai.models.platform.ai_tool import AiTool
from app.modules.ai.models.tenant.biz_ai_message import BizAiMessage
from app.modules.ai.models.tenant.biz_ai_session import BizAiSession
from app.modules.ai.models.tenant.biz_ai_tool_call_log import BizAiToolCallLog
from app.modules.ai.security.desensitize import desensitize_obj
from app.modules.ai.security.permission_guard import PermissionGuard
from app.modules.ai.tools.base import ToolContext, ToolResult, ToolSpec
from app.modules.ai.tools.registry import (
    decode_tool_name,
    encode_tool_name,
    get_registry,
    serialize_for_log,
)


class Orchestrator:
    """会话编排器（每次对话一个实例）"""

    def __init__(self, ctx: EngineContext) -> None:
        self.ctx = ctx
        self._registry = get_registry()

    # ============ 入口 ============

    async def run(self, user_message: str, attachments: Optional[list] = None) -> AsyncIterator[str]:
        """主流程；返回 SSE 字符串迭代器"""

        # 1) 用户消息落库
        user_msg_row = await self._persist_user_message(user_message, attachments)
        yield sse_pack(
            "message",
            {"role": "user", "message_id": user_msg_row.id, "content": user_message},
        )

        # 2) 装配 messages
        history = await ContextManager.load_history_messages(
            self.ctx.tenant_db,
            self.ctx.session.id,
            max_messages=self.ctx.context_window,
        )
        system_msgs = await PromptBuilder.build_system_messages(self.ctx)
        messages: list[ChatMessage] = system_msgs + history

        # 3) 准备工具定义
        tool_defs = await self._prepare_tool_definitions()

        # 4) 多轮 LLM 循环（含工具调用）
        loops = 0
        while loops < self.ctx.max_tool_loops:
            loops += 1

            assistant_text_parts: list[str] = []
            pending_tool_calls: list[ToolCall] = []
            finish_reason: Optional[str] = None
            prompt_tokens, completion_tokens = 0, 0

            async for chunk in self.ctx.provider.chat_stream(
                messages=messages,
                tools=tool_defs or None,
                temperature=self.ctx.temperature,
                max_tokens=self.ctx.max_tokens,
            ):
                if chunk.type == "delta" and chunk.text:
                    assistant_text_parts.append(chunk.text)
                    yield sse_pack("delta", {"content": chunk.text})
                elif chunk.type == "tool_call_done" and chunk.tool_call:
                    pending_tool_calls.append(chunk.tool_call)
                elif chunk.type == "usage":
                    prompt_tokens = chunk.prompt_tokens
                    completion_tokens = chunk.completion_tokens
                elif chunk.type == "finish":
                    finish_reason = chunk.finish_reason

            assistant_text = "".join(assistant_text_parts)

            # 落 assistant 消息
            assistant_msg = await self._persist_assistant_message(
                content=assistant_text or None,
                tool_calls=pending_tool_calls,
                finish_reason=finish_reason,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )

            # 把 assistant 加进 messages 上下文
            messages.append(
                ChatMessage(
                    role="assistant",
                    content=assistant_text or None,
                    tool_calls=pending_tool_calls,
                )
            )

            # 没有工具调用 → 结束
            if not pending_tool_calls:
                yield sse_pack(
                    "done",
                    {
                        "message_id": assistant_msg.id,
                        "finish_reason": finish_reason or "stop",
                        "usage": {
                            "prompt_tokens": prompt_tokens,
                            "completion_tokens": completion_tokens,
                        },
                    },
                )
                return

            # 处理工具调用：可能产生 confirm.required 而提前结束本轮 SSE
            should_pause = False
            for tool_call in pending_tool_calls:
                async for evt in self._dispatch_tool_call(
                    tool_call, assistant_msg.id, messages
                ):
                    if evt == "__PAUSE__":
                        should_pause = True
                    else:
                        yield evt

            if should_pause:
                yield sse_pack(
                    "done",
                    {
                        "message_id": assistant_msg.id,
                        "finish_reason": "confirm_required",
                    },
                )
                return

            # 否则进入下一轮 LLM 推理
            continue

        # 超过最大轮次
        yield sse_pack(
            "error",
            {"message": f"工具调用超过最大轮次（{self.ctx.max_tool_loops}），已中止"},
        )

    # ============ 工具分发 ============

    async def _dispatch_tool_call(
        self,
        tool_call: ToolCall,
        assistant_message_id: int,
        messages: list[ChatMessage],
    ) -> AsyncIterator[str]:
        # tool_call.name 是 LLM wire 名（已编码），先还原成业务 code 查注册表
        wire_name = tool_call.name
        code = decode_tool_name(wire_name)
        spec = self._registry.get(code)
        if spec is None:
            err_text = f"未注册的工具: {code}"
            await self._persist_tool_log(
                tool_call=tool_call,
                spec=None,
                params={},
                status="failed",
                error=err_text,
                latency_ms=0,
                assistant_message_id=assistant_message_id,
            )
            await self._persist_tool_message(tool_call, {"error": err_text}, name=wire_name)
            messages.append(
                ChatMessage(
                    role="tool",
                    tool_call_id=tool_call.id,
                    name=wire_name,
                    content=json.dumps({"error": err_text}, ensure_ascii=False),
                )
            )
            yield sse_pack(
                "tool.result",
                {
                    "tool_call_id": tool_call.id,
                    "tool_code": code,
                    "status": "failed",
                    "error": err_text,
                },
            )
            return

        params = safe_json_loads(tool_call.arguments)
        yield sse_pack(
            "tool.call",
            {
                "tool_call_id": tool_call.id,
                "tool_code": spec.code,
                "tool_name": spec.name,
                "params": desensitize_obj(params),
                "risk_level": spec.risk_level,
            },
        )

        # 权限校验
        try:
            await PermissionGuard.check(
                ctx=ToolContext(
                    db=self.ctx.tenant_db,
                    platform_db=self.ctx.platform_db,
                    user=self.ctx.user,
                    tenant_code=self.ctx.tenant_code,
                    session=self.ctx.session,
                ),
                spec=spec,
                employee_code=self.ctx.employee.code,
            )
        except PermissionException as e:
            await self._persist_tool_log(
                tool_call=tool_call,
                spec=spec,
                params=params,
                status="denied",
                error=e.message,
                latency_ms=0,
                assistant_message_id=assistant_message_id,
            )
            payload = {"error": e.message}
            await self._persist_tool_message(tool_call, payload, name=wire_name)
            messages.append(
                ChatMessage(
                    role="tool",
                    tool_call_id=tool_call.id,
                    name=wire_name,
                    content=json.dumps(payload, ensure_ascii=False),
                )
            )
            yield sse_pack(
                "tool.result",
                {
                    "tool_call_id": tool_call.id,
                    "tool_code": spec.code,
                    "status": "denied",
                    "error": e.message,
                },
            )
            return

        # 高风险确认
        if spec.confirm_required or spec.risk_level == "high":
            confirm_token = uuid.uuid4().hex
            await self._persist_tool_log(
                tool_call=tool_call,
                spec=spec,
                params=params,
                status="pending_confirm",
                error=None,
                latency_ms=0,
                assistant_message_id=assistant_message_id,
                confirm_token=confirm_token,
            )
            yield sse_pack(
                "confirm.required",
                {
                    "tool_call_id": tool_call.id,
                    "tool_code": spec.code,
                    "tool_name": spec.name,
                    "params": desensitize_obj(params),
                    "confirm_token": confirm_token,
                    "risk_level": spec.risk_level,
                    "tip": (
                        "该操作风险较高，请确认后再执行。"
                        "可在前端调用 /api/client/ai/chat/confirm 完成确认。"
                    ),
                },
            )
            yield "__PAUSE__"
            return

        # 直接执行
        async for evt in self._execute_tool(
            tool_call, spec, params, assistant_message_id, messages
        ):
            yield evt

    async def _execute_tool(
        self,
        tool_call: ToolCall,
        spec: ToolSpec,
        params: dict,
        assistant_message_id: int,
        messages: list[ChatMessage],
    ) -> AsyncIterator[str]:
        started = time.perf_counter()
        try:
            tool_ctx = ToolContext(
                db=self.ctx.tenant_db,
                platform_db=self.ctx.platform_db,
                user=self.ctx.user,
                tenant_code=self.ctx.tenant_code,
                session=self.ctx.session,
                extras={
                    "model_config": self.ctx.model_config,
                    "employee_code": self.ctx.employee.code,
                },
            )
            raw = await spec.handler(tool_ctx, **params)
            result: ToolResult
            if isinstance(raw, ToolResult):
                result = raw
            elif isinstance(raw, dict):
                result = ToolResult(success=True, data=raw)
            else:
                result = ToolResult(success=True, data={"value": raw})
        except Exception as e:  # noqa: BLE001
            logger.exception(f"[Orchestrator] 工具 {spec.code} 执行异常: {e!r}")
            result = ToolResult(success=False, error=f"{type(e).__name__}: {e}")
        latency_ms = int((time.perf_counter() - started) * 1000)

        payload = result.to_llm_payload()
        await self._persist_tool_log(
            tool_call=tool_call,
            spec=spec,
            params=params,
            status="success" if result.success else "failed",
            error=result.error if not result.success else None,
            latency_ms=latency_ms,
            assistant_message_id=assistant_message_id,
            result_summary=serialize_for_log(payload),
        )
        # tool 消息回包给 LLM 时 name 必须与 assistant.tool_calls 中的 wire name 一致
        wire_name = tool_call.name
        await self._persist_tool_message(tool_call, payload, name=wire_name)
        messages.append(
            ChatMessage(
                role="tool",
                tool_call_id=tool_call.id,
                name=wire_name,
                content=json.dumps(
                    desensitize_obj(payload), ensure_ascii=False, default=str
                ),
            )
        )
        yield sse_pack(
            "tool.result",
            {
                "tool_call_id": tool_call.id,
                "tool_code": spec.code,
                "status": "success" if result.success else "failed",
                "latency_ms": latency_ms,
                "summary": serialize_for_log(desensitize_obj(payload))[:500],
            },
        )

    # ============ 持久化 ============

    async def _persist_user_message(
        self, content: str, attachments: Optional[list]
    ) -> BizAiMessage:
        msg = BizAiMessage(
            session_id=self.ctx.session.id,
            role="user",
            content=content,
            attachments=attachments or None,
            status=1,
        )
        self.ctx.tenant_db.add(msg)
        await self.ctx.tenant_db.flush()

        self.ctx.session.message_count = (self.ctx.session.message_count or 0) + 1
        from datetime import datetime as _dt

        self.ctx.session.last_message_at = _dt.now()
        if not self.ctx.session.title:
            self.ctx.session.title = content[:40]
        await self.ctx.tenant_db.flush()
        await self.ctx.tenant_db.commit()
        return msg

    async def _persist_assistant_message(
        self,
        content: Optional[str],
        tool_calls: list[ToolCall],
        finish_reason: Optional[str],
        prompt_tokens: int,
        completion_tokens: int,
    ) -> BizAiMessage:
        tc_payload = (
            [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in tool_calls
            ]
            if tool_calls
            else None
        )
        msg = BizAiMessage(
            session_id=self.ctx.session.id,
            role="assistant",
            content=content,
            tool_calls=tc_payload,
            model_used=self.ctx.provider.model,
            prompt_tokens=prompt_tokens or 0,
            completion_tokens=completion_tokens or 0,
            finish_reason=finish_reason,
            status=1,
        )
        self.ctx.tenant_db.add(msg)
        await self.ctx.tenant_db.flush()

        self.ctx.session.message_count = (self.ctx.session.message_count or 0) + 1
        self.ctx.session.total_prompt_tokens = (
            (self.ctx.session.total_prompt_tokens or 0) + (prompt_tokens or 0)
        )
        self.ctx.session.total_completion_tokens = (
            (self.ctx.session.total_completion_tokens or 0) + (completion_tokens or 0)
        )
        from datetime import datetime as _dt

        self.ctx.session.last_message_at = _dt.now()
        await self.ctx.tenant_db.flush()
        await self.ctx.tenant_db.commit()
        return msg

    async def _persist_tool_message(
        self, tool_call: ToolCall, payload: dict, name: str
    ) -> BizAiMessage:
        msg = BizAiMessage(
            session_id=self.ctx.session.id,
            role="tool",
            content=json.dumps(
                desensitize_obj(payload), ensure_ascii=False, default=str
            )[:8000],
            tool_call_id=tool_call.id,
            tool_name=name,
            status=1,
        )
        self.ctx.tenant_db.add(msg)
        await self.ctx.tenant_db.flush()
        self.ctx.session.message_count = (self.ctx.session.message_count or 0) + 1
        await self.ctx.tenant_db.commit()
        return msg

    async def _persist_tool_log(
        self,
        tool_call: ToolCall,
        spec: Optional[ToolSpec],
        params: dict,
        status: str,
        error: Optional[str],
        latency_ms: int,
        assistant_message_id: int,
        result_summary: Optional[str] = None,
        confirm_token: Optional[str] = None,
    ) -> BizAiToolCallLog:
        log = BizAiToolCallLog(
            session_id=self.ctx.session.id,
            message_id=assistant_message_id,
            tool_call_id=tool_call.id,
            tool_code=spec.code if spec else tool_call.name,
            tool_name=spec.name if spec else tool_call.name,
            user_id=self.ctx.user.user_id,
            params=desensitize_obj(params),
            result_summary=result_summary,
            status=status,
            error_message=error,
            latency_ms=latency_ms,
            confirm_token=confirm_token,
        )
        self.ctx.tenant_db.add(log)
        await self.ctx.tenant_db.flush()
        await self.ctx.tenant_db.commit()
        return log

    # ============ 工具定义 ============

    async def _prepare_tool_definitions(self) -> list[ToolDefinition]:
        if not self.ctx.enabled_tool_codes:
            return []
        defs: list[ToolDefinition] = []
        for code in self.ctx.enabled_tool_codes:
            spec = self._registry.get(code)
            if not spec:
                continue
            defs.append(
                ToolDefinition(
                    name=encode_tool_name(spec.code),
                    description=spec.description,
                    parameters=spec.json_schema(),
                )
            )
        return defs

    # ============ 确认续跑 ============

    async def resume_after_confirm(
        self,
        confirm_token: str,
        approved: bool,
    ) -> AsyncIterator[str]:
        """用户在前端点确认/取消后续跑

        - approved=True : 取出 pending_confirm 日志 → 执行工具 → 把结果加入消息 → 进入下一轮 LLM
        - approved=False: 写一条 cancelled 日志 + tool 消息 → 进入下一轮让 LLM 给出友好回复
        """
        log = (
            await self.ctx.tenant_db.execute(
                select(BizAiToolCallLog).where(
                    BizAiToolCallLog.confirm_token == confirm_token,
                    BizAiToolCallLog.status == "pending_confirm",
                    BizAiToolCallLog.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not log:
            yield sse_pack("error", {"message": "未找到待确认的工具调用或已超时"})
            return

        spec = self._registry.get(log.tool_code)
        if not spec:
            yield sse_pack("error", {"message": f"工具 {log.tool_code} 已下线"})
            return

        # 装配 messages：加载历史（含 pending 时已落的 assistant.tool_calls）
        history = await ContextManager.load_history_messages(
            self.ctx.tenant_db,
            self.ctx.session.id,
            max_messages=self.ctx.context_window,
        )
        system_msgs = await PromptBuilder.build_system_messages(self.ctx)
        messages: list[ChatMessage] = system_msgs + history
        tool_defs = await self._prepare_tool_definitions()

        # 构造 wire name，与 LLM 协议保持一致
        wire_name = encode_tool_name(log.tool_code)
        tool_call = ToolCall(
            id=log.tool_call_id or "",
            name=wire_name,
            arguments=json.dumps(log.params or {}, ensure_ascii=False),
        )

        if not approved:
            payload = {"cancelled": True, "reason": "用户取消执行"}
            log.status = "cancelled"
            await self._persist_tool_message(tool_call, payload, name=wire_name)
            messages.append(
                ChatMessage(
                    role="tool",
                    tool_call_id=tool_call.id,
                    name=wire_name,
                    content=json.dumps(payload, ensure_ascii=False),
                )
            )
            await self.ctx.tenant_db.commit()
            yield sse_pack(
                "tool.result",
                {
                    "tool_call_id": tool_call.id,
                    "tool_code": log.tool_code,
                    "status": "cancelled",
                },
            )
        else:
            log.status = "success"  # 占位，_execute_tool 内会再写一条新日志
            await self.ctx.tenant_db.commit()
            async for evt in self._execute_tool(
                tool_call,
                spec,
                log.params or {},
                log.message_id or 0,
                messages,
            ):
                yield evt

        # 续跑 LLM
        loops = 0
        while loops < self.ctx.max_tool_loops:
            loops += 1
            assistant_text_parts: list[str] = []
            pending_tool_calls: list[ToolCall] = []
            finish_reason: Optional[str] = None
            prompt_tokens, completion_tokens = 0, 0

            async for chunk in self.ctx.provider.chat_stream(
                messages=messages,
                tools=tool_defs or None,
                temperature=self.ctx.temperature,
                max_tokens=self.ctx.max_tokens,
            ):
                if chunk.type == "delta" and chunk.text:
                    assistant_text_parts.append(chunk.text)
                    yield sse_pack("delta", {"content": chunk.text})
                elif chunk.type == "tool_call_done" and chunk.tool_call:
                    pending_tool_calls.append(chunk.tool_call)
                elif chunk.type == "usage":
                    prompt_tokens = chunk.prompt_tokens
                    completion_tokens = chunk.completion_tokens
                elif chunk.type == "finish":
                    finish_reason = chunk.finish_reason

            assistant_text = "".join(assistant_text_parts)
            assistant_msg = await self._persist_assistant_message(
                content=assistant_text or None,
                tool_calls=pending_tool_calls,
                finish_reason=finish_reason,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )
            messages.append(
                ChatMessage(
                    role="assistant",
                    content=assistant_text or None,
                    tool_calls=pending_tool_calls,
                )
            )

            if not pending_tool_calls:
                yield sse_pack(
                    "done",
                    {
                        "message_id": assistant_msg.id,
                        "finish_reason": finish_reason or "stop",
                    },
                )
                return

            should_pause = False
            for tool_call in pending_tool_calls:
                async for evt in self._dispatch_tool_call(
                    tool_call, assistant_msg.id, messages
                ):
                    if evt == "__PAUSE__":
                        should_pause = True
                    else:
                        yield evt

            if should_pause:
                yield sse_pack(
                    "done",
                    {
                        "message_id": assistant_msg.id,
                        "finish_reason": "confirm_required",
                    },
                )
                return

        yield sse_pack(
            "error",
            {"message": f"工具调用超过最大轮次（{self.ctx.max_tool_loops}）"},
        )
