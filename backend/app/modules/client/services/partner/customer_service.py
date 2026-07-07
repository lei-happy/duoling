"""
客户管理服务（租户库）
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.partner.customer import Customer
from app.modules.client.schemas.partner.customer import (
    CustomerCreate, CustomerUpdate, CustomerOut,
)


class CustomerService:

    @staticmethod
    async def _generate_customer_code(db: AsyncSession) -> str:
        """生成客户编码: KH + 年月日 + 3 位序号"""
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"KH{today}"
        result = await db.execute(
            select(Customer.customer_code)
            .where(
                Customer.customer_code.isnot(None),
                Customer.customer_code.like(f"{prefix}%"),
                Customer.is_deleted == 0,
            )
            .order_by(Customer.customer_code.desc())
            .limit(1)
        )
        last_code = result.scalar_one_or_none()
        if last_code and len(last_code) > len(prefix):
            try:
                seq = int(last_code[len(prefix) :]) + 1
            except ValueError:
                seq = 1
        else:
            seq = 1
        return f"{prefix}{seq:03d}"

    @staticmethod
    def _order_created_at_clause(sort: Optional[str], order: Optional[str]):
        """按创建时间排序：仅支持 createdAt 字段，其它回退为创建时间倒序。"""
        if sort != "createdAt":
            return Customer.created_at.desc(), Customer.id.desc()
        ol = (order or "descending").lower()
        if ol in ("asc", "ascending"):
            return Customer.created_at.asc(), Customer.id.asc()
        return Customer.created_at.desc(), Customer.id.desc()

    @staticmethod
    async def page_customers(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        customer_type: Optional[int] = None,
        settlement_type: Optional[int] = None,
        status: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> dict:
        base = select(Customer).where(Customer.is_deleted == 0)

        if keyword:
            base = base.where(
                (Customer.customer_name.contains(keyword)) |
                (Customer.customer_code.contains(keyword)) |
                (Customer.contact_person.contains(keyword)) |
                (Customer.contact_phone.contains(keyword))
            )
        if customer_type is not None:
            base = base.where(Customer.customer_type == customer_type)
        if settlement_type is not None:
            base = base.where(Customer.settlement_type == settlement_type)
        if status is not None:
            base = base.where(Customer.status == status)

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        order_clause = CustomerService._order_created_at_clause(sort, order)
        result = await db.execute(
            base.order_by(*order_clause)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [CustomerOut.from_model(item).model_dump() for item in items],
            "count": total,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def get_customer(db: AsyncSession, customer_id: int) -> Customer:
        result = await db.execute(
            select(Customer).where(
                Customer.id == customer_id,
                Customer.is_deleted == 0,
            )
        )
        customer = result.scalar_one_or_none()
        if not customer:
            raise BizException("客户不存在")
        return customer

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

        raw_code = data.customerCode
        if raw_code and str(raw_code).strip():
            code = str(raw_code).strip()
            dup_code = await db.execute(
                select(Customer.id).where(
                    Customer.customer_code == code,
                    Customer.is_deleted == 0,
                )
            )
            if dup_code.scalar_one_or_none():
                raise BizException("客户编码已存在")
        else:
            code = await CustomerService._generate_customer_code(db)

        status_val = 1 if data.status is None else data.status

        customer = Customer(
            customer_code=code,
            customer_name=data.customerName,
            short_name=data.shortName,
            enterprise_id=data.enterpriseId,
            customer_type=data.customerType,
            contact_person=data.contactPerson,
            contact_phone=data.contactPhone,
            address=data.address,
            settlement_type=data.settlementType,
            credit_code=data.creditCode,
            status=status_val,
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
            "customerCode": "customer_code",
            "customerName": "customer_name",
            "shortName": "short_name",
            "enterpriseId": "enterprise_id",
            "customerType": "customer_type",
            "contactPerson": "contact_person",
            "contactPhone": "contact_phone",
            "address": "address",
            "settlementType": "settlement_type",
            "creditCode": "credit_code",
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

    @staticmethod
    async def select_customers(
        db: AsyncSession, keyword: Optional[str] = None
    ) -> list:
        base = select(Customer).where(
            Customer.is_deleted == 0,
            Customer.status == 1,
        )
        if keyword:
            base = base.where(
                (Customer.customer_name.contains(keyword)) |
                (Customer.customer_code.contains(keyword))
            )
        result = await db.execute(base.order_by(Customer.id.desc()).limit(50))
        items = result.scalars().all()
        return [
            {
                "id": item.id,
                "customerCode": item.customer_code,
                "customerName": item.customer_name,
                "shortName": item.short_name,
            }
            for item in items
        ]
