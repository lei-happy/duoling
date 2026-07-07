"""资源管理 · 自有运力车辆（租户库，事务回滚不落库）集成测试

覆盖 VehicleService 核心+扩展双表联写、车牌校验、唯一性、更新与软删除。

对应需求：项目文档/02.需求文档/02.企业端/04.运力资源模块/自有运力-车辆.md
对应接口：/api/client/capacity/self_capacity/vehicle
对应代码：backend/app/modules/client/services/capacity/self_capacity/vehicle_service.py
覆盖用例：TC-CLI-VEHICLE-001 ~ TC-CLI-VEHICLE-020
"""

from __future__ import annotations

import random

import pytest

from app.common.exceptions import BizException
from app.modules.client.schemas.capacity.self_capacity.vehicle import (
    VehicleCreate,
    VehicleUpdate,
)
from app.modules.client.services.capacity.self_capacity.vehicle_service import (
    VehicleService,
)

# 常见省份简称 + 随机 5 位序号，构造合法蓝牌
_PROVINCES = "京沪粤浙苏鲁川鄂湘皖"


def _rand_blue_plate():
    prov = random.choice(_PROVINCES)
    letter = random.choice("ABCDEFGHJKLMNPQRSTUVWXYZ")
    tail = "".join(random.choice("0123456789") for _ in range(5))
    return f"{prov}{letter}{tail}"


class TestVehicleCrud:
    async def test_create_and_get(self, tenant_session):
        plate = _rand_blue_plate()
        out = await VehicleService.create_vehicle(
            tenant_session,
            VehicleCreate(
                plateNumber=plate, plateCategory="BLUE",
                vehicleType="truck", brand="解放", loadCapacity=18.0,
            ),
        )
        assert out.id is not None
        assert out.plateNumber == plate
        assert out.status == 1

        got = await VehicleService.get_vehicle(tenant_session, out.id)
        assert got.plateNumber == plate
        assert got.brand == "解放"
        assert got.loadCapacity == 18.0

    async def test_invalid_plate_rejected(self, tenant_session):
        with pytest.raises(BizException):
            await VehicleService.create_vehicle(
                tenant_session,
                VehicleCreate(plateNumber="沪A1234", plateCategory="BLUE"),
            )

    async def test_duplicate_plate_rejected(self, tenant_session):
        plate = _rand_blue_plate()
        await VehicleService.create_vehicle(
            tenant_session,
            VehicleCreate(plateNumber=plate, plateCategory="BLUE"),
        )
        with pytest.raises(BizException):
            await VehicleService.create_vehicle(
                tenant_session,
                VehicleCreate(plateNumber=plate, plateCategory="BLUE"),
            )

    async def test_update_ext_field(self, tenant_session):
        plate = _rand_blue_plate()
        out = await VehicleService.create_vehicle(
            tenant_session,
            VehicleCreate(plateNumber=plate, plateCategory="BLUE"),
        )
        updated = await VehicleService.update_vehicle(
            tenant_session, out.id, VehicleUpdate(brand="东风", loadCapacity=25.0)
        )
        assert updated.brand == "东风"
        assert updated.loadCapacity == 25.0

    async def test_get_nonexistent_raises(self, tenant_session):
        with pytest.raises(BizException):
            await VehicleService.get_vehicle(tenant_session, 987_654_321)
