"""业务侧锁定编排器

财务单据进入终态（如任务级最终结算单已支付、承运商结算单已支付）时，
锁定关联业务对象的成本字段，禁止业务侧改动或删除。

本期落地任务级最终结算单锁定 task 的能力；承运商结算单锁定复用同一入口（后续）。

注意：锁定只影响 ``task.is_locked`` 等成本保护标记，**不改 ``task.status``**
（业务状态机与财务已解耦，任务关闭由调度员综合判断）。
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


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
