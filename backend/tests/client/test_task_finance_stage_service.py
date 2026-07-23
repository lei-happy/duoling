"""任务级费用单「发起节点」规则 · 服务/接口（租户库，事务回滚不落库）集成测试

在真实租户库上验证发起节点配置的读取、判定与 create_doc 硬拦截，以及
存量租户懒补齐的幂等性。无 DB 环境下 ``tenant_session`` 整体 skip。

覆盖：
  - ``TaskFinanceService._load_stage_rules``：读取 biz_system_config → (enforce, rules)
  - ``TaskFinanceService.creatable_doc_types(db, task_id)``：返回 {taskStatus, enforce, docTypes}
  - ``TaskFinanceService.create_doc``：enforce=true 且节点不允许 → BizException；允许 → 成功
  - ``SystemConfigService._ensure_lazy_defaults``：重复调用不重复插入（幂等）
  - 向后兼容：配置行缺失时 create_doc 不拦截、creatable 返回全类型

对应需求：任务级费用单·发起节点配置（biz_system_config → finance.task_doc_stage_rules）
对应代码：backend/app/modules/client/services/task/task_finance_service.py
          backend/app/modules/client/services/system_config_service.py
覆盖用例：TC-CLI-FINSTAGE-101 ~ TC-CLI-FINSTAGE-106
"""

from __future__ import annotations

import json

import pytest
from sqlalchemy import func, select

from app.common.exceptions import BizException
from app.modules.client.models.system_config import SystemConfig
from app.modules.client.models.task.task import Task
from app.modules.client.schemas.task.task_finance_doc import TaskFinanceDocCreate
from app.modules.client.services.finance.base.constants import DocType, PayeeType
from app.modules.client.services.finance.base.finance_stage_rules import (
    STAGE_RULES_CONFIG_KEY,
)
from app.modules.client.services.system_config_service import SystemConfigService
from app.modules.client.services.task.task_finance_service import TaskFinanceService
from tests.client.conftest import unique_suffix


# ---------------------------------------------------------------------------
# 辅助
# ---------------------------------------------------------------------------
async def _seed_task(session, status: int = -1) -> Task:
    """直插一条最小任务单（避开重量级调度链路），指定任务节点。"""
    task = Task(
        task_no=f"RWFIN{unique_suffix()}",
        task_name="费用节点集成测试任务",
        status=status,
        carrier_type=1,
    )
    session.add(task)
    await session.flush()
    await session.refresh(task)
    return task


async def _set_stage_config(session, *, enforce: bool, rules: dict) -> None:
    """在回滚事务内写入/更新发起节点配置行（config_key 唯一）。"""
    value = json.dumps({
        "enforce": enforce,
        "rules": {str(k): v for k, v in rules.items()},
    })
    row = (await session.execute(
        select(SystemConfig).where(
            SystemConfig.config_key == STAGE_RULES_CONFIG_KEY,
        )
    )).scalar_one_or_none()
    if row:
        row.config_value = value
        row.is_deleted = 0
    else:
        session.add(SystemConfig(
            config_key=STAGE_RULES_CONFIG_KEY,
            config_value=value,
            config_group="finance",
            description="费用单发起节点规则（集成测试写入）",
            value_type="json",
            default_value=value,
        ))
    await session.flush()


async def _soft_delete_stage_config(session) -> None:
    """软删配置行，模拟「存量租户尚未补齐」——get_by_key 将返回 None。"""
    rows = (await session.execute(
        select(SystemConfig).where(
            SystemConfig.config_key == STAGE_RULES_CONFIG_KEY,
        )
    )).scalars().all()
    for r in rows:
        r.is_deleted = 1
    await session.flush()


def _base_create_payload(doc_type: int) -> TaskFinanceDocCreate:
    """构造一张最小可创建费用单（收款人=其他，避免司机/承运商查库）。"""
    return TaskFinanceDocCreate(
        docType=doc_type,
        payeeType=PayeeType.OTHER,
        payeeName="集成测试收款人",
        plannedAmount=100.0,
    )


# ---------------------------------------------------------------------------
# _load_stage_rules / creatable_doc_types
# ---------------------------------------------------------------------------
class TestLoadAndCreatable:
    async def test_load_stage_rules_reads_config(self, tenant_session):
        """TC-CLI-FINSTAGE-101 _load_stage_rules 读取配置 → (enforce, rules)。"""
        await _set_stage_config(
            tenant_session,
            enforce=True,
            rules={
                DocType.PREPAY: [-1, 0],
                DocType.SUPPLEMENT: [5],
                DocType.SETTLE: [5],
                DocType.CONTRACTED: [-1],
            },
        )
        enforce, rules = await TaskFinanceService._load_stage_rules(tenant_session)
        assert enforce is True
        assert rules[DocType.PREPAY] == {-1, 0}
        assert rules[DocType.SETTLE] == {5}

    async def test_creatable_doc_types_structure(self, tenant_session):
        """TC-CLI-FINSTAGE-102 creatable_doc_types 返回 {taskStatus,enforce,docTypes}。"""
        task = await _seed_task(tenant_session, status=-1)
        await _set_stage_config(
            tenant_session,
            enforce=True,
            rules={
                DocType.PREPAY: [-1, 0],       # 待分配可发起
                DocType.SUPPLEMENT: [5],
                DocType.SETTLE: [5],
                DocType.CONTRACTED: [-1],      # 待分配可发起
            },
        )
        result = await TaskFinanceService.creatable_doc_types(
            tenant_session, task.id,
        )
        assert result["taskStatus"] == -1
        assert result["enforce"] is True
        assert result["docTypes"] == [DocType.PREPAY, DocType.CONTRACTED]


