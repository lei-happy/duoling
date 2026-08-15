"""运营调度 · 任务单调度（租户库，事务回滚不落库）集成测试

验证任务单创建、挂接计划明细与分页查询等调度核心链路。

对应需求：doc/02.需求文档/02.企业端/06.运营调度模块/**
对应代码：backend/app/modules/client/services/task/task_service.py
覆盖用例：TC-CLI-TASK-050（创建+挂接子集）
"""

from __future__ import annotations

import uuid
from datetime import date as ddate

import pytest

from app.common.exceptions import BizException
from app.modules.client.models.task.constants import CarrierType
from app.modules.client.models.task.task_status_event import (
    TASK_EVENT_ASSIGN_CARRIER,
    TASK_EVENT_CANCEL,
    TASK_EVENT_CREATE,
    TASK_EVENT_DELIVER,
    TASK_EVENT_DEPART,
    TASK_EVENT_DISPATCH,
    TASK_EVENT_LOAD,
    TASK_EVENT_REVERT_DELIVER,
    TASK_EVENT_REVERT_DEPART,
    TASK_EVENT_SOURCE_CLIENT,
    TASK_EVENT_SOURCE_DRIVER,
    TASK_EVENT_SOURCE_SYSTEM,
)
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.schemas.partner.customer import CustomerCreate
from app.modules.client.schemas.task.task import (
    TaskCarrierAssignmentInfo, TaskCreate, TaskStatusUpdate,
)
from app.modules.client.schemas.task.task_waybill_item import (
    TaskWaybillItemIn, TaskWaybillItemStatusUpdate,
)
from app.modules.client.services.partner.customer_service import CustomerService
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_ARRIVED,
    TASK_CANCELLED,
    TASK_DISPATCHED,
    TASK_LOADED,
    TASK_ON_WAY,
    TASK_PENDING_ASSIGN,
    TASK_SIGNED,
)
from app.modules.client.services.task.task_service import TaskService
from app.modules.client.services.task.task_status_event_service import (
    TaskStatusEventService,
)
from app.modules.client.services.task.task_waybill_item_service import (
    TaskWaybillItemService,
)
from tests.client.conftest import unique_suffix


