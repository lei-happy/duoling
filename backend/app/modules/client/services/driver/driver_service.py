"""
驾驶员管理服务（租户库）

核心表 + 资质表 + 运营表 三表联查、联写逻辑。
"""

from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.driver.driver import Driver
from app.modules.client.models.driver.driver_license import DriverLicense
from app.modules.client.models.driver.driver_operation import DriverOperation
from app.modules.client.models.driver.driver_account import DriverAccount
from app.modules.client.models.organization.biz_department import BizDepartment
from app.modules.client.schemas.driver.driver import (
    DriverCreate, DriverUpdate, DriverOut,
)


class DriverService:

    @staticmethod
    async def _generate_driver_code(db: AsyncSession) -> str:
        """生成司机编号：D + 年份(4位) + 序号(4位+)"""
        year = datetime.now().strftime("%Y")
        prefix = f"D{year}"

        result = await db.execute(
            select(func.count()).select_from(
                select(Driver.id)
                .where(Driver.driver_code.like(f"{prefix}%"))
                .subquery()
            )
        )
        count = (result.scalar() or 0) + 1
        return f"{prefix}{count:04d}"

    @staticmethod
    async def page_drivers(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        driver_type: Optional[int] = None,
        operation_status: Optional[int] = None,
        department_id: Optional[int] = None,
    ) -> dict:
        base = (
            select(
                Driver,
                DriverLicense,
                DriverOperation,
                BizDepartment.dept_name.label("dept_name"),
            )
            .outerjoin(DriverLicense, and_(
                DriverLicense.driver_id == Driver.id,
                DriverLicense.is_deleted == 0,
            ))
            .outerjoin(DriverOperation, and_(
                DriverOperation.driver_id == Driver.id,
                DriverOperation.is_deleted == 0,
            ))
            .outerjoin(BizDepartment, and_(
                BizDepartment.id == DriverOperation.department_id,
                BizDepartment.is_deleted == 0,
            ))
            .where(Driver.is_deleted == 0)
        )

        if keyword:
            base = base.where(
                (Driver.name.contains(keyword)) |
                (Driver.phone.contains(keyword)) |
                (Driver.driver_code.contains(keyword))
            )
        if status is not None:
            base = base.where(Driver.status == status)
        if driver_type is not None:
            base = base.where(DriverOperation.driver_type == driver_type)
        if operation_status is not None:
            base = base.where(DriverOperation.operation_status == operation_status)
        if department_id is not None:
            base = base.where(DriverOperation.department_id == department_id)

        count_base = (
            select(Driver.id)
            .outerjoin(DriverOperation, and_(
                DriverOperation.driver_id == Driver.id,
                DriverOperation.is_deleted == 0,
            ))
            .where(Driver.is_deleted == 0)
        )
        if keyword:
            count_base = count_base.where(
                (Driver.name.contains(keyword)) |
                (Driver.phone.contains(keyword)) |
                (Driver.driver_code.contains(keyword))
            )
        if status is not None:
            count_base = count_base.where(Driver.status == status)
        if driver_type is not None:
            count_base = count_base.where(DriverOperation.driver_type == driver_type)
        if operation_status is not None:
            count_base = count_base.where(DriverOperation.operation_status == operation_status)
        if department_id is not None:
            count_base = count_base.where(DriverOperation.department_id == department_id)

        count_q = select(func.count()).select_from(count_base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Driver.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.all()

        return {
            "list": [
                DriverOut.from_row(d, lic, op, dn).model_dump()
                for d, lic, op, dn in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_driver(db: AsyncSession, driver_id: int) -> DriverOut:
        result = await db.execute(
            select(
                Driver,
                DriverLicense,
                DriverOperation,
                BizDepartment.dept_name.label("dept_name"),
            )
            .outerjoin(DriverLicense, and_(
                DriverLicense.driver_id == Driver.id,
                DriverLicense.is_deleted == 0,
            ))
            .outerjoin(DriverOperation, and_(
                DriverOperation.driver_id == Driver.id,
                DriverOperation.is_deleted == 0,
            ))
            .outerjoin(BizDepartment, and_(
                BizDepartment.id == DriverOperation.department_id,
                BizDepartment.is_deleted == 0,
            ))
            .where(Driver.id == driver_id, Driver.is_deleted == 0)
        )
        row = result.one_or_none()
        if not row:
            raise BizException("驾驶员不存在")
        d, lic, op, dn = row
        return DriverOut.from_row(d, lic, op, dn)

    @staticmethod
    async def create_driver(
        db: AsyncSession, data: DriverCreate
    ) -> DriverOut:
        existing = await db.execute(
            select(Driver).where(
                Driver.phone == data.phone,
                Driver.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"手机号 {data.phone} 已存在")

        driver_code = await DriverService._generate_driver_code(db)

        driver = Driver(
            driver_code=driver_code,
            name=data.name,
            gender=data.gender or 0,
            phone=data.phone,
            id_card=data.idCard,
            avatar=data.avatar,
            emergency_contact=data.emergencyContact,
            emergency_phone=data.emergencyPhone,
            home_address=data.homeAddress,
            status=1,
            remark=data.remark,
        )
        db.add(driver)
        await db.flush()
        await db.refresh(driver)

        license_info = DriverLicense(
            driver_id=driver.id,
            license_type=data.licenseType,
            license_no=data.licenseNo,
            license_expire=data.licenseExpire,
            qualification_no=data.qualificationNo,
            qualification_expire=data.qualificationExpire,
            license_photo=data.licensePhoto,
            qualification_photo=data.qualificationPhoto,
            id_card_front_photo=data.idCardFrontPhoto,
            id_card_back_photo=data.idCardBackPhoto,
        )
        db.add(license_info)

        operation = DriverOperation(
            driver_id=driver.id,
            department_id=data.departmentId,
            driver_type=data.driverType,
            resident_areas=data.residentAreas,
            common_routes=data.commonRoutes,
            operation_status=data.operationStatus or 1,
        )
        db.add(operation)

        await db.flush()
        await db.refresh(license_info)
        await db.refresh(operation)

        dept_name = None
        if operation.department_id:
            r = await db.execute(
                select(BizDepartment.dept_name).where(
                    BizDepartment.id == operation.department_id
                )
            )
            dept_name = r.scalar_one_or_none()

        return DriverOut.from_row(driver, license_info, operation, dept_name)

    @staticmethod
    async def update_driver(
        db: AsyncSession, driver_id: int, data: DriverUpdate
    ) -> DriverOut:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        driver = result.scalar_one_or_none()
        if not driver:
            raise BizException("驾驶员不存在")

        update_data = data.model_dump(exclude_unset=True)

        core_fields = {
            "name": "name",
            "gender": "gender",
            "phone": "phone",
            "idCard": "id_card",
            "avatar": "avatar",
            "emergencyContact": "emergency_contact",
            "emergencyPhone": "emergency_phone",
            "homeAddress": "home_address",
            "status": "status",
            "remark": "remark",
        }
        for schema_f, model_f in core_fields.items():
            if schema_f in update_data:
                setattr(driver, model_f, update_data[schema_f])

        license_fields = {
            "licenseType": "license_type",
            "licenseNo": "license_no",
            "licenseExpire": "license_expire",
            "qualificationNo": "qualification_no",
            "qualificationExpire": "qualification_expire",
            "licensePhoto": "license_photo",
            "qualificationPhoto": "qualification_photo",
            "idCardFrontPhoto": "id_card_front_photo",
            "idCardBackPhoto": "id_card_back_photo",
        }
        has_license_update = any(k in update_data for k in license_fields)
        if has_license_update:
            lic_result = await db.execute(
                select(DriverLicense).where(
                    DriverLicense.driver_id == driver_id,
                    DriverLicense.is_deleted == 0,
                )
            )
            lic = lic_result.scalar_one_or_none()
            if not lic:
                lic = DriverLicense(driver_id=driver_id)
                db.add(lic)
                await db.flush()

            for schema_f, model_f in license_fields.items():
                if schema_f in update_data:
                    setattr(lic, model_f, update_data[schema_f])

        operation_fields = {
            "departmentId": "department_id",
            "driverType": "driver_type",
            "residentAreas": "resident_areas",
            "commonRoutes": "common_routes",
            "operationStatus": "operation_status",
        }
        has_op_update = any(k in update_data for k in operation_fields)
        if has_op_update:
            op_result = await db.execute(
                select(DriverOperation).where(
                    DriverOperation.driver_id == driver_id,
                    DriverOperation.is_deleted == 0,
                )
            )
            op = op_result.scalar_one_or_none()
            if not op:
                op = DriverOperation(driver_id=driver_id)
                db.add(op)
                await db.flush()

            for schema_f, model_f in operation_fields.items():
                if schema_f in update_data:
                    setattr(op, model_f, update_data[schema_f])

        await db.flush()
        return await DriverService.get_driver(db, driver_id)

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

        lic_result = await db.execute(
            select(DriverLicense).where(
                DriverLicense.driver_id == driver_id,
                DriverLicense.is_deleted == 0,
            )
        )
        lic = lic_result.scalar_one_or_none()
        if lic:
            lic.is_deleted = 1

        op_result = await db.execute(
            select(DriverOperation).where(
                DriverOperation.driver_id == driver_id,
                DriverOperation.is_deleted == 0,
            )
        )
        op = op_result.scalar_one_or_none()
        if op:
            op.is_deleted = 1

        acc_result = await db.execute(
            select(DriverAccount).where(
                DriverAccount.driver_id == driver_id,
                DriverAccount.is_deleted == 0,
            )
        )
        for acc in acc_result.scalars().all():
            acc.is_deleted = 1

        await db.flush()

    @staticmethod
    async def update_status(
        db: AsyncSession, driver_id: int, status: int
    ) -> DriverOut:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        driver = result.scalar_one_or_none()
        if not driver:
            raise BizException("驾驶员不存在")

        driver.status = status
        await db.flush()
        return await DriverService.get_driver(db, driver_id)

    @staticmethod
    async def update_operation_status(
        db: AsyncSession, driver_id: int, operation_status: int
    ) -> DriverOut:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        if not result.scalar_one_or_none():
            raise BizException("驾驶员不存在")

        op_result = await db.execute(
            select(DriverOperation).where(
                DriverOperation.driver_id == driver_id,
                DriverOperation.is_deleted == 0,
            )
        )
        op = op_result.scalar_one_or_none()
        if not op:
            op = DriverOperation(driver_id=driver_id, operation_status=operation_status)
            db.add(op)
        else:
            op.operation_status = operation_status

        await db.flush()
        return await DriverService.get_driver(db, driver_id)
