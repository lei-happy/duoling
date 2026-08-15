"""消费流水主数据匹配：卡 → 车 → 司机 → 任务"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.models.energy.card import EnergyCard
from app.modules.client.models.energy.station import EnergyStation
from app.modules.client.services.energy.card_service import EnergyCardService
from app.modules.client.services.energy.constants import (
    MATCH_CONFLICT,
    MATCH_MATCHED,
    MATCH_PARTIAL,
    MATCH_UNMATCHED,
)
from app.modules.client.services.energy.refs.master_data_resolver import MasterDataResolver


class EnergyMatcher:

    @staticmethod
    async def match(db: AsyncSession, std: dict, *, supplier_id: Optional[int] = None) -> dict:
        trace: dict = {}
        card = None
        if std.get("cardNo"):
            card = (await db.execute(
                select(EnergyCard).where(
                    EnergyCard.card_no == str(std["cardNo"]).strip(),
                    EnergyCard.is_deleted == 0,
                )
            )).scalar_one_or_none()
        trace["card"] = {"id": card.id, "no": card.card_no} if card else None

        account = None
        if card:
            account = (await db.execute(
                select(EnergyAccount).where(
                    EnergyAccount.id == card.account_id, EnergyAccount.is_deleted == 0
                )
            )).scalar_one_or_none()
        elif std.get("accountNo"):
            account = (await db.execute(
                select(EnergyAccount).where(
                    EnergyAccount.external_account_no == str(std["accountNo"]).strip(),
                    EnergyAccount.is_deleted == 0,
                )
            )).scalar_one_or_none()
        trace["account"] = {"id": account.id} if account else None

        at: Optional[datetime] = std.get("transactionTime")
        vehicle = None
        driver_id = None
        if card and at:
            binding = await EnergyCardService.find_binding_at(db, card.id, at)
            if binding:
                if binding.vehicle_id:
                    vehicle = await MasterDataResolver.get_vehicle_by_id(db, binding.vehicle_id)
                driver_id = binding.driver_id
                trace["binding"] = {
                    "vehicleId": binding.vehicle_id, "driverId": binding.driver_id,
                }
        if vehicle is None and std.get("vehicleNo"):
            vehicle = await MasterDataResolver.get_vehicle_by_plate(db, str(std["vehicleNo"]))
        trace["vehicle"] = vehicle

        if driver_id is None and vehicle:
            cap = await MasterDataResolver.get_capacity_by_vehicle(db, vehicle["id"])
            if cap:
                driver_id = cap.get("driverId")
                trace["capacity"] = cap

        task = None
        if at and (vehicle or std.get("vehicleNo")):
            task = await MasterDataResolver.find_task_for_vehicle_at(
                db,
                vehicle_id=vehicle["id"] if vehicle else None,
                plate_number=std.get("vehicleNo") or (vehicle or {}).get("plateNumber"),
                at=at,
            )
        trace["task"] = task

        station = None
        if supplier_id and std.get("stationCode"):
            station = (await db.execute(
                select(EnergyStation).where(
                    EnergyStation.supplier_id == supplier_id,
                    EnergyStation.station_code == str(std["stationCode"]).strip(),
                    EnergyStation.is_deleted == 0,
                )
            )).scalar_one_or_none()
        trace["station"] = {"id": station.id} if station else None

        flags = {
            "card": bool(card),
            "vehicle": bool(vehicle),
            "driver": bool(driver_id),
        }
        hit = sum(1 for v in flags.values() if v)
        if hit == 0:
            status = MATCH_UNMATCHED
        elif hit == 3:
            status = MATCH_MATCHED
        else:
            status = MATCH_PARTIAL

        return {
            "matchStatus": status,
            "matchTrace": trace,
            "cardId": card.id if card else None,
            "cardNo": card.card_no if card else std.get("cardNo"),
            "accountId": account.id if account else (card.account_id if card else None),
            "vehicleId": vehicle["id"] if vehicle else None,
            "plateNumber": (vehicle or {}).get("plateNumber") or std.get("vehicleNo"),
            "driverId": driver_id,
            "taskId": task["id"] if task else None,
            "stationId": station.id if station else None,
            "stationName": (station.station_name if station else None) or std.get("stationName"),
        }
