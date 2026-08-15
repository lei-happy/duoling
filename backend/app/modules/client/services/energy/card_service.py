"""能源卡与绑定"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.energy.account import EnergyAccount
from app.modules.client.models.energy.card import EnergyCard
from app.modules.client.models.energy.card_binding import EnergyCardBinding
from app.modules.client.schemas.energy.card import (
    EnergyCardBindIn,
    EnergyCardCreate,
    EnergyCardOut,
    EnergyCardUpdate,
)
from app.modules.client.services.energy.account_service import EnergyAccountService
from app.modules.client.services.energy.constants import STATUS_NORMAL
from app.modules.client.services.energy.refs.master_data_resolver import MasterDataResolver


class EnergyCardService:

    @staticmethod
    async def page(db, page=1, page_size=20, keyword=None, account_id=None, status=None):
        stmt = select(EnergyCard).where(EnergyCard.is_deleted == 0)
        if keyword:
            stmt = stmt.where(EnergyCard.card_no.contains(keyword))
        if account_id:
            stmt = stmt.where(EnergyCard.account_id == account_id)
        if status is not None:
            stmt = stmt.where(EnergyCard.status == status)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar() or 0
        rows = list((await db.execute(
            stmt.order_by(EnergyCard.id.desc()).offset((page - 1) * page_size).limit(page_size)
        )).scalars().all())
        acc_names = {}
        if rows:
            for a in (await db.execute(
                select(EnergyAccount).where(EnergyAccount.id.in_({r.account_id for r in rows}))
            )).scalars().all():
                acc_names[a.id] = a.account_name
        bindings = await EnergyCardService._current_bindings(db, [r.id for r in rows])
        return {
            "list": [
                EnergyCardOut.from_model(
                    r,
                    account_name=acc_names.get(r.account_id),
                    vehicle_id=(bindings.get(r.id) or {}).get("vehicle_id"),
                    driver_id=(bindings.get(r.id) or {}).get("driver_id"),
                ).model_dump()
                for r in rows
            ],
            "count": total,
        }

    @staticmethod
    async def _current_bindings(db, card_ids: list[int]) -> dict[int, dict]:
        if not card_ids:
            return {}
        rows = (await db.execute(
            select(EnergyCardBinding).where(
                EnergyCardBinding.card_id.in_(card_ids),
                EnergyCardBinding.status == 1,
                EnergyCardBinding.end_time.is_(None),
                EnergyCardBinding.is_deleted == 0,
            )
        )).scalars().all()
        return {b.card_id: {"vehicle_id": b.vehicle_id, "driver_id": b.driver_id} for b in rows}

    @staticmethod
    async def get(db: AsyncSession, cid: int) -> EnergyCard:
        r = await db.execute(
            select(EnergyCard).where(EnergyCard.id == cid, EnergyCard.is_deleted == 0)
        )
        obj = r.scalar_one_or_none()
        if obj is None:
            raise BizException("能源卡不存在")
        return obj

    @staticmethod
    async def create(db: AsyncSession, data: EnergyCardCreate) -> EnergyCard:
        await EnergyAccountService.get(db, data.accountId)
        card_no = (data.cardNo or "").strip()
        if not card_no:
            raise BizException("请填写卡号")
        exists = (await db.execute(
            select(EnergyCard.id).where(EnergyCard.card_no == card_no)
        )).scalar_one_or_none()
        if exists:
            raise BizException("卡号已存在")
        obj = EnergyCard(
            account_id=data.accountId,
            card_no=card_no,
            external_card_id=data.externalCardId,
            card_type=data.cardType,
            energy_type=data.energyType,
            status=STATUS_NORMAL,
            remark=data.remark,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    @staticmethod
    async def update(db: AsyncSession, cid: int, data: EnergyCardUpdate) -> EnergyCard:
        obj = await EnergyCardService.get(db, cid)
        payload = data.model_dump(exclude_unset=True)
        mapping = {
            "cardType": "card_type",
            "energyType": "energy_type",
            "status": "status",
            "remark": "remark",
        }
        for k, col in mapping.items():
            if k in payload:
                setattr(obj, col, payload[k])
        await db.flush()
        return obj

    @staticmethod
    async def delete(db: AsyncSession, cid: int) -> None:
        obj = await EnergyCardService.get(db, cid)
        obj.is_deleted = 1
        await db.flush()

    @staticmethod
    async def bind(db: AsyncSession, cid: int, data: EnergyCardBindIn) -> EnergyCardBinding:
        card = await EnergyCardService.get(db, cid)
        if not data.vehicleId and not data.driverId:
            raise BizException("请至少选择车辆或司机")
        if data.vehicleId:
            v = await MasterDataResolver.get_vehicle_by_id(db, data.vehicleId)
            if v is None:
                raise BizException("车辆不存在")
        if data.driverId:
            d = await MasterDataResolver.get_driver_by_id(db, data.driverId)
            if d is None:
                raise BizException("司机不存在")
        await EnergyCardService._close_current(db, card.id)
        binding = EnergyCardBinding(
            card_id=card.id,
            vehicle_id=data.vehicleId,
            driver_id=data.driverId,
            start_time=data.startTime or datetime.now(),
            status=1,
        )
        db.add(binding)
        await db.flush()
        return binding

    @staticmethod
    async def unbind(db: AsyncSession, cid: int) -> None:
        await EnergyCardService.get(db, cid)
        await EnergyCardService._close_current(db, cid)

    @staticmethod
    async def _close_current(db: AsyncSession, card_id: int) -> None:
        rows = (await db.execute(
            select(EnergyCardBinding).where(
                EnergyCardBinding.card_id == card_id,
                EnergyCardBinding.status == 1,
                EnergyCardBinding.end_time.is_(None),
                EnergyCardBinding.is_deleted == 0,
            )
        )).scalars().all()
        now = datetime.now()
        for b in rows:
            b.end_time = now
            b.status = 0

    @staticmethod
    async def find_binding_at(
        db: AsyncSession, card_id: int, at: datetime
    ) -> Optional[EnergyCardBinding]:
        rows = (await db.execute(
            select(EnergyCardBinding).where(
                EnergyCardBinding.card_id == card_id,
                EnergyCardBinding.is_deleted == 0,
                EnergyCardBinding.start_time <= at,
            )
        )).scalars().all()
        for b in rows:
            if b.end_time is None or b.end_time >= at:
                return b
        return None
