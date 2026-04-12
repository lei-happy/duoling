"""
平台运力服务（zt_platform 库）
"""

from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.capacity.sys_capacity import SysCapacity
from app.modules.console.models.tenant.tenant import Tenant


class SysCapacityService:

    @staticmethod
    async def sync_capacity(
        db: AsyncSession,
        tenant_code: str,
        biz_capacity_id: int,
        driver_name: str,
        driver_phone: str,
        plate_number: str,
        status: int = 1,
        bound_at: Optional[datetime] = None,
        unbound_at: Optional[datetime] = None,
    ) -> SysCapacity:
        """创建或更新平台运力记录"""
        result = await db.execute(
            select(SysCapacity).where(
                SysCapacity.tenant_code == tenant_code,
                SysCapacity.biz_capacity_id == biz_capacity_id,
                SysCapacity.is_deleted == 0,
            )
        )
        record = result.scalar_one_or_none()
        if record:
            record.driver_name = driver_name
            record.driver_phone = driver_phone
            record.plate_number = plate_number
            record.status = status
            record.bound_at = bound_at
            record.unbound_at = unbound_at
        else:
            record = SysCapacity(
                tenant_code=tenant_code,
                biz_capacity_id=biz_capacity_id,
                driver_name=driver_name,
                driver_phone=driver_phone,
                plate_number=plate_number,
                status=status,
                bound_at=bound_at,
                unbound_at=unbound_at,
            )
            db.add(record)
        await db.flush()
        return record

    @staticmethod
    async def page_capacities(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        tenant_code: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        """分页查询平台运力列表"""
        query = (
            select(
                SysCapacity.id,
                SysCapacity.tenant_code,
                Tenant.tenant_name.label("tenant_name"),
                SysCapacity.biz_capacity_id,
                SysCapacity.driver_name,
                SysCapacity.driver_phone,
                SysCapacity.plate_number,
                SysCapacity.status,
                SysCapacity.bound_at,
                SysCapacity.unbound_at,
                SysCapacity.created_at,
                SysCapacity.updated_at,
            )
            .outerjoin(Tenant, Tenant.tenant_code == SysCapacity.tenant_code)
            .where(SysCapacity.is_deleted == 0)
        )

        if keyword:
            kw = f"%{keyword}%"
            query = query.where(
                or_(
                    SysCapacity.driver_name.like(kw),
                    SysCapacity.driver_phone.like(kw),
                    SysCapacity.plate_number.like(kw),
                )
            )
        if tenant_code:
            query = query.where(SysCapacity.tenant_code == tenant_code)
        if status is not None:
            query = query.where(SysCapacity.status == status)

        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        query = query.order_by(SysCapacity.id.desc()).offset(
            (page - 1) * limit
        ).limit(limit)
        result = await db.execute(query)
        rows = result.all()

        def _to_dict(r):
            return {
                "id": r.id,
                "tenantCode": r.tenant_code,
                "tenantName": r.tenant_name,
                "bizCapacityId": r.biz_capacity_id,
                "driverName": r.driver_name,
                "driverPhone": r.driver_phone,
                "plateNumber": r.plate_number,
                "status": r.status,
                "boundAt": r.bound_at.strftime("%Y-%m-%d %H:%M:%S") if r.bound_at else None,
                "unboundAt": r.unbound_at.strftime("%Y-%m-%d %H:%M:%S") if r.unbound_at else None,
                "createdAt": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
                "updatedAt": r.updated_at.strftime("%Y-%m-%d %H:%M:%S") if r.updated_at else None,
            }

        return {"list": [_to_dict(r) for r in rows], "count": total}

    @staticmethod
    async def get_capacity(db: AsyncSession, capacity_id: int) -> Optional[dict]:
        """获取单条平台运力详情"""
        query = (
            select(
                SysCapacity.id,
                SysCapacity.tenant_code,
                Tenant.tenant_name.label("tenant_name"),
                SysCapacity.biz_capacity_id,
                SysCapacity.driver_name,
                SysCapacity.driver_phone,
                SysCapacity.plate_number,
                SysCapacity.status,
                SysCapacity.bound_at,
                SysCapacity.unbound_at,
                SysCapacity.created_at,
                SysCapacity.updated_at,
            )
            .outerjoin(Tenant, Tenant.tenant_code == SysCapacity.tenant_code)
            .where(SysCapacity.id == capacity_id, SysCapacity.is_deleted == 0)
        )
        result = await db.execute(query)
        r = result.first()
        if not r:
            return None
        return {
            "id": r.id,
            "tenantCode": r.tenant_code,
            "tenantName": r.tenant_name,
            "bizCapacityId": r.biz_capacity_id,
            "driverName": r.driver_name,
            "driverPhone": r.driver_phone,
            "plateNumber": r.plate_number,
            "status": r.status,
            "boundAt": r.bound_at.strftime("%Y-%m-%d %H:%M:%S") if r.bound_at else None,
            "unboundAt": r.unbound_at.strftime("%Y-%m-%d %H:%M:%S") if r.unbound_at else None,
            "createdAt": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
            "updatedAt": r.updated_at.strftime("%Y-%m-%d %H:%M:%S") if r.updated_at else None,
        }
