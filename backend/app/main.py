"""
智途(ZhiTu) - 物流车队综合操作系统
FastAPI 应用入口
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.events import lifespan
from app.core.middleware import RequestLogMiddleware, TenantMiddleware
from app.common.exceptions import register_exception_handlers

# 导入路由
from app.modules.console.api import router as console_router
from app.modules.client.api import router as client_router
from app.modules.driver.api import router as driver_router
from app.modules.open.api import router as open_router
from app.modules.open_platform.dataplane.rest import router as openapi_rest_router
from app.modules.open_platform.dataplane.mcp import router as openapi_mcp_router


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    settings = get_settings()

    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="智途(ZhiTu) - 物流车队综合操作系统 后端API服务",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_dev else None,
        redoc_url="/redoc" if settings.is_dev else None,
    )

    # ---- 跨域中间件 ----
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ---- 自定义中间件（先注册的后执行，注意顺序） ----
    app.add_middleware(RequestLogMiddleware)
    app.add_middleware(TenantMiddleware)

    # ---- 全局异常处理 ----
    register_exception_handlers(app)

    # ---- 注册路由 ----
    app.include_router(console_router, prefix="/api/console", tags=["管理后台"])
    app.include_router(client_router, prefix="/api/client", tags=["客户端"])
    app.include_router(driver_router, prefix="/api/driver", tags=["司机端"])
    app.include_router(open_router, prefix="/api/open", tags=["开放接口"])

    # ---- 开放平台数据面（本地开发同进程挂载；生产由独立进程 app/open_main.py 承载） ----
    app.include_router(openapi_rest_router, prefix="/openapi/v1", tags=["开放平台-REST"])
    app.include_router(openapi_mcp_router, prefix="/mcp", tags=["开放平台-MCP"])

    # ---- 静态资源（上传文件） ----
    uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

    # ---- 健康检查 ----
    @app.get("/health", tags=["健康检查"])
    async def health_check():
        return {"status": "ok", "service": settings.APP_NAME}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.is_dev,
    )
