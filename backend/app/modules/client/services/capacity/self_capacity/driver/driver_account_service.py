"""
驾驶员账户管理服务（租户库）
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.models.capacity.self_capacity.driver.driver_account import DriverAccount
from app.modules.client.schemas.capacity.self_capacity.driver.driver_account import (
    DriverAccountCreate, DriverAccountUpdate, DriverAccountOut,
)


class DriverAccountService:

    @staticmethod
    async def list_accounts(
        db: AsyncSession, driver_id: int
    ) -> list[dict]:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        if not result.scalar_one_or_none():
            raise BizException("驾驶员不存在")

        result = await db.execute(
            select(DriverAccount).where(
                DriverAccount.driver_id == driver_id,
                DriverAccount.is_deleted == 0,
            ).order_by(DriverAccount.id.desc())
        )
        accounts = result.scalars().all()
        return [DriverAccountOut.from_model(a).model_dump() for a in accounts]

    @staticmethod
    async def create_account(
        db: AsyncSession, driver_id: int, data: DriverAccountCreate
    ) -> DriverAccountOut:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        if not result.scalar_one_or_none():
            raise BizException("驾驶员不存在")

        account = DriverAccount(
            driver_id=driver_id,
            enterprise_id=data.enterpriseId,
            account_type=data.accountType,
            account_name=data.accountName,
            account_no=data.accountNo,
            status=data.status or 1,
        )
        db.add(account)
        await db.flush()
        await db.refresh(account)
        return DriverAccountOut.from_model(account)

    @staticmethod
    async def update_account(
        db: AsyncSession, account_id: int, data: DriverAccountUpdate
    ) -> DriverAccountOut:
        result = await db.execute(
            select(DriverAccount).where(
                DriverAccount.id == account_id,
                DriverAccount.is_deleted == 0,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise BizException("账户不存在")

        update_data = data.model_dump(exclude_unset=True)
        field_map = {
            "accountType": "account_type",
            "enterpriseId": "enterprise_id",
            "accountName": "account_name",
            "accountNo": "account_no",
            "status": "status",
        }
        for schema_f, model_f in field_map.items():
            if schema_f in update_data:
                setattr(account, model_f, update_data[schema_f])

        await db.flush()
        await db.refresh(account)
        return DriverAccountOut.from_model(account)

    @staticmethod
    async def toggle_status(
        db: AsyncSession, account_id: int, status: int
    ) -> DriverAccountOut:
        result = await db.execute(
            select(DriverAccount).where(
                DriverAccount.id == account_id,
                DriverAccount.is_deleted == 0,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise BizException("账户不存在")
        account.status = status
        await db.flush()
        await db.refresh(account)
        return DriverAccountOut.from_model(account)

    @staticmethod
    async def delete_account(db: AsyncSession, account_id: int) -> None:
        result = await db.execute(
            select(DriverAccount).where(
                DriverAccount.id == account_id,
                DriverAccount.is_deleted == 0,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise BizException("账户不存在")
        account.is_deleted = 1
        await db.flush()
