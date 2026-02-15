"""
多租户数据库连接管理

设计思路：
- 平台主库（zt_platform）：全局唯一，应用启动时创建引擎
- 租户业务库（zt_biz_{tenant_code}）：按需动态创建引擎，连接池缓存
"""

from typing import Dict, Optional, AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from loguru import logger

from app.core.config import get_settings


# ============================================================
# ORM 基类
# ============================================================

class PlatformBase(DeclarativeBase):
    """平台主库 ORM 基类"""
    pass


class TenantBase(DeclarativeBase):
    """租户业务库 ORM 基类"""
    pass


# ============================================================
# 数据库管理器
# ============================================================

class DatabaseManager:
    """多租户数据库管理器"""

    def __init__(self):
        self._platform_engine: Optional[AsyncEngine] = None
        self._platform_session_factory: Optional[async_sessionmaker] = None
        self._tenant_engines: Dict[str, AsyncEngine] = {}
        self._tenant_session_factories: Dict[str, async_sessionmaker] = {}

    # ---- 平台库 ----

    async def init_platform_db(self) -> None:
        """初始化平台数据库引擎"""
        settings = get_settings()
        self._platform_engine = create_async_engine(
            settings.platform_db_url,
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=settings.APP_DEBUG,
        )
        self._platform_session_factory = async_sessionmaker(
            bind=self._platform_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info(f"平台数据库引擎已初始化: {settings.PLATFORM_DB_NAME}")

    async def get_platform_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取平台库 Session（用于依赖注入）"""
        if not self._platform_session_factory:
            raise RuntimeError("平台数据库未初始化，请先调用 init_platform_db()")
        async with self._platform_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # ---- 租户库 ----

    def _get_or_create_tenant_engine(self, tenant_code: str) -> AsyncEngine:
        """获取或创建租户数据库引擎（带缓存）"""
        if tenant_code not in self._tenant_engines:
            settings = get_settings()
            engine = create_async_engine(
                settings.tenant_db_url(tenant_code),
                pool_size=10,
                max_overflow=5,
                pool_recycle=3600,
                pool_pre_ping=True,
                echo=settings.APP_DEBUG,
            )
            self._tenant_engines[tenant_code] = engine
            self._tenant_session_factories[tenant_code] = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            logger.info(f"租户数据库引擎已创建: {settings.tenant_database_name(tenant_code)}")
        return self._tenant_engines[tenant_code]

    async def get_tenant_session(
        self, tenant_code: str
    ) -> AsyncGenerator[AsyncSession, None]:
        """获取租户库 Session（用于依赖注入）"""
        self._get_or_create_tenant_engine(tenant_code)
        factory = self._tenant_session_factories[tenant_code]
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # ---- 租户库初始化 ----

    async def create_tenant_database(self, tenant_code: str) -> None:
        """
        为新租户创建独立数据库并初始化表结构
        注意：此操作需要 MySQL 用户有 CREATE DATABASE 权限
        """
        settings = get_settings()
        db_name = settings.tenant_database_name(tenant_code)

        # 使用平台库引擎执行 CREATE DATABASE
        async with self._platform_engine.begin() as conn:
            await conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS `{db_name}` "
                     f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            )
        logger.info(f"租户数据库已创建: {db_name}")

        # 在新库中创建表结构
        engine = self._get_or_create_tenant_engine(tenant_code)
        async with engine.begin() as conn:
            await conn.run_sync(TenantBase.metadata.create_all)
        logger.info(f"租户数据库表结构已初始化: {db_name}")

    # ---- 清理 ----

    async def close_all(self) -> None:
        """关闭所有数据库连接"""
        if self._platform_engine:
            await self._platform_engine.dispose()
            logger.info("平台数据库引擎已关闭")

        for code, engine in self._tenant_engines.items():
            await engine.dispose()
            logger.info(f"租户数据库引擎已关闭: {code}")

        self._tenant_engines.clear()
        self._tenant_session_factories.clear()


# 全局单例
db_manager = DatabaseManager()
