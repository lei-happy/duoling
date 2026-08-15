"""
独立运行的能源同步 worker 入口

    python -m app.workers.energy_sync_main
"""

from __future__ import annotations

import asyncio
import signal

from loguru import logger

from app.core.config import get_settings
from app.core.database import db_manager
from app.modules.client.workers.energy_sync_worker import energy_sync_worker


async def _main() -> None:
    settings = get_settings()
    logger.info(
        f"[energy-worker] 启动 env={settings.APP_ENV} "
        f"platform_db={settings.platform_database_name}"
    )
    await db_manager.init_platform_db()
    energy_sync_worker.start_force()

    stop_event = asyncio.Event()

    def _shutdown(_signum, _frame):
        logger.info(f"[energy-worker] 收到信号 {_signum}，准备优雅退出")
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
        energy_sync_worker.shutdown()
        await db_manager.close_all()
        logger.info("[energy-worker] 已退出")


if __name__ == "__main__":
    asyncio.run(_main())
