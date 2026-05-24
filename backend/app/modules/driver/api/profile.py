"""驾驶员个人中心接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.driver.schemas.profile import (
    DriverProfileOut,
    DriverProfileUpdate,
)
from app.modules.driver.services.driver_context import get_current_driver

router = APIRouter()


@router.get("/me", summary="我的资料")
async def get_my_profile(
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    d = ctx.driver
    return success(
        data=DriverProfileOut(
            id=int(d.id),
            driverCode=d.driver_code,
            name=d.name,
            phone=d.phone,
            gender=int(d.gender or 0),
            avatar=d.avatar,
            idCard=d.id_card,
            emergencyContact=d.emergency_contact,
            emergencyPhone=d.emergency_phone,
            homeAddress=d.home_address,
            status=int(d.status),
            remark=d.remark,
        ).model_dump()
    )


@router.put("/me", summary="更新个人资料（白名单字段）")
async def update_my_profile(
    payload: DriverProfileUpdate,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    ctx = await get_current_driver(tenant_db, current_user)
    d = ctx.driver

    if payload.emergencyContact is not None:
        d.emergency_contact = payload.emergencyContact
    if payload.emergencyPhone is not None:
        d.emergency_phone = payload.emergencyPhone
    if payload.homeAddress is not None:
        d.home_address = payload.homeAddress
    if payload.avatar is not None:
        d.avatar = payload.avatar

    await tenant_db.commit()
    await tenant_db.refresh(d)

    return success(
        data=DriverProfileOut(
            id=int(d.id),
            driverCode=d.driver_code,
            name=d.name,
            phone=d.phone,
            gender=int(d.gender or 0),
            avatar=d.avatar,
            idCard=d.id_card,
            emergencyContact=d.emergency_contact,
            emergencyPhone=d.emergency_phone,
            homeAddress=d.home_address,
            status=int(d.status),
            remark=d.remark,
        ).model_dump()
    )
