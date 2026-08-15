"""连接器实例 + 导入执行"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.connector import EnergyConnector
from app.modules.client.services.energy.constants import CHANNEL_CONNECTOR, CHANNEL_EXCEL
from app.modules.client.services.energy.consumption_service import EnergyConsumptionService
from app.modules.client.services.energy.connectors import (
    ConnectorContext,
    create_connector,
    list_connectors,
)
from app.modules.client.services.energy.supplier_service import EnergySupplierService


class EnergyConnectorService:

    @staticmethod
    def catalog():
        return [
            {"code": s.code, "name": s.name, "syncModes": s.sync_modes, "description": s.description}
            for s in list_connectors()
        ]

    @staticmethod
    async def page(db, page=1, page_size=20, supplier_id=None):
        stmt = select(EnergyConnector).where(EnergyConnector.is_deleted == 0)
        if supplier_id:
            stmt = stmt.where(EnergyConnector.supplier_id == supplier_id)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = (await db.execute(
            stmt.order_by(EnergyConnector.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return {
            "list": [_to_out(x) for x in rows],
            "count": total,
        }

    @staticmethod
    async def get(db, cid: int) -> EnergyConnector:
        r = await db.execute(
            select(EnergyConnector).where(EnergyConnector.id == cid, EnergyConnector.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("数据接入配置不存在")
        return obj

    @staticmethod
    async def create(db, data: dict) -> EnergyConnector:
        await EnergySupplierService.get(db, int(data["supplierId"]))
        code = data.get("connectorCode") or "excel"
        if code not in {s.code for s in list_connectors()}:
            raise BizException("不支持的接入方式")
        obj = EnergyConnector(
            connector_code=code,
            connector_name=(data.get("connectorName") or "").strip() or code,
            supplier_id=int(data["supplierId"]),
            account_id=data.get("accountId"),
            auth_config_json=data.get("authConfig"),
            field_mapping_json=data.get("fieldMapping"),
            sync_mode=data.get("syncMode") or "manual",
            cron=data.get("cron"),
            remark=data.get("remark"),
        )
        db.add(obj)
        await db.flush()
        return obj

    @staticmethod
    async def update(db, cid: int, data: dict) -> EnergyConnector:
        obj = await EnergyConnectorService.get(db, cid)
        for src, col in (
            ("connectorName", "connector_name"),
            ("accountId", "account_id"),
            ("authConfig", "auth_config_json"),
            ("fieldMapping", "field_mapping_json"),
            ("syncMode", "sync_mode"),
            ("cron", "cron"),
            ("status", "status"),
            ("remark", "remark"),
        ):
            if src in data:
                setattr(obj, col, data[src])
        await db.flush()
        return obj

    @staticmethod
    async def delete(db, cid: int) -> None:
        obj = await EnergyConnectorService.get(db, cid)
        obj.is_deleted = 1
        await db.flush()

    @staticmethod
    async def run_import(db, cid: int, rows: list[dict]) -> dict:
        conn = await EnergyConnectorService.get(db, cid)
        imported = 0
        duplicated = 0
        failed = 0
        channel = CHANNEL_EXCEL if conn.connector_code == "excel" else CHANNEL_CONNECTOR
        for row in rows:
            raw = await EnergyConsumptionService.ingest_raw(
                db,
                raw_data=row,
                supplier_id=conn.supplier_id,
                connector_id=conn.id,
                source_channel=channel,
                field_mapping=conn.field_mapping_json,
            )
            if raw.process_status == "processed":
                imported += 1
            elif raw.process_status == "duplicate":
                duplicated += 1
            else:
                failed += 1
        conn.last_sync_time = datetime.now()
        await db.flush()
        return {"imported": imported, "duplicated": duplicated, "failed": failed}

    @staticmethod
    async def pull(db, cid: int) -> dict:
        conn = await EnergyConnectorService.get(db, cid)
        impl = create_connector(conn.connector_code)
        ctx = ConnectorContext(
            supplier_id=conn.supplier_id,
            account_id=conn.account_id,
            auth_config=conn.auth_config_json,
            field_mapping=conn.field_mapping_json,
            cursor=conn.last_success_cursor,
        )
        records = await impl.fetch(ctx)
        result = await EnergyConnectorService.run_import(
            db, cid, [r.data for r in records]
        )
        if ctx.cursor:
            conn.last_success_cursor = ctx.cursor
            await db.flush()
        return result


def _to_out(m: EnergyConnector) -> dict:
    return {
        "id": m.id,
        "connectorCode": m.connector_code,
        "connectorName": m.connector_name,
        "supplierId": m.supplier_id,
        "accountId": m.account_id,
        "fieldMapping": m.field_mapping_json,
        "syncMode": m.sync_mode,
        "cron": m.cron,
        "lastSuccessCursor": m.last_success_cursor,
        "lastSyncTime": m.last_sync_time,
        "lastError": m.last_error,
        "status": m.status,
        "remark": m.remark,
    }
