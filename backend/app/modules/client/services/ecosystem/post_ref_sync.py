"""挂牌状态回写租户库镜像

``biz_eco_post_ref.post_status`` 是给租户库内的业务页面（任务单列表、运力列表）
看的角标数据源。挂牌状态在平台库变了，这里把它抄一份回租户库。

## 失败为什么可以吞掉

镜像只影响一个角标，平台库才是权威。为了角标写失败而回滚整个下架操作，
用户会看到「停止展示失败」但挂牌其实已经不在大厅了——这比角标短时不准糟得多。

## 失败靠什么补

**不是 ``sync_pending``**。那个标记的语义是「租户库有变更待推到平台库」，
方向相反，在这里置位会让补偿 Worker 反向覆盖平台库的正确状态。
本方向的失败由巡检 Worker（`01` §5.2 第三重）比对两库状态后修正。
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.ecosystem.post_ref import BizEcoPostRef


async def mirror_post_status(
    tenant_db: AsyncSession,
    *,
    post_id: int,
    post_no: str,
    status: int,
    now: Optional[datetime] = None,
) -> bool:
    """把挂牌状态抄回租户库镜像

    Returns:
        是否写成功。``False`` 表示角标暂时不准，等巡检修正；调用方不要因此报错。
    """
    try:
        async with tenant_db.begin_nested():
            ref = (
                await tenant_db.execute(
                    select(BizEcoPostRef).where(
                        BizEcoPostRef.post_id == int(post_id),
                        BizEcoPostRef.is_deleted == 0,
                    )
                )
            ).scalars().first()
            if ref is None:
                # 双写窗口里 ref 没落库成功。这里不补建：补建需要源单类型等信息，
                # 猜出来的记录比没有记录更难排查，交巡检 Worker 从平台库反向重建。
                logger.warning(
                    f"[Eco] 挂牌 {post_no} 在租户库没有镜像记录，状态回写跳过，待巡检重建"
                )
                return False
            ref.post_status = int(status)
            ref.last_sync_at = now or datetime.now()
            await tenant_db.flush()
        return True
    except Exception as e:
        logger.error(f"[Eco] 挂牌 {post_no} 状态回写租户库失败，待巡检修正：{e}")
        return False
