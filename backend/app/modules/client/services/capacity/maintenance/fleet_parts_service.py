"""
车辆资产 - 备件主数据 / 库存流水 / 维修厂
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.maintenance.part import FleetPart
from app.modules.client.models.capacity.maintenance.stock_txn import FleetStockTxn
from app.modules.client.models.capacity.maintenance.workshop import FleetWorkshop
from app.modules.client.schemas.capacity.maintenance import (
    PartCreate,
    PartOut,
    PartUpdate,
    StockAdjustBody,
    StockInboundBody,
    StockTxnOut,
    WorkshopCreate,
    WorkshopOut,
    WorkshopUpdate,
)

_CENT = Decimal("0.01")
_ZERO = Decimal("0")


def _money(v: Optional[Decimal]) -> Optional[Decimal]:
    if v is None:
        return None
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)


class FleetPartsService:

    # ---------- 序列化 ----------

    @staticmethod
    def _part_out(row: FleetPart) -> dict[str, Any]:
        qty = Decimal(str(row.qty_on_hand or 0))
        safety = int(row.safety_stock or 0)
        return PartOut(
            id=row.id,
            partCode=row.part_code,
            partName=row.part_name,
            category=row.category,
            unit=row.unit,
            refPrice=row.ref_price,
            safetyStock=safety,
            qtyOnHand=qty,
            status=row.status,
            lowStock=qty < Decimal(safety),
            remark=row.remark,
            createdAt=row.created_at,
            updatedAt=row.updated_at,
        ).model_dump(mode="json")

    @staticmethod
    def _txn_out(row: FleetStockTxn) -> dict[str, Any]:
        return StockTxnOut(
            id=row.id,
            partId=row.part_id,
            partCode=row.part_code,
            partName=row.part_name,
            txnType=row.txn_type,
            qty=row.qty,
            unitCost=row.unit_cost,
            amount=row.amount,
            refType=row.ref_type,
            refId=row.ref_id,
            remark=row.remark,
            createdAt=row.created_at,
        ).model_dump(mode="json")

    @staticmethod
    def _workshop_out(row: FleetWorkshop) -> dict[str, Any]:
        return WorkshopOut(
            id=row.id,
            name=row.name,
            contact=row.contact,
            phone=row.phone,
            address=row.address,
            enabled=row.enabled,
            remark=row.remark,
            createdAt=row.created_at,
            updatedAt=row.updated_at,
        ).model_dump(mode="json")

    # ---------- 备件 ----------

    @staticmethod
    async def _get_part(db: AsyncSession, part_id: int) -> FleetPart:
        row = (
            await db.execute(
                select(FleetPart).where(
                    FleetPart.id == part_id,
                    FleetPart.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("未找到该备件，请刷新后重试")
        return row

    @staticmethod
    async def page_parts(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        low_stock_only: bool = False,
    ) -> dict:
        conditions = [FleetPart.is_deleted == 0]
        if status is not None:
            conditions.append(FleetPart.status == status)
        if keyword:
            like = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    FleetPart.part_code.like(like),
                    FleetPart.part_name.like(like),
                    FleetPart.category.like(like),
                )
            )
        if low_stock_only:
            conditions.append(FleetPart.qty_on_hand < FleetPart.safety_stock)

        total = (
            await db.execute(
                select(func.count()).select_from(FleetPart).where(*conditions)
            )
        ).scalar() or 0
        rows = (
            await db.execute(
                select(FleetPart)
                .where(*conditions)
                .order_by(FleetPart.updated_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [FleetPartsService._part_out(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create_part(db: AsyncSession, body: PartCreate) -> dict:
        code = (body.partCode or "").strip()
        name = (body.partName or "").strip()
        if not code:
            raise BizException("请填写备件编码")
        if not name:
            raise BizException("请填写备件名称")
        exists = (
            await db.execute(
                select(FleetPart.id).where(
                    FleetPart.part_code == code,
                    FleetPart.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if exists:
            raise BizException("该备件编码已存在，请换一个")
        row = FleetPart(
            part_code=code,
            part_name=name,
            category=body.category,
            unit=(body.unit or "个").strip() or "个",
            ref_price=_money(body.refPrice),
            safety_stock=max(int(body.safetyStock or 0), 0),
            qty_on_hand=_ZERO,
            status=1,
            remark=body.remark,
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return FleetPartsService._part_out(row)

    @staticmethod
    async def update_part(
        db: AsyncSession, part_id: int, body: PartUpdate
    ) -> dict:
        row = await FleetPartsService._get_part(db, part_id)
        data = body.model_dump(exclude_unset=True)
        mapping = {
            "partName": "part_name",
            "category": "category",
            "unit": "unit",
            "refPrice": "ref_price",
            "safetyStock": "safety_stock",
            "status": "status",
            "remark": "remark",
        }
        for k, col in mapping.items():
            if k not in data:
                continue
            val = data[k]
            if k == "partName":
                val = (val or "").strip()
                if not val:
                    raise BizException("请填写备件名称")
            if k == "refPrice":
                val = _money(val)
            if k == "safetyStock" and val is not None:
                val = max(int(val), 0)
            if k == "status" and val not in (0, 1):
                raise BizException("备件状态不正确")
            setattr(row, col, val)
        await db.flush()
        await db.refresh(row)
        return FleetPartsService._part_out(row)

    @staticmethod
    async def low_stock_count(db: AsyncSession) -> int:
        return int(
            (
                await db.execute(
                    select(func.count())
                    .select_from(FleetPart)
                    .where(
                        FleetPart.is_deleted == 0,
                        FleetPart.status == 1,
                        FleetPart.qty_on_hand < FleetPart.safety_stock,
                    )
                )
            ).scalar()
            or 0
        )

    # ---------- 库存 ----------

    @staticmethod
    async def inbound(
        db: AsyncSession,
        part_id: int,
        body: StockInboundBody,
        operator_user_id: Optional[int],
    ) -> dict:
        row = await FleetPartsService._get_part(db, part_id)
        if row.status != 1:
            raise BizException("该备件已停用，无法入库")
        qty = Decimal(str(body.qty))
        if qty <= 0:
            raise BizException("入库数量须大于 0")
        unit_cost = _money(body.unitCost) or _money(row.ref_price)
        amount = _money(qty * unit_cost) if unit_cost is not None else None
        row.qty_on_hand = Decimal(str(row.qty_on_hand or 0)) + qty
        txn = FleetStockTxn(
            part_id=row.id,
            part_code=row.part_code,
            part_name=row.part_name,
            txn_type="in",
            qty=qty,
            unit_cost=unit_cost,
            amount=amount,
            ref_type="inbound",
            ref_id=None,
            remark=body.remark or "手工入库",
            created_by=operator_user_id,
        )
        db.add(txn)
        await db.flush()
        await db.refresh(row)
        return FleetPartsService._part_out(row)

    @staticmethod
    async def adjust(
        db: AsyncSession,
        part_id: int,
        body: StockAdjustBody,
        operator_user_id: Optional[int],
    ) -> dict:
        row = await FleetPartsService._get_part(db, part_id)
        delta = Decimal(str(body.qtyDelta))
        if delta == 0:
            raise BizException("调整数量不能为 0")
        new_qty = Decimal(str(row.qty_on_hand or 0)) + delta
        if new_qty < 0:
            raise BizException("调整后库存不能为负数")
        row.qty_on_hand = new_qty
        txn = FleetStockTxn(
            part_id=row.id,
            part_code=row.part_code,
            part_name=row.part_name,
            txn_type="adjust",
            qty=abs(delta),
            unit_cost=_money(row.ref_price),
            amount=None,
            ref_type="adjust",
            ref_id=None,
            remark=body.remark
            or ("盘盈" if delta > 0 else "盘亏"),
            created_by=operator_user_id,
        )
        db.add(txn)
        await db.flush()
        await db.refresh(row)
        return FleetPartsService._part_out(row)

    @staticmethod
    async def issue_for_work_order(
        db: AsyncSession,
        *,
        part_id: int,
        qty: Decimal,
        unit_cost: Optional[Decimal],
        work_order_id: int,
        operator_user_id: Optional[int],
    ) -> None:
        """完工出库（由工单服务调用）"""
        row = await FleetPartsService._get_part(db, part_id)
        q = Decimal(str(qty))
        if q <= 0:
            return
        on_hand = Decimal(str(row.qty_on_hand or 0))
        if on_hand < q:
            raise BizException(
                f"「{row.part_name}」库存不足（现有 {on_hand}，需要 {q}），"
                f"请先入库或改数量"
            )
        cost = _money(unit_cost) or _money(row.ref_price)
        row.qty_on_hand = on_hand - q
        db.add(
            FleetStockTxn(
                part_id=row.id,
                part_code=row.part_code,
                part_name=row.part_name,
                txn_type="out",
                qty=q,
                unit_cost=cost,
                amount=_money(q * cost) if cost is not None else None,
                ref_type="work_order",
                ref_id=work_order_id,
                remark=f"工单出库 #{work_order_id}",
                created_by=operator_user_id,
            )
        )

    @staticmethod
    async def page_stock_txns(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        part_id: Optional[int] = None,
        txn_type: Optional[str] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        conditions = [FleetStockTxn.is_deleted == 0]
        if part_id:
            conditions.append(FleetStockTxn.part_id == part_id)
        if txn_type:
            conditions.append(FleetStockTxn.txn_type == txn_type)
        if keyword:
            like = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    FleetStockTxn.part_code.like(like),
                    FleetStockTxn.part_name.like(like),
                )
            )
        total = (
            await db.execute(
                select(func.count())
                .select_from(FleetStockTxn)
                .where(*conditions)
            )
        ).scalar() or 0
        rows = (
            await db.execute(
                select(FleetStockTxn)
                .where(*conditions)
                .order_by(FleetStockTxn.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [FleetPartsService._txn_out(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    # ---------- 维修厂 ----------

    @staticmethod
    async def page_workshops(
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 50,
        keyword: Optional[str] = None,
        enabled: Optional[int] = None,
    ) -> dict:
        conditions = [FleetWorkshop.is_deleted == 0]
        if enabled is not None:
            conditions.append(FleetWorkshop.enabled == enabled)
        if keyword:
            like = f"%{keyword.strip()}%"
            conditions.append(
                or_(
                    FleetWorkshop.name.like(like),
                    FleetWorkshop.contact.like(like),
                    FleetWorkshop.phone.like(like),
                )
            )
        total = (
            await db.execute(
                select(func.count())
                .select_from(FleetWorkshop)
                .where(*conditions)
            )
        ).scalar() or 0
        rows = (
            await db.execute(
                select(FleetWorkshop)
                .where(*conditions)
                .order_by(FleetWorkshop.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [FleetPartsService._workshop_out(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create_workshop(db: AsyncSession, body: WorkshopCreate) -> dict:
        name = (body.name or "").strip()
        if not name:
            raise BizException("请填写维修厂名称")
        row = FleetWorkshop(
            name=name,
            contact=body.contact,
            phone=body.phone,
            address=body.address,
            enabled=1 if body.enabled is None else int(body.enabled),
            remark=body.remark,
        )
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return FleetPartsService._workshop_out(row)

    @staticmethod
    async def update_workshop(
        db: AsyncSession, workshop_id: int, body: WorkshopUpdate
    ) -> dict:
        row = (
            await db.execute(
                select(FleetWorkshop).where(
                    FleetWorkshop.id == workshop_id,
                    FleetWorkshop.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not row:
            raise BizException("未找到该维修厂，请刷新后重试")
        data = body.model_dump(exclude_unset=True)
        mapping = {
            "name": "name",
            "contact": "contact",
            "phone": "phone",
            "address": "address",
            "enabled": "enabled",
            "remark": "remark",
        }
        for k, col in mapping.items():
            if k in data:
                val = data[k]
                if k == "name":
                    val = (val or "").strip()
                    if not val:
                        raise BizException("请填写维修厂名称")
                setattr(row, col, val)
        await db.flush()
        await db.refresh(row)
        return FleetPartsService._workshop_out(row)

    @staticmethod
    async def get_workshop_name(
        db: AsyncSession, workshop_id: Optional[int]
    ) -> Optional[str]:
        if not workshop_id:
            return None
        row = (
            await db.execute(
                select(FleetWorkshop).where(
                    FleetWorkshop.id == workshop_id,
                    FleetWorkshop.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        return row.name if row else None
