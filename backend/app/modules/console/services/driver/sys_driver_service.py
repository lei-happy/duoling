"""
平台司机服务（zt_platform 库）
"""

from typing import Optional

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.driver.sys_driver import SysDriver
from app.modules.console.models.tenant.tenant import Tenant


class SysDriverService:

    @staticmethod
    async def sync_driver(
        db: AsyncSession,
        tenant_code: str,
        biz_driver_id: int,
        driver_code: str,
        name: str,
        phone: str,
        status: int = 1,
    ) -> SysDriver:
        """创建或更新平台司机记录"""
        result = await db.execute(
            select(SysDriver).where(
                SysDriver.tenant_code == tenant_code,
                SysDriver.biz_driver_id == biz_driver_id,
                SysDriver.is_deleted == 0,
            )
        )
        record = result.scalar_one_or_none()
        if record:
            record.driver_code = driver_code
            record.name = name
            record.phone = phone
            record.status = status
        else:
            record = SysDriver(
                tenant_code=tenant_code,
                biz_driver_id=biz_driver_id,
                driver_code=driver_code,
                name=name,
                phone=phone,
                status=status,
            )
            db.add(record)
        await db.flush()
        return record

    @staticmethod
    async def remove_driver(
        db: AsyncSession,
        tenant_code: str,
        biz_driver_id: int,
    ) -> None:
        """软删除平台司机"""
        result = await db.execute(
            select(SysDriver).where(
                SysDriver.tenant_code == tenant_code,
                SysDriver.biz_driver_id == biz_driver_id,
                SysDriver.is_deleted == 0,
            )
        )
        record = result.scalar_one_or_none()
        if record:
            record.is_deleted = 1
            await db.flush()

    @staticmethod
    async def page_drivers(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        tenant_code: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        """分页查询平台司机列表"""
        query = (
            select(
                SysDriver.id,
                SysDriver.tenant_code,
                Tenant.tenant_name.label("tenant_name"),
                SysDriver.biz_driver_id,
                SysDriver.driver_code,
                SysDriver.name,
                SysDriver.phone,
                SysDriver.status,
                SysDriver.created_at,
                SysDriver.updated_at,
            )
            .outerjoin(Tenant, Tenant.tenant_code == SysDriver.tenant_code)
            .where(SysDriver.is_deleted == 0)
        )

        if keyword:
            kw = f"%{keyword}%"
            query = query.where(
                or_(
                    SysDriver.name.like(kw),
                    SysDriver.phone.like(kw),
                    SysDriver.driver_code.like(kw),
                )
            )
        if tenant_code:
            query = query.where(SysDriver.tenant_code == tenant_code)
        if status is not None:
            query = query.where(SysDriver.status == status)

        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        query = query.order_by(SysDriver.id.desc()).offset(
            (page - 1) * limit
        ).limit(limit)
        result = await db.execute(query)
        rows = result.all()

        def _to_dict(r):
            return {
                "id": r.id,
                "tenantCode": r.tenant_code,
                "tenantName": r.tenant_name,
                "bizDriverId": r.biz_driver_id,
                "driverCode": r.driver_code,
                "name": r.name,
                "phone": r.phone,
                "status": r.status,
                "createdAt": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
                "updatedAt": r.updated_at.strftime("%Y-%m-%d %H:%M:%S") if r.updated_at else None,
            }

        return {"list": [_to_dict(r) for r in rows], "count": total}

    @staticmethod
    async def get_driver(db: AsyncSession, driver_id: int) -> Optional[dict]:
        """获取单条平台司机详情"""
        query = (
            select(
                SysDriver.id,
                SysDriver.tenant_code,
                Tenant.tenant_name.label("tenant_name"),
                SysDriver.biz_driver_id,
                SysDriver.driver_code,
                SysDriver.name,
                SysDriver.phone,
                SysDriver.status,
                SysDriver.created_at,
                SysDriver.updated_at,
            )
            .outerjoin(Tenant, Tenant.tenant_code == SysDriver.tenant_code)
            .where(SysDriver.id == driver_id, SysDriver.is_deleted == 0)
        )
        result = await db.execute(query)
        r = result.first()
        if not r:
            return None
        return {
            "id": r.id,
            "tenantCode": r.tenant_code,
            "tenantName": r.tenant_name,
            "bizDriverId": r.biz_driver_id,
            "driverCode": r.driver_code,
            "name": r.name,
            "phone": r.phone,
            "status": r.status,
            "createdAt": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else None,
            "updatedAt": r.updated_at.strftime("%Y-%m-%d %H:%M:%S") if r.updated_at else None,
        }
