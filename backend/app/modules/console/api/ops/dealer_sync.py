"""
运营后台：经销商同步任务 API
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.exceptions import BizException
from app.common.response import success
from app.modules.console.schemas.ops.dealer_sync import (
    DealerSyncTriggerBody,
    DealerSyncJobOut,
)
from app.modules.console.services.ops.dealer_sync_service import DealerSyncService
from app.modules.console.services.ops.dealer_sync_runner import schedule_dealer_sync_job

router = APIRouter()


@router.post("/trigger")
async def trigger_dealer_sync(
    body: DealerSyncTriggerBody,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await DealerSyncService.create_job(db, body)
    await db.commit()
    await schedule_dealer_sync_job(row.job_id)
    return success(data={"jobId": row.job_id})


@router.get("")
async def page_dealer_sync_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await DealerSyncService.page_jobs(db, page=page, limit=limit)
    return success(data=data)


@router.get("/{job_id}")
async def get_dealer_sync_job(
    job_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await DealerSyncService.get_job(db, job_id)
    if not row:
        raise BizException("任务不存在")
    return success(data=DealerSyncJobOut.from_row(row).model_dump())
