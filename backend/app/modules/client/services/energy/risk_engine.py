"""风控检测（纯规则，阈值来自 biz_energy_rule）"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.energy.consumption import EnergyConsumption
from app.modules.client.models.energy.exception import EnergyException
from app.modules.client.models.energy.rule import EnergyRule
from app.modules.client.models.energy.vehicle_profile import EnergyVehicleProfile
from app.modules.client.services.energy.constants import (
    EXC_PENDING,
    RULE_ABNORMAL_CONSUMPTION,
    RULE_ABNORMAL_PRICE,
    RULE_OVER_TANK,
    RULE_REPEAT_FILL,
    RULE_UNBOUND_VEHICLE,
)


class EnergyRiskEngine:

    @staticmethod
    async def detect(db: AsyncSession, cons: EnergyConsumption) -> list[EnergyException]:
        rules = (await db.execute(
            select(EnergyRule).where(EnergyRule.is_deleted == 0, EnergyRule.status == 1)
        )).scalars().all()
        by_code = {r.rule_code: r for r in rules}
        found: list[EnergyException] = []

        if RULE_OVER_TANK in by_code:
            exc = await _check_over_tank(db, cons, by_code[RULE_OVER_TANK])
            if exc:
                found.append(exc)
        if RULE_REPEAT_FILL in by_code:
            exc = await _check_repeat(db, cons, by_code[RULE_REPEAT_FILL])
            if exc:
                found.append(exc)
        if RULE_ABNORMAL_PRICE in by_code:
            exc = await _check_price(db, cons, by_code[RULE_ABNORMAL_PRICE])
            if exc:
                found.append(exc)
        if RULE_ABNORMAL_CONSUMPTION in by_code:
            exc = await _check_consumption(db, cons, by_code[RULE_ABNORMAL_CONSUMPTION])
            if exc:
                found.append(exc)
        if RULE_UNBOUND_VEHICLE in by_code and not cons.vehicle_id:
            found.append(_make_exc(
                cons, by_code[RULE_UNBOUND_VEHICLE],
                "这笔消费没有匹配到车辆，请人工确认是哪辆车加的",
            ))

        for e in found:
            db.add(e)
        if found:
            cons.exception_status = "abnormal"
        await db.flush()
        return found


def evaluate_over_tank(quantity: Optional[Decimal], tank: Optional[Decimal],
                       multiplier: Decimal) -> bool:
    if quantity is None or tank is None or tank <= 0:
        return False
    return Decimal(quantity) > Decimal(tank) * Decimal(multiplier)


def evaluate_price_deviation(unit_price: Optional[Decimal], avg: Optional[Decimal],
                             ratio: Decimal) -> bool:
    if unit_price is None or avg is None or avg <= 0:
        return False
    return abs(Decimal(unit_price) - Decimal(avg)) / Decimal(avg) > Decimal(ratio)


async def _check_over_tank(db, cons, rule) -> Optional[EnergyException]:
    if not cons.vehicle_id or cons.quantity is None:
        return None
    profile = (await db.execute(
        select(EnergyVehicleProfile).where(
            EnergyVehicleProfile.vehicle_id == cons.vehicle_id,
            EnergyVehicleProfile.is_deleted == 0,
        )
    )).scalar_one_or_none()
    tank = profile.tank_capacity if profile else None
    mult = rule.threshold_value or Decimal("1")
    if evaluate_over_tank(cons.quantity, tank, mult):
        return _make_exc(
            cons, rule,
            f"本次加注 {cons.quantity} 超过油箱容量 {tank} 的 {mult} 倍，请核对是否异常",
            {"quantity": str(cons.quantity), "tankCapacity": str(tank)},
        )
    return None


async def _check_repeat(db, cons, rule) -> Optional[EnergyException]:
    if not cons.vehicle_id:
        return None
    minutes = int(rule.threshold_value or 120)
    since = cons.consumption_time - timedelta(minutes=minutes)
    prev = (await db.execute(
        select(EnergyConsumption).where(
            EnergyConsumption.vehicle_id == cons.vehicle_id,
            EnergyConsumption.id != cons.id,
            EnergyConsumption.is_deleted == 0,
            EnergyConsumption.consumption_time >= since,
            EnergyConsumption.consumption_time <= cons.consumption_time,
        ).limit(1)
    )).scalar_one_or_none()
    if prev:
        return _make_exc(
            cons, rule,
            f"同一车辆在 {minutes} 分钟内再次加注，上一笔是 {prev.consumption_no}",
            {"prevId": prev.id, "windowMinutes": minutes},
        )
    return None


async def _check_price(db, cons, rule) -> Optional[EnergyException]:
    from sqlalchemy import func

    if cons.unit_price is None:
        return None
    avg = (await db.execute(
        select(func.avg(EnergyConsumption.unit_price)).where(
            EnergyConsumption.energy_type == cons.energy_type,
            EnergyConsumption.is_deleted == 0,
            EnergyConsumption.unit_price.is_not(None),
        )
    )).scalar()
    ratio = rule.threshold_value or Decimal("0.15")
    if evaluate_price_deviation(cons.unit_price, avg, ratio):
        return _make_exc(
            cons, rule,
            f"单价 {cons.unit_price} 偏离近期均价 {avg} 超过 {float(ratio) * 100:.0f}%",
            {"unitPrice": str(cons.unit_price), "avgPrice": str(avg)},
        )
    return None


async def _check_consumption(db, cons, rule) -> Optional[EnergyException]:
    if not cons.vehicle_id or not cons.quantity or not cons.mileage or cons.mileage <= 0:
        return None
    profile = (await db.execute(
        select(EnergyVehicleProfile).where(
            EnergyVehicleProfile.vehicle_id == cons.vehicle_id,
            EnergyVehicleProfile.is_deleted == 0,
        )
    )).scalar_one_or_none()
    std = profile.standard_consumption_per_100km if profile else None
    if not std:
        return None
    actual = Decimal(cons.quantity) / Decimal(cons.mileage) * Decimal("100")
    ratio = rule.threshold_value or Decimal("0.3")
    if abs(actual - std) / std > ratio:
        return _make_exc(
            cons, rule,
            f"折合百公里能耗 {actual:.2f}，标准 {std}，偏离超过 {float(ratio) * 100:.0f}%",
            {"actualPer100": str(actual), "standard": str(std)},
        )
    return None


def _make_exc(cons, rule, message, context=None) -> EnergyException:
    return EnergyException(
        consumption_id=cons.id,
        account_id=cons.account_id,
        exception_type=rule.rule_code,
        risk_level=rule.risk_level,
        exception_message=message,
        context_json=context,
        status=EXC_PENDING,
    )
