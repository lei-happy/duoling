"""驾驶员 H5 端测试共享 fixture（本端自建，不依赖根 conftest.py）

设计与 ``tests/test_driver_fund_account.py`` 对齐：
- **集成测试**统一连接测试租户库 ``1001``（库 ``zt_biz_1001_ci``），在**外层事务
  中执行并最终 rollback**，不向数据库落任何数据；
- 本地无法连接租户库时，相关 fixture 直接 ``pytest.skip``，用例记为 skip 而非 fail；
- 纯逻辑用例（Pydantic schema / 输出裁剪等）不依赖以下任何 fixture。

对应设计：doc/01.架构设计/驾驶员H5架构设计.md
        doc/02.需求文档/03.移动端/02.驾驶员H5端/**
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


@pytest.fixture()
async def driver_dispatched_task(driver_ctx):
    """预置司机运力 + 已派车任务 + 1 条待装车挂接行（供全流程集成测试）。"""
    import uuid

    from app.modules.client.models.capacity.self_capacity.capacity import Capacity
    from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
    from app.modules.client.models.task.task import Task
    from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
    from app.modules.client.models.waybill.waybill import Waybill
    from app.modules.client.models.waybill.waybill_cargo import WaybillCargo

    session, ctx = driver_ctx
    suffix = uuid.uuid4().hex[:8]

    waybill = Waybill(
        waybill_no=f"WB{suffix}",
        origin="上海",
        destination="北京",
        quantity=1,
        status=3,
    )
    session.add(waybill)
    await session.flush()

    cargo = WaybillCargo(
        waybill_id=int(waybill.id),
        vehicle_brand="测试品牌",
        vehicle_model="测试车型",
        quantity=1,
        allocated_quantity=1,
    )
    session.add(cargo)
    await session.flush()

    vehicle = Vehicle(
        plate_number=f"沪T{suffix[:5].upper()}",
        plate_category="YELLOW",
    )
    session.add(vehicle)
    await session.flush()

    capacity = Capacity(
        driver_id=ctx.driver_id,
        driver_name=ctx.driver.name,
        driver_phone=ctx.phone,
        vehicle_id=int(vehicle.id),
        plate_number=vehicle.plate_number,
    )
    session.add(capacity)
    await session.flush()

    task = Task(
        task_no=f"TD{suffix}",
        task_name="H5全流程测试",
        status=1,
        capacity_id=int(capacity.id),
        carrier_type=1,
        origin="上海",
        destination="北京",
        main_driver_name=ctx.driver.name,
        plate_number=vehicle.plate_number,
        total_quantity=1,
        waybill_count=1,
    )
    session.add(task)
    await session.flush()

    item = TaskWaybillItem(
        task_id=int(task.id),
        waybill_id=int(waybill.id),
        waybill_cargo_id=int(cargo.id),
        waybill_no=waybill.waybill_no,
        quantity=1,
        status=0,
    )
    session.add(item)
    await session.flush()

    yield session, ctx, task, item


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