async def _seed_dispatchable_waybill(session, quantity: int = 3):
    customer = await CustomerService.create_customer(
        session,
        CustomerCreate(customerName=f"调度客户_{unique_suffix()}"),
    )
    waybill = Waybill(
        waybill_no=f"JH{unique_suffix()}",
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


async def _seed_task_with_item(session, quantity: int = 2):
    """建一张已分配承运方（status=0 待派车）的任务，返回 (task, 唯一挂接行)"""
    waybill, cargo = await _seed_dispatchable_waybill(session, quantity=quantity)
    task = await TaskService.create_task(
        session,
        TaskCreate(
            taskNo=f"RW{unique_suffix()}",
            waybillItems=[
                TaskWaybillItemIn(
                    waybillId=waybill.id,
                    waybillCargoId=cargo.id,
                    quantity=quantity,
                )
            ],
        ),
    )
    await TaskService.complete_carrier_assignment(
        session, task.id,
        TaskCarrierAssignmentInfo(carrierType=CarrierType.SELF),
        current_user_id=1,
    )
    items = await TaskWaybillItemService.list_items_of_task(session, task.id)
    return task, items[0]


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

    async def test_candidate_excludes_cargo_after_full_allocate(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session, quantity=1)
        await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    )
                ],
            ),
        )
        result = await TaskWaybillItemService.list_candidate_cargoes(
            tenant_session, keyword=waybill.waybill_no, limit=50
        )
        assert all(row.cargoId != cargo.id for row in result.items)
        assert result.quantityTotal == 0

    async def test_second_allocate_same_cargo_is_rejected(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session, quantity=1)
        await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    )
                ],
            ),
        )
        with pytest.raises(BizException) as ei:
            await TaskService.create_task(
                tenant_session,
                TaskCreate(
                    taskNo=f"RW{unique_suffix()}",
                    waybillItems=[
                        TaskWaybillItemIn(
                            waybillId=waybill.id,
                            waybillCargoId=cargo.id,
                            quantity=1,
                        )
                    ],
                ),
            )
        msg = str(ei.value)
        assert "已经配到其他任务" in msg
        assert "原台数" not in msg
        assert str(waybill.id) not in msg

    async def test_stale_allocated_column_does_not_block_create(self, tenant_session):
        """allocated_quantity 虚高但没有真实挂接时，不应拦住配载。"""
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session, quantity=1)
        cargo.allocated_quantity = 1
        await tenant_session.flush()

        task = await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    )
                ],
            ),
        )
        assert task.total_quantity == 1
        await tenant_session.refresh(cargo)
        assert int(cargo.allocated_quantity or 0) == 1

    async def test_duplicate_cargo_in_one_request_uses_remaining(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session, quantity=1)
        task = await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    ),
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    ),
                ],
            ),
        )
        items = await TaskWaybillItemService.list_items_of_task(
            tenant_session, task.id
        )
        assert len(items) == 1
        assert int(items[0].quantity) == 1
        assert task.total_quantity == 1

    async def test_create_skips_occupied_and_keeps_available(self, tenant_session):
        taken_wb, taken_cargo = await _seed_dispatchable_waybill(
            tenant_session, quantity=1
        )
        free_wb, free_cargo = await _seed_dispatchable_waybill(
            tenant_session, quantity=1
        )
        await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=taken_wb.id,
                        waybillCargoId=taken_cargo.id,
                        quantity=1,
                    )
                ],
            ),
        )
        task = await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=taken_wb.id,
                        waybillCargoId=taken_cargo.id,
                        quantity=1,
                    ),
                    TaskWaybillItemIn(
                        waybillId=free_wb.id,
                        waybillCargoId=free_cargo.id,
                        quantity=1,
                    ),
                ],
            ),
        )
        items = await TaskWaybillItemService.list_items_of_task(
            tenant_session, task.id
        )
        assert len(items) == 1
        assert int(items[0].waybill_cargo_id) == int(free_cargo.id)

    async def test_cancelled_task_items_do_not_block_create(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session, quantity=1)
        first = await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    )
                ],
            ),
        )
        first.status = 9
        await tenant_session.flush()
        second = await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    )
                ],
            ),
        )
        assert second.total_quantity == 1

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


