from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.services.energy.exception_service import EnergyExceptionService

router = APIRouter()


class ResolveIn(BaseModel):
    status: str
    remark: Optional[str] = None


@router.get("")
async def page_exceptions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    status: Optional[str] = None,
    exceptionType: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyExceptionService.page(
        db, page, page_size, status, exceptionType,
    ))


@router.get("/stats")
async def stats(
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyExceptionService.stats(db))


@router.post("/{eid}/resolve")
@operation_log(module="能源异常", action="处理", description="处理能源异常")
async def resolve(
    eid: int,
    data: ResolveIn,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    await EnergyExceptionService.resolve(
        db, eid, data.status, data.remark or "", processor_id=current_user.user_id,
    )
    return success()
