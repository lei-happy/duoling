from typing import Optional
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.order import Order
from app.modules.client.schemas.order import (
    OrderCreate, OrderUpdate, OrderStatusUpdate, OrderOut,
)


class OrderService:

    @staticmethod
    def _generate_order_no() -> str:
        now = datetime.now()
        import random
        return f"YD{now.strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"

    @staticmethod
    async def page_orders(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        status_in: Optional[list] = None,
    ) -> dict:
        base = select(Order).where(Order.is_deleted == 0)

        if keyword:
            base = base.where(
                (Order.order_no.contains(keyword)) |
                (Order.customer_name.contains(keyword)) |
                (Order.plate_number.contains(keyword)) |
                (Order.driver_name.contains(keyword))
            )
        if status is not None:
            base = base.where(Order.status == status)
        if status_in:
            base = base.where(Order.status.in_(status_in))

        count_q = select(func.count()).select_from(base.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            base.order_by(Order.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = result.scalars().all()

        return {
            "list": [OrderOut.from_model(item).model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def create_order(db: AsyncSession, data: OrderCreate) -> Order:
        order = Order(
            order_no=OrderService._generate_order_no(),
            customer_id=data.customerId,
            customer_name=data.customerName,
            vehicle_id=data.vehicleId,
            plate_number=data.plateNumber,
            driver_id=data.driverId,
            driver_name=data.driverName,
            route_id=data.routeId,
            origin=data.origin,
            destination=data.destination,
            cargo_name=data.cargoName,
            cargo_weight=data.cargoWeight,
            cargo_volume=data.cargoVolume,
            freight_amount=data.freightAmount,
            plan_depart_time=data.planDepartTime,
            plan_arrive_time=data.planArriveTime,
            remark=data.remark,
            status=0,
        )
        db.add(order)
        await db.flush()
        await db.refresh(order)
        return order

    @staticmethod
    async def update_order(db: AsyncSession, order_id: int, data: OrderUpdate) -> Order:
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.is_deleted == 0)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise BizException("运单不存在")

        field_map = {
            "customerId": "customer_id",
            "customerName": "customer_name",
            "vehicleId": "vehicle_id",
            "plateNumber": "plate_number",
            "driverId": "driver_id",
            "driverName": "driver_name",
            "routeId": "route_id",
            "origin": "origin",
            "destination": "destination",
            "cargoName": "cargo_name",
            "cargoWeight": "cargo_weight",
            "cargoVolume": "cargo_volume",
            "freightAmount": "freight_amount",
            "planDepartTime": "plan_depart_time",
            "planArriveTime": "plan_arrive_time",
            "status": "status",
            "remark": "remark",
        }
        for sf, mf in field_map.items():
            val = getattr(data, sf, None)
            if val is not None:
                setattr(order, mf, val)

        await db.flush()
        await db.refresh(order)
        return order

    @staticmethod
    async def update_order_status(
        db: AsyncSession, order_id: int, data: OrderStatusUpdate
    ) -> Order:
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.is_deleted == 0)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise BizException("运单不存在")

        order.status = data.status
        if data.actualDepartTime:
            order.actual_depart_time = data.actualDepartTime
        if data.actualArriveTime:
            order.actual_arrive_time = data.actualArriveTime

        now = datetime.now()
        if data.status == 2 and not order.actual_depart_time:
            order.actual_depart_time = now
        if data.status == 3 and not order.actual_arrive_time:
            order.actual_arrive_time = now

        await db.flush()
        await db.refresh(order)
        return order

    @staticmethod
    async def delete_order(db: AsyncSession, order_id: int) -> None:
        result = await db.execute(
            select(Order).where(Order.id == order_id, Order.is_deleted == 0)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise BizException("运单不存在")
        if order.status not in (0, 6):
            raise BizException("只有待派车或已取消的运单可以删除")
        order.is_deleted = 1
        await db.flush()
