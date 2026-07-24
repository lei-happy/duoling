"""
中间件

- RequestLogMiddleware：请求日志（纯 ASGI，避免 BaseHTTPMiddleware 缓冲 SSE）
- TenantMiddleware    ：从 Token 中提取 tenant_code 注入 request.state（同样纯 ASGI）

注意：必须避免使用 starlette.middleware.base.BaseHTTPMiddleware；它会把
StreamingResponse 的每个 chunk 通过内部 anyio 队列中转，导致 SSE 流被显著
缓冲甚至阻塞，前端要等到响应彻底结束才能拿到事件。
"""

import time
from typing import Optional

from loguru import logger
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.security import decode_access_token


class RequestLogMiddleware:
    """请求日志中间件（纯 ASGI 实现）"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start = time.time()
        status_code: int = 0

        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 0)
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            elapsed = round((time.time() - start) * 1000, 2)
            method = scope.get("method", "")
            path = scope.get("path", "")
            logger.info(
                f"{method} {path} status={status_code} elapsed={elapsed}ms"
            )


class TenantMiddleware:
    """租户识别中间件（纯 ASGI 实现）

    从 Authorization Header 中解析 JWT，提取 tenant_code 并注入 request.state。
    """

    SKIP_PATHS = (
        "/api/console/auth/login",
        "/api/console/auth/refresh",
        "/api/client/auth/login",
        "/api/client/auth/refresh",
        "/api/driver/auth/login",
        "/api/driver/auth/sms-login",
        "/api/driver/auth/refresh",
        "/api/open/",
        "/openapi/v1/",
        "/mcp/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
    )

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # 在 ASGI scope.state 中放置后续依赖会用到的字段
        # FastAPI 的 Request.state 实际就是 scope["state"]
        state: dict = scope.setdefault("state", {})
        state["tenant_code"] = None
        state["current_user"] = None

        path: str = scope.get("path", "")
        if not any(path.startswith(p) for p in self.SKIP_PATHS):
            auth_header: Optional[str] = None
            for name, value in scope.get("headers", []):
                if name == b"authorization":
                    try:
                        auth_header = value.decode("latin-1")
                    except Exception:
                        auth_header = None
                    break
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]
                token_data = decode_access_token(token)
                if token_data:
                    state["current_user"] = token_data
                    state["tenant_code"] = token_data.tenant_code

        await self.app(scope, receive, send)
