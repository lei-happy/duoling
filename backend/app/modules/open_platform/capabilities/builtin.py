"""内置只读能力（首期）

- ping：连接自检，不访问业务库
- customer.query / vehicle.query / waybill.query：分页查询租户业务数据

handler 复用租户库 ORM 直读，做薄查询；字段裁剪与脱敏由注册表统一处理。
"""

import time
from typing import Optional

from sqlalchemy import select, func

from app.modules.open_platform.capabilities.registry import register_capability
from app.modules.open_platform.capabilities.context import OpenContext


def _page_args(params: dict) -> tuple[int, int]:
    page = max(int(params.get("page") or 1), 1)
    page_size = min(max(int(params.get("pageSize") or 20), 1), 100)
    return page, page_size


@register_capability(
    code="ping",
    name="连接自检",
    category="基础",
    description="校验凭证与连通性，返回 pong 与当前租户标识，不访问业务数据。",
    channels=["api", "mcp"],
    needs_tenant_db=False,
    sort_order=0,
)
async def ping(ctx: OpenContext, params: dict, db) -> dict:
    return {
        "pong": True,
        "tenant": ctx.tenant_code,
        "channel": ctx.channel,
        "ts": int(time.time()),
    }


@register_capability(
    code="customer.query",
    name="查询客户",
    category="客商管理",
    description="按名称关键字分页查询客户档案。",
    channels=["api", "mcp"],
    output_fields=[
        "id", "customer_code", "customer_name", "short_name",
        "customer_type", "contact_person", "contact_phone", "status",
    ],
    sensitive_fields=["contact_phone"],
    sort_order=10,
)
async def customer_query(ctx: OpenContext, params: dict, db) -> dict:
    from app.modules.client.models.partner.customer import Customer

    page, page_size = _page_args(params)
    keyword: Optional[str] = params.get("keyword")

    conds = [Customer.is_deleted == 0]
    if keyword:
        conds.append(Customer.customer_name.like(f"%{keyword}%"))

    total = await db.scalar(select(func.count()).select_from(Customer).where(*conds))
    rows = (
        await db.execute(
            select(Customer)
            .where(*conds)
            .order_by(Customer.id.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
    ).scalars().all()

    return {
        "list": [
            {
                "id": r.id,
                "customer_code": r.customer_code,
                "customer_name": r.customer_name,
                "short_name": r.short_name,
                "customer_type": r.customer_type,
                "contact_person": r.contact_person,
                "contact_phone": r.contact_phone,
                "status": r.status,
            }
            for r in rows
        ],
        "total": int(total or 0),
        "page": page,
        "pageSize": page_size,
    }


@register_capability(
    code="vehicle.query",
    name="查询车辆",
    category="运力管理",
    description="按车牌关键字分页查询车辆。",
    channels=["api", "mcp"],
    output_fields=["id", "plate_number", "plate_category", "status"],
    sort_order=20,
)
async def vehicle_query(ctx: OpenContext, params: dict, db) -> dict:
    from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle

    page, page_size = _page_args(params)
    keyword: Optional[str] = params.get("keyword")

    conds = [Vehicle.is_deleted == 0]
    if keyword:
        conds.append(Vehicle.plate_number.like(f"%{keyword}%"))

    total = await db.scalar(select(func.count()).select_from(Vehicle).where(*conds))
    rows = (
        await db.execute(
            select(Vehicle)
            .where(*conds)
            .order_by(Vehicle.id.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
    ).scalars().all()

    return {
        "list": [
            {
                "id": r.id,
                "plate_number": r.plate_number,
                "plate_category": r.plate_category,
                "status": r.status,
            }
            for r in rows
        ],
        "total": int(total or 0),
        "page": page,
        "pageSize": page_size,
    }


@register_capability(
    code="waybill.query",
    name="查询运单",
    category="运输管理",
    description="按运单号/客户关键字分页查询运单。",
    channels=["api", "mcp"],
    output_fields=[
        "id", "waybill_no", "customer_name", "origin", "destination", "quantity",
    ],
    sort_order=30,
)
async def waybill_query(ctx: OpenContext, params: dict, db) -> dict:
    from app.modules.client.models.waybill.waybill import Waybill

    page, page_size = _page_args(params)
    keyword: Optional[str] = params.get("keyword")

    conds = [Waybill.is_deleted == 0]
    if keyword:
        conds.append(Waybill.waybill_no.like(f"%{keyword}%"))

    total = await db.scalar(select(func.count()).select_from(Waybill).where(*conds))
    rows = (
        await db.execute(
            select(Waybill)
            .where(*conds)
            .order_by(Waybill.id.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
    ).scalars().all()

    return {
        "list": [
            {
                "id": r.id,
                "waybill_no": r.waybill_no,
                "customer_name": r.customer_name,
                "origin": r.origin,
                "destination": r.destination,
                "quantity": r.quantity,
            }
            for r in rows
        ],
        "total": int(total or 0),
        "page": page,
        "pageSize": page_size,
    }
