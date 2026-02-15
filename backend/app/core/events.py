"""
应用生命周期事件
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from app.core.database import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动和关闭事件"""
    # ---- 启动 ----
    logger.info("正在启动智途(ZhiTu)后端服务...")
    await db_manager.init_platform_db()
    logger.info("智途(ZhiTu)后端服务启动完成")

    yield

    # ---- 关闭 ----
    logger.info("正在关闭智途(ZhiTu)后端服务...")
    await db_manager.close_all()
    logger.info("智途(ZhiTu)后端服务已关闭")
