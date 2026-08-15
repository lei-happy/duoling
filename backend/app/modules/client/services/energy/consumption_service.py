"""能源消费流水：入库、匹配、记账"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.consumption import EnergyConsumption
from app.modules.client.models.energy.consumption_raw import EnergyConsumptionRaw
from app.modules.client.schemas.energy.consumption import (
    EnergyConsumptionAssignIn,
    EnergyConsumptionCreate,
    EnergyConsumptionOut,
)
from app.modules.client.services.energy.code_util import next_code
from app.modules.client.services.energy.constants import (
    CHANNEL_DRIVER_ADVANCE,
    CHANNEL_MANUAL,
    ENERGY_TYPE_UNITS,
    RAW_DUPLICATE,
    RAW_FAILED,
    RAW_PROCESSED,
    TXN_CONSUMPTION,
)
from app.modules.client.services.energy.fingerprint import build_data_hash
from app.modules.client.services.energy.ledger_service import EnergyLedgerService
from app.modules.client.services.energy.matcher import EnergyMatcher
from app.modules.client.services.energy.normalizer import json_safe_record, normalize_record
from app.modules.client.services.energy.refs.master_data_resolver import MasterDataResolver


class EnergyConsumptionService:

    @staticmethod
    async def page(db, page=1, page_size=20, keyword=None, account_id=None,
                   energy_type=None, match_status=None, source_channel=None,
                   start=None, end=None):
        stmt = select(EnergyConsumption).where(EnergyConsumption.is_deleted == 0)
        if keyword:
            stmt = stmt.where(
                (EnergyConsumption.consumption_no.contains(keyword))
                | (EnergyConsumption.card_no.contains(keyword))
                | (EnergyConsumption.plate_number.contains(keyword))
            )
        if account_id:
            stmt = stmt.where(EnergyConsumption.account_id == account_id)
        if energy_type:
            stmt = stmt.where(EnergyConsumption.energy_type == energy_type)
        if match_status:
            stmt = stmt.where(EnergyConsumption.match_status == match_status)
        if source_channel is not None:
            stmt = stmt.where(EnergyConsumption.source_channel == source_channel)
        if start:
            stmt = stmt.where(EnergyConsumption.consumption_time >= start)
        if end:
            stmt = stmt.where(EnergyConsumption.consumption_time <= end)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = (await db.execute(
            stmt.order_by(EnergyConsumption.consumption_time.desc(), EnergyConsumption.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return {
            "list": [EnergyConsumptionOut.from_model(x).model_dump() for x in rows],
            "count": total,
        }

    @staticmethod
    async def get(db: AsyncSession, cid: int) -> EnergyConsumption:
        r = await db.execute(
            select(EnergyConsumption).where(
                EnergyConsumption.id == cid, EnergyConsumption.is_deleted == 0
            )
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("消费流水不存在")
        return obj

    @staticmethod
    async def create_manual(db: AsyncSession, data: EnergyConsumptionCreate) -> EnergyConsumption:
        if data.amount is None or data.amount <= 0:
            raise BizException("请填写大于 0 的消费金额")
        std = {
            "cardNo": data.cardNo,
            "vehicleNo": data.plateNumber,
            "transactionTime": data.consumptionTime,
            "accountNo": None,
            "stationCode": None,
            "stationName": data.stationName,
        }
        matched = await EnergyMatcher.match(db, std, supplier_id=data.supplierId)
        affecting = 0 if data.sourceChannel == CHANNEL_DRIVER_ADVANCE else data.isLedgerAffecting
        obj = EnergyConsumption(
            consumption_no=await next_code(db, EnergyConsumption, "consumption_no", "EC"),
            supplier_id=data.supplierId,
            station_id=data.stationId or matched.get("stationId"),
            station_name=data.stationName or matched.get("stationName"),
            account_id=data.accountId or matched.get("accountId"),
            card_id=data.cardId or matched.get("cardId"),
            card_no=data.cardNo or matched.get("cardNo"),
            vehicle_id=data.vehicleId or matched.get("vehicleId"),
            plate_number=data.plateNumber or matched.get("plateNumber"),
            driver_id=data.driverId or matched.get("driverId"),
            task_id=matched.get("taskId"),
            energy_type=data.energyType,
            energy_product_id=data.energyProductId,
            product_name=data.productName,
            quantity=data.quantity,
            unit=data.unit or ENERGY_TYPE_UNITS.get(data.energyType),
            unit_price=data.unitPrice,
            amount=data.amount,
            mileage=data.mileage,
            odometer=data.odometer,
            consumption_time=data.consumptionTime,
            source_channel=data.sourceChannel or CHANNEL_MANUAL,
            is_ledger_affecting=affecting,
            match_status=matched["matchStatus"],
            match_trace_json=matched["matchTrace"],
            remark=data.remark,
        )
        if obj.driver_id:
            d = await MasterDataResolver.get_driver_by_id(db, obj.driver_id)
            if d:
                obj.driver_name = d.get("name")
        db.add(obj)
        await db.flush()
        if obj.is_ledger_affecting and obj.account_id:
            txn = await EnergyLedgerService.post(
                db,
                account_id=obj.account_id,
                txn_type=TXN_CONSUMPTION,
                amount=Decimal(obj.amount),
                transaction_time=obj.consumption_time,
                biz_type="consumption",
                biz_id=obj.id,
                remark=f"消费 {obj.consumption_no}",
            )
            obj.ledger_txn_id = txn.id
            await db.flush()
        from app.modules.client.services.energy.risk_engine import EnergyRiskEngine
        await EnergyRiskEngine.detect(db, obj)
        return obj

    @staticmethod
    async def ingest_raw(
        db: AsyncSession,
        *,
        raw_data: dict,
        supplier_id: Optional[int],
        connector_id: Optional[int],
        source_channel: int,
        field_mapping: Optional[dict] = None,
        is_ledger_affecting: int = 1,
    ) -> EnergyConsumptionRaw:
        raw_data = json_safe_record(raw_data)
        std = normalize_record(raw_data, field_mapping)
        data_hash = build_data_hash(
            supplier_id=supplier_id,
            external_transaction_id=std.get("externalTransactionId"),
            card_no=std.get("cardNo"),
            transaction_time=std.get("transactionTime"),
            amount=std.get("amount"),
            quantity=std.get("quantity"),
            station=std.get("stationName") or std.get("stationCode"),
        )
        existed = (await db.execute(
            select(EnergyConsumptionRaw).where(EnergyConsumptionRaw.data_hash == data_hash)
        )).scalar_one_or_none()
        if existed:
            existed.process_status = RAW_DUPLICATE
            await db.flush()
            return existed

        raw = EnergyConsumptionRaw(
            supplier_id=supplier_id,
            connector_id=connector_id,
            external_transaction_id=std.get("externalTransactionId"),
            raw_data=raw_data,
            data_hash=data_hash,
            process_status="pending",
            received_at=datetime.now(),
        )
        db.add(raw)
        await db.flush()
        try:
            cons = await EnergyConsumptionService._persist_from_std(
                db, std,
                supplier_id=supplier_id,
                raw_id=raw.id,
                source_channel=source_channel,
                is_ledger_affecting=is_ledger_affecting,
            )
            raw.process_status = RAW_PROCESSED
            raw.processed_at = datetime.now()
            raw.consumption_id = cons.id
        except Exception as e:  # noqa: BLE001
            raw.process_status = RAW_FAILED
            raw.error_message = str(e)[:1000]
        await db.flush()
        return raw

    @staticmethod
    async def _persist_from_std(
        db, std: dict, *, supplier_id, raw_id, source_channel, is_ledger_affecting,
    ) -> EnergyConsumption:
        if not std.get("amount"):
            raise BizException("消费金额缺失，无法入账")
        if not std.get("transactionTime"):
            raise BizException("消费时间缺失，无法入账")
        matched = await EnergyMatcher.match(db, std, supplier_id=supplier_id)
        affecting = 0 if source_channel == CHANNEL_DRIVER_ADVANCE else is_ledger_affecting
        obj = EnergyConsumption(
            consumption_no=await next_code(db, EnergyConsumption, "consumption_no", "EC"),
            supplier_id=supplier_id,
            station_id=matched.get("stationId"),
            station_name=matched.get("stationName"),
            account_id=matched.get("accountId"),
            card_id=matched.get("cardId"),
            card_no=matched.get("cardNo"),
            vehicle_id=matched.get("vehicleId"),
            plate_number=matched.get("plateNumber"),
            driver_id=matched.get("driverId"),
            task_id=matched.get("taskId"),
            energy_type=std.get("energyType") or "OIL",
            product_name=std.get("productName"),
            quantity=std.get("quantity"),
            unit=std.get("unit") or ENERGY_TYPE_UNITS.get(std.get("energyType") or "OIL"),
            unit_price=std.get("unitPrice"),
            amount=std["amount"],
            mileage=std.get("mileage"),
            odometer=std.get("odometer"),
            consumption_time=std["transactionTime"],
            external_transaction_id=std.get("externalTransactionId"),
            source_channel=source_channel,
            is_ledger_affecting=affecting,
            match_status=matched["matchStatus"],
            match_trace_json=matched["matchTrace"],
            raw_id=raw_id,
        )
        if obj.driver_id:
            d = await MasterDataResolver.get_driver_by_id(db, obj.driver_id)
            if d:
                obj.driver_name = d.get("name")
        db.add(obj)
        await db.flush()
        if obj.is_ledger_affecting and obj.account_id:
            txn = await EnergyLedgerService.post(
                db,
                account_id=obj.account_id,
                txn_type=TXN_CONSUMPTION,
                amount=Decimal(obj.amount),
                transaction_time=obj.consumption_time,
                biz_type="consumption",
                biz_id=obj.id,
                external_txn_id=obj.external_transaction_id,
                remark=f"消费 {obj.consumption_no}",
            )
            obj.ledger_txn_id = txn.id
            await db.flush()
        from app.modules.client.services.energy.risk_engine import EnergyRiskEngine
        await EnergyRiskEngine.detect(db, obj)
        return obj

    @staticmethod
    async def assign(db, cid: int, data: EnergyConsumptionAssignIn) -> EnergyConsumption:
        obj = await EnergyConsumptionService.get(db, cid)
        if data.vehicleId:
            v = await MasterDataResolver.get_vehicle_by_id(db, data.vehicleId)
            if v is None:
                raise BizException("车辆不存在")
            obj.vehicle_id = v["id"]
            obj.plate_number = v["plateNumber"]
        if data.driverId:
            d = await MasterDataResolver.get_driver_by_id(db, data.driverId)
            if d is None:
                raise BizException("司机不存在")
            obj.driver_id = d["id"]
            obj.driver_name = d.get("name")
        if data.taskId:
            obj.task_id = data.taskId
        if data.accountId:
            obj.account_id = data.accountId
        if data.cardId:
            obj.card_id = data.cardId
        if obj.vehicle_id and obj.account_id:
            obj.match_status = "MATCHED"
        elif obj.vehicle_id or obj.account_id or obj.card_id:
            obj.match_status = "PARTIAL"
        await db.flush()
        return obj