# ---------------------------------------------------------------------------
# create_doc 发起节点硬拦截
# ---------------------------------------------------------------------------
class TestCreateDocStageGate:
    async def test_create_doc_blocked_when_enforced_and_not_allowed(
        self, tenant_session,
    ):
        """TC-CLI-FINSTAGE-103 enforce=true 且节点不允许 → create_doc 抛 BizException。"""
        task = await _seed_task(tenant_session, status=3)  # 在途
        await _set_stage_config(
            tenant_session,
            enforce=True,
            rules={DocType.PREPAY: [-1, 0]},  # 在途(3) 不允许发起预付
        )
        with pytest.raises(BizException):
            await TaskFinanceService.create_doc(
                tenant_session, task.id, _base_create_payload(DocType.PREPAY),
            )

    async def test_create_doc_allowed_when_stage_permitted(self, tenant_session):
        """TC-CLI-FINSTAGE-104 enforce=true 且节点允许 → create_doc 成功。"""
        task = await _seed_task(tenant_session, status=-1)  # 待分配
        await _set_stage_config(
            tenant_session,
            enforce=True,
            rules={DocType.PREPAY: [-1, 0, 1]},  # 待分配允许预付
        )
        doc = await TaskFinanceService.create_doc(
            tenant_session, task.id, _base_create_payload(DocType.PREPAY),
        )
        assert doc.id is not None
        assert int(doc.doc_type) == DocType.PREPAY
        assert int(doc.task_id) == task.id

    async def test_create_doc_soft_mode_does_not_block(self, tenant_session):
        """enforce=false 且节点不允许 → 软提示放行，仍可创建（不拦截）。"""
        task = await _seed_task(tenant_session, status=3)  # 在途
        await _set_stage_config(
            tenant_session,
            enforce=False,
            rules={DocType.PREPAY: [-1, 0]},  # 在途不在允许集，但 enforce=false
        )
        doc = await TaskFinanceService.create_doc(
            tenant_session, task.id, _base_create_payload(DocType.PREPAY),
        )
        assert doc.id is not None


# ---------------------------------------------------------------------------
# 懒补齐幂等
# ---------------------------------------------------------------------------
class TestEnsureLazyDefaults:
    async def test_ensure_lazy_defaults_idempotent(self, tenant_session):
        """TC-CLI-FINSTAGE-105 _ensure_lazy_defaults 幂等：重复调用不重复插入。"""
        # 先清掉存量行（硬删本事务内的行），走「插入 + 再次调用不重复」路径
        rows = (await tenant_session.execute(
            select(SystemConfig).where(
                SystemConfig.config_key == STAGE_RULES_CONFIG_KEY,
            )
        )).scalars().all()
        for r in rows:
            await tenant_session.delete(r)
        await tenant_session.flush()

        async def _count() -> int:
            return int((await tenant_session.execute(
                select(func.count(SystemConfig.id)).where(
                    SystemConfig.config_key == STAGE_RULES_CONFIG_KEY,
                )
            )).scalar() or 0)

        assert await _count() == 0

        await SystemConfigService._ensure_lazy_defaults(tenant_session)
        assert await _count() == 1  # 首次补齐插入一条

        await SystemConfigService._ensure_lazy_defaults(tenant_session)
        assert await _count() == 1  # 再次调用不重复插入（幂等）


# ---------------------------------------------------------------------------
# 向后兼容：配置行缺失
# ---------------------------------------------------------------------------
class TestBackwardCompatMissingConfig:
    async def test_create_doc_not_blocked_when_config_missing(self, tenant_session):
        """TC-CLI-FINSTAGE-106a 配置行缺失 → create_doc 不拦截。"""
        task = await _seed_task(tenant_session, status=3)
        await _soft_delete_stage_config(tenant_session)
        doc = await TaskFinanceService.create_doc(
            tenant_session, task.id, _base_create_payload(DocType.SETTLE),
        )
        assert doc.id is not None

    async def test_creatable_returns_all_types_when_config_missing(
        self, tenant_session,
    ):
        """TC-CLI-FINSTAGE-106b 配置行缺失 → creatable 返回全部类型、enforce=false。"""
        task = await _seed_task(tenant_session, status=3)
        await _soft_delete_stage_config(tenant_session)
        result = await TaskFinanceService.creatable_doc_types(
            tenant_session, task.id,
        )
        assert result["enforce"] is False
        assert result["docTypes"] == list(DocType.ALL)
