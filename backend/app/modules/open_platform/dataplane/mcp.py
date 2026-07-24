"""远程 MCP 服务（/mcp/{slug}）

遵循 MCP「Streamable HTTP」传输（JSON-RPC 2.0 over HTTP），供 AI 办公工具
（Trae、WorkBuddy、Cursor、Claude 等）远程连接。支持 initialize /
notifications/initialized / ping / tools/list / tools/call。

合规要点：
- 单端点 POST 承载所有 JSON-RPC 消息；GET 显式返回 405（本服务不提供服务端主动推流）。
- 内容协商：客户端 Accept 含 text/event-stream 时以 SSE 单事件回包，否则回 application/json。
- 通知（无 id 的 JSON-RPC）返回 202 空响应体。
- initialize 协商 protocolVersion：回显客户端所请求且受支持的版本，否则回服务端默认。
- 工具错误走 result.isError（而非 JSON-RPC error），符合 MCP tools/call 语义。

- 连接定位：URL 中的 server_slug + Authorization Bearer(access_key.token)
- 工具集合：MCP 配置 enabled_capabilities ∩ 凭证 scope ∩ 注册表(mcp 通道)
- 工具名：能力码的 "." 替换为 "_"（兼容 MCP 工具名约束），调用时映射回能力码
"""

import json
from typing import Any, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select

from app.core.database import db_manager
from app.modules.open_platform.models.platform.open_mcp_config import OpenMcpConfig
from app.modules.open_platform.capabilities.registry import get_capability, list_capabilities
from app.modules.open_platform.dataplane import errors
from app.modules.open_platform.dataplane.authn import authenticate_mcp
from app.modules.open_platform.dataplane.runner import run_and_audit

router = APIRouter()

# 服务端默认协议版本；同时兼容后续版本的握手回显
PROTOCOL_VERSION = "2024-11-05"
SUPPORTED_PROTOCOL_VERSIONS = {"2024-11-05", "2025-03-26", "2025-06-18"}


def _wants_sse(request: Request) -> bool:
    """客户端是否接受 SSE（Streamable HTTP 允许服务端二选一回包）。"""
    accept = (request.headers.get("accept") or "").lower()
    return "text/event-stream" in accept


def _render(request: Request, body: Any) -> Response:
    """按客户端 Accept 决定以 SSE 单事件或 JSON 回包。"""
    if _wants_sse(request):
        text = json.dumps(body, ensure_ascii=False, default=str)
        sse = f"event: message\ndata: {text}\n\n"
        return Response(content=sse, media_type="text/event-stream")
    return JSONResponse(body)


def _negotiate_version(params: dict) -> str:
    requested = (params or {}).get("protocolVersion")
    if requested in SUPPORTED_PROTOCOL_VERSIONS:
        return requested
    return PROTOCOL_VERSION


def _tool_name(code: str) -> str:
    return code.replace(".", "_")


def _input_schema_for(spec) -> dict:
    """生成工具入参 JSON Schema：优先用能力声明的 input_schema；
    分页查询类（*.query）给出通用关键字/分页参数；其余（如 ping）无参数。"""
    if spec.input_schema:
        return spec.input_schema
    if spec.code.endswith(".query"):
        return {
            "type": "object",
            "properties": {
                "keyword": {"type": "string", "description": "关键字（可选）"},
                "page": {"type": "integer", "description": "页码，默认 1"},
                "pageSize": {"type": "integer", "description": "每页条数，默认 20"},
            },
        }
    return {"type": "object", "properties": {}}


def _code_from_tool(name: str, allowed_codes: set) -> Optional[str]:
    for code in allowed_codes:
        if _tool_name(code) == name:
            return code
    return None


def _rpc_result(rpc_id, result) -> dict:
    return {"jsonrpc": "2.0", "id": rpc_id, "result": result}


