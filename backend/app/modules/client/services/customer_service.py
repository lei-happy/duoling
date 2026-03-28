"""
客户管理服务（租户库）
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.customer import Customer
from app.modules.client.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerOut,
)


class CustomerService:

    @staticmethod
    async def page_customers(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        customer_type: Optional[int] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(Customer).where(Customer.is_deleted == 0)

        if keyword:
            base = base.where(
                (Customer.customer_name.contains(keyword)) |
                (Customer.contact_person.contains(keyword)) |
                (Customer.contact_phone.contains(keyword))
            )
        if customer_type is not None:
            base = base.where(Customer.customer_type == customer_type)
        if status is not None:
            base = base.where(Customer.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Customer.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [CustomerOut.from_model(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create_customer(
        db: AsyncSession, data: CustomerCreate
    ) -> Customer:
        existing = await db.execute(
            select(Customer).where(
                Customer.customer_name == data.customerName,
                Customer.is_deleted == 0,
            )
        )
        if existing.scalar_one_or_none():
            raise BizException(f"客户名称 {data.customerName} 已存在")

        customer = Customer(
            customer_name=data.customerName,
            short_name=data.shortName,
            customer_type=data.customerType,
            contact_person=data.contactPerson,
            contact_phone=data.contactPhone,
            address=data.address,
            remark=data.remark,
        )
        db.add(customer)
        await db.flush()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def update_customer(
        db: AsyncSession, customer_id: int, data: CustomerUpdate
    ) -> Customer:
        result = await db.execute(
            select(Customer).where(
                Customer.id == customer_id,
                Customer.is_deleted == 0,
            )
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise BizException("客户不存在")

        field_map = {
            "customerName": "customer_name",
            "shortName": "short_name",
            "customerType": "customer_type",
            "contactPerson": "contact_person",
            "contactPhone": "contact_phone",
            "address": "address",
            "status": "status",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(customer, model_field, val)

        await db.flush()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def delete_customer(db: AsyncSession, customer_id: int) -> None:
        result = await db.execute(
            select(Customer).where(
                Customer.id == customer_id,
                Customer.is_deleted == 0,
            )
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise BizException("客户不存在")
        customer.is_deleted = 1
        await db.flush()
