"""
行政区域高德同步任务执行器
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import List, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import db_manager
from app.modules.console.models.ops.region_sync_job import RegionSyncJob
from app.modules.console.services.region.amap_district_client import (
    AmapDistrictClient,
    ParsedRegionRow,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


def _append_log(current: Optional[str], line: str) -> str:
    prefix = current or ""
    return prefix + line + "\n"


async def _save_job(session: AsyncSession, job: RegionSyncJob) -> None:
    await session.flush()
    await session.commit()


def _row_to_params(row: ParsedRegionRow) -> dict:
    return {
        "code": row.code,
        "name": row.name,
        "pcode": row.pcode,
        "level": row.level,
        "sort_order": row.sort_order,
        "citycode": row.citycode,
        "longitude": row.longitude,
        "latitude": row.latitude,
        "status": 1,
        "is_deleted": 0,
    }


async def _upsert_regions(session: AsyncSession, rows: List[ParsedRegionRow]) -> None:
    if not rows:
        return

    upsert_sql = text(
        """
        INSERT INTO sys_regions (
            code, name, pcode, level, sort_order, citycode,
            longitude, latitude, status, is_deleted
        ) VALUES (
            :code, :name, :pcode, :level, :sort_order, :citycode,
            :longitude, :latitude, :status, :is_deleted
        )
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            pcode = VALUES(pcode),
            level = VALUES(level),
            sort_order = VALUES(sort_order),
            citycode = VALUES(citycode),
            longitude = VALUES(longitude),
            latitude = VALUES(latitude),
            status = VALUES(status),
            is_deleted = 0,
            updated_at = CURRENT_TIMESTAMP
        """
    )

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i : i + BATCH_SIZE]
        for params in (_row_to_params(r) for r in batch):
            await session.execute(upsert_sql, params)


async def _load_job(session: AsyncSession, job_id: int) -> Optional[RegionSyncJob]:
    result = await session.execute(
        select(RegionSyncJob).where(RegionSyncJob.job_id == job_id)
    )
    return result.scalar_one_or_none()


async def run_region_sync_job(job_id: int) -> None:
    factory = db_manager._platform_session_factory
    if factory is None:
        logger.error("platform session factory not ready, job %s", job_id)
        return

    async with factory() as session:
        job = await _load_job(session, job_id)
        if not job:
            return

        job.status = "running"
        job.progress_pct = 1
        job.log_text = _append_log(job.log_text, "[sync] 任务开始")
        await _save_job(session, job)

    max_concurrent: Optional[int] = None
    request_delay_ms: Optional[int] = None
    async with factory() as session:
        job = await _load_job(session, job_id)
        if job and job.payload_json:
            try:
                payload = json.loads(job.payload_json)
                if payload.get("maxConcurrent") is not None:
                    max_concurrent = int(payload["maxConcurrent"])
                if payload.get("requestDelayMs") is not None:
                    request_delay_ms = int(payload["requestDelayMs"])
            except (json.JSONDecodeError, TypeError, ValueError):
                pass

    client = AmapDistrictClient(
        max_concurrent=max_concurrent,
        request_delay_ms=request_delay_ms,
    )

    async def progress_callback(pct: int, message: str) -> None:
        async with factory() as progress_session:
            progress_job = await _load_job(progress_session, job_id)
            if not progress_job:
                return
            progress_job.progress_pct = min(max(pct, 1), 99)
            progress_job.log_text = _append_log(
                progress_job.log_text, f"[sync] {message}"
            )
            await _save_job(progress_session, progress_job)

    rows: List[ParsedRegionRow] = []
    try:
        rows = await client.fetch_all_regions(progress_callback=progress_callback)

        async with factory() as session:
            job = await _load_job(session, job_id)
            if not job:
                return
            job.log_text = _append_log(
                job.log_text,
                f"[sync] 拉取完成，准备写入 {len(rows)} 条",
            )
            job.progress_pct = 93
            await _save_job(session, job)

            await session.execute(text("UPDATE sys_regions SET is_deleted = 1"))
            await _upsert_regions(session, rows)
            await session.commit()

            job = await _load_job(session, job_id)
            if job:
                job.status = "success"
                job.progress_pct = 100
                job.total_count = len(rows)
                job.error_message = None
                job.log_text = _append_log(
                    job.log_text,
                    f"[sync] 写入成功，共 {len(rows)} 条（含街道）",
                )
                await _save_job(session, job)
    except Exception as exc:
        logger.exception("region sync job %s failed", job_id)
        async with factory() as session:
            await session.rollback()
            job = await _load_job(session, job_id)
            if job:
                job.status = "failed"
                job.progress_pct = 100
                job.error_message = str(exc)[:2000]
                job.log_text = _append_log(job.log_text, f"[sync] 失败: {exc!s}")
                await _save_job(session, job)


async def schedule_region_sync_job(job_id: int) -> None:
    asyncio.create_task(run_region_sync_job(job_id))
