"""
驾驶员管理服务（租户库）
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.driver import Driver
from app.modules.client.schemas.driver import (
    DriverCreate, DriverUpdate, DriverOut,
)


class DriverService:

    @staticmethod
    async def page_drivers(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        license_type: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(Driver).where(Driver.is_deleted == 0)

        if keyword:
            base = base.where(
                (Driver.name.contains(keyword)) |
                (Driver.phone.contains(keyword))
            )
        if license_type:
            base = base.where(Driver.license_type == license_type)
        if status is not None:
            base = base.where(Driver.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Driver.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [DriverOut.from_model(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create_driver(
        db: AsyncSession, data: DriverCreate
    ) -> Driver:
        existing = await db.execute(
            select(Driver).where(
                Driver.phone == data.phone,
                Driver.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"手机号 {data.phone} 已存在")

        driver = Driver(
            user_id=data.userId,
            name=data.name,
            phone=data.phone,
            id_card=data.idCard,
            gender=data.gender,
            license_type=data.licenseType,
            license_no=data.licenseNo,
            license_expire=data.licenseExpire,
            qualification_no=data.qualificationNo,
            qualification_expire=data.qualificationExpire,
            emergency_contact=data.emergencyContact,
            emergency_phone=data.emergencyPhone,
            avatar=data.avatar,
            remark=data.remark,
        )
        db.add(driver)
        await db.flush()
        return driver

    @staticmethod
    async def update_driver(
        db: AsyncSession, driver_id: int, data: DriverUpdate
    ) -> Driver:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        driver = result.scalar_one_or_none()
        if not driver:
            raise BizException("驾驶员不存在")

        field_map = {
            "userId": "user_id",
            "name": "name",
            "phone": "phone",
            "idCard": "id_card",
            "gender": "gender",
            "licenseType": "license_type",
            "licenseNo": "license_no",
            "licenseExpire": "license_expire",
            "qualificationNo": "qualification_no",
            "qualificationExpire": "qualification_expire",
            "emergencyContact": "emergency_contact",
            "emergencyPhone": "emergency_phone",
            "avatar": "avatar",
            "status": "status",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(driver, model_field, val)

        await db.flush()
        return driver

    @staticmethod
    async def delete_driver(db: AsyncSession, driver_id: int) -> None:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        driver = result.scalar_one_or_none()
        if not driver:
            raise BizException("驾驶员不存在")
        driver.is_deleted = 1
        await db.flush()