class TestTaskStatusEvents:
    """状态事件（时间流）埋点：每次状态变更都要留痕并刷新 stage_entered_at"""

    async def test_create_records_event_and_stage_time(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session)
        task = await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    )
                ],
            ),
        )

        events = await TaskStatusEventService.list_events(tenant_session, task.id)
        assert [e.event_type for e in events] == [TASK_EVENT_CREATE]
        assert events[0].to_status == TASK_PENDING_ASSIGN
        assert task.stage_entered_at is not None

    async def test_assignment_and_cancel_append_events(self, tenant_session):
        waybill, cargo = await _seed_dispatchable_waybill(tenant_session)
        task = await TaskService.create_task(
            tenant_session,
            TaskCreate(
                taskNo=f"RW{unique_suffix()}",
                waybillItems=[
                    TaskWaybillItemIn(
                        waybillId=waybill.id,
                        waybillCargoId=cargo.id,
                        quantity=1,
                    )
                ],
            ),
        )
        await TaskService.complete_carrier_assignment(
            tenant_session, task.id,
            TaskCarrierAssignmentInfo(carrierType=CarrierType.SELF),
            current_user_id=1,
        )
        stage_after_assign = task.stage_entered_at

        await TaskService.cancel_task(
            tenant_session, task.id, reason="测试取消", current_user_id=1,
        )

        events = await TaskStatusEventService.list_events(tenant_session, task.id)
        assert [e.event_type for e in events] == [
            TASK_EVENT_CREATE, TASK_EVENT_ASSIGN_CARRIER, TASK_EVENT_CANCEL,
        ]
        cancel_event = events[-1]
        assert cancel_event.to_status == TASK_CANCELLED
        assert cancel_event.reason == "测试取消"
        assert cancel_event.operator_id == 1
        # 进入新阶段后停留计时重置
        assert task.stage_entered_at >= stage_after_assign

    async def test_full_chain_records_forward_and_revert_events(
        self, tenant_session
    ):
        """派车 → 装车（聚合）→ 出发 → 撤回出发：正向与逆向都要各留一条事件"""
        task, item = await _seed_task_with_item(tenant_session)

        await TaskService.update_status(
            tenant_session, task.id, TaskStatusUpdate(status=TASK_DISPATCHED),
            current_user_id=1,
        )
        # 全部 item 装车 → 由聚合驱动 task 1→2
        await TaskWaybillItemService.update_item_status(
            tenant_session, item.id, TaskWaybillItemStatusUpdate(status=1),
        )
        assert int(task.status) == TASK_LOADED

        await TaskService.update_status(
            tenant_session, task.id, TaskStatusUpdate(status=TASK_ON_WAY),
            current_user_id=1,
        )
        await TaskService.revert_status(
            tenant_session, task.id,
            target_status=TASK_LOADED,
            reason="测试撤回出发",
            current_user_id=1,
        )

        events = await TaskStatusEventService.list_events(tenant_session, task.id)
        assert [e.event_type for e in events] == [
            TASK_EVENT_CREATE,
            TASK_EVENT_ASSIGN_CARRIER,
            TASK_EVENT_DISPATCH,
            TASK_EVENT_LOAD,
            TASK_EVENT_DEPART,
            TASK_EVENT_REVERT_DEPART,
        ]
        # 聚合跳转来源为系统，人工跳转来源为企业端
        load_event = events[3]
        assert load_event.source == TASK_EVENT_SOURCE_SYSTEM
        assert events[4].source == TASK_EVENT_SOURCE_CLIENT
        revert_event = events[-1]
        assert revert_event.from_status == TASK_ON_WAY
        assert revert_event.to_status == TASK_LOADED
        assert revert_event.reason == "测试撤回出发"

    async def test_deliver_aggregation_records_system_event(self, tenant_session):
        """item 全部交车 → task 4→5 由聚合驱动，事件来源必须是系统聚合"""
        task, item = await _seed_task_with_item(tenant_session)
        await TaskService.update_status(
            tenant_session, task.id, TaskStatusUpdate(status=TASK_DISPATCHED),
            current_user_id=1,
        )
        await TaskWaybillItemService.update_item_status(
            tenant_session, item.id, TaskWaybillItemStatusUpdate(status=1),
        )
        await TaskService.update_status(
            tenant_session, task.id, TaskStatusUpdate(status=TASK_ON_WAY),
            current_user_id=1,
        )
        await TaskWaybillItemService.update_item_status(
            tenant_session, item.id, TaskWaybillItemStatusUpdate(status=2),
        )
        assert int(task.status) == TASK_ARRIVED

        await TaskWaybillItemService.update_item_status(
            tenant_session, item.id, TaskWaybillItemStatusUpdate(status=3),
        )
        assert int(task.status) == TASK_SIGNED

        events = await TaskStatusEventService.list_events(tenant_session, task.id)
        deliver = [e for e in events if e.event_type == TASK_EVENT_DELIVER]
        assert len(deliver) == 1
        assert deliver[0].source == TASK_EVENT_SOURCE_SYSTEM
        assert deliver[0].from_status == TASK_ARRIVED

        # 撤销交车（item 3→2）反向聚合，同样留痕
        await TaskWaybillItemService.update_item_status(
            tenant_session, item.id, TaskWaybillItemStatusUpdate(status=2),
        )
        assert int(task.status) == TASK_ARRIVED
        events = await TaskStatusEventService.list_events(tenant_session, task.id)
        assert events[-1].event_type == TASK_EVENT_REVERT_DELIVER
        assert events[-1].source == TASK_EVENT_SOURCE_SYSTEM

    async def test_driver_source_recorded(self, tenant_session):
        """司机端触发的状态变更，事件来源要记成驾驶员端而不是企业端"""
        task, item = await _seed_task_with_item(tenant_session)
        await TaskService.update_status(
            tenant_session, task.id, TaskStatusUpdate(status=TASK_DISPATCHED),
            current_user_id=1,
        )
        await TaskWaybillItemService.update_item_status(
            tenant_session, item.id, TaskWaybillItemStatusUpdate(status=1),
        )
        await TaskService.update_status(
            tenant_session, task.id, TaskStatusUpdate(status=TASK_ON_WAY),
            source=TASK_EVENT_SOURCE_DRIVER,
        )

        events = await TaskStatusEventService.list_events(tenant_session, task.id)
        depart = [e for e in events if e.event_type == TASK_EVENT_DEPART]
        assert len(depart) == 1
        assert depart[0].source == TASK_EVENT_SOURCE_DRIVER

    async def test_same_status_does_not_reset_stage_timer(self, tenant_session):
        """重复提交同一状态：不新增事件，也不能把「本阶段停留」计时清零"""
        task, _item = await _seed_task_with_item(tenant_session)
        stage_before = task.stage_entered_at
        events_before = await TaskStatusEventService.list_events(
            tenant_session, task.id
        )

        TaskStatusEventService.apply_status(
            tenant_session, task, int(task.status),
            event_type=TASK_EVENT_ASSIGN_CARRIER,
        )
        await tenant_session.flush()

        events_after = await TaskStatusEventService.list_events(
            tenant_session, task.id
        )
        assert len(events_after) == len(events_before)
        assert task.stage_entered_at == stage_before


