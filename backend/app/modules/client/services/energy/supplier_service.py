"""能源供应商 / 站点"""

from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.station import EnergyStation
from app.modules.client.models.energy.supplier import EnergySupplier
from app.modules.client.schemas.energy.supplier import (
    EnergyStationCreate,
    EnergyStationOut,
    EnergyStationUpdate,
    EnergySupplierCreate,
    EnergySupplierOut,
    EnergySupplierUpdate,
)
from app.modules.client.services.energy.code_util import next_code


class EnergySupplierService:

    @staticmethod
    async def page(db: AsyncSession, page=1, page_size=20, keyword=None, supplier_type=None, status=None):
        stmt = select(EnergySupplier).where(EnergySupplier.is_deleted == 0)
        if keyword:
            stmt = stmt.where(
                (EnergySupplier.supplier_code.contains(keyword))
                | (EnergySupplier.supplier_name.contains(keyword))
            )
        if supplier_type is not None:
            stmt = stmt.where(EnergySupplier.supplier_type == supplier_type)
        if status is not None:
            stmt = stmt.where(EnergySupplier.status == status)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = (await db.execute(
            stmt.order_by(EnergySupplier.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return {
            "list": [EnergySupplierOut.from_model(x).model_dump() for x in rows],
            "count": total,
        }

    @staticmethod
    async def get(db: AsyncSession, sid: int) -> EnergySupplier:
        r = await db.execute(
            select(EnergySupplier).where(EnergySupplier.id == sid, EnergySupplier.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("供应商不存在")
        return obj

    @staticmethod
    async def create(db: AsyncSession, data: EnergySupplierCreate) -> EnergySupplier:
        code = (data.supplierCode or "").strip() or await next_code(
            db, EnergySupplier, "supplier_code", "ES"
        )
        exists = (await db.execute(
            select(EnergySupplier.id).where(
                EnergySupplier.supplier_code == code, EnergySupplier.is_deleted == 0
            )
        )).scalar_one_or_none()
        if exists:
            raise BizException("供应商编码已存在")
        obj = EnergySupplier(
            supplier_code=code,
            supplier_name=data.supplierName.strip(),
            supplier_type=data.supplierType,
            contact_name=data.contactName,
            contact_phone=data.contactPhone,
            remark=data.remark,
        )
        db.add(obj)
        await db.flush()
        return obj

    @staticmethod
    async def update(db: AsyncSession, sid: int, data: EnergySupplierUpdate) -> EnergySupplier:
        obj = await EnergySupplierService.get(db, sid)
        payload = data.model_dump(exclude_unset=True)
        mapping = {
            "supplierName": "supplier_name",
            "supplierType": "supplier_type",
            "status": "status",
            "contactName": "contact_name",
            "contactPhone": "contact_phone",
            "remark": "remark",
        }
        for k, col in mapping.items():
            if k in payload:
                setattr(obj, col, payload[k])
        await db.flush()
        return obj

    @staticmethod
    async def delete(db: AsyncSession, sid: int) -> None:
        obj = await EnergySupplierService.get(db, sid)
        obj.is_deleted = 1
        await db.flush()


class EnergyStationService:

    @staticmethod
    async def page(db: AsyncSession, page=1, page_size=20, supplier_id=None, keyword=None):
        stmt = select(EnergyStation).where(EnergyStation.is_deleted == 0)
        if supplier_id:
            stmt = stmt.where(EnergyStation.supplier_id == supplier_id)
        if keyword:
            stmt = stmt.where(
                (EnergyStation.station_code.contains(keyword))
                | (EnergyStation.station_name.contains(keyword))
            )
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = (await db.execute(
            stmt.order_by(EnergyStation.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return {
            "list": [EnergyStationOut.from_model(x).model_dump() for x in rows],
            "count": total,
        }

    @staticmethod
    async def get(db: AsyncSession, sid: int) -> EnergyStation:
        r = await db.execute(
            select(EnergyStation).where(EnergyStation.id == sid, EnergyStation.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("站点不存在")
        return obj

    @staticmethod
    async def create(db: AsyncSession, data: EnergyStationCreate) -> EnergyStation:
        await EnergySupplierService.get(db, data.supplierId)
        obj = EnergyStation(
            supplier_id=data.supplierId,
            station_code=data.stationCode.strip(),
            station_name=data.stationName.strip(),
            address=data.address,
            longitude=data.longitude,
            latitude=data.latitude,
            remark=data.remark,
        )
        db.add(obj)
        await db.flush()
        return obj

    @staticmethod
    async def update(db: AsyncSession, sid: int, data: EnergyStationUpdate) -> EnergyStation:
        obj = await EnergyStationService.get(db, sid)
        payload = data.model_dump(exclude_unset=True)
        mapping = {
            "stationName": "station_name",
            "address": "address",
            "longitude": "longitude",
            "latitude": "latitude",
            "status": "status",
            "remark": "remark",
        }
        for k, col in mapping.items():
            if k in payload:
                setattr(obj, col, payload[k])
        await db.flush()
        return obj

    @staticmethod
    async def delete(db: AsyncSession, sid: int) -> None:
        obj = await EnergyStationService.get(db, sid)
        obj.is_deleted = 1
        await db.flush()
