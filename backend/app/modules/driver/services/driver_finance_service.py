"""
驾驶员财务服务

口径：
- 列表 / 详情 / 汇总：所有查询强制 ``payee_type=1 AND payee_id=当前 driver_id``
  → 跨企业不可见（数据隔离由租户库自动保障）
- 同一手机号在 A、B 两个企业的财务数据天然由 tenant_code 切库隔离
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.driver.driver_account import (
    DriverAccount,
)
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
from app.modules.client.models.task.task_finance_item import TaskFinanceItem
from app.modules.driver.schemas.finance import (
    DriverAccountOut,
    DriverFinanceDetail,
    DriverFinanceItemOut,
    DriverFinanceListItem,
    DriverFinanceSummary,
    FinanceMonthlyAmount,
)
from app.modules.driver.services.driver_context import DriverContext

PAYEE_TYPE_DRIVER = 1
STATUS_PAID = 3
STATUS_CANCELLED = 4


def _to_float(v: Optional[Decimal]) -> float:
    return float(v) if v is not None else 0.0


class DriverFinanceService:
    """驾驶员视角的费用单/账户/汇总"""

    # ------------------------------------------------------------------
    # 列表
    # ------------------------------------------------------------------
    @staticmethod
    async def list_my_docs(
        db: AsyncSession,
        ctx: DriverContext,
        *,
        doc_type: Optional[int] = None,
        status: Optional[int] = None,
        year_month: Optional[str] = None,
        page: int = 1,
        page_size: int = 15,
    ) -> Tuple[List[DriverFinanceListItem], int]:
        conds = [
            TaskFinanceDoc.is_deleted == 0,
            TaskFinanceDoc.payee_type == PAYEE_TYPE_DRIVER,
            TaskFinanceDoc.payee_id == ctx.driver_id,
        ]
        if doc_type is not None:
            conds.append(TaskFinanceDoc.doc_type == doc_type)
        if status is not None:
            conds.append(TaskFinanceDoc.status == status)
        if year_month:
            try:
                y, m = year_month.split("-")
                start = datetime(int(y), int(m), 1)
                if int(m) == 12:
                    end = datetime(int(y) + 1, 1, 1)
                else:
                    end = datetime(int(y), int(m) + 1, 1)
                conds.append(TaskFinanceDoc.created_at >= start)
                conds.append(TaskFinanceDoc.created_at < end)
            except Exception:
                raise BizException("yearMonth 格式不正确，应为 YYYY-MM")

        total = int(
            (await db.execute(select(func.count(TaskFinanceDoc.id)).where(*conds)))
            .scalar_one()
        )

        page = max(1, page)
        page_size = max(1, min(page_size, 100))
        rows = (
            await db.execute(
                select(TaskFinanceDoc)
                .where(*conds)
                .order_by(TaskFinanceDoc.created_at.desc(), TaskFinanceDoc.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()

        # 关联任务编号（一次性查询，避免 N+1）
        task_ids = list({int(d.task_id) for d in rows})
        task_no_map: dict[int, str] = {}
        if task_ids:
            tres = await db.execute(
                select(Task.id, Task.task_no).where(Task.id.in_(task_ids))
            )
            task_no_map = {int(tid): tn for tid, tn in tres.all()}

        items = [
            DriverFinanceService._to_list_item(d, task_no_map.get(int(d.task_id)))
            for d in rows
        ]
        return items, total

    # ------------------------------------------------------------------
    # 详情
    # ------------------------------------------------------------------
    @staticmethod
    async def get_doc(
        db: AsyncSession, ctx: DriverContext, doc_id: int
    ) -> DriverFinanceDetail:
        res = await db.execute(
            select(TaskFinanceDoc).where(
                TaskFinanceDoc.id == doc_id,
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.payee_type == PAYEE_TYPE_DRIVER,
                TaskFinanceDoc.payee_id == ctx.driver_id,
            )
        )
        doc = res.scalar_one_or_none()
        if not doc:
            raise BizException("费用单不存在或无权访问")

        item_rows = (
            await db.execute(
                select(TaskFinanceItem)
                .where(
                    TaskFinanceItem.finance_doc_id == doc.id,
                    TaskFinanceItem.is_deleted == 0,
                )
                .order_by(TaskFinanceItem.sort_order.asc(), TaskFinanceItem.id.asc())
            )
        ).scalars().all()

        task_no = None
        t_res = await db.execute(
            select(Task.task_no).where(Task.id == int(doc.task_id))
        )
        task_no = t_res.scalar_one_or_none()

        base = DriverFinanceService._to_list_item(doc, task_no)
        return DriverFinanceDetail(
            **base.model_dump(),
            items=[
                DriverFinanceItemOut(
                    id=int(it.id),
                    itemType=it.item_type,
                    itemName=it.item_name,
                    quantity=_to_float(it.quantity) if it.quantity is not None else None,
                    unit=it.unit,
                    unitPrice=(
                        _to_float(it.unit_price)
                        if it.unit_price is not None
                        else None
                    ),
                    amount=_to_float(it.amount),
                )
                for it in item_rows
            ],
            payVoucherUrl=doc.pay_voucher_url,
        )

    # ------------------------------------------------------------------
    # 汇总
    # ------------------------------------------------------------------
    @staticmethod
    async def summary(
        db: AsyncSession,
        ctx: DriverContext,
        year_month: Optional[str] = None,
    ) -> DriverFinanceSummary:
        # 累计：所有已支付费用单
        base_conds = [
            TaskFinanceDoc.is_deleted == 0,
            TaskFinanceDoc.payee_type == PAYEE_TYPE_DRIVER,
            TaskFinanceDoc.payee_id == ctx.driver_id,
            TaskFinanceDoc.status == STATUS_PAID,
        ]

        async def sum_by_type(doc_type: int) -> float:
            r = await db.execute(
                select(func.coalesce(func.sum(TaskFinanceDoc.actual_amount), 0))
                .where(*base_conds, TaskFinanceDoc.doc_type == doc_type)
            )
            return float(r.scalar_one() or 0)

        prepaid = await sum_by_type(1)
        supplement = await sum_by_type(2)
        settled = await sum_by_type(3)

        # 按月：近 6 个月，按 actual_pay_time
        from sqlalchemy import literal_column

        rows = (
            await db.execute(
                select(
                    func.date_format(TaskFinanceDoc.actual_pay_time, "%Y-%m").label("ym"),
                    func.coalesce(func.sum(TaskFinanceDoc.actual_amount), 0).label("amt"),
                )
                .where(*base_conds, TaskFinanceDoc.actual_pay_time.is_not(None))
                .group_by(literal_column("ym"))
                .order_by(literal_column("ym").desc())
                .limit(6)
            )
        ).all()
        by_month = [
            FinanceMonthlyAmount(month=str(ym), amount=float(amt or 0))
            for ym, amt in rows
        ]
        by_month.reverse()

        return DriverFinanceSummary(
            totalIncome=prepaid + supplement + settled,
            prepaidAmount=prepaid,
            supplementAmount=supplement,
            settledAmount=settled,
            byMonth=by_month,
        )

    # ------------------------------------------------------------------
    # 收款账户
    # ------------------------------------------------------------------
    @staticmethod
    async def list_my_accounts(
        db: AsyncSession, ctx: DriverContext
    ) -> List[DriverAccountOut]:
        rows = (
            await db.execute(
                select(DriverAccount)
                .where(
                    DriverAccount.driver_id == ctx.driver_id,
                    DriverAccount.is_deleted == 0,
                )
                .order_by(DriverAccount.id.asc())
            )
        ).scalars().all()
        return [
            DriverAccountOut(
                id=int(a.id),
                accountType=int(a.account_type),
                accountName=a.account_name,
                accountNo=a.account_no,
                balance=_to_float(a.balance),
                status=int(a.status),
            )
            for a in rows
        ]

    # ------------------------------------------------------------------
    # 资金账户（往来账）— 只读，硬过滤只看自己
    # ------------------------------------------------------------------
    @staticmethod
    async def get_my_fund_account(
        db: AsyncSession, ctx: DriverContext
    ) -> dict:
        from app.modules.client.services.capacity.self_capacity.driver import (
            DriverFundAccountService,
        )

        acc = await DriverFundAccountService.get_account(db, ctx.driver_id)
        return acc.model_dump()

    @staticmethod
    async def list_my_fund_transactions(
        db: AsyncSession,
        ctx: DriverContext,
        *,
        biz_type: Optional[int] = None,
        page: int = 1,
        page_size: int = 15,
    ) -> Tuple[List[dict], int]:
        from app.modules.client.services.capacity.self_capacity.driver import (
            DriverFundAccountService,
        )

        return await DriverFundAccountService.list_transactions(
            db, ctx.driver_id,
            biz_type=biz_type, page=page, page_size=page_size,
        )

    # ------------------------------------------------------------------
    # 输出裁剪
    # ------------------------------------------------------------------
    @staticmethod
    def _to_list_item(
        d: TaskFinanceDoc, task_no: Optional[str]
    ) -> DriverFinanceListItem:
        return DriverFinanceListItem(
            id=int(d.id),
            docNo=d.doc_no,
            docType=int(d.doc_type),
            isFinal=int(d.is_final or 0),
            taskId=int(d.task_id),
            taskNo=task_no,
            payeeName=d.payee_name,
            plannedAmount=_to_float(d.planned_amount),
            actualAmount=(
                _to_float(d.actual_amount) if d.actual_amount is not None else None
            ),
            status=int(d.status),
            plannedPayTime=d.planned_pay_time,
            actualPayTime=d.actual_pay_time,
            payMethod=int(d.pay_method) if d.pay_method is not None else None,
            remark=d.remark,
        )
