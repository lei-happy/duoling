"""智途开放平台数据面 —— 独立进程入口（zhitu-openapi）

与业务主应用（app.main）分离部署，避免对外调用与内部业务抢占资源：
- 仅承载数据面：/openapi/v1（REST）与 /mcp（远程 MCP）
- 自带鉴权（HMAC / Bearer），不复用企业端 JWT 中间件
- 独立子域（如 openapi.zhitu.com）+ 独立进程/容器，可独立扩缩容

本地开发可直接：
    uvicorn app.open_main:app --reload --port 8100
生产由独立容器运行本入口。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import get_settings
from app.core.database import db_manager
from app.common.exceptions import register_exception_handlers
from app.modules.open_platform.dataplane.rest import router as openapi_rest_router
from app.modules.open_platform.dataplane.mcp import router as openapi_mcp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("正在启动智途开放平台数据面服务...")
    await db_manager.init_platform_db()
    # 触发内置能力注册
    import app.modules.open_platform.capabilities  # noqa: F401
    logger.info("开放平台数据面服务启动完成")
    yield
    await db_manager.close_all()
    logger.info("开放平台数据面服务已关闭")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="智途开放平台 API",
        description="智途(ZhiTu) 开放平台数据面：REST 开放接口 + 远程 MCP 服务",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_dev else None,
        redoc_url="/redoc" if settings.is_dev else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(openapi_rest_router, prefix="/openapi/v1", tags=["开放平台-REST"])
    app.include_router(openapi_mcp_router, prefix="/mcp", tags=["开放平台-MCP"])

    @app.get("/health", tags=["健康检查"])
    async def health_check():
        return {"status": "ok", "service": "zhitu-openapi"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.open_main:app",
        host=settings.APP_HOST,
        port=8100,
        reload=settings.is_dev,
    )
