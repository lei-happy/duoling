"""开放接口（Open / LITE / 运力宝）测试基座 fixture

本端独立 conftest（根 `tests/conftest.py` 由「运营后台端」任务负责，此处不依赖）。

提供四类 fixture：

1. ``platform_client``  — httpx.AsyncClient + ASGITransport 直连 ``app.main:app``，
   并在 fixture 内初始化平台库引擎。无法连接平台库（``zt_platform_ci``）时整体 skip，
   保证「无 DB/服务时用例 skip 而非 fail」。
2. ``tenant_session`` — 连接测试租户库 ``1001``（``zt_biz_1001_ci``），外层事务中执行、
   **结束时回滚，不落库**（参考 ``tests/test_driver_fund_account.py``）。
3. ``platform_session`` — 平台库外层事务回滚 session，供 service 层集成测试直连使用。
4. ``lite_dispatch_client`` — 在 ``platform_client`` 基础上预置 LITE 占位 token 与
   ``tenant_code`` 查询参数，供运力上报 HTTP 用例复用。

约定：租户固定 ``1001``，平台库 ``zt_platform``（开发库带 ``_ci`` 后缀）。
"""

import pytest
import pytest_asyncio

TEST_TENANT = "1001"
LITE_PLACEHOLDER_TOKEN = "dummy-lite-token"
LITE_DISPATCH_PATH = "/api/open/lite/carrier/task/{task_id}/dispatch"


def lite_dispatch_url(task_id: int, tenant_code: str = TEST_TENANT) -> str:
    """LITE 运力上报 URL（占位 token 需配合 ``tenant_code`` 查询参数）。"""
    return f"/api/open/lite/carrier/task/{task_id}/dispatch?tenant_code={tenant_code}"


def lite_dispatch_body(**override) -> dict:
    """运力上报最小合法请求体。"""
    data = dict(
        mainDriverName="李司机",
        mainDriverPhone="13800000000",
        plateNumber="京A12345",
    )
    data.update(override)
    return data


def lite_dispatch_headers(token: str = LITE_PLACEHOLDER_TOKEN) -> dict:
    return {"X-Lite-Token": token}


async def _platform_db_reachable() -> bool:
    """探测平台库是否可连接，初始化 db_manager 引擎；不可达返回 False。"""
    from sqlalchemy import text
    from app.core.database import db_manager

    try:
        if db_manager._platform_session_factory is None:
            await db_manager.init_platform_db()
        async with db_manager._platform_session_factory() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest_asyncio.fixture()
async def platform_client():
    """httpx AsyncClient 直连 FastAPI app（平台库不可达时 skip）。

    注意：ASGITransport 不会触发 lifespan，因此需手动初始化平台库引擎。
    开放接口无需认证，TenantMiddleware 对 ``/api/open/`` 直接放行。
    """
    if not await _platform_db_reachable():
        pytest.skip("平台库 zt_platform_ci 不可连接，跳过开放接口 HTTP 集成用例")

    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture()
async def lite_dispatch_client(platform_client):
    """带 LITE 占位 token 与 tenant_code 的 HTTP 客户端包装。"""
    client = platform_client

    async def post_dispatch(task_id: int, *, json=None, headers=None, tenant_code=TEST_TENANT):
        payload = json if json is not None else lite_dispatch_body()
        hdrs = headers if headers is not None else lite_dispatch_headers()
        return await client.post(
            lite_dispatch_url(task_id, tenant_code=tenant_code),
            headers=hdrs,
            json=payload,
        )

    client.post_dispatch = post_dispatch  # type: ignore[attr-defined]
    yield client


@pytest_asyncio.fixture()
async def platform_session():
    """平台库外层事务 session，结束回滚不落库。"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from app.core.config import get_settings

    settings = get_settings()
    try:
        engine = create_async_engine(settings.platform_db_url)
        conn = await engine.connect()
    except Exception as e:  # pragma: no cover - 无 DB 时跳过
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


@pytest_asyncio.fixture()
async def tenant_session():
    """测试租户库 1001 外层事务 session，结束回滚不落库。"""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from app.core.config import get_settings

    settings = get_settings()
    try:
        engine = create_async_engine(settings.tenant_db_url(TEST_TENANT))
        conn = await engine.connect()
    except Exception as e:  # pragma: no cover - 无 DB 时跳过
        pytest.skip(f"租户库 {TEST_TENANT} 不可连接：{e}")

    trans = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await conn.close()
        await engine.dispose()
