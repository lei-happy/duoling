"""运营调度 · 任务预警落库与口径一致性（租户库，事务回滚不落库）集成测试

改造前最刺眼的问题是「卡片上写着 3 条预警，点进去列表只有 1 条」——
卡片和列表各算各的。这里把两条链路放在同一批数据上跑，验证它们同源。

另外验证任务推进到下一阶段后，上一阶段的预警会自动消除而不是残留。

对应需求：doc/02.需求文档/02.企业端/06.运营调度模块/04.任务预警体系设计.md
对应代码：backend/app/modules/client/services/task/alert/engine.py
          backend/app/modules/client/services/task/task_alert_service.py
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from app.modules.client.models.task.constants import CarrierType
from app.modules.client.models.task.task_alert import (
    ALERT_LEVEL_CRITICAL,
    ALERT_STATUS_ACTIVE,
    ALERT_STATUS_AUTO_RESOLVED,
    TaskAlert,
)
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.schemas.partner.customer import CustomerCreate
from app.modules.client.schemas.task.task import TaskCarrierAssignmentInfo, TaskCreate
from app.modules.client.schemas.task.task_waybill_item import TaskWaybillItemIn
from app.modules.client.services.partner.customer_service import CustomerService
from app.modules.client.services.state_machine.task_state_machine import (
    TASK_DISPATCHED,
    TASK_PENDING_DISPATCH,
)
from app.modules.client.services.task.alert.catalog import RULE_DISPATCH_TIMEOUT
from app.modules.client.services.task.alert.engine import TaskAlertEngine
from app.modules.client.services.task.task_alert_service import TaskAlertService
from app.modules.client.services.task.task_service import TaskService
from tests.client.conftest import unique_suffix


async def _seed_overdue_task(session, *, overdue_hours: int = 5):
    """建一张「计划装车时间已过、仍停在待派车」的任务。"""
    customer = await CustomerService.create_customer(
        session, CustomerCreate(customerName=f"预警客户_{unique_suffix()}")
    )
    waybill = Waybill(
        waybill_no=f"JH{unique_suffix()}",
        customer_id=customer.id,
        customer_name=customer.customer_name,
        origin="测试出发地",
        destination="测试目的地",
        quantity=2,
        status=1,
    )
    session.add(waybill)
    await session.flush()
    cargo = WaybillCargo(waybill_id=waybill.id, quantity=2)
    session.add(cargo)
    await session.flush()

    task = await TaskService.create_task(
        session,
        TaskCreate(
            taskNo=f"RW{unique_suffix()}",
            plannedLoadTime=datetime.now() - timedelta(hours=overdue_hours),
            waybillItems=[
                TaskWaybillItemIn(
                    waybillId=waybill.id, waybillCargoId=cargo.id, quantity=2
                )
            ],
        ),
    )
    await TaskService.complete_carrier_assignment(
        session,
        task.id,
        TaskCarrierAssignmentInfo(carrierType=CarrierType.SELF),
        current_user_id=1,
    )
    await session.flush()
    return task


async def _alerts_of(session, task_id: int) -> list[TaskAlert]:
    r = await session.execute(
        select(TaskAlert).where(
            TaskAlert.task_id == task_id, TaskAlert.is_deleted == 0
        )
    )
    return list(r.scalars().all())


class TestTaskAlertMaterialization:
    async def test_overdue_task_gets_a_critical_alert(self, tenant_session):
        task = await _seed_overdue_task(tenant_session)

        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )

        alerts = await _alerts_of(tenant_session, task.id)
        by_code = {a.rule_code: a for a in alerts}
        assert RULE_DISPATCH_TIMEOUT in by_code
        hit = by_code[RULE_DISPATCH_TIMEOUT]
        assert hit.level == ALERT_LEVEL_CRITICAL
        assert hit.status == ALERT_STATUS_ACTIVE
        assert hit.stage == TASK_PENDING_DISPATCH
        assert hit.overdue_minutes > 0
        # 快照要能解释「当时为什么报」，规则改了历史仍可复盘
        assert hit.snapshot_json is not None

    async def test_repeated_scan_is_upsert_not_insert(self, tenant_session):
        task = await _seed_overdue_task(tenant_session)

        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )
        first = await _alerts_of(tenant_session, task.id)
        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )
        second = await _alerts_of(tenant_session, task.id)

        assert len(second) == len(first)
        assert {a.id for a in second} == {a.id for a in first}

    async def test_moving_to_next_stage_auto_resolves_previous_alert(
        self, tenant_session
    ):
        task = await _seed_overdue_task(tenant_session)
        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )
        before = {
            a.rule_code: a.status
            for a in await _alerts_of(tenant_session, task.id)
        }
        assert before.get(RULE_DISPATCH_TIMEOUT) == ALERT_STATUS_ACTIVE

        # 派完车推进到「待装车」，待派车超时这条就不该再挂着
        task.status = TASK_DISPATCHED
        task.stage_entered_at = datetime.now()
        await tenant_session.flush()
        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )

        after = {
            a.rule_code: a for a in await _alerts_of(tenant_session, task.id)
        }
        stale = after[RULE_DISPATCH_TIMEOUT]
        assert stale.status == ALERT_STATUS_AUTO_RESOLVED
        assert stale.resolved_at is not None


class TestCardAndListConsistency:
    """卡片计数与列表条数必须完全一致 —— 这是本次改造的核心验收点"""

    async def test_stage_counts_match_list_filter(self, tenant_session):
        task = await _seed_overdue_task(tenant_session)
        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )

        stats = await TaskService.workbench_stats(tenant_session)
        stage_alerts = stats["stageAlerts"][str(TASK_PENDING_DISPATCH)]

        _rows, critical_total = await TaskService.page_tasks(
            tenant_session,
            page=1,
            page_size=1,
            status=TASK_PENDING_DISPATCH,
            alert_level="critical",
        )
        _rows, warn_total = await TaskService.page_tasks(
            tenant_session,
            page=1,
            page_size=1,
            status=TASK_PENDING_DISPATCH,
            alert_level="warn",
        )
        assert stage_alerts["critical"] == critical_total
        assert stage_alerts["warn"] == warn_total

    async def test_three_buckets_add_up_to_stage_total(self, tenant_session):
        task = await _seed_overdue_task(tenant_session)
        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )

        stats = await TaskService.workbench_stats(tenant_session)
        total = stats["totals"]["pendingDispatch"]
        _rows, normal_total = await TaskService.page_tasks(
            tenant_session,
            page=1,
            page_size=1,
            status=TASK_PENDING_DISPATCH,
            alert_level="normal",
        )
        bucket = stats["stageAlerts"][str(TASK_PENDING_DISPATCH)]

        # 「常 + 关注 + 严重」= 本阶段总数，卡片上三个数字才对得上
        assert normal_total + bucket["warn"] + bucket["critical"] == total

    async def test_dismissed_alert_leaves_the_alert_bucket(self, tenant_session):
        task = await _seed_overdue_task(tenant_session)
        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )
        alerts = await _alerts_of(tenant_session, task.id)
        for a in alerts:
            await TaskAlertService.dismiss(
                tenant_session, a.id, user_id=1, reason="客户已同意延后"
            )

        # 忽略后既不该再占「关注/严重」，也不该从阶段里消失，而是回到「常」
        alerting, _ = await TaskService.page_tasks(
            tenant_session,
            page=1,
            page_size=200,
            status=TASK_PENDING_DISPATCH,
            alert_level="any",
        )
        normal, _ = await TaskService.page_tasks(
            tenant_session,
            page=1,
            page_size=200,
            status=TASK_PENDING_DISPATCH,
            alert_level="normal",
        )
        assert task.id not in {t.id for t in alerting}
        assert task.id in {t.id for t in normal}


class TestAlertHandling:
    async def test_dismiss_requires_a_reason(self, tenant_session):
        from app.common.exceptions import BizException

        task = await _seed_overdue_task(tenant_session)
        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )
        alert = (await _alerts_of(tenant_session, task.id))[0]

        with pytest.raises(BizException):
            await TaskAlertService.dismiss(
                tenant_session, alert.id, user_id=1, reason="   "
            )

    async def test_resolved_alert_cannot_be_handled_twice(self, tenant_session):
        from app.common.exceptions import BizException

        task = await _seed_overdue_task(tenant_session)
        await TaskAlertEngine.recompute_tasks(
            tenant_session, [task.id], commit=False
        )
        alert = (await _alerts_of(tenant_session, task.id))[0]

        await TaskAlertService.resolve(
            tenant_session, alert.id, user_id=1, remark="已催承运商"
        )
        with pytest.raises(BizException):
            await TaskAlertService.resolve(tenant_session, alert.id, user_id=1)


class TestAlertRuleConfig:
    async def test_create_rule_can_serialize_created_at(self, tenant_session):
        """新增后立刻读 created_at 不能走同步懒加载（异步 Session 会 MissingGreenlet）。"""
        from app.modules.client.schemas.task.task_alert import (
            TaskAlertRuleCreate,
            TaskAlertRuleOut,
        )
        from app.modules.client.services.task.task_alert_rule_service import (
            TaskAlertRuleService,
            scope_summary,
        )

        row = await TaskAlertRuleService.create(
            tenant_session,
            TaskAlertRuleCreate(
                ruleCode=RULE_DISPATCH_TIMEOUT,
                # 带维度，避免撞上租户里已有的默认阈值行
                customerType=3,
                timeBasis=2,
                warnAheadMinutes=90,
                criticalAfterMinutes=0,
                priority=0,
                status=1,
            ),
        )
        names = await TaskAlertRuleService.resolve_scope_names(
            tenant_session, [row]
        )
        out = TaskAlertRuleOut.from_model(
            row, scope_summary=scope_summary(row, names)
        )
        assert out.id
        assert out.createdAt is not None
        assert out.isDefault is False
