"""共享测试基座（全端复用）

本文件提供接口测试的通用 fixture，供 ``tests/console``、``tests/client``、
``tests/driver``、``tests/open`` 等各端脚本复用：

1. **HTTP 测试客户端**：基于 ``httpx.AsyncClient`` + ``ASGITransport`` 直连
   ``app.main:app``，无需真正起 uvicorn 端口。
2. **平台库事务回滚 Session**：连接平台库 ``zt_platform_ci``，开启外层事务，
   通过 ``dependency_overrides`` 注入到 ``get_platform_db``，测试结束整体
   ``rollback``——**任何写操作都不会落库**。
3. **健壮的 skip**：本地无法连接数据库时，依赖 DB 的 fixture 走 ``pytest.skip``，
   而非 fail；纯逻辑用例不依赖这些 fixture，可正常收集并通过。
4. **各端登录辅助**：``login_console`` 已实现；``login_client`` / ``login_driver``
   预留同款签名（租户维度），其他端脚本可直接复用，避免重复造轮子。

设计要点
--------
- ``get_platform_db`` 被覆盖为「绑定到同一连接、``join_transaction_mode=
  create_savepoint``」的 Session。业务代码内部的 ``db.commit()`` 只会释放
  SAVEPOINT，最终外层事务 ``rollback`` 时全部回滚。
- 认证 client 通过真实登录接口 ``POST /api/console/auth/login`` 拿 token，
  再塞进 ``Authorization`` 头，贴近真实调用链（含 ``TenantMiddleware`` 解析）。
- ``make_console_token`` 提供「伪造 token」能力，便于构造越权/异常 token 的反向用例，
  不依赖库内是否已 seed 特定用户。

对应测试体系总纲：``项目文档/06.测试用例体系/README.md``
"""

from __future__ import annotations

from typing import AsyncGenerator, Optional, Tuple

import httpx
import pytest
from httpx import ASGITransport


# ============================================================
# 常量：测试租户 / 各端默认账号
# ============================================================

TENANT_CODE = "1001"  # 固定测试租户（开发库 zt_biz_1001_ci）

# 运营后台端（Console）默认超级管理员（见 backend/scripts/seed/seed_data.py）
CONSOLE_ADMIN_PHONE = "13800000000"
CONSOLE_ADMIN_PASSWORD = "admin123"

# 其他端登录默认账号占位（由对应端脚本按需覆盖/补充；此处仅登记，避免硬编码分散）
CLIENT_LOGIN_DEFAULT = {"phone": "13800000000", "password": "admin123", "tenant_code": TENANT_CODE}
DRIVER_LOGIN_DEFAULT = {"phone": "", "password": ""}

BASE_URL = "http://test"


# ============================================================
# 底层工具
# ============================================================

def _get_app():
    """惰性导入 FastAPI app（避免收集期就触发重依赖导入）"""
    from app.main import app

    return app


def _platform_db_url() -> str:
    from app.core.config import get_settings

    return get_settings().platform_db_url


# ============================================================
# 平台库事务回滚 Session
# ============================================================

@pytest.fixture()
async def _platform_conn():
    """连接平台库并开启外层事务；结束时 rollback，保证不落库。

    连接失败（本地无 DB / 网络不通）→ 整体 skip。
    """
    from sqlalchemy.ext.asyncio import create_async_engine

    try:
        engine = create_async_engine(_platform_db_url())
        conn = await engine.connect()
    except Exception as e:  # pragma: no cover - 环境无 DB 时跳过
        pytest.skip(f"平台库不可连接：{e}")

    trans = await conn.begin()
    try:
        yield conn
    finally:
        if trans.is_active:
            await trans.rollback()
        await conn.close()
        await engine.dispose()


