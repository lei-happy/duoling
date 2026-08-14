"""业务侧锁定编排器

财务单据进入终态（如任务级最终结算单已支付、承运商结算单已支付）时，
锁定关联业务对象的成本字段，禁止业务侧改动或删除。

已落地：任务级最终结算单锁 task、客户结算单收妥锁 waybill、承运商结算单付妥批量锁
task、司机工资单发放标记 ``payroll_settled``。

锁定与解锁都带 ``locked_by_doc_id`` 归属判断：一张运单可能先后进入不同财务流程，
不记来源就会出现「撤销 A 单收款把 B 单的锁也解了」。

注意：锁定只影响 ``task.is_locked`` 等成本保护标记，**不改 ``task.status``**
（业务状态机与财务已解耦，任务关闭由调度员综合判断）。
"""

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.task.task import Task
from app.modules.client.models.waybill.waybill import Waybill


class LockOrchestrator:
    """业务对象锁定/解锁编排"""

    @staticmethod
    async def lock_task_if_final(
        db: AsyncSession,
        *,
        task,
        doc_type: int,
        is_final: int,
        by_doc_id: int,
    ) -> bool:
        """任务级最终结算单已支付时锁定任务成本字段。

        仅当 ``doc_type=3`` 且 ``is_final=1`` 时生效；返回是否执行了锁定。
        幂等：已被同一单据锁定则不重复写。
        """
        if int(doc_type) != 3 or int(is_final or 0) != 1:
            return False
        if int(getattr(task, "is_locked", 0) or 0) == 1:
            return False
        task.is_locked = 1
        task.locked_at = datetime.now()
        task.locked_by_doc_id = by_doc_id
        await db.flush()
        return True

    @staticmethod
    async def lock_waybills(
        db: AsyncSession,
        waybill_ids: Sequence[int],
        *,
        by_doc_id: int,
    ) -> int:
        """客户结算单收妥时锁定关联运单，返回实际锁定条数。

        只锁未锁的：已被其他单据锁定的运单保留原锁定来源，否则撤销本单收款时
        会把别人的锁一并解开。
        """
        ids = [int(x) for x in waybill_ids if x]
        if not ids:
            return 0
        r = await db.execute(
            update(Waybill)
            .where(Waybill.id.in_(ids), Waybill.is_locked == 0)
            .values(
                is_locked=1,
                locked_at=datetime.now(),
                locked_by_doc_id=by_doc_id,
            )
        )
        await db.flush()
        return int(r.rowcount or 0)

    @staticmethod
    async def unlock_waybills(
        db: AsyncSession,
        *,
        by_doc_id: int,
        waybill_ids: Optional[Sequence[int]] = None,
    ) -> int:
        """撤销收款时解锁运单，只解开由本单据锁定的那些。"""
        stmt = update(Waybill).where(
            Waybill.is_locked == 1,
            Waybill.locked_by_doc_id == by_doc_id,
        )
        if waybill_ids:
            stmt = stmt.where(Waybill.id.in_([int(x) for x in waybill_ids if x]))
        r = await db.execute(
            stmt.values(is_locked=0, locked_at=None, locked_by_doc_id=None)
        )
        await db.flush()
        return int(r.rowcount or 0)

    @staticmethod
    async def lock_tasks(
        db: AsyncSession,
        task_ids: Sequence[int],
        *,
        by_doc_id: int,
    ) -> int:
        """承运商结算单付妥时批量锁定任务成本字段，返回实际锁定条数。

        与 ``lock_waybills`` 同规则：只锁未锁的，保留他单的锁定来源。
        """
        ids = [int(x) for x in task_ids if x]
        if not ids:
            return 0
        r = await db.execute(
            update(Task)
            .where(Task.id.in_(ids), Task.is_locked == 0)
            .values(
                is_locked=1,
                locked_at=datetime.now(),
                locked_by_doc_id=by_doc_id,
            )
        )
        await db.flush()
        return int(r.rowcount or 0)

    @staticmethod
    async def unlock_tasks(
        db: AsyncSession,
        *,
        by_doc_id: int,
        task_ids: Optional[Sequence[int]] = None,
    ) -> int:
        """撤销付款时解锁任务，只解开由本单据锁定的那些。"""
        stmt = update(Task).where(
            Task.is_locked == 1,
            Task.locked_by_doc_id == by_doc_id,
        )
        if task_ids:
            stmt = stmt.where(Task.id.in_([int(x) for x in task_ids if x]))
        r = await db.execute(
            stmt.values(is_locked=0, locked_at=None, locked_by_doc_id=None)
        )
        await db.flush()
        return int(r.rowcount or 0)

    @staticmethod
    async def mark_tasks_payroll_settled(
        db: AsyncSession,
        task_ids: Sequence[int],
        *,
        settled: bool,
    ) -> int:
        """工资单发放 / 撤销发放时标记任务的发薪状态。

        与 ``is_locked`` 分开：工资发放锁的是「这些任务的提成已经付过了」，不锁任务
        的承运成本——自有车任务的成本还要参与经营核算，锁死会挡住调度侧的正常修订。
        """
        ids = [int(x) for x in task_ids if x]
        if not ids:
            return 0
        r = await db.execute(
            update(Task)
            .where(Task.id.in_(ids))
            .values(payroll_settled=1 if settled else 0)
        )
        await db.flush()
        return int(r.rowcount or 0)

    @staticmethod
    async def mark_tasks_payroll_bound(
        db: AsyncSession,
        task_ids: Sequence[int],
        *,
        bound: bool,
    ) -> int:
        """任务挂入 / 移出工资单时维护软锁标记。"""
        ids = [int(x) for x in task_ids if x]
        if not ids:
            return 0
        r = await db.execute(
            update(Task)
            .where(Task.id.in_(ids))
            .values(is_payroll_bound=1 if bound else 0)
        )
        await db.flush()
        return int(r.rowcount or 0)

    @staticmethod
    async def lock_settlements(
        db: AsyncSession,
        settle_ids: Sequence[int],
        *,
        by_doc_id: int,
    ) -> int:
        """销项票开出后锁定客户结算单，返回实际锁定条数。

        锁的是「这些钱已经开过票了」：金额再改就与票面不符，税务上说不清。与运单锁
        同规则，只锁未锁的、记锁定来源。
        """
        from app.modules.client.models.finance.customer_settlement import (
            CustomerSettlement,
        )

        ids = [int(x) for x in settle_ids if x]
        if not ids:
            return 0
        r = await db.execute(
            update(CustomerSettlement)
            .where(CustomerSettlement.id.in_(ids), CustomerSettlement.is_locked == 0)
            .values(
                is_locked=1,
                locked_at=datetime.now(),
                locked_by_doc_id=by_doc_id,
            )
        )
        await db.flush()
        return int(r.rowcount or 0)

    @staticmethod
    async def unlock_settlements(
        db: AsyncSession,
        *,
        by_doc_id: int,
        settle_ids: Optional[Sequence[int]] = None,
    ) -> int:
        """发票作废 / 红冲时解锁结算单，只解开由本张票锁定的那些。"""
        from app.modules.client.models.finance.customer_settlement import (
            CustomerSettlement,
        )

        stmt = update(CustomerSettlement).where(
            CustomerSettlement.is_locked == 1,
            CustomerSettlement.locked_by_doc_id == by_doc_id,
        )
        if settle_ids:
            stmt = stmt.where(
                CustomerSettlement.id.in_([int(x) for x in settle_ids if x])
            )
        r = await db.execute(
            stmt.values(is_locked=0, locked_at=None, locked_by_doc_id=None)
        )
        await db.flush()
        return int(r.rowcount or 0)

    @staticmethod
    async def unlock_task(
        db: AsyncSession,
        *,
        task,
        by_doc_id: Optional[int] = None,
    ) -> bool:
        """撤销最终结算单时解锁任务。

        若指定 ``by_doc_id``，仅当锁定来源匹配时才解锁（避免误解他单锁定）。
        """
        if int(getattr(task, "is_locked", 0) or 0) != 1:
            return False
        if by_doc_id is not None and task.locked_by_doc_id not in (None, by_doc_id):
            return False
        task.is_locked = 0
        task.locked_at = None
        task.locked_by_doc_id = None
        await db.flush()
        return True
