"""
承运商合同服务（租户库）
"""

from datetime import date
from typing import Optional, Tuple

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.carrier_contract import CarrierContract
from app.modules.client.models.billing.carrier_rate import CarrierRate
from app.modules.client.schemas.billing.carrier_contract import (
    CarrierContractCreate, CarrierContractUpdate, CarrierContractOut,
)
from app.modules.client.services.billing.carrier_freight_calc_service import (
    CarrierFreightCalcService,
)
from app.modules.client.services.billing.carrier_freight_calc_task_service import (
    CarrierFreightCalcTaskService,
    TASK_CONTRACT_CHANGED,
)


# 合同变更涉及的字段（除 status 之外，影响任务计算的字段）
CONTRACT_BILLING_FIELDS = {"effective_date", "expiry_date", "carrier_id"}


async def _enqueue_for_contract(
    db: AsyncSession,
    contract: CarrierContract,
    *,
    triggered_by_user_id: Optional[int] = None,
) -> int:
    """合同变更后扫承运商任务入队重算。返回新建任务条数。"""
    task_ids = await CarrierFreightCalcService.find_affected_tasks_for_contract(
        db, contract,
    )
    if not task_ids:
        return 0
    return await CarrierFreightCalcTaskService.enqueue_many_tasks(
        db, task_ids,
        task_type=TASK_CONTRACT_CHANGED,
        source_target_type="contract",
        source_target_id=contract.id,
        priority=5,
        triggered_by_user_id=triggered_by_user_id,
    )


