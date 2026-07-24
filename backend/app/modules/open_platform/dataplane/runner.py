"""能力执行 + 审计（REST / MCP 共用）

统一：scope 校验 → 计时执行 → 落审计（成功/失败/拒绝）→ 错误翻译为对外错误码。
审计写租户库，best-effort，不影响主调用返回。
"""

import time
from typing import Any

from loguru import logger

from app.common.exceptions import BizException
from app.modules.open_platform.capabilities.registry import dispatch, get_capability
from app.modules.open_platform.capabilities.context import OpenContext
from app.modules.open_platform.services.audit_service import AuditService
from app.modules.open_platform.dataplane import errors


def _mask_params(params: dict) -> dict:
    """入参脱敏：对常见敏感键做掩码，避免审计泄露。"""
    if not isinstance(params, dict):
        return {}
    masked = {}
    sensitive = {"phone", "mobile", "contact_phone", "password", "id_card", "idcard"}
    for k, v in params.items():
        if k.lower() in sensitive and isinstance(v, str) and len(v) >= 7:
            masked[k] = v[:3] + "****" + v[-2:]
        else:
            masked[k] = v
    return masked


async def run_and_audit(
    ctx: OpenContext,
    capability_code: str,
    params: dict,
    *,
    method: str = "POST",
    path: str = "",
) -> Any:
    started = time.time()
    status = "success"
    error_code = ""
    http_status = 200
    summary = ""

    try:
        errors_spec = get_capability(capability_code)
        if errors_spec is None or errors_spec.stability == "offline":
            raise errors.not_found_cap()

        # scope 校验
        if capability_code not in (ctx.scope or []):
            raise errors.forbidden_scope(capability_code)

        result = await dispatch(capability_code, params, ctx)
        if isinstance(result, dict) and "total" in result:
            summary = f"total={result.get('total')}"
        return result

    except errors.OpenApiError as e:
        status = "denied" if e.http_status in (401, 403, 429) else "failed"
        error_code = e.error_code
        http_status = e.http_status
        summary = e.message
        raise
    except BizException as e:
        status = "failed"
        error_code = "BIZ_ERROR"
        http_status = 200
        summary = e.message
        raise errors.bad_request(e.message)
    except Exception as e:  # pragma: no cover
        status = "failed"
        error_code = "INTERNAL_ERROR"
        http_status = 500
        summary = "内部错误"
        logger.exception(f"开放平台能力执行异常 cap={capability_code}: {e}")
        raise errors.OpenApiError(500, "INTERNAL_ERROR", "服务内部错误，请稍后重试")
    finally:
        latency = int((time.time() - started) * 1000)
        await AuditService.record(
            ctx.tenant_code,
            {
                "request_id": ctx.request_id,
                "app_id": ctx.app_id,
                "credential_id": ctx.credential_id,
                "channel": ctx.channel,
                "capability_code": capability_code,
                "method": method,
                "path": path,
                "params_masked": _mask_params(params),
                "status": status,
                "error_code": error_code,
                "http_status": http_status,
                "latency_ms": latency,
                "client_ip": ctx.client_ip,
                "user_agent": ctx.user_agent,
                "result_summary": str(summary)[:255],
            },
        )
