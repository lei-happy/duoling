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
from sqlalchemy import select

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
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.driver.driver_route import (
    DriverRoute,
)
from app.modules.client.models.capacity.social_capacity.social_capacity import (
    SocialCapacity,
)
from app.modules.client.services.capacity.self_capacity.recommend.service import (
    SOCIAL_POOL_ENGINE,
)
from app.modules.client.models.task.task_dispatch_selection import (
    TaskDispatchSelection,
)
from app.modules.client.schemas.task.task import (
    DispatchSelectionFeedback,
    TaskAssignCarrierRequest,
    TaskCarrierAssignmentInfo,
    TaskCarrierInfo,
    TaskCreate,
    TaskStatusUpdate,
)
from app.modules.client.services.capacity.self_capacity.capacity_service import (
    CapacityService,
)
from app.modules.client.services.capacity.self_capacity.recommend import (
    CapacityRecommendService,
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
from tests.client.conftest import unique_phone, unique_suffix


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


async def _seed_social_capacity(
    session,
    *,
    name: str,
    phone: str | None = None,
    plate: str | None = None,
    id_card: str | None = None,
    approval_status: int = 2,
    status: int = 1,
    rating_score: float | None = None,
    rating_level: int | None = None,
):
    cap = SocialCapacity(
        social_code=f"S{unique_suffix()}",
        driver_name=name,
        driver_phone=phone or unique_phone(),
        plate_number=plate or f"皖{unique_suffix(5)}",
        driver_id_card=id_card,
        approval_status=approval_status,
        status=status,
        rating_score=rating_score,
        rating_level=rating_level,
    )
    session.add(cap)
    await session.flush()
    await session.refresh(cap)
    return cap


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


def _unique_driver_id() -> int:
    return int(uuid.uuid4().int % 1_000_000_000) + 20_000_000


async def _make_capacity(
    session,
    *,
    name: str,
    plate: str,
    operation_status: int,
    driver_id: int | None = None,
) -> Capacity:
    cap = Capacity(
        driver_id=driver_id or _unique_driver_id(),
        driver_name=name,
        driver_phone=unique_phone(),
        vehicle_id=_unique_driver_id(),
        plate_number=plate,
        status=1,
        operation_status=operation_status,
    )
    session.add(cap)
    await session.flush()
    return cap


class TestCapacityRecommendAndSelection:
    async def test_heuristic_orders_available_route_then_transit(
        self, tenant_session
    ):
        task, _item = await _seed_task_with_item(tenant_session)
        task.origin = "石家庄"
        task.origin_code = "130100"
        task.destination = "三明"
        task.destination_code = "350400"
        await tenant_session.flush()

        tag = unique_suffix(4)
        available_route = await _make_capacity(
            tenant_session,
            name=f"推荐甲{tag}",
            plate=f"冀A{tag}1",
            operation_status=1,
        )
        available = await _make_capacity(
            tenant_session,
            name=f"推荐乙{tag}",
            plate=f"冀A{tag}2",
            operation_status=1,
        )
        in_transit = await _make_capacity(
            tenant_session,
            name=f"推荐丙{tag}",
            plate=f"冀A{tag}3",
            operation_status=2,
        )
        on_leave = await _make_capacity(
            tenant_session,
            name=f"休假丁{tag}",
            plate=f"冀A{tag}4",
            operation_status=3,
        )
        tenant_session.add(
            DriverRoute(
                driver_id=available_route.driver_id,
                origin_code="130100",
                origin_name="石家庄",
                dest_code="350400",
                dest_name="三明",
                status=1,
            )
        )
        await tenant_session.flush()

        result = await CapacityRecommendService.recommend_for_task(
            tenant_session, task.id, limit=50,
        )
        assert result.engine == "heuristic_v1"
        ranks = {item.capacityId: item.rank for item in result.items}
        assert available_route.id in ranks
        assert available.id in ranks
        assert in_transit.id in ranks
        assert on_leave.id not in ranks
        assert ranks[available_route.id] < ranks[available.id] < ranks[in_transit.id]

        top = next(
            item for item in result.items if item.capacityId == available_route.id
        )
        codes = {r.code for r in top.reasons}
        assert "AVAILABLE" in codes
        assert "FAMILIAR_ROUTE" in codes
        assert any("常跑" in r.text for r in top.reasons)

        transit = next(
            item for item in result.items if item.capacityId == in_transit.id
        )
        assert any(r.code == "IN_TRANSIT" for r in transit.reasons)

        filtered = await CapacityRecommendService.recommend_for_task(
            tenant_session, task.id, keyword=f"休假丁{tag}", limit=20,
        )
        leave_ids = {item.capacityId for item in filtered.items}
        assert on_leave.id in leave_ids
        leave_item = next(
            item for item in filtered.items if item.capacityId == on_leave.id
        )
        assert any(r.code == "ON_LEAVE" for r in leave_item.reasons)

    async def test_occupied_capacity_excluded_from_default_recommend(
        self, tenant_session
    ):
        """已被其他未完成任务占用的运力，默认推荐不再出现。"""
        pending_task, _ = await _seed_task_with_item(tenant_session)
        occupied = await _make_capacity(
            tenant_session,
            name=f"占用司机{unique_suffix(4)}",
            plate=f"冀D{unique_suffix(4)}",
            operation_status=1,
        )
        occupying_task, _ = await _seed_task_with_item(tenant_session)
        await TaskService.assign_carrier(
            tenant_session,
            occupying_task.id,
            TaskAssignCarrierRequest(
                carrier=TaskCarrierInfo(
                    carrierType=CarrierType.SELF,
                    capacityId=occupied.id,
                    mainDriverName=occupied.driver_name,
                    plateNumber=occupied.plate_number,
                ),
            ),
            current_user_id=1,
        )

        default = await CapacityRecommendService.recommend_for_task(
            tenant_session, pending_task.id, limit=50,
        )
        default_ids = {item.capacityId for item in default.items}
        assert occupied.id not in default_ids

        searched = await CapacityRecommendService.recommend_for_task(
            tenant_session,
            pending_task.id,
            keyword=occupied.driver_name,
            limit=20,
        )
        hit = next(
            item for item in searched.items if item.capacityId == occupied.id
        )
        assert any(r.code == "ASSIGNED_OTHER" for r in hit.reasons)
        assert not any(r.code == "AVAILABLE" for r in hit.reasons)

        reassign = await CapacityRecommendService.recommend_for_task(
            tenant_session, occupying_task.id, limit=50,
        )
        reassign_ids = {item.capacityId for item in reassign.items}
        assert occupied.id in reassign_ids

    async def test_assign_carrier_writes_capacity_in_transit(
        self, tenant_session
    ):
        task, _item = await _seed_task_with_item(tenant_session)
        cap = await _make_capacity(
            tenant_session,
            name=f"回写司机{unique_suffix(4)}",
            plate=f"冀E{unique_suffix(4)}",
            operation_status=1,
        )
        await TaskService.assign_carrier(
            tenant_session,
            task.id,
            TaskAssignCarrierRequest(
                carrier=TaskCarrierInfo(
                    carrierType=CarrierType.SELF,
                    capacityId=cap.id,
                    mainDriverName=cap.driver_name,
                    plateNumber=cap.plate_number,
                ),
            ),
            current_user_id=1,
        )
        await tenant_session.refresh(cap)
        assert int(cap.operation_status) == 2

        await TaskService.cancel_task(
            tenant_session, task.id, reason="测试释放运力", current_user_id=1,
        )
        await tenant_session.refresh(cap)
        assert int(cap.operation_status) == 1

    async def test_reassign_releases_previous_capacity(self, tenant_session):
        task, _item = await _seed_task_with_item(tenant_session)
        old = await _make_capacity(
            tenant_session,
            name=f"原司机{unique_suffix(4)}",
            plate=f"冀F{unique_suffix(4)}",
            operation_status=1,
        )
        new = await _make_capacity(
            tenant_session,
            name=f"新司机{unique_suffix(4)}",
            plate=f"冀G{unique_suffix(4)}",
            operation_status=1,
        )
        await TaskService.assign_carrier(
            tenant_session,
            task.id,
            TaskAssignCarrierRequest(
                carrier=TaskCarrierInfo(
                    carrierType=CarrierType.SELF,
                    capacityId=old.id,
                    mainDriverName=old.driver_name,
                    plateNumber=old.plate_number,
                ),
            ),
            current_user_id=1,
        )
        await TaskService.assign_carrier(
            tenant_session,
            task.id,
            TaskAssignCarrierRequest(
                carrier=TaskCarrierInfo(
                    carrierType=CarrierType.SELF,
                    capacityId=new.id,
                    mainDriverName=new.driver_name,
                    plateNumber=new.plate_number,
                ),
            ),
            current_user_id=1,
        )
        await tenant_session.refresh(old)
        await tenant_session.refresh(new)
        assert int(old.operation_status) == 1
        assert int(new.operation_status) == 2

    async def test_list_stats_heals_stale_idle_capacity(self, tenant_session):
        task, _item = await _seed_task_with_item(tenant_session)
        cap = await _make_capacity(
            tenant_session,
            name=f"漂移司机{unique_suffix(4)}",
            plate=f"冀H{unique_suffix(4)}",
            operation_status=1,
        )
        await TaskService.assign_carrier(
            tenant_session,
            task.id,
            TaskAssignCarrierRequest(
                carrier=TaskCarrierInfo(
                    carrierType=CarrierType.SELF,
                    capacityId=cap.id,
                    mainDriverName=cap.driver_name,
                    plateNumber=cap.plate_number,
                ),
            ),
            current_user_id=1,
        )
        cap.operation_status = 1
        await tenant_session.flush()

        stats = await CapacityService.list_stats(tenant_session)
        await tenant_session.refresh(cap)
        assert int(cap.operation_status) == 2
        assert stats["inTransit"] >= 1

    async def test_assign_carrier_writes_selection(self, tenant_session):
        task, _item = await _seed_task_with_item(tenant_session)
        cap = await _make_capacity(
            tenant_session,
            name="留痕司机",
            plate=f"冀B{unique_suffix(4)}",
            operation_status=1,
        )
        await TaskService.assign_carrier(
            tenant_session,
            task.id,
            TaskAssignCarrierRequest(
                carrier=TaskCarrierInfo(
                    carrierType=CarrierType.SELF,
                    capacityId=cap.id,
                    mainDriverName=cap.driver_name,
                    plateNumber=cap.plate_number,
                ),
                selection=DispatchSelectionFeedback(
                    engine="heuristic_v1",
                    source="recommended",
                    shownCapacityIds=[cap.id],
                    topRecommendedId=cap.id,
                    selectedCapacityId=cap.id,
                    selectedRank=1,
                ),
            ),
            current_user_id=1,
        )
        rows = (
            await tenant_session.execute(
                select(TaskDispatchSelection).where(
                    TaskDispatchSelection.task_id == task.id,
                    TaskDispatchSelection.is_deleted == 0,
                )
            )
        ).scalars().all()
        assert len(rows) == 1
        assert rows[0].engine == "heuristic_v1"
        assert rows[0].source == "recommended"
        assert rows[0].adopted == 1
        assert rows[0].selected_capacity_id == cap.id
        assert rows[0].shown_capacity_ids == [cap.id]

    async def test_assign_carrier_without_selection_still_works(
        self, tenant_session
    ):
        task, _item = await _seed_task_with_item(tenant_session)
        cap = await _make_capacity(
            tenant_session,
            name="无留痕司机",
            plate=f"冀C{unique_suffix(4)}",
            operation_status=1,
        )
        await TaskService.assign_carrier(
            tenant_session,
            task.id,
            TaskAssignCarrierRequest(
                carrier=TaskCarrierInfo(
                    carrierType=CarrierType.SELF,
                    capacityId=cap.id,
                    mainDriverName=cap.driver_name,
                    plateNumber=cap.plate_number,
                ),
            ),
            current_user_id=1,
        )
        refreshed = await TaskService.get_or_404(tenant_session, task.id)
        assert int(refreshed.status) == TASK_DISPATCHED
        assert refreshed.capacity_id == cap.id
        rows = (
            await tenant_session.execute(
                select(TaskDispatchSelection).where(
                    TaskDispatchSelection.task_id == task.id,
                    TaskDispatchSelection.is_deleted == 0,
                )
            )
        ).scalars().all()
        assert rows == []

    async def test_social_task_recommend_lists_pool(self, tenant_session):
        task, _ = await _seed_task_with_item(tenant_session)
        task.carrier_type = CarrierType.SOCIAL
        await tenant_session.flush()

        high = await _seed_social_capacity(
            tenant_session, name="高评司机", rating_level=1, rating_score=4.8,
        )
        low = await _seed_social_capacity(
            tenant_session, name="低评司机", rating_level=3, rating_score=2.1,
        )
        draft = await _seed_social_capacity(
            tenant_session, name="草稿司机", approval_status=0, status=0,
        )

        result = await CapacityRecommendService.recommend_for_task(
            tenant_session, task.id, limit=50,
        )
        assert result.engine == SOCIAL_POOL_ENGINE
        ids = [item.capacityId for item in result.items]
        assert high.id in ids
        assert low.id in ids
        assert draft.id not in ids
        assert ids.index(high.id) < ids.index(low.id)
        top = next(item for item in result.items if item.capacityId == high.id)
        assert any(r.code == "RATING" and "A" in r.text for r in top.reasons)

        filtered = await CapacityRecommendService.recommend_for_task(
            tenant_session, task.id, keyword=low.driver_name, limit=20,
        )
        assert {item.capacityId for item in filtered.items} == {low.id}

    async def test_assign_social_fills_snapshot_from_pool(self, tenant_session):
        task, _ = await _seed_task_with_item(tenant_session)
        task.carrier_type = CarrierType.SOCIAL
        await tenant_session.flush()
        social = await _seed_social_capacity(
            tenant_session,
            name="档案司机",
            phone="19912345678",
            plate="皖S12345",
            id_card="340123199001011234",
        )

        await TaskService.assign_carrier(
            tenant_session,
            task.id,
            TaskAssignCarrierRequest(
                carrier=TaskCarrierInfo(
                    carrierType=CarrierType.SOCIAL,
                    socialDriverId=social.id,
                ),
                selection=DispatchSelectionFeedback(
                    engine=SOCIAL_POOL_ENGINE,
                    source="recommended",
                    shownCapacityIds=[social.id],
                    topRecommendedId=social.id,
                    selectedCapacityId=social.id,
                    selectedRank=1,
                ),
            ),
            current_user_id=1,
        )
        refreshed = await TaskService.get_or_404(tenant_session, task.id)
        assert int(refreshed.status) == TASK_DISPATCHED
        assert refreshed.social_driver_id == social.id
        assert refreshed.main_driver_name == "档案司机"
        assert refreshed.main_driver_phone == "19912345678"
        assert refreshed.plate_number == "皖S12345"
        assert refreshed.main_driver_id_card == "340123199001011234"
