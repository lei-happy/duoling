"""挂牌下架时的意向失效（平台库，租户端与运营端共用）

发布方主动停止展示、平台强制下架、到期自动下架、源单失效下架——四条路径的
挂牌都不在大厅了，挂着的意向必须一起收口。这段逻辑放在共用模块里，是因为
四条路径各写一份的结果一定是「运营强制下架忘了失效意向」这类漏项：
挂牌不见了，同行还在「待响应」里干等，找不到任何解释。

## 已选定的意向为什么不动

``SELECTED`` 意向背后有一张成交单在跑，把它作废会让成交单指向一条无效意向，
履约、评价、纠纷追溯全部失去来源。已选定的合作要终止，走的是成交单的
终止流程，而不是从挂牌侧把意向抽掉。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.ecosystem.constants import (
    IntentInvalidReason,
    IntentStatus,
)
from app.modules.console.models.ecosystem.intent import SysEcoIntent

# 会被挂牌下架顺带失效的意向状态
INVALIDATABLE = (IntentStatus.PENDING, IntentStatus.TALKING)


@dataclass
class InvalidatedIntent:
    """被顺带失效的意向，供上层发通知"""

    intent_id: int
    intent_no: str
    initiator_tenant_code: str


async def invalidate_active_intents(
    db: AsyncSession,
    *,
    post: Any,
    reason: int = IntentInvalidReason.POST_DELISTED,
    now: Optional[datetime] = None,
) -> List[InvalidatedIntent]:
    """让待响应与洽谈中的意向失效，并重算挂牌上的有效意向数

    Args:
        reason: ``IntentInvalidReason`` 之一。同一段代码服务下架、过期、
            被他人成交三种场景，原因由调用方给，这里不猜。
    """
    rows = (
        await db.execute(
            select(SysEcoIntent).where(
                SysEcoIntent.post_id == int(post.id),
                SysEcoIntent.status.in_(INVALIDATABLE),
                SysEcoIntent.is_deleted == 0,
            )
        )
    ).scalars().all()

    invalidated: List[InvalidatedIntent] = []
    for row in rows:
        row.status = IntentStatus.INVALID
        row.invalid_reason = int(reason)
        invalidated.append(
            InvalidatedIntent(
                intent_id=int(row.id),
                intent_no=row.intent_no,
                initiator_tenant_code=row.initiator_tenant_code,
            )
        )
    await db.flush()

    post.intent_count = await recount_active_intents(db, post)
    return invalidated


async def recount_active_intents(db: AsyncSession, post: Any) -> int:
    """重算有效意向数

    重算而不是做减法：冗余计数本来就可能因为历史原因漂移，每次下架正好是一个
    免费的纠偏点，做减法只会把已有的偏差一路带下去。
    """
    return int(
        (
            await db.execute(
                select(func.count())
                .select_from(SysEcoIntent)
                .where(
                    SysEcoIntent.post_id == int(post.id),
                    SysEcoIntent.status.in_(IntentStatus.ACTIVE),
                    SysEcoIntent.is_deleted == 0,
                )
            )
        ).scalar()
        or 0
    )
