"""
独立运行的运费计算 worker 入口

使用方式：
    python -m app.workers.freight_calc_main

部署在 deploy/docker/docker-compose.yml 的 backend-worker 服务中，
与 backend (uvicorn) 共用同一镜像，仅启动命令不同。

实现要点：
  1) 初始化平台库连接（启动时）
  2) 复用 FreightCalcWorker（APScheduler 内嵌）执行扫表/认领/执行循环
  3) 监听 SIGTERM/SIGINT 优雅退出
"""

from __future__ import annotations

import asyncio
import signal

from loguru import logger

from app.core.database import db_manager
from app.core.config import get_settings
from app.modules.client.workers.freight_calc_worker import (
    freight_calc_worker,
)


async def _main() -> None:
    settings = get_settings()
    logger.info(
        f"[freight-worker] 启动 env={settings.APP_ENV} "
        f"platform_db={settings.platform_database_name}"
    )

    # 初始化平台库（worker 需要从 sys_tenant 读取活跃租户列表）
    await db_manager.init_platform_db()

    # 强制启动 scheduler（不受 FREIGHT_CALC_WORKER_ENABLED 影响）
    freight_calc_worker.start_force()

    # 等待退出信号
    stop_event = asyncio.Event()

    def _shutdown(_signum, _frame):
        logger.info(f"[freight-worker] 收到信号 {_signum}，准备优雅退出")
        try:
            asyncio.get_event_loop().call_soon_threadsafe(stop_event.set)
        except Exception:
            stop_event.set()

    # Windows 不支持 SIGTERM，但支持 SIGINT；Linux 支持两者
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
        logger.info("[freight-worker] 正在关闭 scheduler 与数据库连接")
        freight_calc_worker.shutdown()
        await db_manager.close_all()
        logger.info("[freight-worker] 已退出")


if __name__ == "__main__":
    asyncio.run(_main())
