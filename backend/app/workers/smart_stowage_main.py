"""
独立运行的智能配载 worker 入口

使用方式：
    python -m app.workers.smart_stowage_main

与 backend (uvicorn) 共用同一镜像，仅启动命令不同。扫 biz_smart_stowage_task
异步执行配载方案生成（供"定时自动预配"场景）。
"""

from __future__ import annotations

import asyncio
import signal

from loguru import logger

from app.core.database import db_manager
from app.core.config import get_settings
from app.modules.client.workers.smart_stowage_worker import smart_stowage_worker


async def _main() -> None:
    settings = get_settings()
    logger.info(
        f"[smart-stowage-worker] 启动 env={settings.APP_ENV} "
        f"platform_db={settings.platform_database_name}"
    )

    await db_manager.init_platform_db()

    smart_stowage_worker.start_force()

    stop_event = asyncio.Event()

    def _shutdown(_signum, _frame):
        logger.info(f"[smart-stowage-worker] 收到信号 {_signum}，准备优雅退出")
        try:
            asyncio.get_event_loop().call_soon_threadsafe(stop_event.set)
        except Exception:
            stop_event.set()

    for sig_name in ("SIGTERM", "SIGINT"):
        sig = getattr(signal, sig_name, None)
        if sig is None:
            continue
        try:
            signal.signal(sig, _shutdown)
        except (ValueError, OSError):
            pass

    try:
        await stop_event.wait()
    finally:
        logger.info("[smart-stowage-worker] 正在关闭 scheduler 与数据库连接")
        smart_stowage_worker.shutdown()
        await db_manager.close_all()
        logger.info("[smart-stowage-worker] 已退出")


if __name__ == "__main__":
    asyncio.run(_main())
