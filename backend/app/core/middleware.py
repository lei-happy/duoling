"""
中间件

- 请求日志中间件
- 租户识别中间件（从 Token 中提取 tenant_code 注入 request.state）
"""

import time
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger

from app.core.security import decode_access_token


class RequestLogMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start = time.time()
        response = await call_next(request)
        elapsed = round((time.time() - start) * 1000, 2)
        logger.info(
            f"{request.method} {request.url.path} "
            f"status={response.status_code} "
            f"elapsed={elapsed}ms"
        )
        return response


class TenantMiddleware(BaseHTTPMiddleware):
    """
    租户识别中间件
    从 Authorization Header 中解析 JWT，提取 tenant_code 并注入 request.state
    """

    # 不需要租户识别的路径前缀
    SKIP_PATHS = (
        "/api/console/auth/login",
        "/api/client/auth/login",
        "/api/open/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
    )

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # 初始化 state
        request.state.tenant_code = None
        request.state.current_user = None

        # 跳过无需识别的路径
        path = request.url.path
        if any(path.startswith(p) for p in self.SKIP_PATHS):
            return await call_next(request)

        # 尝试解析 Token
        auth_header: Optional[str] = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            token_data = decode_access_token(token)
            if token_data:
                request.state.current_user = token_data
                request.state.tenant_code = token_data.tenant_code

        return await call_next(request)
