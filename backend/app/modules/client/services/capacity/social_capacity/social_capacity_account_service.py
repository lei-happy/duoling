"""
社会运力 - 结算账户服务

负责一对多结算账户的 CRUD 与默认账户互斥逻辑：
  - 新增首条自动设为默认
  - 设置默认时把同 social_capacity_id 内其他账户的 is_default 置 0
  - 删除当前默认账户后自动把"创建时间最早的正常账户"提升为新的默认
"""

from typing import List, Optional

from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.social_capacity.social_capacity import (
    SocialCapacity,
)
from app.modules.client.models.capacity.social_capacity.social_capacity_account import (
    SocialCapacityAccount,
)
from app.modules.client.schemas.capacity.social_capacity.social_capacity_account import (
    SocialCapacityAccountCreate,
    SocialCapacityAccountUpdate,
    SocialCapacityAccountOut,
)


class SocialCapacityAccountService:
    """结算账户服务"""

    # ------------------------------ 内部 ------------------------------
    @staticmethod
    async def _ensure_capacity_exists(
        db: AsyncSession, social_capacity_id: int
    ) -> SocialCapacity:
        result = await db.execute(
            select(SocialCapacity).where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("社会运力不存在")
        return capacity

    @staticmethod
    async def _clear_other_defaults(
        db: AsyncSession, social_capacity_id: int, exclude_account_id: int
    ) -> None:
        """把同 social_capacity_id 内其他账户的 is_default 全部置 0。"""
        result = await db.execute(
            select(SocialCapacityAccount).where(
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
                SocialCapacityAccount.id != exclude_account_id,
                SocialCapacityAccount.is_default == 1,
            )
        )
        for acc in result.scalars().all():
            acc.is_default = 0

    @staticmethod
    async def _ensure_default_after_change(
        db: AsyncSession, social_capacity_id: int
    ) -> None:
        """删除 / 停用 / 删默认 之后兜底：若当前没有默认账户，则把创建时间最早的正常账户置默认。"""
        result = await db.execute(
            select(SocialCapacityAccount).where(
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
                SocialCapacityAccount.is_default == 1,
            )
        )
        if result.scalar_one_or_none():
            return
        candidate_q = (
            select(SocialCapacityAccount)
            .where(
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
                SocialCapacityAccount.status == 1,
            )
            .order_by(asc(SocialCapacityAccount.created_at), asc(SocialCapacityAccount.id))
            .limit(1)
        )
        candidate = (await db.execute(candidate_q)).scalar_one_or_none()
        if candidate:
            candidate.is_default = 1

    # ------------------------------ 查询 ------------------------------
    @staticmethod
    async def list_accounts(
        db: AsyncSession, social_capacity_id: int
    ) -> List[dict]:
        await SocialCapacityAccountService._ensure_capacity_exists(db, social_capacity_id)

        result = await db.execute(
            select(SocialCapacityAccount)
            .where(
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
            )
            .order_by(
                SocialCapacityAccount.is_default.desc(),
                asc(SocialCapacityAccount.created_at),
                asc(SocialCapacityAccount.id),
            )
        )
        accounts = result.scalars().all()
        return [SocialCapacityAccountOut.from_model(a).model_dump() for a in accounts]

    @staticmethod
    async def get_default(
        db: AsyncSession, social_capacity_id: int
    ) -> Optional[SocialCapacityAccount]:
        result = await db.execute(
            select(SocialCapacityAccount).where(
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
                SocialCapacityAccount.is_default == 1,
            )
        )
        return result.scalar_one_or_none()

    # ------------------------------ 写 ------------------------------
    @staticmethod
    async def create_account(
        db: AsyncSession,
        social_capacity_id: int,
        data: SocialCapacityAccountCreate,
    ) -> SocialCapacityAccountOut:
        await SocialCapacityAccountService._ensure_capacity_exists(db, social_capacity_id)

        # 判断是否需要自动设为默认（首条账户）
        existing_q = await db.execute(
            select(SocialCapacityAccount.id).where(
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
            )
        )
        is_first = existing_q.first() is None
        is_default = data.isDefault if (data.isDefault is not None) else 0
        if is_first:
            is_default = 1

        account = SocialCapacityAccount(
            social_capacity_id=social_capacity_id,
            account_type=data.accountType,
            account_label=data.accountLabel,
            account_name=data.accountName,
            account_no=data.accountNo,
            bank_name=data.bankName,
            bank_branch=data.bankBranch,
            holder_id_card=data.holderIdCard,
            is_default=is_default,
            status=data.status if data.status is not None else 1,
            remark=data.remark,
        )
        db.add(account)
        await db.flush()

        if is_default == 1:
            await SocialCapacityAccountService._clear_other_defaults(
                db, social_capacity_id, account.id
            )

        await db.flush()
        await db.refresh(account)
        return SocialCapacityAccountOut.from_model(account)

    @staticmethod
    async def update_account(
        db: AsyncSession,
        social_capacity_id: int,
        account_id: int,
        data: SocialCapacityAccountUpdate,
    ) -> SocialCapacityAccountOut:
        result = await db.execute(
            select(SocialCapacityAccount).where(
                SocialCapacityAccount.id == account_id,
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise BizException("结算账户不存在")

        update = data.model_dump(exclude_unset=True)
        field_map = {
            "accountType": "account_type",
            "accountLabel": "account_label",
            "accountName": "account_name",
            "accountNo": "account_no",
            "bankName": "bank_name",
            "bankBranch": "bank_branch",
            "holderIdCard": "holder_id_card",
            "isDefault": "is_default",
            "status": "status",
            "remark": "remark",
        }
        for k, m in field_map.items():
            if k in update:
                setattr(account, m, update[k])

        await db.flush()

        if update.get("isDefault") == 1:
            await SocialCapacityAccountService._clear_other_defaults(
                db, social_capacity_id, account.id
            )
        elif update.get("status") == 0 and account.is_default == 1:
            account.is_default = 0
            await SocialCapacityAccountService._ensure_default_after_change(
                db, social_capacity_id
            )

        await db.flush()
        await db.refresh(account)
        return SocialCapacityAccountOut.from_model(account)

    @staticmethod
    async def delete_account(
        db: AsyncSession,
        social_capacity_id: int,
        account_id: int,
    ) -> None:
        result = await db.execute(
            select(SocialCapacityAccount).where(
                SocialCapacityAccount.id == account_id,
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise BizException("结算账户不存在")

        was_default = account.is_default == 1
        account.is_deleted = 1
        account.is_default = 0
        await db.flush()

        if was_default:
            await SocialCapacityAccountService._ensure_default_after_change(
                db, social_capacity_id
            )
            await db.flush()

    @staticmethod
    async def set_default(
        db: AsyncSession,
        social_capacity_id: int,
        account_id: int,
    ) -> SocialCapacityAccountOut:
        result = await db.execute(
            select(SocialCapacityAccount).where(
                SocialCapacityAccount.id == account_id,
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
            )
        )
        account = result.scalar_one_or_none()
        if not account:
            raise BizException("结算账户不存在")
        if account.status != 1:
            raise BizException("仅启用状态的账户可设为默认")

        account.is_default = 1
        await SocialCapacityAccountService._clear_other_defaults(
            db, social_capacity_id, account.id
        )
        await db.flush()
        await db.refresh(account)
        return SocialCapacityAccountOut.from_model(account)
