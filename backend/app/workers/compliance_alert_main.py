"""
独立运行的证照监控 worker 入口

使用方式：
    python -m app.workers.compliance_alert_main

部署在 deploy/docker/docker-compose.yml 的 backend-compliance-worker 服务中，
与 backend (uvicorn) 共用同一镜像，仅启动命令不同。

实现要点（对齐 freight_calc_main）：
  1) 初始化平台库连接（启动时）
  2) 复用 ComplianceAlertWorker（APScheduler 内嵌）执行多租户扫描循环
  3) 监听 SIGTERM/SIGINT 优雅退出
"""

from __future__ import annotations

import asyncio
import signal

from loguru import logger

from app.core.config import get_settings
from app.core.database import db_manager
from app.modules.client.workers.compliance_alert_worker import (
    compliance_alert_worker,
)


async def _main() -> None:
    settings = get_settings()
    logger.info(
        f"[compliance-worker] 启动 env={settings.APP_ENV} "
        f"platform_db={settings.platform_database_name}"
    )

    await db_manager.init_platform_db()

    compliance_alert_worker.start_force()

    stop_event = asyncio.Event()

    def _shutdown(_signum, _frame):
        logger.info(f"[compliance-worker] 收到信号 {_signum}，准备优雅退出")
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
        logger.info("[compliance-worker] 正在关闭 scheduler 与数据库连接")
        compliance_alert_worker.shutdown()
        await db_manager.close_all()
        logger.info("[compliance-worker] 已退出")


if __name__ == "__main__":
    asyncio.run(_main())