class CarrierContractService:

    @staticmethod
    def _order_created_at_clause(
        sort: Optional[str], order: Optional[str]
    ) -> Tuple:
        if sort != "createdAt":
            return (
                CarrierContract.created_at.desc(),
                CarrierContract.id.desc(),
            )
        ol = (order or "descending").lower()
        if ol in ("asc", "ascending"):
            return (
                CarrierContract.created_at.asc(),
                CarrierContract.id.asc(),
            )
        return (
            CarrierContract.created_at.desc(),
            CarrierContract.id.desc(),
        )

    @staticmethod
    async def page_contracts(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        carrier_id: Optional[int] = None,
        status: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> dict:
        base = select(CarrierContract).where(CarrierContract.is_deleted == 0)

        if keyword:
            base = base.where(
                (CarrierContract.contract_no.contains(keyword)) |
                (CarrierContract.contract_name.contains(keyword)) |
                (CarrierContract.carrier_name.contains(keyword))
            )
        if carrier_id is not None:
            base = base.where(CarrierContract.carrier_id == carrier_id)
        if status is not None:
            base = base.where(CarrierContract.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        order_clause = CarrierContractService._order_created_at_clause(sort, order)
        result = await db.execute(
            base.order_by(*order_clause)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        contract_ids = [c.id for c in items]
        total_by_cid: dict[int, int] = {}
        active_by_cid: dict[int, int] = {}
        if contract_ids:
            today = date.today()
            tot_rows = (
                await db.execute(
                    select(CarrierRate.contract_id, func.count())
                    .where(
                        CarrierRate.contract_id.in_(contract_ids),
                        CarrierRate.is_deleted == 0,
                    )
                    .group_by(CarrierRate.contract_id)
                )
            ).all()
            for cid, cnt in tot_rows:
                total_by_cid[int(cid)] = int(cnt)

            act_rows = (
                await db.execute(
                    select(CarrierRate.contract_id, func.count())
                    .where(
                        CarrierRate.contract_id.in_(contract_ids),
                        CarrierRate.is_deleted == 0,
                        CarrierRate.status == 1,
                        or_(
                            CarrierRate.effective_date.is_(None),
                            CarrierRate.effective_date <= today,
                        ),
                        or_(
                            CarrierRate.expiry_date.is_(None),
                            CarrierRate.expiry_date >= today,
                        ),
                    )
                    .group_by(CarrierRate.contract_id)
                )
            ).all()
            for cid, cnt in act_rows:
                active_by_cid[int(cid)] = int(cnt)

        out_list = []
        for item in items:
            cid = int(item.id)
            row = CarrierContractOut.from_model(item).model_copy(
                update={
                    "totalRateCount": total_by_cid.get(cid, 0),
                    "activeRateCount": active_by_cid.get(cid, 0),
                }
            )
            out_list.append(row.model_dump())

        return {
            "list": out_list,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_contract(db: AsyncSession, contract_id: int) -> CarrierContract:
        result = await db.execute(
            select(CarrierContract).where(
                CarrierContract.id == contract_id,
                CarrierContract.is_deleted == 0,
            )
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise BizException("合同不存在")
        return contract

    @staticmethod
    async def create_contract(
        db: AsyncSession, data: CarrierContractCreate
    ) -> CarrierContract:
        existing = await db.execute(
            select(CarrierContract).where(
                CarrierContract.contract_no == data.contractNo,
                CarrierContract.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"合同编号 {data.contractNo} 已存在")

        contract = CarrierContract(
            contract_no=data.contractNo,
            contract_name=data.contractName,
            carrier_id=data.carrierId,
            carrier_name=data.carrierName,
            effective_date=data.effectiveDate,
            expiry_date=data.expiryDate,
            remark=data.remark,
            status=0,
        )
        db.add(contract)
        await db.flush()
        await db.refresh(contract)
        return contract

    @staticmethod
    async def update_contract(
        db: AsyncSession, contract_id: int, data: CarrierContractUpdate,
        *, current_user_id: Optional[int] = None,
    ) -> CarrierContract:
        result = await db.execute(
            select(CarrierContract).where(
                CarrierContract.id == contract_id,
                CarrierContract.is_deleted == 0,
            )
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise BizException("合同不存在")

        field_map = {
            "contractName": "contract_name",
            "carrierId": "carrier_id",
            "carrierName": "carrier_name",
            "effectiveDate": "effective_date",
            "expiryDate": "expiry_date",
            "status": "status",
            "remark": "remark",
        }
        billing_changed = False
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                if model_field in CONTRACT_BILLING_FIELDS:
                    if getattr(contract, model_field, None) != val:
                        billing_changed = True
                setattr(contract, model_field, val)

        if billing_changed:
            contract.contract_version = (contract.contract_version or 1) + 1

        await db.flush()
        await db.refresh(contract)

        if billing_changed and contract.status == 1:
            try:
                await _enqueue_for_contract(
                    db, contract, triggered_by_user_id=current_user_id,
                )
            except Exception:
                pass

        return contract

    @staticmethod
    async def activate_contract(
        db: AsyncSession, contract_id: int,
        *, current_user_id: Optional[int] = None,
    ) -> CarrierContract:
        contract = await CarrierContractService.get_contract(db, contract_id)
        if contract.status != 0:
            raise BizException("仅草稿状态的合同可以激活")
        contract.status = 1
        contract.contract_version = (contract.contract_version or 1) + 1
        await db.flush()
        await db.refresh(contract)
        try:
            await _enqueue_for_contract(
                db, contract, triggered_by_user_id=current_user_id,
            )
        except Exception:
            pass
        return contract

    @staticmethod
    async def terminate_contract(
        db: AsyncSession, contract_id: int,
        *, current_user_id: Optional[int] = None,
    ) -> CarrierContract:
        contract = await CarrierContractService.get_contract(db, contract_id)
        if contract.status != 1:
            raise BizException("仅生效中的合同可以终止")
        contract.status = 2
        contract.contract_version = (contract.contract_version or 1) + 1
        await db.flush()
        await db.refresh(contract)
        try:
            await _enqueue_for_contract(
                db, contract, triggered_by_user_id=current_user_id,
            )
        except Exception:
            pass
        return contract

    @staticmethod
    async def resume_contract(
        db: AsyncSession, contract_id: int,
        *, current_user_id: Optional[int] = None,
    ) -> CarrierContract:
        """将已终止的合同恢复为生效（可逆终止）。"""
        contract = await CarrierContractService.get_contract(db, contract_id)
        if contract.status != 2:
            raise BizException("仅已终止的合同可以恢复生效")
        contract.status = 1
        contract.contract_version = (contract.contract_version or 1) + 1
        await db.flush()
        await db.refresh(contract)
        try:
            await _enqueue_for_contract(
                db, contract, triggered_by_user_id=current_user_id,
            )
        except Exception:
            pass
        return contract

    @staticmethod
    async def delete_contract(db: AsyncSession, contract_id: int) -> None:
        contract = await CarrierContractService.get_contract(db, contract_id)
        if contract.status == 1:
            raise BizException("生效中的合同不能删除")
        contract.is_deleted = 1
        await db.flush()
