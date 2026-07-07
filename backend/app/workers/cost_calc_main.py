"""
独立运行的成本计算 worker 入口

使用方式：
    python -m app.workers.cost_calc_main

与 backend (uvicorn) 共用同一镜像，仅启动命令不同。扫 biz_cost_calc_task
异步执行任务应付成本计算。
"""

from __future__ import annotations

import asyncio
import signal

from loguru import logger

from app.core.database import db_manager
from app.core.config import get_settings
from app.modules.client.workers.cost_calc_worker import cost_calc_worker


async def _main() -> None:
    settings = get_settings()
    logger.info(
        f"[cost-worker] 启动 env={settings.APP_ENV} "
        f"platform_db={settings.platform_database_name}"
    )

    await db_manager.init_platform_db()

    # 强制启动 scheduler（不受 COST_CALC_WORKER_ENABLED 影响）
    cost_calc_worker.start_force()

    stop_event = asyncio.Event()

    def _shutdown(_signum, _frame):
        logger.info(f"[cost-worker] 收到信号 {_signum}，准备优雅退出")
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
        logger.info("[cost-worker] 正在关闭 scheduler 与数据库连接")
        cost_calc_worker.shutdown()
        await db_manager.close_all()
        logger.info("[cost-worker] 已退出")


if __name__ == "__main__":
    asyncio.run(_main())
