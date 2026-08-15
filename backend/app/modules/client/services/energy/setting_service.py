"""能源设置：商品、车辆档案、风控规则"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.product import EnergyProduct
from app.modules.client.models.energy.rule import EnergyRule
from app.modules.client.models.energy.vehicle_profile import EnergyVehicleProfile
from app.modules.client.services.energy.constants import (
    ENERGY_TYPE_UNITS,
    RULE_ABNORMAL_CONSUMPTION,
    RULE_ABNORMAL_PRICE,
    RULE_OVER_TANK,
    RULE_REPEAT_FILL,
    RULE_UNBOUND_VEHICLE,
)
from app.modules.client.services.energy.refs.master_data_resolver import MasterDataResolver


_DEFAULT_RULES = [
    (RULE_OVER_TANK, "超油箱容量", "1", "HIGH"),
    (RULE_REPEAT_FILL, "短时间重复加注", "120", "MEDIUM"),
    (RULE_ABNORMAL_PRICE, "异常单价", "0.15", "MEDIUM"),
    (RULE_ABNORMAL_CONSUMPTION, "异常油耗", "0.30", "MEDIUM"),
    (RULE_UNBOUND_VEHICLE, "未匹配车辆", None, "LOW"),
]


class EnergyProductService:

    @staticmethod
    async def list_all(db):
        rows = (await db.execute(
            select(EnergyProduct).where(EnergyProduct.is_deleted == 0)
            .order_by(EnergyProduct.energy_type, EnergyProduct.id)
        )).scalars().all()
        return [_product_out(x) for x in rows]

    @staticmethod
    async def create(db, data: dict) -> EnergyProduct:
        code = (data.get("productCode") or "").strip()
        if not code:
            raise BizException("请填写商品编码")
        exists = (await db.execute(
            select(EnergyProduct.id).where(EnergyProduct.product_code == code)
        )).scalar_one_or_none()
        if exists:
            raise BizException("商品编码已存在")
        energy_type = data.get("energyType") or "OIL"
        name = (data.get("productName") or "").strip()
        if not name:
            raise BizException("请填写商品名称")
        obj = EnergyProduct(
            energy_type=energy_type,
            product_code=code,
            product_name=name,
            standard_unit=data.get("standardUnit") or ENERGY_TYPE_UNITS.get(energy_type, "L"),
            remark=data.get("remark"),
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db, pid: int, data: dict) -> EnergyProduct:
        r = await db.execute(
            select(EnergyProduct).where(EnergyProduct.id == pid, EnergyProduct.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("能源商品不存在")
        for src, col in (
            ("productName", "product_name"),
            ("standardUnit", "standard_unit"),
            ("status", "status"),
            ("remark", "remark"),
        ):
            if src in data:
                setattr(obj, col, data[src])
        await db.flush()
        return obj

    @staticmethod
    async def delete(db, pid: int) -> None:
        r = await db.execute(
            select(EnergyProduct).where(EnergyProduct.id == pid, EnergyProduct.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("能源商品不存在")
        obj.is_deleted = 1
        await db.flush()


class EnergyVehicleProfileService:

    @staticmethod
    async def page(db, page=1, page_size=20, keyword=None):
        stmt = select(EnergyVehicleProfile).where(EnergyVehicleProfile.is_deleted == 0)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = (await db.execute(
            stmt.order_by(EnergyVehicleProfile.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return {"list": [_profile_out(x) for x in rows], "count": total}

    @staticmethod
    async def upsert(db, data: dict) -> EnergyVehicleProfile:
        vid = int(data["vehicleId"])
        v = await MasterDataResolver.get_vehicle_by_id(db, vid)
        if v is None:
            raise BizException("车辆不存在")
        existed = (await db.execute(
            select(EnergyVehicleProfile).where(
                EnergyVehicleProfile.vehicle_id == vid,
                EnergyVehicleProfile.is_deleted == 0,
            )
        )).scalar_one_or_none()
        obj = existed or EnergyVehicleProfile(vehicle_id=vid)
        obj.energy_type = data.get("energyType") or "OIL"
        obj.default_product_id = data.get("defaultProductId")
        obj.tank_capacity = data.get("tankCapacity")
        obj.battery_capacity = data.get("batteryCapacity")
        obj.standard_consumption_per_100km = data.get("standardConsumptionPer100km")
        obj.remark = data.get("remark")
        if existed is None:
            db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj


class EnergyRuleService:

    @staticmethod
    async def list_all(db):
        rows = list((await db.execute(
            select(EnergyRule).where(EnergyRule.is_deleted == 0).order_by(EnergyRule.id)
        )).scalars().all())
        if not rows:
            rows = await EnergyRuleService.ensure_defaults(db)
        return [_rule_out(x) for x in rows]

    @staticmethod
    async def ensure_defaults(db) -> list[EnergyRule]:
        created = []
        for code, name, threshold, level in _DEFAULT_RULES:
            obj = EnergyRule(
                rule_code=code, rule_name=name,
                threshold_value=threshold, risk_level=level, status=1,
            )
            db.add(obj)
            created.append(obj)
        await db.flush()
        return created

    @staticmethod
    async def update(db, rid: int, data: dict) -> EnergyRule:
        r = await db.execute(
            select(EnergyRule).where(EnergyRule.id == rid, EnergyRule.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("风控规则不存在")
        for src, col in (
            ("thresholdValue", "threshold_value"),
            ("riskLevel", "risk_level"),
            ("status", "status"),
            ("remark", "remark"),
        ):
            if src in data:
                setattr(obj, col, data[src])
        await db.flush()
        return obj


def _product_out(m) -> dict:
    return {
        "id": m.id,
        "energyType": m.energy_type,
        "productCode": m.product_code,
        "productName": m.product_name,
        "standardUnit": m.standard_unit,
        "status": m.status,
        "remark": m.remark,
    }


def _profile_out(m) -> dict:
    return {
        "id": m.id,
        "vehicleId": m.vehicle_id,
        "energyType": m.energy_type,
        "defaultProductId": m.default_product_id,
        "tankCapacity": m.tank_capacity,
        "batteryCapacity": m.battery_capacity,
        "standardConsumptionPer100km": m.standard_consumption_per_100km,
        "remark": m.remark,
    }


def _rule_out(m) -> dict:
    return {
        "id": m.id,
        "ruleCode": m.rule_code,
        "ruleName": m.rule_name,
        "energyType": m.energy_type,
        "thresholdValue": m.threshold_value,
        "riskLevel": m.risk_level,
        "status": m.status,
        "remark": m.remark,
    }
