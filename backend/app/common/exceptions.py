"""
自定义异常 & 全局异常处理
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger


class BizException(Exception):
    """业务异常"""

    def __init__(self, message: str = "业务处理失败", code: int = -1):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthException(Exception):
    """认证异常"""

    def __init__(self, message: str = "认证失败，请重新登录"):
        self.message = message
        super().__init__(self.message)


class PermissionException(Exception):
    """权限异常"""

    def __init__(self, message: str = "没有操作权限"):
        self.message = message
        super().__init__(self.message)


class TenantException(Exception):
    """租户异常"""

    def __init__(self, message: str = "租户信息无效"):
        self.message = message
        super().__init__(self.message)


def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(BizException)
    async def biz_exception_handler(request: Request, exc: BizException):
        return JSONResponse(
            status_code=200,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(AuthException)
    async def auth_exception_handler(request: Request, exc: AuthException):
        return JSONResponse(
            status_code=401,
            content={"code": 401, "message": exc.message, "data": None},
        )

    @app.exception_handler(PermissionException)
    async def permission_exception_handler(request: Request, exc: PermissionException):
        return JSONResponse(
            status_code=403,
            content={"code": 403, "message": exc.message, "data": None},
        )

    @app.exception_handler(TenantException)
    async def tenant_exception_handler(request: Request, exc: TenantException):
        return JSONResponse(
            status_code=400,
            content={"code": 400, "message": exc.message, "data": None},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": exc.detail,
                "data": None,
            },
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(f"未处理的异常: {request.method} {request.url}")
        return JSONResponse(
            status_code=500,
            content={"code": 500, "message": "服务器内部错误", "data": None},
        )
