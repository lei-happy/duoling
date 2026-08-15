"""能源异常中心"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.exception import EnergyException
from app.modules.client.services.energy.constants import EXC_IGNORED, EXC_PROCESSED


class EnergyExceptionService:

    @staticmethod
    async def page(db, page=1, page_size=20, status=None, exception_type=None):
        stmt = select(EnergyException).where(EnergyException.is_deleted == 0)
        if status:
            stmt = stmt.where(EnergyException.status == status)
        if exception_type:
            stmt = stmt.where(EnergyException.exception_type == exception_type)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = (await db.execute(
            stmt.order_by(EnergyException.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return {"list": [_out(x) for x in rows], "count": total}

    @staticmethod
    async def stats(db) -> dict:
        rows = (await db.execute(
            select(EnergyException.status, func.count()).where(
                EnergyException.is_deleted == 0
            ).group_by(EnergyException.status)
        )).all()
        data = {s: int(c) for s, c in rows}
        return {
            "pending": data.get("pending", 0),
            "processed": data.get("processed", 0),
            "ignored": data.get("ignored", 0),
        }

    @staticmethod
    async def resolve(db, eid: int, status: str, remark: str, processor_id=None):
        r = await db.execute(
            select(EnergyException).where(
                EnergyException.id == eid, EnergyException.is_deleted == 0
            )
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("异常记录不存在")
        if status not in (EXC_PROCESSED, EXC_IGNORED):
            raise BizException("请选择「已处理」或「忽略」")
        obj.status = status
        obj.process_remark = remark
        obj.processor_id = processor_id
        obj.processed_at = datetime.now()
        await db.flush()
        return obj


def _out(m: EnergyException) -> dict:
    return {
        "id": m.id,
        "consumptionId": m.consumption_id,
        "accountId": m.account_id,
        "exceptionType": m.exception_type,
        "riskLevel": m.risk_level,
        "exceptionMessage": m.exception_message,
        "context": m.context_json,
        "status": m.status,
        "processorId": m.processor_id,
        "processedAt": m.processed_at,
        "processRemark": m.process_remark,
        "createdAt": m.created_at,
    }
