"""
承运商运费计算 Worker（多租户轮询，与收入/成本侧 Worker 对称）

部署形态：
  - 推荐：独立 docker service（入口 app/workers/carrier_freight_calc_main.py）。
  - 兼容：环境变量 CARRIER_FREIGHT_WORKER_ENABLED=1 时也能在 API 进程内嵌启动
    （仅本地开发 / 单实例场景，多 uvicorn worker 生产环境禁止打开）。

实现要点：
  - APScheduler 定时（默认 5s）扫所有 db_initialized=1 的租户库，
    认领并执行 biz_carrier_freight_calc_task。
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
from app.modules.client.services.billing.carrier_freight_calc_service import (
    CarrierFreightCalcService,
)
from app.modules.client.services.billing.carrier_freight_calc_task_service import (
    CarrierFreightCalcTaskService,
)


class CarrierFreightCalcWorker:
    """承运商运费计算 worker（多租户轮询）"""

    def __init__(self) -> None:
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._running_lock = asyncio.Lock()
        self._enabled = self._read_enabled()
        self._interval_sec = int(os.getenv("CARRIER_FREIGHT_WORKER_INTERVAL", "5"))
        self._batch_size = int(os.getenv("CARRIER_FREIGHT_WORKER_BATCH", "20"))
        self._tenants_missing_table: set[str] = set()

    @staticmethod
    def _read_enabled() -> bool:
        v = os.getenv("CARRIER_FREIGHT_WORKER_ENABLED", "0").strip().lower()
        return v not in ("0", "false", "no", "off")

    # ---------- 调度入口 ----------

    def start(self) -> None:
        if not self._enabled:
            logger.info(
                "[CarrierFreightWorker] API 进程内未启动（CARRIER_FREIGHT_WORKER_ENABLED!=1）；"
                "请确认独立 carrier-freight-worker 容器已运行"
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
            id="carrier_freight_calc_tick",
            max_instances=1,
            coalesce=True,
        )
        self._scheduler.start()
        logger.info(
            f"[CarrierFreightWorker] 已启动，间隔 {self._interval_sec}s，"
            f"每租户每轮 {self._batch_size} 条"
        )

    def shutdown(self) -> None:
        if self._scheduler:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception as e:
                logger.warning(f"[CarrierFreightWorker] shutdown 异常: {e}")
            self._scheduler = None
            logger.info("[CarrierFreightWorker] 已停止")

    # ---------- 调度循环 ----------

    async def _tick_safely(self) -> None:
        if self._running_lock.locked():
            return
        async with self._running_lock:
            try:
                await self._tick()
            except Exception as e:  # noqa: BLE001
                logger.exception(f"[CarrierFreightWorker] tick 异常: {e}")

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
                    if code not in self._tenants_missing_table:
                        self._tenants_missing_table.add(code)
                        logger.warning(
                            f"[CarrierFreightWorker] 跳过租户 {code}：承运运费引擎表缺失（"
                            f"未开通 billing_carrier_freight 功能？）。后续轮询将静默跳过。"
                        )
                else:
                    logger.warning(f"[CarrierFreightWorker] 处理租户 {code} 失败: {e}")

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
            tasks = await CarrierFreightCalcTaskService.claim_pending(
                session, batch_size=self._batch_size,
            )
            if not tasks:
                await session.commit()
                return
            for task in tasks:
                await self._run_one_task(session, task)
            await session.commit()

    async def _run_one_task(self, session: AsyncSession, task) -> None:
        try:
            if task.target_type == "task":
                await CarrierFreightCalcService.calculate_and_persist(
                    session,
                    task_id=task.target_id,
                    triggered_by=task.task_type,
                    triggered_user_id=task.triggered_by_user_id,
                )
                await CarrierFreightCalcTaskService.mark_success(session, task.id)
            else:
                await CarrierFreightCalcTaskService.mark_failed(
                    session, task.id,
                    f"unsupported target_type: {task.target_type}",
                )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"[CarrierFreightWorker] task#{task.id} (task={task.target_id}) 执行失败: {e}"
            )
            try:
                await CarrierFreightCalcTaskService.mark_failed(session, task.id, repr(e))
            except Exception:
                logger.exception("[CarrierFreightWorker] mark_failed 二次失败")


# 全局单例
carrier_freight_calc_worker = CarrierFreightCalcWorker()


def setup_worker_with_settings() -> None:
    _ = get_settings()
    carrier_freight_calc_worker.start()


def shutdown_worker() -> None:
    carrier_freight_calc_worker.shutdown()
