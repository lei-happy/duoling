"""
驾驶员资金账户（往来账）服务

核心保证：
- 记账走行锁（``SELECT ... FOR UPDATE``），读余额→算新余额→插流水→更新账户，全部同一事务；
- 余额只能被流水改变，``account.balance == Σ transaction.delta``；
- 流水 append-only，写错只能新增反向冲正流水（不 update/delete）。
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.models.capacity.social_capacity.social_capacity import (
    SocialCapacity,
)
from app.modules.client.models.capacity.self_capacity.driver.driver_fund_account import (
    DriverFundAccount,
)
from app.modules.client.models.capacity.self_capacity.driver.driver_fund_transaction import (
    DriverFundTransaction,
)
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.schemas.capacity.self_capacity.driver.driver_fund_account import (
    DriverFundAccountOut,
    DriverFundTransactionCreate,
    DriverFundTransactionOut,
)

# 业务类型常量（对齐 biz_driver_fund_transaction.biz_type 注释）
BIZ_TYPE_PREPAY_REGISTER = 1   # 预付登记（delta<0，系统联动亦复用）
BIZ_TYPE_PREPAY_REVERSE = 2    # 退款入账 / 预付冲正（delta>0）
BIZ_TYPE_MANUAL_IN = 3         # 人工入账（delta>0）
BIZ_TYPE_MANUAL_OUT = 4        # 人工出账（delta<0）
BIZ_TYPE_ADJUST = 5            # 人工调整（由 direction 决定符号，强制备注）

# 手工业务类型对应的余额变动方向（正=入账/余额增；负=出账/余额减）
_MANUAL_BIZ_SIGN = {
    BIZ_TYPE_PREPAY_REGISTER: -1,  # 预付登记（司机占用公司资金）
    BIZ_TYPE_PREPAY_REVERSE: +1,   # 退款入账
    BIZ_TYPE_MANUAL_IN: +1,        # 人工入账
    BIZ_TYPE_MANUAL_OUT: -1,       # 人工出账
    # BIZ_TYPE_ADJUST 人工调整：由 direction 决定符号
}
_MANUAL_BIZ_TYPES = {
    BIZ_TYPE_PREPAY_REGISTER, BIZ_TYPE_PREPAY_REVERSE,
    BIZ_TYPE_MANUAL_IN, BIZ_TYPE_MANUAL_OUT, BIZ_TYPE_ADJUST,
}

# 流水方向（direction，由 delta 符号派生）
DIRECTION_IN = 1
DIRECTION_OUT = 2

# 流水来源
SOURCE_MANUAL = 1
SOURCE_SYSTEM = 2

# 收款方类型（owner_type）
OWNER_DRIVER = 1   # 自有司机 biz_driver.id
OWNER_CARRIER = 2  # 承运商（预留）
OWNER_SOCIAL = 3   # 社会运力 biz_social_capacity.id
_VALID_OWNER_TYPES = {OWNER_DRIVER, OWNER_CARRIER, OWNER_SOCIAL}

# 账户状态
STATUS_NORMAL = 1
STATUS_FROZEN = 0

# 人工调整强制备注最小长度
MANUAL_REMARK_MIN_LEN = 5

# 流水台账分页上限
MAX_PAGE_SIZE = 100


class DriverFundAccountService:
    """驾驶员资金账户"""

    # ------------------------------------------------------------------
    # 流水号生成
    # ------------------------------------------------------------------
    @staticmethod
    async def _generate_txn_no(db: AsyncSession) -> str:
        today = date.today().strftime("%Y%m%d")
        prefix = f"DF{today}"
        r = await db.execute(
            select(func.count(DriverFundTransaction.id)).where(
                DriverFundTransaction.txn_no.like(f"{prefix}%")
            )
        )
        cnt = int(r.scalar() or 0) + 1
        return f"{prefix}{cnt:05d}"

    # ------------------------------------------------------------------
    # 账户获取 / 懒创建
    # ------------------------------------------------------------------
    @staticmethod
    async def _ensure_owner(
        db: AsyncSession, owner_type: int, owner_id: int
    ) -> None:
        """校验收款方存在：type=1 自有司机，type=3 社会运力。"""
        if owner_type not in _VALID_OWNER_TYPES:
            raise BizException("不支持的收款方类型")
        if owner_type == OWNER_DRIVER:
            exists = (await db.execute(
                select(Driver.id).where(
                    Driver.id == owner_id, Driver.is_deleted == 0
                )
            )).scalar_one_or_none()
            if not exists:
                raise BizException("驾驶员不存在")
        elif owner_type == OWNER_SOCIAL:
            exists = (await db.execute(
                select(SocialCapacity.id).where(
                    SocialCapacity.id == owner_id,
                    SocialCapacity.is_deleted == 0,
                )
            )).scalar_one_or_none()
            if not exists:
                raise BizException("社会运力不存在")
        else:
            raise BizException("承运商资金账户暂未开放")

    @staticmethod
    async def _resolve_enterprise_id(
        db: AsyncSession, enterprise_id: Optional[int]
    ) -> int:
        """把 None 归一到租户默认经营主体，保证账户按主体唯一定位。"""
        if enterprise_id:
            return enterprise_id
        from app.modules.client.services.organization.business_entity_service import (
            BusinessEntityService,
        )
        default_entity = await BusinessEntityService.ensure_default(db)
        return default_entity.id

    @staticmethod
    async def _get_or_create(
        db: AsyncSession, owner_type: int, owner_id: int,
        enterprise_id: Optional[int],
        *, for_update: bool = False,
    ) -> DriverFundAccount:
        # 账户按 (owner_type, owner_id, enterprise_id) 唯一定位（uk_dfa_owner_ent）。
        # enterprise_id 为空时归一到租户默认经营主体，避免 NULL 造成账户碎裂。
        enterprise_id = await DriverFundAccountService._resolve_enterprise_id(
            db, enterprise_id
        )
        stmt = select(DriverFundAccount).where(
            DriverFundAccount.owner_type == owner_type,
            DriverFundAccount.owner_id == owner_id,
            DriverFundAccount.enterprise_id == enterprise_id,
            DriverFundAccount.is_deleted == 0,
        )
        if for_update:
            stmt = stmt.with_for_update()
        acc = (await db.execute(stmt)).scalar_one_or_none()
        if acc:
            return acc

        acc = DriverFundAccount(
            owner_type=owner_type,
            owner_id=owner_id,
            enterprise_id=enterprise_id,
            balance=Decimal("0"),
            frozen_amount=Decimal("0"),
            total_in=Decimal("0"),
            total_out=Decimal("0"),
            status=STATUS_NORMAL,
        )
        db.add(acc)
        await db.flush()
        # 回填服务端默认值（created_at/updated_at），避免后续属性访问触发同步懒加载
        await db.refresh(acc)
        if for_update:
            # 重新以行锁读取，保证后续记账并发安全
            acc = (
                await db.execute(
                    select(DriverFundAccount)
                    .where(DriverFundAccount.id == acc.id)
                    .with_for_update()
                )
            ).scalar_one()
        return acc

    # ------------------------------------------------------------------
    # 查询：账户
    # ------------------------------------------------------------------
    @staticmethod
    async def get_account(
        db: AsyncSession, owner_id: int, enterprise_id: Optional[int] = None,
        *, owner_type: int = OWNER_DRIVER,
    ) -> DriverFundAccountOut:
        await DriverFundAccountService._ensure_owner(db, owner_type, owner_id)
        acc = await DriverFundAccountService._get_or_create(
            db, owner_type, owner_id, enterprise_id
        )
        return DriverFundAccountOut.from_model(acc)

    # ------------------------------------------------------------------
    # 查询：流水台账（分页）
    # ------------------------------------------------------------------
    @staticmethod
    async def list_transactions(
        db: AsyncSession,
        owner_id: int,
        *,
        owner_type: int = OWNER_DRIVER,
        biz_type: Optional[int] = None,
        source: Optional[int] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[list[dict], int]:
        conds = [
            DriverFundTransaction.owner_type == owner_type,
            DriverFundTransaction.owner_id == owner_id,
            DriverFundTransaction.is_deleted == 0,
        ]
        if biz_type is not None:
            conds.append(DriverFundTransaction.biz_type == biz_type)
        if source is not None:
            conds.append(DriverFundTransaction.source == source)
        if start is not None:
            conds.append(DriverFundTransaction.created_at >= start)
        if end is not None:
            conds.append(DriverFundTransaction.created_at < end)

        total = int(
            (await db.execute(
                select(func.count(DriverFundTransaction.id)).where(*conds)
            )).scalar_one()
        )

        page = max(1, page)
        page_size = max(1, min(page_size, MAX_PAGE_SIZE))
        rows = (
            await db.execute(
                select(DriverFundTransaction)
                .where(*conds)
                .order_by(
                    DriverFundTransaction.created_at.desc(),
                    DriverFundTransaction.id.desc(),
                )
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        items = [
            DriverFundTransactionOut.from_model(t).model_dump() for t in rows
        ]
        return items, total

    # ------------------------------------------------------------------
    # 记账（行锁 + 原子写流水）
    # ------------------------------------------------------------------
    @staticmethod
    def _resolve_delta(
        biz_type: int, amount: Decimal, direction: Optional[int]
    ) -> Decimal:
        if biz_type == BIZ_TYPE_ADJUST:
            if direction not in (DIRECTION_IN, DIRECTION_OUT):
                raise BizException("人工调整必须指定方向 direction（1-入 2-出）")
            sign = 1 if direction == DIRECTION_IN else -1
        else:
            sign = _MANUAL_BIZ_SIGN[biz_type]
        return (amount if sign > 0 else -amount)

    @staticmethod
    async def post_transaction(
        db: AsyncSession,
        owner_id: int,
        data: DriverFundTransactionCreate,
        *,
        operator_id: Optional[int],
        enterprise_id: Optional[int] = None,
        owner_type: int = OWNER_DRIVER,
    ) -> DriverFundTransactionOut:
        if data.bizType not in _MANUAL_BIZ_TYPES:
            raise BizException("不支持的记账类型")
        if data.amount is None or data.amount <= 0:
            raise BizException("金额必须大于 0")
        if data.bizType == BIZ_TYPE_ADJUST:
            if not data.remark or len(data.remark.strip()) < MANUAL_REMARK_MIN_LEN:
                raise BizException(
                    f"人工调整必须填写不少于 {MANUAL_REMARK_MIN_LEN} 字的备注"
                )

        await DriverFundAccountService._ensure_owner(db, owner_type, owner_id)
        acc = await DriverFundAccountService._get_or_create(
            db, owner_type, owner_id, enterprise_id, for_update=True
        )
        if acc.status == STATUS_FROZEN:
            raise BizException("账户已冻结，禁止记账")

        delta = DriverFundAccountService._resolve_delta(
            data.bizType, data.amount, data.direction
        )
        operator_name = await DriverFundAccountService._resolve_operator_name(
            db, operator_id
        )
        txn = await DriverFundAccountService._write_txn(
            db, acc,
            biz_type=data.bizType,
            delta=delta,
            amount=data.amount,
            source=SOURCE_MANUAL,
            operator_id=operator_id,
            operator_name=operator_name,
            related_task_id=data.relatedTaskId,
            related_finance_doc_id=data.relatedFinanceDocId,
            voucher_url=data.voucherUrl,
            remark=data.remark,
        )
        return DriverFundTransactionOut.from_model(txn)

    # ------------------------------------------------------------------
    # 通用写流水（要求 acc 已行锁；余额与流水同事务原子更新）
    # ------------------------------------------------------------------
    @staticmethod
    async def _write_txn(
        db: AsyncSession,
        acc: DriverFundAccount,
        *,
        biz_type: int,
        delta: Decimal,
        amount: Decimal,
        source: int,
        operator_id: Optional[int],
        operator_name: Optional[str],
        related_task_id: Optional[int] = None,
        related_finance_doc_id: Optional[int] = None,
        voucher_url: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> DriverFundTransaction:
        before = acc.balance or Decimal("0")
        after = before + delta
        txn = DriverFundTransaction(
            account_id=acc.id,
            owner_type=acc.owner_type,
            owner_id=acc.owner_id,
            enterprise_id=acc.enterprise_id,
            txn_no=await DriverFundAccountService._generate_txn_no(db),
            biz_type=biz_type,
            direction=DIRECTION_IN if delta > 0 else DIRECTION_OUT,
            amount=amount,
            delta=delta,
            balance_before=before,
            balance_after=after,
            related_task_id=related_task_id,
            related_finance_doc_id=related_finance_doc_id,
            source=source,
            operator_id=operator_id,
            operator_name=operator_name,
            voucher_url=voucher_url,
            remark=remark,
        )
        db.add(txn)
        acc.balance = after
        if delta > 0:
            acc.total_in = (acc.total_in or Decimal("0")) + delta
        else:
            acc.total_out = (acc.total_out or Decimal("0")) + (-delta)
        acc.last_txn_at = datetime.now()
        await db.flush()
        await db.refresh(txn)
        return txn

    # ------------------------------------------------------------------
    # 系统联动：预付单支付 → 预付登记；撤销支付 → 冲正
    # ------------------------------------------------------------------
    @staticmethod
    async def system_register_prepay(
        db: AsyncSession,
        *,
        owner_id: int,
        amount: Decimal,
        enterprise_id: Optional[int],
        task_id: Optional[int],
        finance_doc_id: int,
        operator_id: Optional[int],
        doc_no: Optional[str] = None,
        owner_type: int = OWNER_DRIVER,
    ) -> Optional[DriverFundTransaction]:
        """预付单支付后登记为账户预付（delta<0：收款方占用公司资金）。幂等。"""
        if amount is None or amount <= 0:
            return None
        # 幂等：同一费用单已登记过则跳过
        exists = (
            await db.execute(
                select(DriverFundTransaction.id).where(
                    DriverFundTransaction.related_finance_doc_id == finance_doc_id,
                    DriverFundTransaction.biz_type == BIZ_TYPE_PREPAY_REGISTER,
                    DriverFundTransaction.source == SOURCE_SYSTEM,
                    DriverFundTransaction.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if exists:
            return None

        acc = await DriverFundAccountService._get_or_create(
            db, owner_type, owner_id, enterprise_id, for_update=True
        )
        operator_name = await DriverFundAccountService._resolve_operator_name(
            db, operator_id
        )
        return await DriverFundAccountService._write_txn(
            db, acc,
            biz_type=BIZ_TYPE_PREPAY_REGISTER,
            delta=-amount,
            amount=amount,
            source=SOURCE_SYSTEM,
            operator_id=operator_id,
            operator_name=operator_name,
            related_task_id=task_id,
            related_finance_doc_id=finance_doc_id,
            remark=f"预付单支付自动登记{f'（{doc_no}）' if doc_no else ''}",
        )

    @staticmethod
    async def system_reverse_prepay(
        db: AsyncSession,
        *,
        finance_doc_id: int,
        operator_id: Optional[int],
        doc_no: Optional[str] = None,
    ) -> Optional[DriverFundTransaction]:
        """撤销预付单支付 → 冲正之前的预付登记（delta>0）。幂等。"""
        # 找到原始预付登记
        origin = (
            await db.execute(
                select(DriverFundTransaction).where(
                    DriverFundTransaction.related_finance_doc_id == finance_doc_id,
                    DriverFundTransaction.biz_type == BIZ_TYPE_PREPAY_REGISTER,
                    DriverFundTransaction.source == SOURCE_SYSTEM,
                    DriverFundTransaction.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not origin:
            return None
        # 幂等：已冲正过则跳过
        reversed_exists = (
            await db.execute(
                select(DriverFundTransaction.id).where(
                    DriverFundTransaction.related_finance_doc_id == finance_doc_id,
                    DriverFundTransaction.biz_type == BIZ_TYPE_PREPAY_REVERSE,
                    DriverFundTransaction.source == SOURCE_SYSTEM,
                    DriverFundTransaction.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if reversed_exists:
            return None

        acc = (
            await db.execute(
                select(DriverFundAccount)
                .where(DriverFundAccount.id == origin.account_id)
                .with_for_update()
            )
        ).scalar_one_or_none()
        if not acc:
            return None
        operator_name = await DriverFundAccountService._resolve_operator_name(
            db, operator_id
        )
        return await DriverFundAccountService._write_txn(
            db, acc,
            biz_type=BIZ_TYPE_PREPAY_REVERSE,
            delta=origin.amount,
            amount=origin.amount,
            source=SOURCE_SYSTEM,
            operator_id=operator_id,
            operator_name=operator_name,
            related_task_id=origin.related_task_id,
            related_finance_doc_id=finance_doc_id,
            remark=f"撤销预付单支付自动冲正{f'（{doc_no}）' if doc_no else ''}",
        )

    # ------------------------------------------------------------------
    # 冻结 / 解冻
    # ------------------------------------------------------------------
    @staticmethod
    async def toggle_status(
        db: AsyncSession, account_id: int, status: int
    ) -> DriverFundAccountOut:
        if status not in (STATUS_NORMAL, STATUS_FROZEN):
            raise BizException("非法状态值")
        acc = (
            await db.execute(
                select(DriverFundAccount).where(
                    DriverFundAccount.id == account_id,
                    DriverFundAccount.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not acc:
            raise BizException("资金账户不存在")
        acc.status = status
        await db.flush()
        await db.refresh(acc)
        return DriverFundAccountOut.from_model(acc)

    # ------------------------------------------------------------------
    # 工具
    # ------------------------------------------------------------------
    @staticmethod
    async def _resolve_operator_name(
        db: AsyncSession, operator_id: Optional[int]
    ) -> Optional[str]:
        if not operator_id:
            return None
        u = (
            await db.execute(
                select(BizUser).where(
                    BizUser.id == operator_id, BizUser.is_deleted == 0
                )
            )
        ).scalar_one_or_none()
        if not u:
            return None
        return u.nickname or u.real_name or u.phone
