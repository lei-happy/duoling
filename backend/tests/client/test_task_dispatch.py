"""运营调度 · 任务单调度（租户库，事务回滚不落库）集成测试

验证任务单创建、挂接运单明细与分页查询等调度核心链路。

对应需求：doc/02.需求文档/02.企业端/06.运营调度模块/**
对应代码：backend/app/modules/client/services/task/task_service.py
覆盖用例：TC-CLI-TASK-050（创建+挂接子集）
"""

from __future__ import annotations

import uuid

import pytest

from app.common.exceptions import BizException
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.schemas.partner.customer import CustomerCreate
from app.modules.client.schemas.task.task import TaskCreate
from app.modules.client.schemas.task.task_waybill_item import TaskWaybillItemIn
from app.modules.client.services.partner.customer_service import CustomerService
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_PENDING_ASSIGN,
)
from app.modules.client.services.task.task_service import TaskService
from tests.client.conftest import unique_suffix


async def _seed_dispatchable_waybill(session, quantity: int = 3):
    customer = await CustomerService.create_customer(
        session,
        CustomerCreate(customerName=f"调度客户_{unique_suffix()}"),
    )
    waybill = Waybill(
        waybill_no=f"YD{unique_suffix()}",
        customer_id=customer.id,
        customer_name=customer.customer_name,
        origin="测试出发地",
        destination="测试目的地",
        quantity=quantity,
        status=1,
    )
    session.add(waybill)
    await session.flush()
    await session.refresh(waybill)

    cargo = WaybillCargo(
        waybill_id=waybill.id,
        quantity=quantity,
        vehicle_brand="测试品牌",
        vehicle_model="测试车型",
    )
    session.add(cargo)
    await session.flush()
    await session.refresh(cargo)
    return waybill, cargo


class TestTaskDispatch:
    async def test_create_task_with_waybill_items(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session)
        task_no = f"RW{unique_suffix()}"

        task = await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=task_no,
                taskName=f"集成测试任务_{uuid.uuid4().hex[:4]}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=2,
                    )
                ],
            ),
        )

        assert task.id is not None
        assert task.task_no == task_no
        assert int(task.status) == TASK_PENDING_ASSIGN
        assert task.total_quantity == 2
        assert task.waybill_count == 1

        tasks, total = await TaskService.page_tasks(
            tenant_session, page=1, page_size=20, keyword=task_no
        )
        assert total >= 1
        assert any(t.task_no == task_no for t in tasks)

        got = await TaskService.get_or_404(tenant_session, task.id)
        assert got.task_no == task_no

    async def test_list_candidate_cargoes_includes_seeded(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session, quantity=5)
        from app.modules.client.services.task.task_waybill_item_service import (
            TaskWaybillItemService,
        )

        result = await TaskWaybillItemService.list_candidate_cargoes(
            tenant_session, keyword=waybill.waybill_no, limit=50
        )
        assert result.quantityTotal >= 5
        assert any(row.cargoId == cargo.id for row in result.items)

    async def test_duplicate_task_no_rejected(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session)
        task_no = f"RW{unique_suffix()}"
        payload = TaskCreate(
            taskNo=task_no,
            waybillItems=[
                TaskWaybillItemIn(
                    waybillId=waybill.id,
                    waybillCargoId=cargo.id,
                    quantity=1,
                )
            ],
        )
        await TaskService.create_task(tenant_session, payload)
        waybill2, cargo2 = await _seed_dispatchable_waybill(tenant_session)

        with pytest.raises(BizException):
            await TaskService.create_task(
                tenant_session,
                TaskCreate(
                    taskNo=task_no,
                    waybillItems=[
                        TaskWaybillItemIn(
                            waybillId=waybill2.id,
                            waybillCargoId=cargo2.id,
                            quantity=1,
                        )
                    ],
                ),
            )
