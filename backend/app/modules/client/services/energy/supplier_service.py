"""能源供应商 / 站点"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.product import EnergyProduct
from app.modules.client.models.energy.station import EnergyStation
from app.modules.client.models.energy.station_product import EnergyStationProduct
from app.modules.client.models.energy.supplier import EnergySupplier
from app.modules.client.schemas.energy.supplier import (
    EnergyStationCreate,
    EnergyStationOut,
    EnergyStationProductIn,
    EnergyStationProductOut,
    EnergyStationUpdate,
    EnergySupplierCreate,
    EnergySupplierOut,
    EnergySupplierUpdate,
)
from app.modules.client.services.energy.code_util import next_code
from app.modules.client.services.energy.constants import ENERGY_TYPE_UNITS, ENERGY_TYPES


_ENERGY_TYPE_VALUES = {x["value"] for x in ENERGY_TYPES}


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
        rows = list((await db.execute(
            stmt.order_by(EnergySupplier.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all())
        counts: dict[int, int] = {}
        if rows:
            for sid, cnt in (await db.execute(
                select(EnergyStation.supplier_id, func.count()).where(
                    EnergyStation.supplier_id.in_([r.id for r in rows]),
                    EnergyStation.is_deleted == 0,
                ).group_by(EnergyStation.supplier_id)
            )).all():
                counts[int(sid)] = int(cnt)
        return {
            "list": [
                EnergySupplierOut.from_model(x, station_count=counts.get(x.id, 0)).model_dump()
                for x in rows
            ],
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
        name = (data.supplierName or "").strip()
        if not name:
            raise BizException("请填写供应商名称")
        code = (data.supplierCode or "").strip() or await next_code(
            db, EnergySupplier, "supplier_code", "ES"
        )
        exists = (await db.execute(
            select(EnergySupplier.id).where(EnergySupplier.supplier_code == code)
        )).scalar_one_or_none()
        if exists:
            raise BizException("供应商编码已存在")
        obj = EnergySupplier(
            supplier_code=code,
            supplier_name=name,
            supplier_type=data.supplierType,
            contact_name=data.contactName,
            contact_phone=data.contactPhone,
            remark=data.remark,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
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
    async def page(
        db, page=1, page_size=20, supplier_id=None, keyword=None, energy_type=None,
    ):
        stmt = select(EnergyStation).where(EnergyStation.is_deleted == 0)
        if supplier_id:
            stmt = stmt.where(EnergyStation.supplier_id == supplier_id)
        if keyword:
            stmt = stmt.where(
                (EnergyStation.station_code.contains(keyword))
                | (EnergyStation.station_name.contains(keyword))
                | (EnergyStation.address.contains(keyword))
            )
        if energy_type:
            stmt = stmt.where(EnergyStation.id.in_(
                select(EnergyStationProduct.station_id).where(
                    EnergyStationProduct.is_deleted == 0,
                    EnergyStationProduct.energy_type == energy_type,
                )
            ))
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = list((await db.execute(
            stmt.order_by(EnergyStation.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all())
        return {
            "list": await EnergyStationService._dump_rows(db, rows),
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
    async def detail(db: AsyncSession, sid: int) -> dict:
        obj = await EnergyStationService.get(db, sid)
        dumped = await EnergyStationService._dump_rows(db, [obj])
        return dumped[0]

    @staticmethod
    async def create(db: AsyncSession, data: EnergyStationCreate) -> EnergyStation:
        await EnergySupplierService.get(db, data.supplierId)
        code = (data.stationCode or "").strip()
        name = (data.stationName or "").strip()
        if not code:
            raise BizException("请填写站点编码")
        if not name:
            raise BizException("请填写站点名称")
        EnergyStationService._assert_lng_lat(data.longitude, data.latitude)
        exists = (await db.execute(
            select(EnergyStation.id).where(
                EnergyStation.supplier_id == data.supplierId,
                EnergyStation.station_code == code,
            )
        )).scalar_one_or_none()
        if exists:
            raise BizException("该供应商下站点编码已存在")
        obj = EnergyStation(
            supplier_id=data.supplierId,
            station_code=code,
            station_name=name,
            address=data.address,
            longitude=data.longitude,
            latitude=data.latitude,
            remark=data.remark,
        )
        db.add(obj)
        await db.flush()
        await EnergyStationService._replace_products(db, obj.id, data.products or [])
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, sid: int, data: EnergyStationUpdate) -> EnergyStation:
        obj = await EnergyStationService.get(db, sid)
        payload = data.model_dump(exclude_unset=True)
        EnergyStationService._assert_lng_lat(
            payload.get("longitude", obj.longitude),
            payload.get("latitude", obj.latitude),
        )
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
        if "products" in payload:
            await EnergyStationService._replace_products(db, obj.id, data.products or [])
        await db.flush()
        return obj

    @staticmethod
    async def delete(db: AsyncSession, sid: int) -> None:
        obj = await EnergyStationService.get(db, sid)
        obj.is_deleted = 1
        rows = (await db.execute(
            select(EnergyStationProduct).where(
                EnergyStationProduct.station_id == sid,
                EnergyStationProduct.is_deleted == 0,
            )
        )).scalars().all()
        for row in rows:
            row.is_deleted = 1
        await db.flush()

    @staticmethod
    def _assert_lng_lat(lng, lat) -> None:
        if lng is not None and not (Decimal("-180") <= Decimal(lng) <= Decimal("180")):
            raise BizException("经度应在 -180 到 180 之间")
        if lat is not None and not (Decimal("-90") <= Decimal(lat) <= Decimal("90")):
            raise BizException("纬度应在 -90 到 90 之间")

    @staticmethod
    async def _replace_products(
        db: AsyncSession, station_id: int, items: list[EnergyStationProductIn],
    ) -> None:
        seen: set[tuple[str, int]] = set()
        normalized: list[dict] = []
        for item in items:
            energy_type = (item.energyType or "").strip().upper()
            if energy_type not in _ENERGY_TYPE_VALUES:
                raise BizException("请选择正确的能源类型")
            if item.settlementPrice is None or Decimal(item.settlementPrice) <= 0:
                raise BizException("结算价必须大于 0")
            product_id = int(item.productId or 0)
            product_name = (item.productName or "").strip() or None
            unit = (item.unit or "").strip() or ENERGY_TYPE_UNITS.get(energy_type, "")
            if product_id:
                prod = (await db.execute(
                    select(EnergyProduct).where(
                        EnergyProduct.id == product_id, EnergyProduct.is_deleted == 0,
                    )
                )).scalar_one_or_none()
                if prod is None:
                    raise BizException("能源商品不存在，请先在能源设置里维护")
                energy_type = prod.energy_type
                product_name = prod.product_name
                unit = prod.standard_unit or unit
            key = (energy_type, product_id)
            if key in seen:
                raise BizException("同一站点下同一商品只能有一条结算价")
            seen.add(key)
            normalized.append({
                "energy_type": energy_type,
                "product_id": product_id,
                "product_name": product_name,
                "settlement_price": Decimal(item.settlementPrice),
                "unit": unit or ENERGY_TYPE_UNITS.get(energy_type, "L"),
            })

        existed = list((await db.execute(
            select(EnergyStationProduct).where(
                EnergyStationProduct.station_id == station_id,
            )
        )).scalars().all())
        by_key = {(r.energy_type, int(r.product_id or 0)): r for r in existed}
        keep: set[tuple[str, int]] = set()
        for item in normalized:
            key = (item["energy_type"], item["product_id"])
            keep.add(key)
            row = by_key.get(key)
            if row is None:
                db.add(EnergyStationProduct(station_id=station_id, **item))
                continue
            row.is_deleted = 0
            row.product_name = item["product_name"]
            row.settlement_price = item["settlement_price"]
            row.unit = item["unit"]
            row.status = 1
        for key, row in by_key.items():
            if key not in keep:
                row.is_deleted = 1
        await db.flush()

    @staticmethod
    async def _dump_rows(db: AsyncSession, rows: list[EnergyStation]) -> list[dict]:
        if not rows:
            return []
        names: dict[int, str] = {}
        for s in (await db.execute(
            select(EnergySupplier).where(EnergySupplier.id.in_({r.supplier_id for r in rows}))
        )).scalars().all():
            names[s.id] = s.supplier_name
        products_by_station: dict[int, list[EnergyStationProductOut]] = {r.id: [] for r in rows}
        for p in (await db.execute(
            select(EnergyStationProduct).where(
                EnergyStationProduct.station_id.in_([r.id for r in rows]),
                EnergyStationProduct.is_deleted == 0,
            ).order_by(EnergyStationProduct.id)
        )).scalars().all():
            products_by_station.setdefault(p.station_id, []).append(
                EnergyStationProductOut(
                    id=p.id,
                    energyType=p.energy_type,
                    productId=p.product_id or None,
                    productName=p.product_name,
                    settlementPrice=p.settlement_price,
                    unit=p.unit,
                )
            )
        return [
            EnergyStationOut.from_model(
                r,
                supplier_name=names.get(r.supplier_id),
                products=products_by_station.get(r.id, []),
            ).model_dump()
            for r in rows
        ]
