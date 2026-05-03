"""
客户端：AI 对话主接口

POST /ai/chat          : 发起对话，SSE 流式返回
POST /ai/chat/confirm  : 高风险操作确认后续跑（同样 SSE）
"""

from __future__ import annotations

from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.core.dependencies import (
    get_current_user,
    get_platform_db,
    get_tenant_code,
    get_tenant_db,
)
from app.core.security import TokenData
from app.modules.ai.engine.orchestrator import Orchestrator
from app.modules.ai.engine.runtime_context import EngineContext
from app.modules.ai.engine.streaming import sse_pack
from app.modules.ai.llm.factory import LLMProviderFactory
from app.modules.ai.schemas.client.chat import ChatRequest, ConfirmRequest
from app.modules.ai.security.quota import (
    check_rate_limit,
    check_token_quota,
    get_fallback_message,
)
from app.modules.ai.services.chat_service import ChatService
from app.modules.ai.services.employee_service import EmployeeService

router = APIRouter()


def _sse_response(generator: AsyncIterator[str]) -> StreamingResponse:
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",  # nginx 关闭代理缓冲
            "Connection": "keep-alive",
        },
    )


def _extract_llm_error_detail(e: Exception) -> str:
    """从 OpenAI SDK 异常中尽量抽取出 API 返回的真正报错信息

    BadRequestError(message=..., body={'error': {'message': ..., 'code': ...}})
    """
    detail = getattr(e, "message", None) or str(e)
    body = getattr(e, "body", None)
    if isinstance(body, dict):
        err = body.get("error") if isinstance(body.get("error"), dict) else body
        if isinstance(err, dict):
            msg = err.get("message") or err.get("msg")
            code = err.get("code") or err.get("type")
            if msg:
                detail = f"{msg}" + (f" (code={code})" if code else "")
    # 兜底裁剪，避免 SSE 单条过长
    return (detail or "")[:500]


@router.post("")
async def chat(
    body: ChatRequest,
    tenant_code: str = Depends(get_tenant_code),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    user: TokenData = Depends(get_current_user),
):
    """发起对话；SSE 流式返回

    注意：所有前置校验（员工存在、限流、配额、Provider 可用）都通过 SSE
    error 事件返回，避免 BizException 被全局异常处理改写成普通 JSON 响应，
    导致前端 SSE 解析到空内容、UI 上只看到时间戳的现象。
    """

    async def generator() -> AsyncIterator[str]:
        try:
            employee = await EmployeeService.get_by_code(
                platform_db, body.employeeCode
            )
            if not employee or employee.status != 1:
                yield sse_pack(
                    "error",
                    {"message": f"数字员工 {body.employeeCode} 不可用，请联系管理员"},
                )
                return

            await check_rate_limit(platform_db, user.user_id)
            await check_token_quota(platform_db, tenant_db)

            session = await ChatService.get_or_create_session(
                tenant_db,
                user,
                employee_code=employee.code,
                employee_name=employee.name,
                session_id=body.sessionId,
            )
            yield sse_pack(
                "session",
                {
                    "sessionId": session.id,
                    "sessionNo": session.session_no,
                    "employeeCode": employee.code,
                    "employeeName": employee.name,
                },
            )

            enabled_tool_codes = await EmployeeService.list_enabled_tool_codes(
                platform_db, employee.id
            )
            model_config = employee.model_config_json or {}
            provider = await LLMProviderFactory.get(
                platform_db,
                provider_code=model_config.get("provider_code"),
                model_override=model_config.get("model"),
            )

            ctx = EngineContext(
                user=user,
                tenant_code=tenant_code,
                tenant_db=tenant_db,
                platform_db=platform_db,
                employee=employee,
                session=session,
                provider=provider,
                enabled_tool_codes=enabled_tool_codes,
                model_config=model_config,
            )
            orchestrator = Orchestrator(ctx)

            async for evt in orchestrator.run(
                user_message=body.content,
                attachments=body.attachments,
            ):
                yield evt
        except BizException as e:
            yield sse_pack("error", {"message": e.message})
        except Exception as e:  # noqa: BLE001
            logger.exception(f"[AI Chat] 异常: {e!r}")
            fallback = await get_fallback_message(platform_db)
            yield sse_pack("delta", {"content": fallback})
            yield sse_pack(
                "error",
                {
                    "message": (
                        f"模型调用失败: {type(e).__name__}: "
                        f"{_extract_llm_error_detail(e)}"
                    ),
                    "fallback": True,
                },
            )

    return _sse_response(generator())


@router.post("/confirm")
async def chat_confirm(
    body: ConfirmRequest,
    tenant_code: str = Depends(get_tenant_code),
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    user: TokenData = Depends(get_current_user),
):
    """用户确认高风险动作后续跑"""

    async def generator() -> AsyncIterator[str]:
        try:
            session = await ChatService.get_or_create_session(
                tenant_db,
                user,
                employee_code="",
                employee_name=None,
                session_id=body.sessionId,
            )
            employee = await EmployeeService.get_by_code(
                platform_db, session.employee_code
            )
            if not employee:
                yield sse_pack("error", {"message": "原始数字员工不存在"})
                return

            yield sse_pack(
                "session",
                {
                    "sessionId": session.id,
                    "sessionNo": session.session_no,
                },
            )

            enabled_tool_codes = await EmployeeService.list_enabled_tool_codes(
                platform_db, employee.id
            )
            model_config = employee.model_config_json or {}
            provider = await LLMProviderFactory.get(
                platform_db,
                provider_code=model_config.get("provider_code"),
                model_override=model_config.get("model"),
            )

            ctx = EngineContext(
                user=user,
                tenant_code=tenant_code,
                tenant_db=tenant_db,
                platform_db=platform_db,
                employee=employee,
                session=session,
                provider=provider,
                enabled_tool_codes=enabled_tool_codes,
                model_config=model_config,
            )
            orchestrator = Orchestrator(ctx)

            async for evt in orchestrator.resume_after_confirm(
                confirm_token=body.confirmToken,
                approved=body.approved,
            ):
                yield evt
        except BizException as e:
            yield sse_pack("error", {"message": e.message})
        except Exception as e:  # noqa: BLE001
            logger.exception(f"[AI Confirm] 异常: {e!r}")
            fallback = await get_fallback_message(platform_db)
            yield sse_pack("delta", {"content": fallback})
            yield sse_pack(
                "error",
                {
                    "message": (
                        f"模型调用失败: {type(e).__name__}: "
                        f"{_extract_llm_error_detail(e)}"
                    ),
                    "fallback": True,
                },
            )

    return _sse_response(generator())
