"""驾驶员任务服务测试（薄层：按 driver 过滤 + 可见性校验）

分两层：
1. 纯逻辑：``_to_list_item`` 输出裁剪、``_accepted_task_ids`` 空集短路、
   ``_build_visibility_condition`` 条件构造；
2. 集成：连租户库 ``1001``，新建司机的任务列表为空，访问不属于自己的任务/挂接行被拒。

对应需求：项目文档/02.需求文档/03.移动端/02.驾驶员H5端/02.任务流转与司机动作.md
覆盖用例：TC-DRV-TASK-001/002/008/009/010
"""

from types import SimpleNamespace

import pytest

from app.common.exceptions import BizException
from app.modules.driver.services.driver_task_service import DriverTaskService


def _fake_task(**over):
    base = dict(
        id=1, task_no="T0001", task_name="测试任务", status=1,
        origin="上海", destination="北京",
        planned_load_time=None, planned_arrive_time=None,
        actual_load_time=None, actual_arrive_time=None,
        total_quantity=3, waybill_count=2,
        main_driver_name="王师傅", plate_number="沪A12345",
        carrier_type=1, prepaid_amount=100, settled_amount=0,
        carrier_cost_amount=None,
    )
    base.update(over)
    return SimpleNamespace(**base)


# =====================================================================
# 1) 纯逻辑
# =====================================================================
class TestPureLogic:
    def test_to_list_item_mapping(self):
        item = DriverTaskService._to_list_item(_fake_task(), accepted=True)
        assert item.taskNo == "T0001"
        assert item.accepted is True
        assert item.customerName is None  # 司机端不下发客户名
        assert item.carrierType == 1

    def test_to_list_item_none_numeric_defaults(self):
        item = DriverTaskService._to_list_item(
            _fake_task(total_quantity=None, waybill_count=None, prepaid_amount=None)
        )
        assert item.totalQuantity == 0
        assert item.waybillCount == 0
        assert item.prepaidAmount == 0

    async def test_accepted_task_ids_empty_short_circuit(self):
        # 空 task_ids 直接返回空集，不触库（传 None 亦安全）
        assert await DriverTaskService._accepted_task_ids(None, []) == set()

    def test_visibility_condition_builds_with_social_only(self):
        cond = DriverTaskService._build_visibility_condition([], 5)
        # 至少包含 social_driver_id 条件，可被 SQLAlchemy 编译
        assert cond is not None
        assert "social_driver_id" in str(cond)

    def test_visibility_condition_includes_capacity(self):
        cond = DriverTaskService._build_visibility_condition([1, 2, 3], 5)
        assert "capacity_id" in str(cond)


# =====================================================================
# 2) 集成（真实租户库，事务回滚）
# =====================================================================
class TestTaskIntegration:
    async def test_list_my_tasks_empty(self, driver_ctx):
        # BUG-DRV-001 已修复：list_my_tasks 改用 `col IS NULL` 升序模拟空值置底，
        # 不再输出 MySQL 非法的 `NULLS LAST`，新建司机列表可正常返回空集。
        session, ctx = driver_ctx
        items, total = await DriverTaskService.list_my_tasks(session, ctx)
        assert total == 0
        assert items == []

    async def test_visible_task_unknown_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        with pytest.raises(BizException):
            await DriverTaskService._get_visible_task_or_404(
                session, ctx, 999_000_111
            )

    async def test_accept_unknown_task_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        from app.modules.driver.schemas.task import DriverAcceptTaskRequest

        with pytest.raises(BizException):
            await DriverTaskService.accept(
                session, ctx, 999_000_111, DriverAcceptTaskRequest()
            )

    async def test_visible_item_unknown_rejected(self, driver_ctx):
        session, ctx = driver_ctx
        with pytest.raises(BizException):
            await DriverTaskService._get_visible_item_or_404(
                session, ctx, 999_000_111
            )
