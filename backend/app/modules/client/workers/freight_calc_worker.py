"""
运费计算 Worker

部署形态：
  - 推荐：作为独立 docker service 运行（参见
    deploy/docker/docker-compose.yml 的 backend-worker 服务），
    入口是 app/workers/freight_calc_main.py。
  - 兼容：通过环境变量 FREIGHT_CALC_WORKER_ENABLED=1 也能让 API 进程
    内嵌启动（仅供本地开发或单实例小流量场景，不要在多 uvicorn worker
    生产环境下打开，否则会出现多实例重复扫表）。

实现要点：
  - APScheduler 定时（默认 5s）扫所有 db_initialized=1 的租户库，
    认领并执行 biz_freight_calc_task。
  - 每次每个租户最多处理 batch_size 条，避免占住事件循环。
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
from app.modules.client.services.billing.freight_calc_service import FreightCalcService
from app.modules.client.services.billing.freight_calc_task_service import (
    FreightCalcTaskService,
)


class FreightCalcWorker:
    """运费计算 worker（多租户轮询）"""

    def __init__(self) -> None:
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._running_lock = asyncio.Lock()
        self._enabled = self._read_enabled()
        self._interval_sec = int(os.getenv("FREIGHT_CALC_WORKER_INTERVAL", "5"))
        self._batch_size = int(os.getenv("FREIGHT_CALC_WORKER_BATCH", "20"))
        # 表缺失的租户：跳过本轮，并降噪日志（每个租户只警告一次，
        # 重启 worker 或下次 ready_set 重置后再触发警告）
        self._tenants_missing_table: set[str] = set()

    @staticmethod
    def _read_enabled() -> bool:
        # 默认关闭：避免与独立 worker 容器重复扫表；
        # 独立 worker 容器内通过 setup_force() 强制启动。
        v = os.getenv("FREIGHT_CALC_WORKER_ENABLED", "0").strip().lower()
        return v not in ("0", "false", "no", "off")

    # ---------- 调度入口 ----------

    def start(self) -> None:
        """API 进程内嵌启动（仅当 FREIGHT_CALC_WORKER_ENABLED=1 时生效）。"""
        if not self._enabled:
            logger.info(
                "[FreightCalcWorker] API 进程内未启动（FREIGHT_CALC_WORKER_ENABLED!=1）；"
                "请确认独立 backend-worker 容器已运行"
            )
            return
        self._do_start()

    def start_force(self) -> None:
        """独立 worker 进程入口强制启动（不受 FREIGHT_CALC_WORKER_ENABLED 影响）。"""
        self._do_start()

    def _do_start(self) -> None:
        if self._scheduler is not None:
            return
        self._scheduler = AsyncIOScheduler()
        self._scheduler.add_job(
            self._tick_safely,
            "interval",
            seconds=self._interval_sec,
            id="freight_calc_tick",
            max_instances=1,
            coalesce=True,
        )
        self._scheduler.start()
        logger.info(
            f"[FreightCalcWorker] 已启动，间隔 {self._interval_sec}s，"
            f"每租户每轮 {self._batch_size} 条"
        )

    def shutdown(self) -> None:
        if self._scheduler:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception as e:
                logger.warning(f"[FreightCalcWorker] shutdown 异常: {e}")
            self._scheduler = None
            logger.info("[FreightCalcWorker] 已停止")

    # ---------- 调度循环 ----------

    async def _tick_safely(self) -> None:
        if self._running_lock.locked():
            return
        async with self._running_lock:
            try:
                await self._tick()
            except Exception as e:  # noqa: BLE001
                logger.exception(f"[FreightCalcWorker] tick 异常: {e}")

    async def _tick(self) -> None:
        codes = await self._list_active_tenant_codes()
        if not codes:
            return
        for code in codes:
            try:
                await self._process_tenant(code)
            except Exception as e:  # noqa: BLE001
                # 表不存在（1146）通常是新租户库尚未跑过迁移脚本，
                # 跳过该租户，每个租户只打印一次警告，避免日志刷屏。
                msg = str(e)
                if "1146" in msg or "doesn't exist" in msg:
                    if code not in self._tenants_missing_table:
                        self._tenants_missing_table.add(code)
                        logger.warning(
                            f"[FreightCalcWorker] 跳过租户 {code}：业务表缺失（"
                            f"未跑 migrate_freight_engine.py？）。后续轮询将静默跳过，"
                            f"如已建表请重启 worker 触发重检。"
                        )
                else:
                    logger.warning(f"[FreightCalcWorker] 处理租户 {code} 失败: {e}")

    async def _list_active_tenant_codes(self) -> list[str]:
        """从平台库查 db_initialized=1 的租户编码"""
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
        """处理单个租户库的待办任务"""
        # 已知表缺失的租户直接跳过，不再连库
        if tenant_code in self._tenants_missing_table:
            return

        # 直接拿 session（不走 dependency 包装）
        db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
        factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001

        async with factory() as session:
            # 认领批次
            tasks = await FreightCalcTaskService.claim_pending(
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
            if task.target_type == "waybill":
                await FreightCalcService.calculate_and_persist(
                    session,
                    waybill_id=task.target_id,
                    triggered_by=task.task_type,
                    triggered_user_id=task.triggered_by_user_id,
                )
                await FreightCalcTaskService.mark_success(session, task.id)
            else:
                # 当前 worker 只处理 waybill 粒度任务；其它类型应在入队时
                # 已展开为多条 waybill 任务，不应直接出现在这里
                await FreightCalcTaskService.mark_failed(
                    session, task.id,
                    f"unsupported target_type: {task.target_type}",
                )
        except Exception as e:  # noqa: BLE001
            logger.warning(
                f"[FreightCalcWorker] task#{task.id} (waybill={task.target_id}) "
                f"执行失败: {e}"
            )
            try:
                await FreightCalcTaskService.mark_failed(session, task.id, repr(e))
            except Exception:
                logger.exception("[FreightCalcWorker] mark_failed 二次失败")


# 全局单例
freight_calc_worker = FreightCalcWorker()


def setup_worker_with_settings() -> None:
    """供 events.lifespan 调用"""
    _ = get_settings()
    freight_calc_worker.start()


def shutdown_worker() -> None:
    freight_calc_worker.shutdown()
