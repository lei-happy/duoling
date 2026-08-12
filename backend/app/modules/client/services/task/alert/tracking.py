"""
任务预警的即时重算通道

调度员点完「派车」，工作台的阶段卡就该立刻正确 —— 等 worker 下一轮扫描
（默认 180s）才刷新，看板与操作之间会有一段肉眼可见的错位。

但推进任务状态的入口散落在企业端、驾驶员端、承运商端十几个接口里，
逐个接口手动调重算既啰嗦又必然漏掉新加的入口。这里换个思路：

1. 用 SQLAlchemy 的 ``after_flush`` 事件被动记录本次会话碰过哪些任务；
2. 在租户会话 commit 之前（``session_hooks``）统一重算这些任务的预警。

于是预警与业务改动天然同事务：业务回滚，预警也跟着回滚；业务成功，
看板立刻是对的。新接口不需要知道预警的存在。
"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.session_hooks import register_pre_commit_hook
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_waybill_item import TaskWaybillItem
from app.modules.client.services.task.alert.engine import TaskAlertEngine

_PENDING_KEY = "task_alert_pending_ids"
_BUSY_KEY = "task_alert_recomputing"


def _collect(session: Session, _flush_context, _instances=None) -> None:
    """记录本次 flush 涉及的任务 ID。

    挂接行也要算进来：装车台数、客户、车型都来自挂接行，改了它们同样会
    影响预警判定（例如漏装台数）。
    """
    if session.info.get(_BUSY_KEY):
        return
    pending: Optional[set] = session.info.get(_PENDING_KEY)
    for obj in list(session.new) + list(session.dirty) + list(session.deleted):
        task_id = None
        if isinstance(obj, Task):
            task_id = obj.id
        elif isinstance(obj, TaskWaybillItem):
            task_id = obj.task_id
        if not task_id:
            continue
        if pending is None:
            pending = set()
            session.info[_PENDING_KEY] = pending
        pending.add(int(task_id))


event.listen(Session, "after_flush", _collect)


async def sync_pending_task_alerts(db: AsyncSession) -> None:
    """提交前钩子：重算本次会话碰过的任务的预警。"""
    sync_session = db.sync_session
    pending = sync_session.info.get(_PENDING_KEY)
    if not pending:
        return

    sync_session.info[_BUSY_KEY] = True
    try:
        # 循环消费：重算过程本身可能再次触发 flush，新进来的 ID 一并处理完
        while pending:
            batch = sorted(pending)
            pending.clear()
            await TaskAlertEngine.recompute_tasks(db, batch, commit=False)
            pending = sync_session.info.get(_PENDING_KEY) or set()
    finally:
        sync_session.info[_BUSY_KEY] = False
        sync_session.info.pop(_PENDING_KEY, None)


register_pre_commit_hook(sync_pending_task_alerts)
