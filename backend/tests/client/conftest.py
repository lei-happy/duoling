"""企业端（Client Web）测试共享基座 fixture。

> 说明：项目根 `backend/tests/conftest.py` 由「运营后台端」任务统一维护。
> 本文件是企业端**自建**的本端 fixture，仅覆盖 `tests/client/**`，
> 不修改根 conftest.py，避免与其它端任务冲突。

提供：
  - ``tenant_session``    ：连接测试租户库 ``zt_biz_1001_ci``，外层事务执行、
                            结束时统一 rollback，**不落库**；无 DB 时 skip。
  - ``platform_session``  ：连接平台库 ``zt_platform_ci``，同样事务回滚、不落库。
  - ``http_client``       ：httpx.AsyncClient + ASGITransport 直连 app.main:app，
                            **不触发 lifespan**（不启动 worker / 不初始化 db_manager）。
                            适用于鉴权门槛（401/403/400）等无需真实 DB 的冒烟用例。

约定见：doc/06.测试用例体系/README.md（第四章 测试脚本约定）。
"""

from __future__ import annotations

import uuid

import pytest

# 测试租户固定 1001（开发库 zt_biz_1001_ci），平台库 zt_platform_ci。
TENANT_CODE = "1001"


def unique_suffix(n: int = 8) -> str:
    """生成短随机后缀，避免集成测试数据冲突。"""
    return uuid.uuid4().hex[:n]


def unique_phone() -> str:
    """生成未占用的 11 位测试手机号（199 号段）。"""
    return f"199{int(uuid.uuid4().hex[:8], 16) % 10 ** 8:08d}"


def unique_code(prefix: str) -> str:
    """生成带前缀的唯一业务编码。"""
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


# ---------------------------------------------------------------------------
# 租户库会话（事务回滚，不落库）
# ---------------------------------------------------------------------------
@pytest.fixture()
async def tenant_session():
    """连接测试租户库，开启外层事务，测试结束统一回滚。

    连接失败（本地无 DB / 库不存在）时整体 skip，保证 CI 无 DB 环境不 fail。
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.core.config import get_settings

    settings = get_settings()
    try:
        engine = create_async_engine(settings.tenant_db_url(TENANT_CODE))
        conn = await engine.connect()
    except Exception as e:  # pragma: no cover - 环境无 DB 时跳过
        pytest.skip(f"租户库 {TENANT_CODE} 不可连接：{e}")

    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
        await engine.dispose()


# ---------------------------------------------------------------------------
# 平台库会话（事务回滚，不落库）
# ---------------------------------------------------------------------------
@pytest.fixture()
async def platform_session():
    """连接平台库 zt_platform_ci，开启外层事务，结束回滚。无 DB 时 skip。"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.core.config import get_settings

    settings = get_settings()
    try:
        engine = create_async_engine(settings.platform_db_url)
        conn = await engine.connect()
    except Exception as e:  # pragma: no cover - 环境无 DB 时跳过
        pytest.skip(f"平台库不可连接：{e}")

    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
        await engine.dispose()


# ---------------------------------------------------------------------------
# HTTP 客户端（不触发 lifespan）
# ---------------------------------------------------------------------------
@pytest.fixture()
async def http_client():
    """直连 ASGI app 的 httpx.AsyncClient（不跑 lifespan、不初始化 db_manager）。

    仅用于「鉴权门槛」类冒烟：未带 Token 访问受保护接口应 401；
    这些用例在 TenantMiddleware / get_current_user 层即被拦截，不触达 DB。
    """
    try:
        import httpx
        from httpx import ASGITransport
    except Exception as e:  # pragma: no cover
        pytest.skip(f"httpx 不可用：{e}")

    from app.main import app

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client
