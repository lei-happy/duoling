"""限流与防重放

优先用 Redis（多实例共享），Redis 不可用时降级为进程内实现（开发/单机可用，
参照 AI 模块 quota.py 的进程内滑窗思路）。这样本地无 Redis 也能跑通与测试。

- nonce 防重放：seen_nonce(key, ttl) 返回 True 表示已见过（重放）
- 固定窗口计数限流：hit_rate_limit(key, limit, window_sec) 返回 True 表示超限
"""

import time
import threading
from typing import Optional

from loguru import logger

try:  # Redis 为可选依赖
    import redis as _redis  # type: ignore
except Exception:  # pragma: no cover
    _redis = None


_redis_client = None
_redis_inited = False

# 进程内降级存储
_lock = threading.Lock()
_local_nonce: dict[str, float] = {}
_local_counter: dict[str, tuple[int, float]] = {}


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
        logger.info("开放平台限流已接入 Redis")
    except Exception:
        _redis_client = None
        logger.warning("Redis 不可用，开放平台限流降级为进程内实现（仅适合单机/开发）")
    return _redis_client


def seen_nonce(key: str, ttl_sec: int) -> bool:
    """记录并判断 nonce 是否重复。首次出现返回 False，重复返回 True。"""
    client = _get_redis()
    if client is not None:
        try:
            # set NX：不存在才写入；已存在说明重放
            ok = client.set(f"op:nonce:{key}", "1", nx=True, ex=ttl_sec)
            return not bool(ok)
        except Exception:
            pass
    now = time.time()
    with _lock:
        _evict_local_nonce(now)
        if key in _local_nonce:
            return True
        _local_nonce[key] = now + ttl_sec
        return False


def _evict_local_nonce(now: float) -> None:
    if len(_local_nonce) < 4096:
        return
    for k in [k for k, exp in _local_nonce.items() if exp < now]:
        _local_nonce.pop(k, None)


def hit_rate_limit(key: str, limit: int, window_sec: int) -> bool:
    """固定窗口计数。超过 limit 返回 True（应拒绝）。limit<=0 表示不限。"""
    if limit <= 0:
        return False
    client = _get_redis()
    if client is not None:
        try:
            redis_key = f"op:rl:{key}"
            cnt = client.incr(redis_key)
            if cnt == 1:
                client.expire(redis_key, window_sec)
            return cnt > limit
        except Exception:
            pass
    now = time.time()
    with _lock:
        cnt, reset_at = _local_counter.get(key, (0, now + window_sec))
        if now >= reset_at:
            cnt, reset_at = 0, now + window_sec
        cnt += 1
        _local_counter[key] = (cnt, reset_at)
        return cnt > limit


def reset_local() -> None:
    """测试辅助：清空进程内计数与 nonce。"""
    with _lock:
        _local_nonce.clear()
        _local_counter.clear()
