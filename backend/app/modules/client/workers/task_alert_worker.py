"""
任务预警 Worker（调度工作台阶段预警扫描引擎）

部署形态与证照监控 worker 一致：
  - 推荐：独立 docker service（deploy/docker/docker-compose.yml 的
    backend-task-alert-worker），入口 app/workers/task_alert_main.py。
  - 兼容：TASK_ALERT_WORKER_ENABLED=1 时可在 API 进程内嵌启动（仅本地开发；
    多 uvicorn worker 的生产环境请勿打开，否则多实例重复扫描）。

与证照监控的关键差异是**扫描频率**：证照到期是「天」级变化，一小时扫一次绰绰有余；
任务预警是「分钟」级变化，调度员盯着看板做决策，默认 180s 一轮。
任务状态变更还会走即时重算通道，所以这里只需兜住「时间流逝」这一类触发。
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy import text

from app.core.config import get_settings
from app.core.database import db_manager
from app.modules.client.services.task.alert.engine import TaskAlertEngine

_ALERT_TABLES = ("biz_task_alert", "biz_task_alert_rule")
# 扫描依赖的任务业务表；缺失说明该租户未开通调度域，直接跳过
_PREREQUISITE_TABLES = ("biz_task", "biz_task_waybill_item")


class TaskAlertWorker:
    """任务预警 worker（多租户轮询）"""

    def __init__(self) -> None:
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._running_lock = asyncio.Lock()
        self._enabled = self._read_enabled()
        self._interval_sec = int(os.getenv("TASK_ALERT_WORKER_INTERVAL", "180"))
        self._tenants_skipped: set[str] = set()

    @staticmethod
    def _read_enabled() -> bool:
        v = os.getenv("TASK_ALERT_WORKER_ENABLED", "0").strip().lower()
        return v not in ("0", "false", "no", "off")

    # ---------- 调度入口 ----------

    def start(self) -> None:
        """API 进程内嵌启动（仅当 TASK_ALERT_WORKER_ENABLED=1 时生效）。"""
        if not self._enabled:
            logger.info(
                "[TaskAlertWorker] API 进程内未启动（TASK_ALERT_WORKER_ENABLED!=1）；"
                "请确认独立 backend-task-alert-worker 容器已运行"
            )
            return
        self._do_start()

    def start_force(self) -> None:
        """独立 worker 进程入口强制启动。"""
        self._do_start()

    def _do_start(self) -> None:
        if self._scheduler is not None:
            return
        self._scheduler = AsyncIOScheduler()
        self._scheduler.add_job(
            self._tick_safely,
            "interval",
            seconds=self._interval_sec,
            id="task_alert_tick",
            max_instances=1,
            coalesce=True,
            next_run_time=None,
        )
        self._scheduler.start()
        try:
            asyncio.get_event_loop().create_task(self._tick_safely())
        except Exception:  # noqa: BLE001
            pass
        logger.info(f"[TaskAlertWorker] 已启动，扫描间隔 {self._interval_sec}s")

    def shutdown(self) -> None:
        if self._scheduler:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"[TaskAlertWorker] shutdown 异常: {e}")
            self._scheduler = None
            logger.info("[TaskAlertWorker] 已停止")

    # ---------- 调度循环 ----------

    async def _tick_safely(self) -> None:
        if self._running_lock.locked():
            return
        async with self._running_lock:
            try:
                await self._tick()
            except Exception as e:  # noqa: BLE001
                logger.exception(f"[TaskAlertWorker] tick 异常: {e}")

    async def _tick(self) -> None:
        codes = await self._list_active_tenant_codes()
        if not codes:
            return
        for code in codes:
            try:
                await self._process_tenant(code)
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if "1146" in msg or "doesn't exist" in msg:
                    if code not in self._tenants_skipped:
                        self._tenants_skipped.add(code)
                        logger.warning(
                            f"[TaskAlertWorker] 跳过租户 {code}：调度业务表缺失"
                            f"（未开通运营调度域？）。后续轮询静默跳过。"
                        )
                else:
                    logger.warning(f"[TaskAlertWorker] 处理租户 {code} 失败: {e}")

    async def _list_active_tenant_codes(self) -> list[str]:
        factory = db_manager._platform_session_factory  # noqa: SLF001
        if factory is None:
            return []
        async with factory() as session:
            r = await session.execute(text(
                "SELECT tenant_code FROM sys_tenant "
                "WHERE is_deleted = 0 AND db_initialized = 1"
            ))
            return [row[0] for row in r.all()]

    async def _process_tenant(self, tenant_code: str) -> None:
        if tenant_code in self._tenants_skipped:
            return

        if not await self._has_prerequisite_tables(tenant_code):
            if tenant_code not in self._tenants_skipped:
                self._tenants_skipped.add(tenant_code)
                logger.info(
                    f"[TaskAlertWorker] 租户 {tenant_code} 未开通运营调度域，跳过"
                )
            return

        # 老租户库幂等补建预警表
        await db_manager.ensure_tenant_tables(tenant_code, list(_ALERT_TABLES))

        db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
        factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001
        async with factory() as session:
            stats = await TaskAlertEngine.scan_tenant(session)
        if stats.get("created") or stats.get("resolved"):
            logger.info(f"[TaskAlertWorker] 租户 {tenant_code} 扫描: {stats}")

    async def _has_prerequisite_tables(self, tenant_code: str) -> bool:
        db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
        factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001
        async with factory() as session:
            r = await session.execute(
                text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() AND table_name IN "
                    "(:t1, :t2)"
                ),
                {"t1": _PREREQUISITE_TABLES[0], "t2": _PREREQUISITE_TABLES[1]},
            )
            return (r.scalar() or 0) >= len(_PREREQUISITE_TABLES)


# 全局单例
task_alert_worker = TaskAlertWorker()


def setup_worker_with_settings() -> None:
    """供 events.lifespan 调用"""
    _ = get_settings()
    task_alert_worker.start()


def shutdown_worker() -> None:
    task_alert_worker.shutdown()
