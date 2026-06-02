"""
运营后台：行政区域高德同步任务 API
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.exceptions import BizException
from app.common.response import success
from app.modules.console.schemas.ops.region_sync import (
    RegionSyncTriggerBody,
    RegionSyncJobOut,
)
from app.modules.console.services.region.region_sync_service import RegionSyncService
from app.modules.console.services.region.region_sync_runner import schedule_region_sync_job

router = APIRouter()


@router.post("/trigger")
async def trigger_sync(
    body: RegionSyncTriggerBody,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    if await RegionSyncService.has_running_job(db):
        raise BizException("已有同步任务正在执行，请稍后再试")
    row = await RegionSyncService.create_job(db, body)
    await db.commit()
    await schedule_region_sync_job(row.job_id)
    return success(data={"jobId": row.job_id})


@router.get("")
async def page_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await RegionSyncService.page_jobs(db, page=page, limit=limit)
    return success(
        data={
            "list": [RegionSyncJobOut.from_row(r).model_dump() for r in data["list"]],
            "count": data["count"],
        }
    )


@router.get("/{job_id}")
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await RegionSyncService.get_job(db, job_id)
    if not row:
        raise BizException("任务不存在")
    return success(data=RegionSyncJobOut.from_row(row).model_dump())
