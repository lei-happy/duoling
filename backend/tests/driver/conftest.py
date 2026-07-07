"""驾驶员 H5 端测试共享 fixture（本端自建，不依赖根 conftest.py）

设计与 ``tests/test_driver_fund_account.py`` 对齐：
- **集成测试**统一连接测试租户库 ``1001``（库 ``zt_biz_1001_ci``），在**外层事务
  中执行并最终 rollback**，不向数据库落任何数据；
- 本地无法连接租户库时，相关 fixture 直接 ``pytest.skip``，用例记为 skip 而非 fail；
- 纯逻辑用例（Pydantic schema / 输出裁剪等）不依赖以下任何 fixture。

对应设计：项目文档/01.架构设计/驾驶员H5架构设计.md
        项目文档/02.需求文档/03.移动端/02.驾驶员H5端/**
"""

from __future__ import annotations

import pytest

# 测试租户固定 1001（库 zt_biz_1001_ci），平台库 zt_platform_ci
_TENANT = "1001"


# ---------------------------------------------------------------------------
# 租户库连接（外层事务 + 回滚，不落库）
# ---------------------------------------------------------------------------
@pytest.fixture()
async def tenant_session():
    """连接测试租户库，开启外层事务并在结束时回滚。

    产出一个可直接传给各 ``Driver*Service`` 的 ``AsyncSession``。
    连接失败（本地无 DB / 无网络）时整体 skip。
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from app.core.config import get_settings

    settings = get_settings()
    try:
        engine = create_async_engine(settings.tenant_db_url(_TENANT))
        conn = await engine.connect()
    except Exception as e:  # pragma: no cover - 环境无 DB 时跳过
        pytest.skip(f"租户库 {_TENANT} 不可连接：{e}")

    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
        await engine.dispose()


@pytest.fixture()
async def platform_session():
    """连接平台库 ``zt_platform_ci``，外层事务 + 回滚，用于 auth 相关查询。

    连接失败时整体 skip。
    """
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


@pytest.fixture()
async def driver_ctx(tenant_session):
    """在租户库内预置一名临时在职司机，并构造对应的 ``DriverContext``。

    返回 ``(session, ctx)``；session 与 ctx 共享同一外层事务，结束回滚。
    """
    from app.modules.client.models.capacity.self_capacity.driver.driver import (
        Driver,
    )
    from app.modules.driver.services.driver_context import DriverContext

    driver = Driver(
        driver_code="TEST_DRV_H5",
        name="H5测试司机",
        phone="19900001234",
        user_id=990001,
        gender=1,
        status=1,
    )
    tenant_session.add(driver)
    await tenant_session.flush()

    ctx = DriverContext(
        user_id=990001,
        phone="19900001234",
        tenant_code=_TENANT,
        driver=driver,
    )
    yield tenant_session, ctx


def make_token(
    *,
    user_id: int = 990001,
    phone: str = "19900001234",
    user_type: int = 3,
    tenant_code: str | None = _TENANT,
):
    """构造一个 ``TokenData``，用于直接驱动 ``get_current_driver`` 等依赖。"""
    from app.core.security import TokenData

    return TokenData(
        user_id=user_id,
        phone=phone,
        user_type=user_type,
        tenant_code=tenant_code,
        roles=[],
    )
