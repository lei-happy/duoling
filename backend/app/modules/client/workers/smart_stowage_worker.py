"""
智能配载 Worker（多租户轮询，预留给"定时自动预配"）

本版智能配载以"调度员手动一键生成"为主，API 内同步产出方案；本 worker 为
未来"待配池达阈值/定时自动预配"预留，与承运/成本/运费 worker 同构：

  - APScheduler 定时扫所有 db_initialized=1 的租户库；
  - 认领 status=pending 的 biz_smart_stowage_task 并执行 run_generation。
  - 手动同步路径会把任务直接置为 running/success，worker 不会重复处理。

部署形态：
  - 独立 docker service（入口 app/workers/smart_stowage_main.py）；
  - 或 SMART_STOWAGE_WORKER_ENABLED=1 时在 API 进程内嵌启动（仅本地/单实例）。
"""

from __future__ import annotations

import asyncio
import os
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import db_manager
from app.modules.client.services.task.smart_stowage.smart_stowage_service import (
    SmartStowageService,
)
from app.modules.client.services.task.smart_stowage.stowage_task_service import (
    SmartStowageTaskService,
)


class SmartStowageWorker:
    """智能配载 worker（多租户轮询）"""

    def __init__(self) -> None:
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._running_lock = asyncio.Lock()
        self._enabled = self._read_enabled()
        self._interval_sec = int(os.getenv("SMART_STOWAGE_WORKER_INTERVAL", "10"))
        self._batch_size = int(os.getenv("SMART_STOWAGE_WORKER_BATCH", "5"))
        self._tenants_missing_table: set[str] = set()

    @staticmethod
    def _read_enabled() -> bool:
        v = os.getenv("SMART_STOWAGE_WORKER_ENABLED", "0").strip().lower()
        return v not in ("0", "false", "no", "off")

    # ---------- 调度入口 ----------

    def start(self) -> None:
        if not self._enabled:
            logger.info(
                "[SmartStowageWorker] API 进程内未启动（SMART_STOWAGE_WORKER_ENABLED!=1）；"
                "手动生成走同步路径，无需常驻 worker"
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
            self._tick_safely,
            "interval",
            seconds=self._interval_sec,
            id="smart_stowage_tick",
            max_instances=1,
            coalesce=True,
        )
        self._scheduler.start()
        logger.info(
            f"[SmartStowageWorker] 已启动，间隔 {self._interval_sec}s，"
            f"每租户每轮 {self._batch_size} 条"
        )

    def shutdown(self) -> None:
        if self._scheduler:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"[SmartStowageWorker] shutdown 异常: {e}")
            self._scheduler = None
            logger.info("[SmartStowageWorker] 已停止")

    # ---------- 调度循环 ----------

    async def _tick_safely(self) -> None:
        if self._running_lock.locked():
            return
        async with self._running_lock:
            try:
                await self._tick()
            except Exception as e:  # noqa: BLE001
                logger.exception(f"[SmartStowageWorker] tick 异常: {e}")

    async def _tick(self) -> None:
        codes = await self._list_active_tenant_codes()
        for code in codes:
            try:
                await self._process_tenant(code)
            except Exception as e:  # noqa: BLE001
                msg = str(e)
                if "1146" in msg or "doesn't exist" in msg:
                    if code not in self._tenants_missing_table:
                        self._tenants_missing_table.add(code)
                        logger.warning(
                            f"[SmartStowageWorker] 跳过租户 {code}：智能配载表缺失（"
                            f"未开通 smart_stowage 功能？）。后续轮询将静默跳过。"
                        )
                else:
                    logger.warning(f"[SmartStowageWorker] 处理租户 {code} 失败: {e}")

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
            tasks = await SmartStowageTaskService.claim_pending(
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
            await SmartStowageService.run_generation(session, task.id)
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"[SmartStowageWorker] task#{task.id} 生成失败: {e}"
            )
            try:
                await SmartStowageTaskService.mark_failed(session, task.id, repr(e))
            except Exception:
                logger.exception("[SmartStowageWorker] mark_failed 二次失败")


# 全局单例
smart_stowage_worker = SmartStowageWorker()


def setup_worker_with_settings() -> None:
    _ = get_settings()
    smart_stowage_worker.start()


def shutdown_worker() -> None:
    smart_stowage_worker.shutdown()