class TestWorkbenchTimeFilter:
    """工作台时间维度筛选

    「进入当前阶段」必须对每条任务都成立，否则 KPI 卡片会在切换阶段时互相归零：
    按节点维度（如派车时间）筛选时，尚未走到该节点的任务字段为 NULL 会被整体排除。
    """

    @staticmethod
    def _today_range():
        today = ddate.today()
        return today, today

    async def test_stage_entered_at_covers_task_in_every_stage(self, tenant_session):
        """刚建的待派车任务，按「进入当前阶段」筛今天必须能筛到"""
        task, _item = await _seed_task_with_item(tenant_session)
        start, end = self._today_range()

        _tasks, total = await TaskService.page_tasks(
            tenant_session,
            page=1,
            page_size=20,
            keyword=task.task_no,
            time_field="stageEnteredAt",
            time_start=start,
            time_end=end,
        )
        assert total == 1

    async def test_stage_entered_at_follows_status_change(self, tenant_session):
        """状态推进后，进入阶段时间随之更新，任务仍在今天的窗口内"""
        task, _item = await _seed_task_with_item(tenant_session)
        await TaskService.update_status(
            tenant_session, task.id, TaskStatusUpdate(status=TASK_DISPATCHED),
            current_user_id=1,
        )
        start, end = self._today_range()

        _tasks, total = await TaskService.page_tasks(
            tenant_session,
            page=1,
            page_size=20,
            keyword=task.task_no,
            time_field="stageEnteredAt",
            time_start=start,
            time_end=end,
        )
        assert total == 1

    async def test_node_scoped_field_excludes_task_before_that_node(
        self, tenant_session
    ):
        """待派车任务没有派车时间，按「派车时间」筛必然落空——正是卡片归零的成因"""
        task, _item = await _seed_task_with_item(tenant_session)
        start, end = self._today_range()

        _tasks, total = await TaskService.page_tasks(
            tenant_session,
            page=1,
            page_size=20,
            keyword=task.task_no,
            time_field="dispatchedAt",
            time_start=start,
            time_end=end,
        )
        assert total == 0

    async def test_workbench_stats_stable_across_stage_dimension(
        self, tenant_session
    ):
        """同一批任务：按「进入当前阶段」统计时，待派车计数不受影响"""
        task, _item = await _seed_task_with_item(tenant_session)
        start, end = self._today_range()

        stats = await TaskService.workbench_stats(
            tenant_session,
            keyword=task.task_no,
            time_field="stageEnteredAt",
            time_start=start,
            time_end=end,
        )
        assert stats["totals"]["pendingDispatch"] == 1
