"""运力分组服务集成测试（连接测试租户库，事务回滚不落库）

覆盖：分组创建/唯一校验/编辑/启停/删除、成员批量增删、多组归属、
以司机为锚点的 get_group_ids_for_driver（供计费预加载）。

对应需求：doc/02.需求文档/02.企业端/02.资源管理模块/05.运力分组.md
对应代码：backend/app/modules/client/services/capacity/self_capacity/capacity_group_service.py
覆盖用例：TC-CLI-CAPGROUP-001 ~ TC-CLI-CAPGROUP-020
"""

from __future__ import annotations

import pytest

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.schemas.capacity.self_capacity.capacity_group import (
    CapacityGroupCreate,
    CapacityGroupUpdate,
)
from app.modules.client.services.capacity.self_capacity.capacity_group_service import (
    CapacityGroupService,
)

from tests.client.conftest import unique_code, unique_phone

pytestmark = pytest.mark.asyncio


async def _make_capacity(session, driver_id: int, name: str, plate: str) -> Capacity:
    cap = Capacity(
        driver_id=driver_id,
        driver_name=name,
        driver_phone=unique_phone(),
        vehicle_id=driver_id * 10 + 1,
        plate_number=plate,
        status=1,
        operation_status=1,
    )
    session.add(cap)
    await session.flush()
    return cap


async def test_create_and_name_unique(tenant_session):
    name = f"测试分组_{unique_code('N')}"
    out = await CapacityGroupService.create_group(
        tenant_session, CapacityGroupCreate(groupName=name), operator_user_id=1
    )
    assert out.id and out.groupName == name
    assert out.groupCode  # 留空自动生成
    assert out.status == 1

    # 同名再建 → 业务异常
    with pytest.raises(BizException):
        await CapacityGroupService.create_group(
            tenant_session, CapacityGroupCreate(groupName=name)
        )


async def test_code_unique(tenant_session):
    code = unique_code("CG")
    await CapacityGroupService.create_group(
        tenant_session,
        CapacityGroupCreate(groupName=f"A_{unique_code('N')}", groupCode=code),
    )
    with pytest.raises(BizException):
        await CapacityGroupService.create_group(
            tenant_session,
            CapacityGroupCreate(groupName=f"B_{unique_code('N')}", groupCode=code),
        )


async def test_update_and_status_and_delete(tenant_session):
    out = await CapacityGroupService.create_group(
        tenant_session, CapacityGroupCreate(groupName=f"改_{unique_code('N')}")
    )
    new_name = f"改后_{unique_code('N')}"
    upd = await CapacityGroupService.update_group(
        tenant_session, out.id, CapacityGroupUpdate(groupName=new_name, color="#FF0000")
    )
    assert upd.groupName == new_name and upd.color == "#FF0000"

    await CapacityGroupService.update_status(tenant_session, out.id, 0)
    page = await CapacityGroupService.page_groups(tenant_session, status=0)
    assert any(g["id"] == out.id for g in page["list"])

    await CapacityGroupService.delete_group(tenant_session, out.id)
    with pytest.raises(BizException):
        await CapacityGroupService.update_status(tenant_session, out.id, 1)


async def test_members_add_dedupe_and_remove(tenant_session):
    g = await CapacityGroupService.create_group(
        tenant_session, CapacityGroupCreate(groupName=f"成员_{unique_code('N')}")
    )
    d1 = 900001
    d2 = 900002
    cap1 = await _make_capacity(tenant_session, d1, "张三", "沪A00001")
    cap2 = await _make_capacity(tenant_session, d2, "李四", "沪A00002")

    res = await CapacityGroupService.add_members(
        tenant_session, g.id, [cap1.id, cap2.id], operator_user_id=1
    )
    assert res["added"] == 2

    # 重复添加同一司机 → 全部跳过，抛业务异常
    with pytest.raises(BizException):
        await CapacityGroupService.add_members(tenant_session, g.id, [cap1.id])

    members = await CapacityGroupService.page_members(tenant_session, g.id)
    assert members["total"] == 2

    # 移出一个（按 driver_id）
    rm = await CapacityGroupService.remove_members(
        tenant_session, g.id, driver_ids=[d1]
    )
    assert rm["removed"] == 1
    members2 = await CapacityGroupService.page_members(tenant_session, g.id)
    assert members2["total"] == 1


async def test_multi_group_and_group_ids_for_driver(tenant_session):
    driver_id = 900010
    cap = await _make_capacity(tenant_session, driver_id, "多组司机", "沪A00010")

    g1 = await CapacityGroupService.create_group(
        tenant_session, CapacityGroupCreate(groupName=f"月薪_{unique_code('N')}")
    )
    g2 = await CapacityGroupService.create_group(
        tenant_session, CapacityGroupCreate(groupName=f"华东_{unique_code('N')}")
    )
    await CapacityGroupService.add_members(tenant_session, g1.id, [cap.id])
    await CapacityGroupService.add_members(tenant_session, g2.id, [cap.id])

    ids = await CapacityGroupService.get_group_ids_for_driver(tenant_session, driver_id)
    assert {g1.id, g2.id} <= ids

    # 停用 g2 后不应再计入（计费仅取启用分组）
    await CapacityGroupService.update_status(tenant_session, g2.id, 0)
    ids2 = await CapacityGroupService.get_group_ids_for_driver(tenant_session, driver_id)
    assert g1.id in ids2 and g2.id not in ids2


async def test_member_count_in_page(tenant_session):
    g = await CapacityGroupService.create_group(
        tenant_session, CapacityGroupCreate(groupName=f"计数_{unique_code('N')}")
    )
    cap = await _make_capacity(tenant_session, 900020, "计数司机", "沪A00020")
    await CapacityGroupService.add_members(tenant_session, g.id, [cap.id])

    page = await CapacityGroupService.page_groups(tenant_session, keyword=g.groupName)
    row = next(x for x in page["list"] if x["id"] == g.id)
    assert row["memberCount"] == 1
