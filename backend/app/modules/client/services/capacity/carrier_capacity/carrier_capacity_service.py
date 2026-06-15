"""
承运商运力建档服务（CRUD）

首版聚焦「建档 + 证照监控 + 调度可用」：创建即生效，不走多级审批
（approval_status=2 / status=1）。后续可对接审批中心补充提交/审核流程。
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.carrier_capacity.carrier_capacity import (
    CarrierCapacity,
)
from app.modules.client.models.capacity.carrier_capacity.carrier_capacity_driver import (
    CarrierCapacityDriver,
)
from app.modules.client.models.capacity.carrier_capacity.carrier_capacity_vehicle import (
    CarrierCapacityVehicle,
)
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.schemas.capacity.carrier_capacity.carrier_capacity import (
    CarrierCapacityCreate,
    CarrierCapacityDetail,
    CarrierCapacityDriverInfo,
    CarrierCapacityListItem,
    CarrierCapacityUpdate,
    CarrierCapacityVehicleInfo,
)


def _vehicle_kwargs(info: CarrierCapacityVehicleInfo) -> dict:
    return {
        "plate_number": info.plateNumber,
        "plate_category": info.plateCategory or "YELLOW",
        "vehicle_type": info.vehicleType,
        "brand": info.brand,
        "model": info.model,
        "color": info.color,
        "vin": info.vin,
        "engine_no": info.engineNo,
        "load_capacity": info.loadCapacity,
        "volume_capacity": info.volumeCapacity,
        "length": info.length,
        "width": info.width,
        "height": info.height,
        "axle_count": info.axleCount,
        "has_trailer": info.hasTrailer or 0,
        "trailer_plate": info.trailerPlate,
        "trailer_type": info.trailerType,
        "trailer_load_capacity": info.trailerLoadCapacity,
        "registration_date": info.registrationDate,
        "inspection_expire": info.inspectionExpire,
        "insurance_expire": info.insuranceExpire,
        "transport_license_no": info.transportLicenseNo,
        "transport_license_expire": info.transportLicenseExpire,
        "vehicle_license_photo": info.vehicleLicensePhoto,
        "vehicle_license_back_photo": info.vehicleLicenseBackPhoto,
        "transport_license_photo": info.transportLicensePhoto,
        "vehicle_photo": info.vehiclePhoto,
    }


def _driver_kwargs(info: CarrierCapacityDriverInfo) -> dict:
    return {
        "name": info.name,
        "gender": info.gender or 0,
        "phone": info.phone,
        "id_card": info.idCard,
        "birth_date": info.birthDate,
        "avatar": info.avatar,
        "license_type": info.licenseType,
        "license_no": info.licenseNo,
        "license_issue_date": info.licenseIssueDate,
        "license_expire": info.licenseExpire,
        "license_class": info.licenseClass,
        "qualification_no": info.qualificationNo,
        "qualification_expire": info.qualificationExpire,
        "license_photo": info.licensePhoto,
        "qualification_photo": info.qualificationPhoto,
        "id_card_front_photo": info.idCardFrontPhoto,
        "id_card_back_photo": info.idCardBackPhoto,
        "emergency_contact": info.emergencyContact,
        "emergency_phone": info.emergencyPhone,
        "home_address": info.homeAddress,
    }


def _vehicle_info(v: CarrierCapacityVehicle) -> CarrierCapacityVehicleInfo:
    return CarrierCapacityVehicleInfo(
        plateNumber=v.plate_number,
        plateCategory=v.plate_category,
        vehicleType=v.vehicle_type,
        brand=v.brand,
        model=v.model,
        color=v.color,
        vin=v.vin,
        engineNo=v.engine_no,
        loadCapacity=float(v.load_capacity) if v.load_capacity is not None else None,
        volumeCapacity=float(v.volume_capacity) if v.volume_capacity is not None else None,
        length=float(v.length) if v.length is not None else None,
        width=float(v.width) if v.width is not None else None,
        height=float(v.height) if v.height is not None else None,
        axleCount=v.axle_count,
        hasTrailer=v.has_trailer,
        trailerPlate=v.trailer_plate,
        trailerType=v.trailer_type,
        trailerLoadCapacity=float(v.trailer_load_capacity)
        if v.trailer_load_capacity is not None
        else None,
        registrationDate=v.registration_date,
        inspectionExpire=v.inspection_expire,
        insuranceExpire=v.insurance_expire,
        transportLicenseNo=v.transport_license_no,
        transportLicenseExpire=v.transport_license_expire,
        vehicleLicensePhoto=v.vehicle_license_photo,
        vehicleLicenseBackPhoto=v.vehicle_license_back_photo,
        transportLicensePhoto=v.transport_license_photo,
        vehiclePhoto=v.vehicle_photo,
    )


def _driver_info(d: CarrierCapacityDriver) -> CarrierCapacityDriverInfo:
    return CarrierCapacityDriverInfo(
        name=d.name,
        gender=d.gender,
        phone=d.phone,
        idCard=d.id_card,
        birthDate=d.birth_date,
        avatar=d.avatar,
        licenseType=d.license_type,
        licenseNo=d.license_no,
        licenseIssueDate=d.license_issue_date,
        licenseExpire=d.license_expire,
        licenseClass=d.license_class,
        qualificationNo=d.qualification_no,
        qualificationExpire=d.qualification_expire,
        licensePhoto=d.license_photo,
        qualificationPhoto=d.qualification_photo,
        idCardFrontPhoto=d.id_card_front_photo,
        idCardBackPhoto=d.id_card_back_photo,
        emergencyContact=d.emergency_contact,
        emergencyPhone=d.emergency_phone,
        homeAddress=d.home_address,
    )


class CarrierCapacityService:
    """承运商运力建档"""

    @staticmethod
    async def _generate_code(db: AsyncSession) -> str:
        year = datetime.now().year
        prefix = f"C{year}"
        cnt = (
            await db.execute(
                select(func.count())
                .select_from(CarrierCapacity)
                .where(CarrierCapacity.carrier_capacity_code.like(f"{prefix}%"))
            )
        ).scalar() or 0
        return f"{prefix}{cnt + 1:05d}"

    @staticmethod
    async def _load_carrier(db: AsyncSession, carrier_id: int) -> Carrier:
        carrier = (
            await db.execute(
                select(Carrier).where(
                    Carrier.id == carrier_id,
                    Carrier.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if carrier is None:
            raise BizException("承运商不存在或已删除")
        return carrier

    @staticmethod
    async def _check_unique(
        db: AsyncSession,
        *,
        phone: str,
        plate: str,
        exclude_id: Optional[int] = None,
    ) -> None:
        for field, value, label in (
            (CarrierCapacity.driver_phone, phone, "手机号"),
            (CarrierCapacity.plate_number, plate, "车牌号"),
        ):
            conds = [
                field == value,
                CarrierCapacity.is_deleted == 0,
                CarrierCapacity.approval_status != 3,
            ]
            if exclude_id is not None:
                conds.append(CarrierCapacity.id != exclude_id)
            exists = (
                await db.execute(
                    select(CarrierCapacity.id).where(*conds).limit(1)
                )
            ).scalar_one_or_none()
            if exists is not None:
                raise BizException(f"该{label}已存在承运商运力档案")

    @staticmethod
    async def create(
        db: AsyncSession, data: CarrierCapacityCreate, user_id: Optional[int]
    ) -> CarrierCapacityDetail:
        carrier = await CarrierCapacityService._load_carrier(db, data.carrierId)
        await CarrierCapacityService._check_unique(
            db, phone=data.driver.phone, plate=data.vehicle.plateNumber
        )

        code = await CarrierCapacityService._generate_code(db)
        cc = CarrierCapacity(
            carrier_capacity_code=code,
            carrier_id=carrier.id,
            carrier_name=carrier.carrier_name,
            driver_name=data.driver.name,
            driver_phone=data.driver.phone,
            driver_id_card=data.driver.idCard,
            plate_number=data.vehicle.plateNumber,
            vehicle_type_label=data.vehicle.vehicleType,
            source=data.source,
            source_remark=data.sourceRemark,
            remark=data.remark,
            approval_status=2,
            status=1,
            created_user_id=user_id,
            updated_user_id=user_id,
        )
        db.add(cc)
        await db.flush()

        db.add(
            CarrierCapacityVehicle(
                carrier_capacity_id=cc.id, **_vehicle_kwargs(data.vehicle)
            )
        )
        db.add(
            CarrierCapacityDriver(
                carrier_capacity_id=cc.id, **_driver_kwargs(data.driver)
            )
        )
        await db.commit()
        return await CarrierCapacityService.get_detail(db, cc.id)

    @staticmethod
    async def page(
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        keyword: Optional[str] = None,
        carrier_id: Optional[int] = None,
        status: Optional[int] = None,
    ) -> dict:
        conds = [CarrierCapacity.is_deleted == 0]
        if carrier_id is not None:
            conds.append(CarrierCapacity.carrier_id == carrier_id)
        if status is not None:
            conds.append(CarrierCapacity.status == status)
        if keyword:
            like = f"%{keyword}%"
            conds.append(
                CarrierCapacity.driver_name.like(like)
                | CarrierCapacity.driver_phone.like(like)
                | CarrierCapacity.plate_number.like(like)
                | CarrierCapacity.carrier_name.like(like)
            )

        total = (
            await db.execute(
                select(func.count()).select_from(CarrierCapacity).where(*conds)
            )
        ).scalar() or 0
        rows = (
            await db.execute(
                select(CarrierCapacity)
                .where(*conds)
                .order_by(CarrierCapacity.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()

        items = [
            CarrierCapacityListItem(
                id=r.id,
                carrierCapacityCode=r.carrier_capacity_code,
                carrierId=r.carrier_id,
                carrierName=r.carrier_name,
                driverName=r.driver_name,
                driverPhone=r.driver_phone,
                plateNumber=r.plate_number,
                vehicleTypeLabel=r.vehicle_type_label,
                approvalStatus=r.approval_status,
                status=r.status,
                createdAt=r.created_at,
            ).model_dump()
            for r in rows
        ]
        return {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_detail(db: AsyncSession, cc_id: int) -> CarrierCapacityDetail:
        cc = (
            await db.execute(
                select(CarrierCapacity).where(
                    CarrierCapacity.id == cc_id,
                    CarrierCapacity.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if cc is None:
            raise BizException("承运商运力档案不存在")
        vehicle = (
            await db.execute(
                select(CarrierCapacityVehicle).where(
                    CarrierCapacityVehicle.carrier_capacity_id == cc_id,
                    CarrierCapacityVehicle.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        driver = (
            await db.execute(
                select(CarrierCapacityDriver).where(
                    CarrierCapacityDriver.carrier_capacity_id == cc_id,
                    CarrierCapacityDriver.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        return CarrierCapacityDetail(
            id=cc.id,
            carrierCapacityCode=cc.carrier_capacity_code,
            carrierId=cc.carrier_id,
            carrierName=cc.carrier_name,
            driverName=cc.driver_name,
            driverPhone=cc.driver_phone,
            driverIdCard=cc.driver_id_card,
            plateNumber=cc.plate_number,
            vehicleTypeLabel=cc.vehicle_type_label,
            source=cc.source,
            sourceRemark=cc.source_remark,
            approvalStatus=cc.approval_status,
            status=cc.status,
            statusRemark=cc.status_remark,
            remark=cc.remark,
            createdAt=cc.created_at,
            vehicle=_vehicle_info(vehicle) if vehicle else None,
            driver=_driver_info(driver) if driver else None,
        )

    @staticmethod
    async def update(
        db: AsyncSession,
        cc_id: int,
        data: CarrierCapacityUpdate,
        user_id: Optional[int],
    ) -> CarrierCapacityDetail:
        cc = (
            await db.execute(
                select(CarrierCapacity).where(
                    CarrierCapacity.id == cc_id,
                    CarrierCapacity.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if cc is None:
            raise BizException("承运商运力档案不存在")

        if data.carrierId is not None and data.carrierId != cc.carrier_id:
            carrier = await CarrierCapacityService._load_carrier(db, data.carrierId)
            cc.carrier_id = carrier.id
            cc.carrier_name = carrier.carrier_name

        new_phone = data.driver.phone if data.driver else cc.driver_phone
        new_plate = data.vehicle.plateNumber if data.vehicle else cc.plate_number
        await CarrierCapacityService._check_unique(
            db, phone=new_phone, plate=new_plate, exclude_id=cc_id
        )

        if data.source is not None:
            cc.source = data.source
        if data.sourceRemark is not None:
            cc.source_remark = data.sourceRemark
        if data.remark is not None:
            cc.remark = data.remark

        if data.vehicle is not None:
            cc.plate_number = data.vehicle.plateNumber
            cc.vehicle_type_label = data.vehicle.vehicleType
            vehicle = (
                await db.execute(
                    select(CarrierCapacityVehicle).where(
                        CarrierCapacityVehicle.carrier_capacity_id == cc_id,
                        CarrierCapacityVehicle.is_deleted == 0,
                    )
                )
            ).scalar_one_or_none()
            kwargs = _vehicle_kwargs(data.vehicle)
            if vehicle is None:
                db.add(CarrierCapacityVehicle(carrier_capacity_id=cc_id, **kwargs))
            else:
                for k, v in kwargs.items():
                    setattr(vehicle, k, v)

        if data.driver is not None:
            cc.driver_name = data.driver.name
            cc.driver_phone = data.driver.phone
            cc.driver_id_card = data.driver.idCard
            driver = (
                await db.execute(
                    select(CarrierCapacityDriver).where(
                        CarrierCapacityDriver.carrier_capacity_id == cc_id,
                        CarrierCapacityDriver.is_deleted == 0,
                    )
                )
            ).scalar_one_or_none()
            kwargs = _driver_kwargs(data.driver)
            if driver is None:
                db.add(CarrierCapacityDriver(carrier_capacity_id=cc_id, **kwargs))
            else:
                for k, v in kwargs.items():
                    setattr(driver, k, v)

        cc.updated_user_id = user_id
        await db.commit()
        return await CarrierCapacityService.get_detail(db, cc_id)

    @staticmethod
    async def update_status(
        db: AsyncSession, cc_id: int, status: int, status_remark: Optional[str]
    ) -> None:
        cc = (
            await db.execute(
                select(CarrierCapacity).where(
                    CarrierCapacity.id == cc_id,
                    CarrierCapacity.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if cc is None:
            raise BizException("承运商运力档案不存在")
        cc.status = status
        cc.status_remark = status_remark
        await db.commit()

    @staticmethod
    async def delete(db: AsyncSession, cc_id: int) -> None:
        cc = (
            await db.execute(
                select(CarrierCapacity).where(
                    CarrierCapacity.id == cc_id,
                    CarrierCapacity.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if cc is None:
            raise BizException("承运商运力档案不存在")
        cc.is_deleted = 1
        await db.commit()
