"""
AI 调用限流与 Token 配额

- 用户级 QPS 限流：进程内滑动窗口（够轻量；多实例部署时需要后续接 Redis）
- 租户级 Token 日配额：从 biz_ai_session 实时聚合
- 配置项存 sys_platform_setting：
  - ai.rate_limit_per_minute      默认 30
  - ai.token_daily_limit_per_tenant 默认 0（0 表示不限）
  - ai.fallback_message           兜底回复
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from datetime import date
from typing import Deque, Optional

from sqlalchemy import func, select, text as sa_text
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.ai.models.tenant.biz_ai_session import BizAiSession


_RATE_BUCKETS: dict[int, Deque[float]] = defaultdict(deque)


async def _load_int_setting(
    platform_db: AsyncSession, key: str, default: int
) -> int:
    row = (
        await platform_db.execute(
            sa_text(
                "SELECT config_value FROM sys_platform_setting "
                "WHERE config_key = :k AND is_deleted = 0 LIMIT 1"
            ),
            {"k": key},
        )
    ).first()
    if not row or not row[0]:
        return default
    try:
        return int(row[0])
    except (TypeError, ValueError):
        return default


async def _load_str_setting(
    platform_db: AsyncSession, key: str, default: str
) -> str:
    row = (
        await platform_db.execute(
            sa_text(
                "SELECT config_value FROM sys_platform_setting "
                "WHERE config_key = :k AND is_deleted = 0 LIMIT 1"
            ),
            {"k": key},
        )
    ).first()
    if not row or not row[0]:
        return default
    return str(row[0])


async def get_fallback_message(platform_db: AsyncSession) -> str:
    return await _load_str_setting(
        platform_db,
        "ai.fallback_message",
        "服务暂时繁忙，请稍后再试。如有紧急需求请联系客服。",
    )


async def check_rate_limit(
    platform_db: AsyncSession, user_id: int
) -> None:
    """用户级每分钟 QPS 限流（进程内滑窗）"""
    limit = await _load_int_setting(platform_db, "ai.rate_limit_per_minute", 30)
    if limit <= 0:
        return
    now = time.time()
    bucket = _RATE_BUCKETS[user_id]
    while bucket and now - bucket[0] > 60.0:
        bucket.popleft()
    if len(bucket) >= limit:
        raise BizException(
            f"对话过于频繁（{limit}/分钟），请稍候再试", code=42901
        )
    bucket.append(now)


async def check_token_quota(
    platform_db: AsyncSession, tenant_db: AsyncSession
) -> None:
    """租户级 Token 日配额（自然日累计 prompt+completion）"""
    limit = await _load_int_setting(
        platform_db, "ai.token_daily_limit_per_tenant", 0
    )
    if limit <= 0:
        return
    today = date.today()
    sum_pt, sum_ct = await _sum_today_tokens(tenant_db, today)
    used = (sum_pt or 0) + (sum_ct or 0)
    if used >= limit:
        raise BizException(
            f"租户今日 AI Token 用量已达上限（{used}/{limit}）", code=42902
        )


async def _sum_today_tokens(
    tenant_db: AsyncSession, today: date
) -> tuple[int, int]:
    row = (
        await tenant_db.execute(
            select(
                func.coalesce(func.sum(BizAiSession.total_prompt_tokens), 0),
                func.coalesce(func.sum(BizAiSession.total_completion_tokens), 0),
            ).where(
                BizAiSession.is_deleted == 0,
                func.date(BizAiSession.last_message_at) == today,
            )
        )
    ).first()
    if not row:
        return 0, 0
    return int(row[0] or 0), int(row[1] or 0)
