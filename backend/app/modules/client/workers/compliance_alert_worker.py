"""
证照监控 Worker（资质到期扫描引擎）

部署形态（与运费计算 worker 完全一致的设计）：
  - 推荐：作为独立 docker service 运行（deploy/docker/docker-compose.yml 的
    backend-compliance-worker），入口 app/workers/compliance_alert_main.py。
  - 兼容：环境变量 COMPLIANCE_WORKER_ENABLED=1 时也能在 API 进程内嵌启动
    （仅本地开发 / 单实例小流量；多 uvicorn worker 生产环境请勿打开，
    否则多实例重复扫描）。

实现要点：
  - APScheduler 定时（默认 3600s）扫所有 db_initialized=1 的租户库；
    证照到期是「天」级变化，无需高频，独立进程避免拖累 API 性能。
  - 每个租户：先幂等补建 biz_compliance_alert 表，再调 ComplianceScanService。
  - 表缺失 / 未开通运力域的租户跳过，并降噪日志（每租户只警告一次）。
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
from app.modules.client.services.compliance.compliance_scan_service import (
    ComplianceScanService,
)

_ALERT_TABLE = "biz_compliance_alert"
# 扫描依赖的运力业务表；任一缺失说明该租户未开通运力域，直接跳过
_PREREQUISITE_TABLES = ("biz_vehicle", "biz_driver")


class ComplianceAlertWorker:
    """证照监控 worker（多租户轮询）"""

    def __init__(self) -> None:
        self._scheduler: Optional[AsyncIOScheduler] = None
        self._running_lock = asyncio.Lock()
        self._enabled = self._read_enabled()
        self._interval_sec = int(os.getenv("COMPLIANCE_WORKER_INTERVAL", "3600"))
        self._tenants_skipped: set[str] = set()

    @staticmethod
    def _read_enabled() -> bool:
        v = os.getenv("COMPLIANCE_WORKER_ENABLED", "0").strip().lower()
        return v not in ("0", "false", "no", "off")

    # ---------- 调度入口 ----------

    def start(self) -> None:
        """API 进程内嵌启动（仅当 COMPLIANCE_WORKER_ENABLED=1 时生效）。"""
        if not self._enabled:
            logger.info(
                "[ComplianceWorker] API 进程内未启动（COMPLIANCE_WORKER_ENABLED!=1）；"
                "请确认独立 backend-compliance-worker 容器已运行"
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
            id="compliance_alert_tick",
            max_instances=1,
            coalesce=True,
            next_run_time=None,
        )
        self._scheduler.start()
        # 启动后立即跑一次（不必等第一个 interval）
        try:
            asyncio.get_event_loop().create_task(self._tick_safely())
        except Exception:
            pass
        logger.info(
            f"[ComplianceWorker] 已启动，扫描间隔 {self._interval_sec}s"
        )

    def shutdown(self) -> None:
        if self._scheduler:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"[ComplianceWorker] shutdown 异常: {e}")
            self._scheduler = None
            logger.info("[ComplianceWorker] 已停止")

    # ---------- 调度循环 ----------

    async def _tick_safely(self) -> None:
        if self._running_lock.locked():
            return
        async with self._running_lock:
            try:
                await self._tick()
            except Exception as e:  # noqa: BLE001
                logger.exception(f"[ComplianceWorker] tick 异常: {e}")

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
                            f"[ComplianceWorker] 跳过租户 {code}：运力业务表缺失"
                            f"（未开通运力域？）。后续轮询静默跳过。"
                        )
                else:
                    logger.warning(f"[ComplianceWorker] 处理租户 {code} 失败: {e}")

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

        # 预检：缺运力业务表的租户直接跳过（不报错刷屏）
        if not await self._has_prerequisite_tables(tenant_code):
            if tenant_code not in self._tenants_skipped:
                self._tenants_skipped.add(tenant_code)
                logger.info(
                    f"[ComplianceWorker] 租户 {tenant_code} 未开通运力域，跳过"
                )
            return

        # 老租户库幂等补建预警表
        await db_manager.ensure_tenant_tables(tenant_code, [_ALERT_TABLE])

        db_manager._get_or_create_tenant_engine(tenant_code)  # noqa: SLF001
        factory = db_manager._tenant_session_factories[tenant_code]  # noqa: SLF001
        async with factory() as session:
            stats = await ComplianceScanService.scan_tenant(session)
        if stats.get("candidates"):
            logger.info(f"[ComplianceWorker] 租户 {tenant_code} 扫描: {stats}")

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
compliance_alert_worker = ComplianceAlertWorker()


def setup_worker_with_settings() -> None:
    """供 events.lifespan 调用"""
    _ = get_settings()
    compliance_alert_worker.start()


def shutdown_worker() -> None:
    compliance_alert_worker.shutdown()
