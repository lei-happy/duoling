"""银行账户 Service（文档 10 §3.3）

账户是主数据，不走单据状态机，所以这里不继承 ``FinanceDocService``。

``balance`` 是**账面值**：由收款登记与打款执行两个动作维护，不与银行真实余额自动
对平（手续费、利息、跨行在途都会让两者有差）。要对齐就用「余额校准」，校准必须填
原因并留痕——账面余额被人悄悄改过是查账时最难受的情况。
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Any, List, Optional, Tuple

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.bank_account import BankAccount
from app.modules.client.services.finance.base.constants import (
    AccountUsageScope,
    BankAccountType,
)
from app.modules.client.services.finance.base.finance_doc_event_writer import (
    FinanceDocEventWriter,
    FinanceEventType,
)

_CENT = Decimal("0.01")
# 账户维度的事件用虚拟大类，doc_id 记账户 ID（账户不是单据，没有 doc_no）
ACCOUNT_DOC_KIND = "bank_account"


class BankAccountService:
    """企业银行账户主数据"""

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    @classmethod
    async def get_or_404(cls, db: AsyncSession, account_id: int) -> BankAccount:
        r = await db.execute(
            select(BankAccount).where(
                BankAccount.id == account_id, BankAccount.is_deleted == 0,
            )
        )
        account = r.scalar_one_or_none()
        if account is None:
            raise BizException("银行账户不存在或已删除")
        return account

    @classmethod
    async def page_list(
        cls,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        enterprise_id: Optional[int] = None,
        account_type: Optional[int] = None,
        usage_scope: Optional[int] = None,
        status: Optional[int] = None,
    ) -> Tuple[List[BankAccount], int]:
        stmt = select(BankAccount).where(BankAccount.is_deleted == 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                BankAccount.account_name.like(kw)
                | BankAccount.account_no.like(kw)
                | BankAccount.bank_name.like(kw)
            )
        if enterprise_id:
            stmt = stmt.where(BankAccount.enterprise_id == enterprise_id)
        if account_type is not None:
            stmt = stmt.where(BankAccount.account_type == account_type)
        if usage_scope is not None:
            stmt = stmt.where(BankAccount.usage_scope == usage_scope)
        if status is not None:
            stmt = stmt.where(BankAccount.status == status)

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(
                BankAccount.sort_order.asc(), BankAccount.id.asc(),
            )
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def options(
        cls,
        db: AsyncSession,
        *,
        enterprise_id: Optional[int] = None,
        for_pay: Optional[bool] = None,
    ) -> List[BankAccount]:
        """下拉用：只返回启用中的账户，并按用途过滤。

        ``for_pay=True`` 时排除「仅收款」账户，反之排除「仅付款」——把明显不该出现的
        账户先滤掉，比让出纳自己认要省事。
        """
        stmt = select(BankAccount).where(
            BankAccount.is_deleted == 0, BankAccount.status == 1,
        )
        if enterprise_id:
            stmt = stmt.where(BankAccount.enterprise_id == enterprise_id)
        if for_pay is True:
            stmt = stmt.where(
                BankAccount.usage_scope != AccountUsageScope.RECEIVE_ONLY
            )
        elif for_pay is False:
            stmt = stmt.where(
                BankAccount.usage_scope != AccountUsageScope.PAY_ONLY
            )
        r = await db.execute(
            stmt.order_by(BankAccount.sort_order.asc(), BankAccount.id.asc())
        )
        return list(r.scalars().all())

    # ------------------------------------------------------------------
    # 建档与维护
    # ------------------------------------------------------------------
    @classmethod
    async def create(
        cls,
        db: AsyncSession,
        *,
        enterprise_id: int,
        account_name: str,
        account_no: str,
        bank_name: Optional[str] = None,
        bank_branch: Optional[str] = None,
        account_type: int = BankAccountType.GENERAL,
        currency: str = "CNY",
        usage_scope: int = AccountUsageScope.BOTH,
        balance: Optional[Decimal] = None,
        is_default_receive: int = 0,
        is_default_pay: int = 0,
        sort_order: int = 0,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> BankAccount:
        name = (account_name or "").strip()
        no = (account_no or "").strip()
        if not name:
            raise BizException("请填写账户名称（户名）")
        if not no:
            raise BizException("请填写银行账号")
        await cls._assert_no_duplicate(db, no)

        account = BankAccount(
            enterprise_id=int(enterprise_id),
            account_name=name,
            account_no=no,
            bank_name=bank_name,
            bank_branch=bank_branch,
            account_type=int(account_type),
            currency=(currency or "CNY").strip().upper(),
            usage_scope=int(usage_scope),
            balance=_money(balance or 0),
            is_default_receive=int(is_default_receive or 0),
            is_default_pay=int(is_default_pay or 0),
            sort_order=int(sort_order or 0),
            remark=remark,
            dedup_key=BankAccount.build_dedup_key(no),
        )
        db.add(account)
        await db.flush()
        await cls._apply_default_flags(db, account)
        await FinanceDocEventWriter.write(
            db,
            doc_kind=ACCOUNT_DOC_KIND,
            doc_id=account.id,
            event_type=FinanceEventType.CREATE,
            operator_id=operator_id,
            occurred_amount=account.balance,
            reason=f"新建银行账户 {account.display_label}",
        )
        await db.flush()
        return account

    @classmethod
    async def update(
        cls,
        db: AsyncSession,
        account_id: int,
        *,
        account_name: Optional[str] = None,
        account_no: Optional[str] = None,
        bank_name: Optional[str] = None,
        bank_branch: Optional[str] = None,
        account_type: Optional[int] = None,
        currency: Optional[str] = None,
        usage_scope: Optional[int] = None,
        is_default_receive: Optional[int] = None,
        is_default_pay: Optional[int] = None,
        status: Optional[int] = None,
        sort_order: Optional[int] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> BankAccount:
        """维护账户信息。余额不在这里改——改余额一律走「校准」。"""
        account = await cls.get_or_404(db, account_id)
        if account_no is not None:
            no = account_no.strip()
            if not no:
                raise BizException("请填写银行账号")
            if no != account.account_no:
                await cls._assert_no_duplicate(db, no, exclude_id=account_id)
                account.account_no = no
                account.dedup_key = BankAccount.build_dedup_key(no)
        if account_name is not None:
            if not account_name.strip():
                raise BizException("请填写账户名称（户名）")
            account.account_name = account_name.strip()
        if bank_name is not None:
            account.bank_name = bank_name
        if bank_branch is not None:
            account.bank_branch = bank_branch
        if account_type is not None:
            account.account_type = int(account_type)
        if currency is not None:
            account.currency = currency.strip().upper()
        if usage_scope is not None:
            account.usage_scope = int(usage_scope)
        if is_default_receive is not None:
            account.is_default_receive = int(is_default_receive)
        if is_default_pay is not None:
            account.is_default_pay = int(is_default_pay)
        if status is not None:
            account.status = int(status)
        if sort_order is not None:
            account.sort_order = int(sort_order)
        if remark is not None:
            account.remark = remark
        await db.flush()
        await cls._apply_default_flags(db, account)
        return account

    @classmethod
    async def set_status(
        cls,
        db: AsyncSession,
        account_id: int,
        status: int,
        operator_id: Optional[int] = None,
    ) -> BankAccount:
        """启用 / 停用。停用只影响新单据选账户，不动历史记录。"""
        account = await cls.get_or_404(db, account_id)
        account.status = 1 if int(status) == 1 else 0
        if account.status == 0:
            account.is_default_receive = 0
            account.is_default_pay = 0
        await db.flush()
        return account

    @classmethod
    async def soft_delete(cls, db: AsyncSession, account_id: int) -> None:
        """删除账户。有余额或已产生流水的账户不许删，只能停用。"""
        account = await cls.get_or_404(db, account_id)
        if Decimal(str(account.balance or 0)) != 0:
            raise BizException(
                "这个账户账面还有余额，不能删除；如果不再使用请改成「停用」"
            )
        if await cls._has_flow(db, account_id):
            raise BizException(
                "这个账户已经有收付记录，删掉会让历史流水找不到账户；请改成「停用」"
            )
        account.is_deleted = 1
        account.dedup_key = None
        account.is_default_receive = 0
        account.is_default_pay = 0
        await db.flush()

    # ------------------------------------------------------------------
    # 余额
    # ------------------------------------------------------------------
    @classmethod
    async def apply_delta(
        cls,
        db: AsyncSession,
        account_id: Optional[int],
        delta: Decimal,
        *,
        reason: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> Optional[BankAccount]:
        """按增量调整账面余额（收款为正、付款为负）。

        ``account_id`` 为空直接返回：不少单据允许不指定账户（现金、抵账），这时账面
        余额本来就不该动，静默跳过比抛错更合理。
        """
        if not account_id:
            return None
        amount = _money(delta)
        if amount == 0:
            return None
        account = await cls.get_or_404(db, int(account_id))
        account.balance = _money(Decimal(str(account.balance or 0)) + amount)
        await db.flush()
        if reason:
            await FinanceDocEventWriter.write(
                db,
                doc_kind=ACCOUNT_DOC_KIND,
                doc_id=account.id,
                event_type=(
                    FinanceEventType.PAY if amount < 0
                    else FinanceEventType.RECEIPT_CLAIM
                ),
                occurred_amount=amount,
                operator_id=operator_id,
                reason=reason,
                payload_snapshot={"balanceAfter": float(account.balance)},
            )
            await db.flush()
        return account

    @classmethod
    async def calibrate(
        cls,
        db: AsyncSession,
        account_id: int,
        *,
        balance: Decimal,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> BankAccount:
        """余额校准：把账面值对齐到银行实际余额，必填原因并留痕。"""
        text = (reason or "").strip()
        if len(text) < 5:
            raise BizException("请说明校准原因，不少于 5 个字（例如：银行手续费扣款）")
        account = await cls.get_or_404(db, account_id)
        before = Decimal(str(account.balance or 0))
        after = _money(balance)
        if before == after:
            raise BizException("填写的余额与账面余额一致，无需校准")
        account.balance = after
        await db.flush()
        await FinanceDocEventWriter.write(
            db,
            doc_kind=ACCOUNT_DOC_KIND,
            doc_id=account.id,
            event_type=FinanceEventType.BALANCE_CALIBRATE,
            occurred_amount=_money(after - before),
            operator_id=operator_id,
            reason=text,
            payload_snapshot={
                "balanceBefore": float(before),
                "balanceAfter": float(after),
            },
        )
        await db.flush()
        return account

    @classmethod
    async def list_events(cls, db: AsyncSession, account_id: int) -> List:
        await cls.get_or_404(db, account_id)
        return await FinanceDocEventWriter.list_by_doc(
            db, ACCOUNT_DOC_KIND, account_id,
        )

    @classmethod
    async def balance_summary(
        cls, db: AsyncSession, *, enterprise_id: Optional[int] = None,
    ) -> dict:
        """出纳台顶部的资金总览：账户数与账面余额合计。"""
        stmt = select(
            func.count(BankAccount.id),
            func.coalesce(func.sum(BankAccount.balance), 0),
        ).where(BankAccount.is_deleted == 0, BankAccount.status == 1)
        if enterprise_id:
            stmt = stmt.where(BankAccount.enterprise_id == enterprise_id)
        count, total = (await db.execute(stmt)).one()
        return {
            "accountCount": int(count or 0),
            "balanceTotal": float(total or 0),
        }

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @classmethod
    async def _apply_default_flags(
        cls, db: AsyncSession, account: BankAccount,
    ) -> None:
        """同主体同用途的默认账户唯一：新设默认时把同主体其他账户的标记清掉。"""
        for column, flag in (
            (BankAccount.is_default_receive, account.is_default_receive),
            (BankAccount.is_default_pay, account.is_default_pay),
        ):
            if int(flag or 0) != 1:
                continue
            await db.execute(
                update(BankAccount)
                .where(
                    BankAccount.enterprise_id == account.enterprise_id,
                    BankAccount.id != account.id,
                    BankAccount.is_deleted == 0,
                )
                .values({column: 0})
            )
        await db.flush()

    @classmethod
    async def _assert_no_duplicate(
        cls,
        db: AsyncSession,
        account_no: str,
        *,
        exclude_id: Optional[int] = None,
    ) -> None:
        stmt = select(BankAccount.id, BankAccount.account_name).where(
            BankAccount.dedup_key == BankAccount.build_dedup_key(account_no),
            BankAccount.is_deleted == 0,
        )
        if exclude_id:
            stmt = stmt.where(BankAccount.id != exclude_id)
        row = (await db.execute(stmt.limit(1))).one_or_none()
        if row is not None:
            raise BizException(
                f"这个账号已经建过档了（{row[1]}），请直接用那条记录"
            )

    @classmethod
    async def _has_flow(cls, db: AsyncSession, account_id: int) -> bool:
        from app.modules.client.models.finance.payment_batch import PaymentBatch
        from app.modules.client.models.finance.receipt_voucher import ReceiptVoucher

        receipts = int((await db.execute(
            select(func.count(ReceiptVoucher.id)).where(
                ReceiptVoucher.bank_account_id == account_id,
                ReceiptVoucher.is_deleted == 0,
            )
        )).scalar() or 0)
        if receipts:
            return True
        batches = int((await db.execute(
            select(func.count(PaymentBatch.id)).where(
                PaymentBatch.bank_account_id == account_id,
                PaymentBatch.is_deleted == 0,
            )
        )).scalar() or 0)
        return batches > 0


def _money(v: Any) -> Decimal:
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)
