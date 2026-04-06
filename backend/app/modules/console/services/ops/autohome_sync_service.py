"""
汽车之家同步任务：创建、分页、详情
"""

import json
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.ops.autohome_sync_job import AutohomeSyncJob
from app.modules.console.schemas.ops.autohome_sync import (
    AutohomeSyncJobOut,
    AutohomeSyncTriggerBody,
)


class AutohomeSyncService:
    @staticmethod
    async def create_job(
        db: AsyncSession, body: AutohomeSyncTriggerBody
    ) -> AutohomeSyncJob:
        jt = (body.jobType or "probe").strip().lower()
        if jt not in ("probe", "full"):
            jt = "probe"
        if jt == "probe":
            payload: dict = {"autohomeSeriesId": body.autohomeSeriesId}
        else:
            payload = {
                "maxBrands": body.maxBrands,
                "delayMs": body.delayMs,
                "includeInactiveBrands": body.includeInactiveBrands,
                "fetchSpecs": body.fetchSpecs,
            }
        row = AutohomeSyncJob(
            job_type=jt,
            status="pending",
            progress_pct=0,
            payload_json=json.dumps(payload, ensure_ascii=False),
            log_text="",
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return row

    @staticmethod
    async def get_job(db: AsyncSession, job_id: int) -> Optional[AutohomeSyncJob]:
        r = await db.execute(
            select(AutohomeSyncJob).where(AutohomeSyncJob.job_id == job_id)
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def page_jobs(
        db: AsyncSession, page: int = 1, limit: int = 20
    ) -> dict:
        base = select(AutohomeSyncJob)
        count_q = select(func.count()).select_from(AutohomeSyncJob)
        total = (await db.execute(count_q)).scalar() or 0
        result = await db.execute(
            base.order_by(AutohomeSyncJob.job_id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        rows = result.scalars().all()
        return {
            "list": [AutohomeSyncJobOut.from_row(r).model_dump() for r in rows],
            "count": int(total),
        }
