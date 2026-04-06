"""
运营后台：汽车之家同步任务 API
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.exceptions import BizException
from app.common.response import success
from app.modules.console.schemas.ops.autohome_sync import (
    AutohomeSyncTriggerBody,
    AutohomeSyncJobOut,
)
from app.modules.console.services.ops.autohome_sync_service import AutohomeSyncService
from app.modules.console.services.ops.autohome_crawl_runner import schedule_probe_job
from app.modules.console.services.ops.autohome_full_sync import schedule_full_sync_job

router = APIRouter()


@router.post("/trigger")
async def trigger_sync(
    body: AutohomeSyncTriggerBody,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    jt = (body.jobType or "probe").strip().lower()
    if jt not in ("probe", "full"):
        raise BizException("jobType 仅支持 probe 或 full")
    row = await AutohomeSyncService.create_job(db, body)
    await db.commit()
    if jt == "probe":
        await schedule_probe_job(row.job_id)
    else:
        await schedule_full_sync_job(row.job_id)
    return success(data={"jobId": row.job_id})


@router.get("")
async def page_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await AutohomeSyncService.page_jobs(db, page=page, limit=limit)
    return success(data=data)


@router.get("/{job_id}")
async def get_job(
    job_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await AutohomeSyncService.get_job(db, job_id)
    if not row:
        raise BizException("任务不存在")
    return success(data=AutohomeSyncJobOut.from_row(row).model_dump())