@pytest.fixture()
async def platform_db(_platform_conn):
    """绑定到外层事务连接的 AsyncSession。

    ``join_transaction_mode="create_savepoint"``：业务代码内部 commit 只释放
    SAVEPOINT，外层事务不受影响，最终统一回滚。
    """
    from sqlalchemy.ext.asyncio import AsyncSession

    session = AsyncSession(
        bind=_platform_conn,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        await session.close()


# ============================================================
# HTTP 客户端
# ============================================================

@pytest.fixture()
async def app_with_rollback_db(platform_db):
    """返回注入了「回滚 Session」的 app，并在结束时清理 dependency_overrides。"""
    from app.core.dependencies import get_platform_db

    app = _get_app()

    async def _override_platform_db() -> AsyncGenerator:
        yield platform_db

    app.dependency_overrides[get_platform_db] = _override_platform_db
    try:
        yield app
    finally:
        app.dependency_overrides.pop(get_platform_db, None)


@pytest.fixture()
async def client(app_with_rollback_db) -> AsyncGenerator[httpx.AsyncClient, None]:
    """未认证 HTTP 客户端（平台库写操作走回滚，不落库）。

    ``raise_app_exceptions=False``：未处理的服务端异常（500）以 HTTP 响应形式
    返回，与生产环境（全局异常处理器返回 500）一致，便于对错误路径断言，
    而不是把异常抛进测试框架。
    """
    transport = ASGITransport(app=app_with_rollback_db, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as c:
        yield c


# ============================================================
# 登录辅助
# ============================================================

async def login_console(
    c: httpx.AsyncClient,
    phone: str = CONSOLE_ADMIN_PHONE,
    password: str = CONSOLE_ADMIN_PASSWORD,
) -> Tuple[Optional[str], httpx.Response]:
    """运营后台端登录，返回 (access_token 或 None, 原始响应)。"""
    resp = await c.post(
        "/api/console/auth/login",
        json={"phone": phone, "password": password},
    )
    token = None
    if resp.status_code == 200:
        body = resp.json()
        if body.get("code") == 0 and body.get("data"):
            token = body["data"].get("access_token")
    return token, resp


async def login_client(
    c: httpx.AsyncClient,
    phone: str = CLIENT_LOGIN_DEFAULT["phone"],
    password: str = CLIENT_LOGIN_DEFAULT["password"],
    tenant_code: Optional[str] = TENANT_CODE,
) -> Tuple[Optional[str], httpx.Response]:
    """企业端登录辅助（预留，供 tests/client 复用）。

    企业端可能返回多企业选择态，调用方需自行处理 needSelectTenant。
    """
    payload = {"phone": phone, "password": password}
    if tenant_code:
        payload["tenant_code"] = tenant_code
    resp = await c.post("/api/client/auth/login", json=payload)
    token = None
    if resp.status_code == 200:
        body = resp.json()
        data = body.get("data") or {}
        if body.get("code") == 0 and data.get("access_token"):
            token = data.get("access_token")
    return token, resp


def make_console_token(
    user_id: int = 1,
    phone: str = CONSOLE_ADMIN_PHONE,
    user_type: int = 0,
    roles: Optional[list] = None,
) -> str:
    """伪造一枚 Console 端 access_token（用于越权/异常 token 反向用例）。

    不查库，直接用项目的签名逻辑，保证中间件能正常解析。
    """
    from app.core.security import TokenData, create_access_token

    return create_access_token(
        TokenData(
            user_id=user_id,
            phone=phone,
            user_type=user_type,
            tenant_code=None,
            roles=roles or ["super_admin"],
        )
    )


@pytest.fixture()
async def console_token(client) -> str:
    """通过真实登录接口获取运营后台管理员 token；登录失败则 skip。"""
    token, resp = await login_console(client)
    if not token:
        pytest.skip(
            f"运营后台管理员登录失败，无法进行认证接口测试："
            f"status={resp.status_code} body={resp.text[:200]}"
        )
    return token


@pytest.fixture()
async def auth_client(app_with_rollback_db, console_token) -> AsyncGenerator[httpx.AsyncClient, None]:
    """已认证的运营后台 HTTP 客户端（默认带 Authorization 头）。"""
    transport = ASGITransport(app=app_with_rollback_db, raise_app_exceptions=False)
    headers = {"Authorization": f"Bearer {console_token}"}
    async with httpx.AsyncClient(
        transport=transport, base_url=BASE_URL, headers=headers
    ) as c:
        yield c
