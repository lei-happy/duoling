"""
合作客户（反向视角）服务
B 视角：本租户作为承运商被哪些 A 公司纳入了合作关系。
数据源：sys_carrier_link.linked_tenant_code = current_tenant_code
"""

from typing import List, Tuple, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.system.carrier_link import CarrierLink
from app.modules.console.models.tenant.tenant import Tenant


class CarrierInboundService:

    @staticmethod
    async def list_page(
        platform_db: AsyncSession,
        linked_tenant_code: str,
        keyword: Optional[str] = None,
        link_status: Optional[int] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[dict], int]:
        """分页查询本租户作为承运商的合作客户列表。

        返回 dict 列表，其中字段已合并 sys_tenant 的实时基础信息（A 公司名称、联系人、地址等）。
        """
        # 主查询：左联 sys_tenant 拿对方企业基础信息
        base = (
            select(CarrierLink, Tenant)
            .outerjoin(
                Tenant,
                (Tenant.tenant_code == CarrierLink.source_tenant_code)
                & (Tenant.is_deleted == 0),
            )
            .where(
                CarrierLink.linked_tenant_code == linked_tenant_code,
                CarrierLink.is_deleted == 0,
            )
        )

        if link_status is not None:
            base = base.where(CarrierLink.link_status == link_status)

        if keyword:
            kw = f"%{keyword}%"
            base = base.where(
                (Tenant.tenant_name.like(kw))
                | (CarrierLink.source_tenant_name.like(kw))
                | (CarrierLink.source_carrier_name.like(kw))
            )

        # count
        count_stmt = (
            select(func.count())
            .select_from(CarrierLink)
            .outerjoin(
                Tenant,
                (Tenant.tenant_code == CarrierLink.source_tenant_code)
                & (Tenant.is_deleted == 0),
            )
            .where(
                CarrierLink.linked_tenant_code == linked_tenant_code,
                CarrierLink.is_deleted == 0,
            )
        )
        if link_status is not None:
            count_stmt = count_stmt.where(CarrierLink.link_status == link_status)
        if keyword:
            kw = f"%{keyword}%"
            count_stmt = count_stmt.where(
                (Tenant.tenant_name.like(kw))
                | (CarrierLink.source_tenant_name.like(kw))
                | (CarrierLink.source_carrier_name.like(kw))
            )

        total = (await platform_db.execute(count_stmt)).scalar() or 0

        rows_stmt = (
            base.order_by(CarrierLink.created_at.desc())
            .offset(max(0, (page - 1) * page_size))
            .limit(page_size)
        )
        rs = await platform_db.execute(rows_stmt)
        rows = rs.all()

        items: List[dict] = []
        for link, tenant in rows:
            items.append({
                "id": link.id,
                "sourceTenantCode": link.source_tenant_code,
                "sourceTenantName": (
                    (tenant.tenant_name if tenant else None)
                    or link.source_tenant_name
                ),
                "sourceTenantShortName": tenant.short_name if tenant else None,
                "sourceContactPerson": tenant.contact_person if tenant else None,
                "sourceContactPhone": tenant.contact_phone if tenant else None,
                "sourceProvince": tenant.province if tenant else None,
                "sourceCity": tenant.city if tenant else None,
                "sourceAddress": tenant.address if tenant else None,
                "sourceCarrierId": link.source_carrier_id,
                "sourceCarrierName": link.source_carrier_name,
                "cooperationStart": link.cooperation_start,
                "linkStatus": link.link_status,
                "createdAt": link.created_at,
            })
        return items, int(total)
