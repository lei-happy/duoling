"""
能源同步 Worker（多租户轮询，与 CostCalcWorker 对称）

部署：独立 docker service（入口 app/workers/energy_sync_main.py）。
兼容：ENERGY_SYNC_WORKER_ENABLED=1 时也可在 API 进程内嵌启动。
"""

from __future__ import annotations

import asyncio
import os
from datetime import date
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import db_manager
from app.modules.client.services.energy.allocation_service import EnergyAllocationService
from app.modules.client.services.energy.connector_service import EnergyConnectorService
from app.modules.client.services.energy.snapshot_service import EnergySnapshotService
from app.modules.client.services.energy.sync_task_service import EnergySyncTaskService


class EnergySyncWorker:

    def __init__(self) -> None:
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._running_lock = asyncio.Lock()
        self._enabled = self._read_enabled()
        self._interval_sec = int(os.getenv("ENERGY_SYNC_WORKER_INTERVAL", "30"))
        self._batch_size = int(os.getenv("ENERGY_SYNC_WORKER_BATCH", "10"))
        self._tenants_missing_table: set[str] = set()

    @staticmethod
    def _read_enabled() -> bool:
        v = os.getenv("ENERGY_SYNC_WORKER_ENABLED", "0").strip().lower()
        return v not in ("0", "false", "no", "off")

    def start(self) -> None:
        if not self._enabled:
            logger.info(
                "[EnergySyncWorker] API 进程内未启动（ENERGY_SYNC_WORKER_ENABLED!=1）；"
                "请确认独立 energy-worker 容器已运行"
            )
            return
        self._do_start()

    def start_force(self) -> None:
        self._do_start()

    def _do_start(self) -> None:
        if self._scheduler is not None:
            return
        self._scheduler = AsyncIOScheduler()
        self._scheduler.add_job(
            self._tick_safely, "interval", seconds=self._interval_sec,
            id="energy_sync_tick", max_instances=1, coalesce=True,
        )
        self._scheduler.add_job(
            self._daily_safely, "cron", hour=1, minute=10,
            id="energy_daily_snapshot", max_instances=1, coalesce=True,
        )
        self._scheduler.start()
        logger.info(f"[EnergySyncWorker] 已启动，间隔 {self._interval_sec}s")

    def shutdown(self) -> None:
        if self._scheduler:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception as e:
                logger.warning(f"[EnergySyncWorker] shutdown 异常: {e}")
            self._scheduler = None

    async def _tick_safely(self) -> None:
        if self._running_lock.locked():
            return
        async with self._running_lock:
            try:
                await self._tick()
            except Exception as e:  # noqa: BLE001
                logger.exception(f"[EnergySyncWorker] tick 异常: {e}")

    async def _daily_safely(self) -> None:
        try:
            await self._daily()
        except Exception as e:  # noqa: BLE001
            logger.exception(f"[EnergySyncWorker] daily 异常: {e}")

    async def _tick(self) -> None:
        for code in await self._list_active_tenant_codes():
            try:
                await self._process_tenant(code)
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if "1146" in msg or "doesn't exist" in msg:
                    if code not in self._tenants_missing_table:
                        self._tenants_missing_table.add(code)
                        logger.warning(
                            f"[EnergySyncWorker] 跳过租户 {code}：能源表缺失"
                        )
                else:
                    logger.warning(f"[EnergySyncWorker] 处理租户 {code} 失败: {e}")

    async def _daily(self) -> None:
        yesterday = date.today()
        for code in await self._list_active_tenant_codes():
            if code in self._tenants_missing_table:
                continue
            try:
                db_manager._get_or_create_tenant_engine(code)  # noqa: SLF001
                factory = db_manager._tenant_session_factories[code]  # noqa: SLF001
                async with factory() as session:
                    await EnergySnapshotService.build_day(session, yesterday)
                    await EnergyAllocationService.refresh_day(session, yesterday)
                    await session.commit()
            except Exception as e:  # noqa: BLE001
                logger.warning(f"[EnergySyncWorker] 日终 {code} 失败: {e}")

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
        if tenant_code in self._tenants_missing_table:
            return
        db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
        factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001
        async with factory() as session:
            tasks = await EnergySyncTaskService.claim_pending(
                session, batch_size=self._batch_size,
            )
            if not tasks:
                await session.commit()
                return
            for task in tasks:
                await self._run_one(session, task)
            await session.commit()

    async def _run_one(self, session: AsyncSession, task) -> None:
        try:
            if task.task_type == "pull" and task.connector_id:
                await EnergyConnectorService.pull(session, task.connector_id)
            elif task.task_type == "allocate":
                await EnergyAllocationService.refresh_day(session, date.today())
            elif task.task_type == "snapshot":
                await EnergySnapshotService.build_day(session, date.today())
            else:
                await EnergySyncTaskService.mark_failed(
                    session, task.id, f"unsupported task_type: {task.task_type}",
                )
                return
            await EnergySyncTaskService.mark_success(session, task.id)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"[EnergySyncWorker] task#{task.id} 失败: {e}")
            await EnergySyncTaskService.mark_failed(session, task.id, repr(e))


energy_sync_worker = EnergySyncWorker()


def setup_worker_with_settings() -> None:
    _ = get_settings()
    energy_sync_worker.start()


def shutdown_worker() -> None:
    energy_sync_worker.shutdown()
