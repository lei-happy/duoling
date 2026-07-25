"""服务平台业务编号生成

规则见 07.数据库设计.md §3.6：``前缀 + yyyyMMdd + 4 位日流水``，
例如 ``HY202607250001``。编号在平台库维度生成（全局唯一，不分租户）。

三层保障，缺一不可：

1. **Redis INCR**（``eco:seq:{prefix}:{yyyyMMdd}``，TTL 48 小时）——多实例并发下
   拿到互不重复的流水号。
2. **库内兜底**——Redis 不可用、或当日首次自增（含 Redis 丢键重启）时，
   回库取当日最大流水续号。这一步是 Redis 重启后不产生重复号的关键：
   若只信 INCR，Redis 丢键会让流水从 1 重新开始，与已有编号全线撞车。
3. **唯一索引 + 重试**——``uk_eco_post_no`` 等唯一索引是最后防线。
   调用方插入冲突时用 ``prefer_db=True`` 重新取号，能立刻收敛到库内真实水位。

沿用项目既有的 Redis 使用方式（同步客户端 + 不可用时降级），
见 ``app/modules/open_platform/security/ratelimit.py``。
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.ecosystem.constants import PostNoPrefix, PostType
from app.modules.console.models.ecosystem.deal import SysEcoDeal
from app.modules.console.models.ecosystem.intent import SysEcoIntent
from app.modules.console.models.ecosystem.post import SysEcoPost
from app.modules.console.models.ecosystem.report import SysEcoReport

try:  # Redis 为可选依赖
    import redis as _redis  # type: ignore
except Exception:  # pragma: no cover
    _redis = None


SEQ_TTL_SECONDS = 48 * 3600
SEQ_DIGITS = 4
# 单日流水上限：4 位数满了说明当天发布量已远超预期，此时宁可报错也不能
# 静默滚到 5 位——编号长度变化会打乱所有依赖定长解析的地方。
MAX_DAILY_SEQ = 9999

# 前缀 → (模型, 编号列)
_NO_COLUMNS = {
    PostNoPrefix.CARGO_POST: (SysEcoPost, SysEcoPost.post_no),
    PostNoPrefix.CAPACITY_POST: (SysEcoPost, SysEcoPost.post_no),
    PostNoPrefix.INTENT: (SysEcoIntent, SysEcoIntent.intent_no),
    PostNoPrefix.DEAL: (SysEcoDeal, SysEcoDeal.deal_no),
    PostNoPrefix.REPORT: (SysEcoReport, SysEcoReport.report_no),
}

_redis_client = None
_redis_inited = False


def _get_redis():
    global _redis_client, _redis_inited
    if _redis_inited:
        return _redis_client
    _redis_inited = True
    if _redis is None:
        _redis_client = None
        return None
    try:
        from app.core.config import get_settings

        client = _redis.Redis.from_url(
            get_settings().redis_url, socket_connect_timeout=0.3, socket_timeout=0.3
        )
        client.ping()
        _redis_client = client
        logger.info("服务平台编号生成已接入 Redis")
    except Exception:
        _redis_client = None
        logger.warning(
            "Redis 不可用，服务平台编号改用库内取号（单机可用；多实例并发下依赖唯一索引兜底）"
        )
    return _redis_client


def reset_redis_cache() -> None:
    """重置 Redis 客户端缓存（供测试使用）"""
    global _redis_client, _redis_inited
    _redis_client = None
    _redis_inited = False


class EcoNumberService:
    """业务编号生成"""

    @staticmethod
    def prefix_for_post(post_type: int) -> str:
        return (
            PostNoPrefix.CARGO_POST
            if int(post_type) == PostType.CARGO
            else PostNoPrefix.CAPACITY_POST
        )

    @staticmethod
    async def next_post_no(
        db: AsyncSession, post_type: int, *, prefer_db: bool = False
    ) -> str:
        """生成挂牌编号：货源 ``HY...``、运力 ``YL...``"""
        return await EcoNumberService.next_no(
            db, EcoNumberService.prefix_for_post(post_type), prefer_db=prefer_db
        )

    @staticmethod
    async def next_no(
        db: AsyncSession, prefix: str, *, prefer_db: bool = False, today: Optional[date] = None
    ) -> str:
        """生成一个业务编号

        Args:
            prefix: 见 ``PostNoPrefix``
            prefer_db: 直接走库内取号并把 Redis 水位抬到库内真实值。
                插入遇到唯一索引冲突后重试时用它，避免反复撞同一批号。
        """
        if prefix not in _NO_COLUMNS:
            raise ValueError(f"未知的编号前缀：{prefix}")

        day = (today or date.today()).strftime("%Y%m%d")
        seq: Optional[int] = None

        if not prefer_db:
            seq = EcoNumberService._redis_next(prefix, day)

        if seq is None or prefer_db:
            db_max = await EcoNumberService._db_max_seq(db, prefix, day)
            seq = db_max + 1
            EcoNumberService._redis_set_floor(prefix, day, seq)
        elif seq == 1:
            # 当日首个流水，或 Redis 丢键后从 1 重新开始。两种情况无法区分，
            # 因此一律回库核对：库里已有编号时以库为准，否则 1 就是对的。
            db_max = await EcoNumberService._db_max_seq(db, prefix, day)
            if db_max >= 1:
                seq = db_max + 1
                EcoNumberService._redis_set_floor(prefix, day, seq)

        if seq > MAX_DAILY_SEQ:
            raise ValueError(
                f"{prefix} 当日编号已达上限 {MAX_DAILY_SEQ}，请联系管理员处理"
            )

        return f"{prefix}{day}{seq:0{SEQ_DIGITS}d}"

    # ------------------------------------------------------------------
    # Redis
    # ------------------------------------------------------------------

    @staticmethod
    def _seq_key(prefix: str, day: str) -> str:
        return f"eco:seq:{prefix}:{day}"

    @staticmethod
    def _redis_next(prefix: str, day: str) -> Optional[int]:
        """Redis 自增取号；不可用时返回 None 交给库内兜底"""
        client = _get_redis()
        if client is None:
            return None
        key = EcoNumberService._seq_key(prefix, day)
        try:
            seq = int(client.incr(key))
            # 每次都续 TTL：key 只在当天使用，48 小时足够覆盖跨时区与延迟场景
            client.expire(key, SEQ_TTL_SECONDS)
            return seq
        except Exception as e:  # pragma: no cover - Redis 异常路径
            logger.warning(f"服务平台编号 Redis 自增失败，改用库内取号：{e}")
            return None

    @staticmethod
    def _redis_set_floor(prefix: str, day: str, value: int) -> None:
        """把 Redis 水位抬到 ``value``（仅在当前值更低时）

        用于 Redis 丢键或库内兜底之后校准，避免下一次取号又撞车。
        这里存在极小的竞态窗口，但唯一索引仍是最后防线，
        为此引入 Lua 脚本不值得。
        """
        client = _get_redis()
        if client is None:
            return
        key = EcoNumberService._seq_key(prefix, day)
        try:
            current = client.get(key)
            if current is None or int(current) < value:
                client.set(key, value, ex=SEQ_TTL_SECONDS)
        except Exception as e:  # pragma: no cover
            logger.warning(f"服务平台编号 Redis 校准失败（不影响本次取号）：{e}")

    # ------------------------------------------------------------------
    # 库内兜底
    # ------------------------------------------------------------------

    @staticmethod
    async def _db_max_seq(db: AsyncSession, prefix: str, day: str) -> int:
        """取当日已用的最大流水

        **不过滤 is_deleted**：唯一索引对软删行同样生效，已删除的编号仍占位，
        必须跳过。这一点与任务单号生成同理（见 task_code_name_generator.py）。
        """
        _model, column = _NO_COLUMNS[prefix]
        head = f"{prefix}{day}"
        rows = (
            await db.execute(select(column).where(column.like(f"{head}%")))
        ).scalars().all()

        max_seq = 0
        head_len = len(head)
        for no in rows:
            if not no or len(no) <= head_len:
                continue
            tail = no[head_len:]
            if tail.isdigit():
                max_seq = max(max_seq, int(tail))
        return max_seq
