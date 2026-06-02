"""
行政区域高德同步任务：创建、分页、详情
"""

import json
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.ops.region_sync_job import RegionSyncJob
from app.modules.console.schemas.ops.region_sync import RegionSyncTriggerBody


class RegionSyncService:
    @staticmethod
    async def create_job(
        db: AsyncSession, body: RegionSyncTriggerBody
    ) -> RegionSyncJob:
        payload = {}
        if body.maxConcurrent is not None:
            payload["maxConcurrent"] = body.maxConcurrent
        if body.requestDelayMs is not None:
            payload["requestDelayMs"] = body.requestDelayMs

        row = RegionSyncJob(
            status="pending",
            progress_pct=0,
            payload_json=json.dumps(payload, ensure_ascii=False) if payload else None,
            log_text="",
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def get_job(db: AsyncSession, job_id: int) -> Optional[RegionSyncJob]:
        result = await db.execute(
            select(RegionSyncJob).where(RegionSyncJob.job_id == job_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def page_jobs(db: AsyncSession, page: int = 1, limit: int = 20) -> dict:
        count_q = select(func.count()).select_from(RegionSyncJob)
        total = (await db.execute(count_q)).scalar() or 0
        result = await db.execute(
            select(RegionSyncJob)
            .order_by(RegionSyncJob.job_id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = result.scalars().all()
        return {
            "list": rows,
            "count": int(total),
        }

    @staticmethod
    async def has_running_job(db: AsyncSession) -> bool:
        result = await db.execute(
            select(func.count())
            .select_from(RegionSyncJob)
            .where(RegionSyncJob.status.in_(("pending", "running")))
        )
        return (result.scalar() or 0) > 0
