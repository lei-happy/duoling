from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.modules.client.schemas.energy.card import (
    EnergyCardBindIn,
    EnergyCardCreate,
    EnergyCardOut,
    EnergyCardUpdate,
)
from app.modules.client.services.energy.card_service import EnergyCardService

router = APIRouter()


@router.get("")
async def page_cards(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    accountId: Optional[int] = None,
    status: Optional[int] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    return success(data=await EnergyCardService.page(
        db, page, page_size, keyword, accountId, status,
    ))


@router.post("")
@operation_log(module="能源卡", action="新增", description="新增能源卡")
async def create_card(
    data: EnergyCardCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyCardService.create(db, data)
    return success(data=EnergyCardOut.from_model(obj).model_dump())


@router.put("/{cid}")
@operation_log(module="能源卡", action="编辑", description="编辑能源卡")
async def update_card(
    cid: int,
    data: EnergyCardUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    obj = await EnergyCardService.update(db, cid, data)
    return success(data=EnergyCardOut.from_model(obj).model_dump())


@router.delete("/{cid}")
@operation_log(module="能源卡", action="删除", description="删除能源卡")
async def delete_card(
    cid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyCardService.delete(db, cid)
    return success()


@router.post("/{cid}/bind")
@operation_log(module="能源卡", action="绑定", description="能源卡绑定车辆/司机")
async def bind_card(
    cid: int,
    data: EnergyCardBindIn,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyCardService.bind(db, cid, data)
    return success()


@router.post("/{cid}/unbind")
@operation_log(module="能源卡", action="解绑", description="能源卡解绑")
async def unbind_card(
    cid: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await EnergyCardService.unbind(db, cid)
    return success()
