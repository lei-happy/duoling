"""
Console 平台经销商 API
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_platform_db, get_current_user
from app.core.security import TokenData
from app.common.response import success
from app.modules.console.schemas.basicdata.dealer import (
    DealerCreate,
    DealerUpdate,
    DealerOut,
)
from app.modules.console.services.basicdata.dealer_service import DealerService

router = APIRouter()


@router.get("")
async def page_dealers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    data = await DealerService.page_dealers(
        db, page=page, limit=limit, keyword=keyword
    )
    return success(data=data)


@router.get("/{dealer_id}")
async def get_dealer(
    dealer_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    item = await DealerService.get_dealer(db, dealer_id)
    return success(data=item.model_dump())


@router.post("")
async def create_dealer(
    data: DealerCreate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await DealerService.create_dealer(db, data)
    await db.flush()
    await db.refresh(row)
    payload = DealerOut.from_model(row).model_dump()
    return success(data=payload)


@router.put("/{dealer_id}")
async def update_dealer(
    dealer_id: int,
    data: DealerUpdate,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    row = await DealerService.update_dealer(db, dealer_id, data)
    await db.flush()
    await db.refresh(row)
    payload = DealerOut.from_model(row).model_dump()
    return success(data=payload)


@router.delete("/{dealer_id}")
async def delete_dealer(
    dealer_id: int,
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await DealerService.delete_dealer(db, dealer_id)
    return success()