def _rpc_error(rpc_id, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": code, "message": message}}


async def _load_config(slug: str) -> Optional[OpenMcpConfig]:
    async for db in db_manager.get_platform_session():
        return await db.scalar(
            select(OpenMcpConfig).where(
                OpenMcpConfig.server_slug == slug,
                OpenMcpConfig.is_deleted == 0,
                OpenMcpConfig.status == "enabled",
            )
        )
    return None


def _allowed_codes(cfg: OpenMcpConfig, scope: list) -> set:
    enabled = set(cfg.enabled_capabilities or [])
    scoped = set(scope or [])
    registered = {s.code for s in list_capabilities("mcp")}
    return enabled & scoped & registered


@router.get("/{slug}")
async def mcp_stream_unsupported(slug: str):
    """Streamable HTTP 允许客户端用 GET 打开服务端推流；本服务无主动推送，按规范回 405。"""
    return JSONResponse(
        status_code=405,
        headers={"Allow": "POST"},
        content=_rpc_error(None, -32000, "本服务不支持服务端推流，请使用 POST"),
    )


@router.post("/{slug}")
async def mcp_endpoint(slug: str, request: Request):
    cfg = await _load_config(slug)
    if cfg is None:
        return JSONResponse(
            status_code=404,
            content={"error": "MCP_NOT_FOUND", "message": "连接不存在或已停用"},
        )

    try:
        cred, ctx = await authenticate_mcp(request, expected_credential_id=cfg.credential_id)
    except errors.OpenApiError as e:
        return JSONResponse(
            status_code=e.http_status,
            content={"error": e.error_code, "message": e.message},
        )

    try:
        payload = json.loads(await request.body() or b"{}")
    except Exception:
        return _render(request, _rpc_error(None, -32700, "Parse error"))

    # 批量请求：逐条处理（兼容旧客户端；2025-06-18 起已不要求）
    if isinstance(payload, list):
        responses = [await _handle_rpc(item, cfg, ctx) for item in payload]
        responses = [r for r in responses if r is not None]
        if not responses:
            return Response(status_code=202)
        return _render(request, responses)

    resp = await _handle_rpc(payload, cfg, ctx)
    if resp is None:
        # 通知（无 id）：按规范返回 202，无响应体
        return Response(status_code=202)
    return _render(request, resp)


async def _handle_rpc(payload: dict, cfg: OpenMcpConfig, ctx) -> Optional[dict]:
    method = payload.get("method")
    rpc_id = payload.get("id")
    is_notification = rpc_id is None

    if method == "initialize":
        return _rpc_result(
            rpc_id,
            {
                "protocolVersion": _negotiate_version(payload.get("params") or {}),
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": cfg.display_name, "version": "1.0.0"},
            },
        )

    if method in ("notifications/initialized", "initialized"):
        return None

    if method == "ping":
        return _rpc_result(rpc_id, {})

    allowed = _allowed_codes(cfg, ctx.scope)

    if method == "tools/list":
        tools = []
        for spec in list_capabilities("mcp"):
            if spec.code not in allowed:
                continue
            tools.append(
                {
                    "name": _tool_name(spec.code),
                    "description": spec.description or spec.name,
                    "inputSchema": _input_schema_for(spec),
                }
            )
        return _rpc_result(rpc_id, {"tools": tools})

    if method == "tools/call":
        params = payload.get("params") or {}
        tool_name = params.get("name")
        arguments = params.get("arguments") or {}
        code = _code_from_tool(tool_name, allowed)
        if code is None:
            if is_notification:
                return None
            return _rpc_result(
                rpc_id,
                {
                    "content": [{"type": "text", "text": "工具不存在或未授权"}],
                    "isError": True,
                },
            )
        try:
            result = await run_and_audit(
                ctx, code, arguments, method="MCP", path=f"/mcp/{cfg.server_slug}"
            )
            text = json.dumps(result, ensure_ascii=False, default=str)
            return _rpc_result(
                rpc_id, {"content": [{"type": "text", "text": text}], "isError": False}
            )
        except errors.OpenApiError as e:
            return _rpc_result(
                rpc_id,
                {"content": [{"type": "text", "text": e.message}], "isError": True},
            )

    if is_notification:
        return None
    return _rpc_error(rpc_id, -32601, f"Method not found: {method}")
