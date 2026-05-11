"""
运价合同服务（租户库）
"""

from typing import Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.billing.freight_contract import FreightContract
from app.modules.client.schemas.billing.freight_contract import (
    FreightContractCreate, FreightContractUpdate, FreightContractOut,
)


class FreightContractService:

    @staticmethod
    def _order_created_at_clause(
        sort: Optional[str], order: Optional[str]
    ) -> Tuple:
        """按创建时间排序：仅支持 createdAt，其它回退为创建时间倒序。"""
        if sort != "createdAt":
            return (
                FreightContract.created_at.desc(),
                FreightContract.id.desc(),
            )
        ol = (order or "descending").lower()
        if ol in ("asc", "ascending"):
            return (
                FreightContract.created_at.asc(),
                FreightContract.id.asc(),
            )
        return (
            FreightContract.created_at.desc(),
            FreightContract.id.desc(),
        )

    @staticmethod
    async def page_contracts(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        customer_id: Optional[int] = None,
        status: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> dict:
        base = select(FreightContract).where(FreightContract.is_deleted == 0)

        if keyword:
            base = base.where(
                (FreightContract.contract_no.contains(keyword)) |
                (FreightContract.contract_name.contains(keyword)) |
                (FreightContract.customer_name.contains(keyword))
            )
        if customer_id is not None:
            base = base.where(FreightContract.customer_id == customer_id)
        if status is not None:
            base = base.where(FreightContract.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        order_clause = FreightContractService._order_created_at_clause(
            sort, order
        )
        result = await db.execute(
            base.order_by(*order_clause)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [FreightContractOut.from_model(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_contract(db: AsyncSession, contract_id: int) -> FreightContract:
        result = await db.execute(
            select(FreightContract).where(
                FreightContract.id == contract_id,
                FreightContract.is_deleted == 0,
            )
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise BizException("合同不存在")
        return contract

    @staticmethod
    async def create_contract(
        db: AsyncSession, data: FreightContractCreate
    ) -> FreightContract:
        existing = await db.execute(
            select(FreightContract).where(
                FreightContract.contract_no == data.contractNo,
                FreightContract.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"合同编号 {data.contractNo} 已存在")

        contract = FreightContract(
            contract_no=data.contractNo,
            contract_name=data.contractName,
            customer_id=data.customerId,
            customer_name=data.customerName,
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
        db: AsyncSession, contract_id: int, data: FreightContractUpdate
    ) -> FreightContract:
        result = await db.execute(
            select(FreightContract).where(
                FreightContract.id == contract_id,
                FreightContract.is_deleted == 0,
            )
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise BizException("合同不存在")

        field_map = {
            "contractName": "contract_name",
            "customerId": "customer_id",
            "customerName": "customer_name",
            "effectiveDate": "effective_date",
            "expiryDate": "expiry_date",
            "status": "status",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(contract, model_field, val)

        await db.flush()
        await db.refresh(contract)
        return contract

    @staticmethod
    async def activate_contract(
        db: AsyncSession, contract_id: int
    ) -> FreightContract:
        result = await db.execute(
            select(FreightContract).where(
                FreightContract.id == contract_id,
                FreightContract.is_deleted == 0,
            )
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise BizException("合同不存在")
        if contract.status != 0:
            raise BizException("仅草稿状态的合同可以激活")
        contract.status = 1
        await db.flush()
        await db.refresh(contract)
        return contract

    @staticmethod
    async def terminate_contract(
        db: AsyncSession, contract_id: int
    ) -> FreightContract:
        result = await db.execute(
            select(FreightContract).where(
                FreightContract.id == contract_id,
                FreightContract.is_deleted == 0,
            )
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise BizException("合同不存在")
        if contract.status != 1:
            raise BizException("仅生效中的合同可以终止")

        contract.status = 2
        await db.flush()
        await db.refresh(contract)
        return contract

    @staticmethod
    async def resume_contract(
        db: AsyncSession, contract_id: int
    ) -> FreightContract:
        """将已终止的合同恢复为生效（可逆终止）。"""
        result = await db.execute(
            select(FreightContract).where(
                FreightContract.id == contract_id,
                FreightContract.is_deleted == 0,
            )
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise BizException("合同不存在")
        if contract.status != 2:
            raise BizException("仅已终止的合同可以恢复生效")

        contract.status = 1
        await db.flush()
        await db.refresh(contract)
        return contract

    @staticmethod
    async def delete_contract(db: AsyncSession, contract_id: int) -> None:
        result = await db.execute(
            select(FreightContract).where(
                FreightContract.id == contract_id,
                FreightContract.is_deleted == 0,
            )
        )
        contract = result.scalar_one_or_none()
        if not contract:
            raise BizException("合同不存在")
        if contract.status == 1:
            raise BizException("生效中的合同不能删除")
        contract.is_deleted = 1
        await db.flush()
