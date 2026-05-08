"""
承运商结算账户服务（租户库）
- 一对多 CRUD
- 默认账户互斥（同一 carrier_id 内最多 1 条 is_default=1）
- 删除保护（已被运单引用的账户禁止删除，本期没有运单引用上下文，仅保留分支）
"""

from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.partner.carrier_settlement import CarrierSettlement
from app.modules.client.schemas.partner.carrier_settlement import (
    CarrierSettlementCreate, CarrierSettlementUpdate, CarrierSettlementOut,
)


class CarrierSettlementService:

    @staticmethod
    async def list_by_carrier(
        db: AsyncSession, carrier_id: int
    ) -> List[CarrierSettlement]:
        result = await db.execute(
            select(CarrierSettlement).where(
                CarrierSettlement.carrier_id == carrier_id,
                CarrierSettlement.is_deleted == 0,
            ).order_by(
                CarrierSettlement.is_default.desc(),
                CarrierSettlement.sort_order.asc(),
                CarrierSettlement.id.asc(),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_default(
        db: AsyncSession, carrier_id: int
    ) -> Optional[CarrierSettlement]:
        result = await db.execute(
            select(CarrierSettlement).where(
                CarrierSettlement.carrier_id == carrier_id,
                CarrierSettlement.is_deleted == 0,
                CarrierSettlement.is_default == 1,
                CarrierSettlement.status == 1,
            ).limit(1)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_default_map(
        db: AsyncSession, carrier_ids: List[int]
    ) -> dict:
        """批量取默认结算账户：{carrier_id: CarrierSettlement}"""
        if not carrier_ids:
            return {}
        result = await db.execute(
            select(CarrierSettlement).where(
                CarrierSettlement.carrier_id.in_(carrier_ids),
                CarrierSettlement.is_deleted == 0,
                CarrierSettlement.is_default == 1,
                CarrierSettlement.status == 1,
            )
        )
        return {s.carrier_id: s for s in result.scalars().all()}

    @staticmethod
    async def get_or_404(
        db: AsyncSession, carrier_id: int, settlement_id: int
    ) -> CarrierSettlement:
        result = await db.execute(
            select(CarrierSettlement).where(
                CarrierSettlement.id == settlement_id,
                CarrierSettlement.carrier_id == carrier_id,
                CarrierSettlement.is_deleted == 0,
            )
        )
        s = result.scalar_one_or_none()
        if not s:
            raise BizException("结算账户不存在")
        return s

    @staticmethod
    async def _clear_other_defaults(
        db: AsyncSession, carrier_id: int, exclude_id: Optional[int] = None
    ) -> None:
        """同一 carrier_id 下其他账户的 is_default 置 0"""
        stmt = (
            update(CarrierSettlement)
            .where(
                CarrierSettlement.carrier_id == carrier_id,
                CarrierSettlement.is_deleted == 0,
                CarrierSettlement.is_default == 1,
            )
            .values(is_default=0)
        )
        if exclude_id is not None:
            stmt = stmt.where(CarrierSettlement.id != exclude_id)
        await db.execute(stmt)

    @staticmethod
    async def create(
        db: AsyncSession, carrier_id: int, data: CarrierSettlementCreate
    ) -> CarrierSettlement:
        is_default = data.isDefault or 0
        settlement = CarrierSettlement(
            carrier_id=carrier_id,
            account_label=data.accountLabel,
            account_type=data.accountType or 0,
            settlement_type=data.settlementType,
            settlement_period=data.settlementPeriod,
            settlement_day=data.settlementDay,
            bank_name=data.bankName,
            bank_branch=data.bankBranch,
            bank_account=data.bankAccount,
            bank_account_name=data.bankAccountName,
            swift_code=data.swiftCode,
            tax_rate=data.taxRate,
            applicable_scope=data.applicableScope,
            is_default=is_default,
            status=data.status if data.status is not None else 1,
            sort_order=data.sortOrder or 0,
            remark=data.remark,
        )
        db.add(settlement)
        await db.flush()

        if is_default == 1:
            await CarrierSettlementService._clear_other_defaults(
                db, carrier_id, exclude_id=settlement.id
            )
            await db.flush()

        await db.refresh(settlement)
        return settlement

    @staticmethod
    async def update(
        db: AsyncSession,
        carrier_id: int,
        settlement_id: int,
        data: CarrierSettlementUpdate,
    ) -> CarrierSettlement:
        settlement = await CarrierSettlementService.get_or_404(
            db, carrier_id, settlement_id
        )

        field_map = {
            "accountLabel": "account_label",
            "accountType": "account_type",
            "settlementType": "settlement_type",
            "settlementPeriod": "settlement_period",
            "settlementDay": "settlement_day",
            "bankName": "bank_name",
            "bankBranch": "bank_branch",
            "bankAccount": "bank_account",
            "bankAccountName": "bank_account_name",
            "swiftCode": "swift_code",
            "taxRate": "tax_rate",
            "applicableScope": "applicable_scope",
            "status": "status",
            "sortOrder": "sort_order",
            "remark": "remark",
        }
        for sf, mf in field_map.items():
            v = getattr(data, sf, None)
            if v is not None:
                setattr(settlement, mf, v)

        if data.isDefault is not None:
            settlement.is_default = data.isDefault
            if data.isDefault == 1:
                await CarrierSettlementService._clear_other_defaults(
                    db, carrier_id, exclude_id=settlement.id
                )

        await db.flush()
        await db.refresh(settlement)
        return settlement

    @staticmethod
    async def set_default(
        db: AsyncSession, carrier_id: int, settlement_id: int
    ) -> CarrierSettlement:
        settlement = await CarrierSettlementService.get_or_404(
            db, carrier_id, settlement_id
        )
        if settlement.status != 1:
            raise BizException("已停用的账户不能设为默认")
        await CarrierSettlementService._clear_other_defaults(
            db, carrier_id, exclude_id=settlement.id
        )
        settlement.is_default = 1
        await db.flush()
        await db.refresh(settlement)
        return settlement

    @staticmethod
    async def toggle_status(
        db: AsyncSession, carrier_id: int, settlement_id: int
    ) -> CarrierSettlement:
        settlement = await CarrierSettlementService.get_or_404(
            db, carrier_id, settlement_id
        )
        settlement.status = 0 if settlement.status == 1 else 1
        # 停用时同步取消默认
        if settlement.status == 0 and settlement.is_default == 1:
            settlement.is_default = 0
        await db.flush()
        await db.refresh(settlement)
        return settlement

    @staticmethod
    async def delete(
        db: AsyncSession, carrier_id: int, settlement_id: int
    ) -> None:
        settlement = await CarrierSettlementService.get_or_404(
            db, carrier_id, settlement_id
        )
        # 远期：检查是否被运单引用，若引用则禁止删除仅可停用
        # 本期暂未集成运单引用检查，留档案级软删
        settlement.is_deleted = 1
        if settlement.is_default == 1:
            settlement.is_default = 0
        await db.flush()

    @staticmethod
    async def cascade_soft_delete(
        db: AsyncSession, carrier_id: int
    ) -> None:
        """承运商软删时级联软删全部结算账户"""
        await db.execute(
            update(CarrierSettlement)
            .where(
                CarrierSettlement.carrier_id == carrier_id,
                CarrierSettlement.is_deleted == 0,
            )
            .values(is_deleted=1)
        )
