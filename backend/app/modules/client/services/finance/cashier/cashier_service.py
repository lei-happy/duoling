"""出纳台聚合 Service（文档 10 §一、§三）

出纳台不新增数据，只把「今天要动钱的事」聚到一屏：待认领的到账、待付的单、在批
待执行、账户余额，以及一条统一的资金流水。

资金流水只覆盖**有账户归属**的动作：收款到账（``receipt_voucher.bank_account_id``）
与打款批次执行（批次账户）。承运商结算单直接登记付款、司机工资现金发放这类没指定
企业账户的，进不了账户流水——硬把它们塞进来只会让账面余额算错。
"""

from datetime import date as ddate, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.finance.carrier_settlement_doc import (
    CarrierSettlementDoc,
)
from app.modules.client.models.finance.customer_settlement import CustomerSettlement
from app.modules.client.models.finance.driver_payroll import DriverPayroll
from app.modules.client.models.finance.payment_batch import (
    PaymentBatch,
    PaymentBatchItem,
)
from app.modules.client.models.finance.receipt_voucher import ReceiptVoucher
from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
from app.modules.client.services.finance.base.constants import (
    BatchExecStatus,
    PayableDocKind,
    ReceiveMethod,
    PayMethod,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    FIN_CANCELLED,
    FIN_PAID,
    FIN_PARTIAL,
    FIN_REVIEWED,
)
from app.modules.client.services.finance.cashier.bank_account_service import (
    BankAccountService,
)
from app.modules.client.services.finance.cashier.payment_batch_service import (
    PaymentBatchService,
)
from app.modules.client.services.finance.customer.receipt_voucher_service import (
    ReceiptVoucherService,
)

# 流水方向
FLOW_IN = 1
FLOW_OUT = 2


class CashierService:
    """出纳工作台聚合"""

    # ------------------------------------------------------------------
    # 工作台
    # ------------------------------------------------------------------
    @classmethod
    async def overview(
        cls, db: AsyncSession, *, enterprise_id: Optional[int] = None,
    ) -> dict:
        """出纳台顶部指标：钱在哪、今天要处理什么。"""
        receipt = await ReceiptVoucherService.cashier_stats(db)
        balance = await BankAccountService.balance_summary(
            db, enterprise_id=enterprise_id,
        )
        payable = await cls.payable_stats(db)
        receivable = await cls._receivable_stats(db)
        today = ddate.today()
        today_out = await cls._flow_total(
            db, direction=FLOW_OUT, date_from=today, date_to=today,
        )
        return {
            **receipt,
            **balance,
            **payable,
            **receivable,
            "todayPaidAmount": float(today_out),
            "asOf": datetime.now(),
        }

    @classmethod
    async def payable_stats(cls, db: AsyncSession) -> dict:
        """应付侧：待入批、在批待执行、逾期未付。"""
        pending_count = 0
        pending_amount = Decimal("0")
        overdue_count = 0
        today = ddate.today()
        taken = await PaymentBatchService._taken_doc_keys(db)

        for kind, model, amount_col in (
            (
                PayableDocKind.CARRIER_SETTLE,
                CarrierSettlementDoc,
                CarrierSettlementDoc.planned_amount,
            ),
            (
                PayableDocKind.DRIVER_PAYROLL,
                DriverPayroll,
                DriverPayroll.net_amount,
            ),
            (
                PayableDocKind.TASK_FINANCE,
                TaskFinanceDoc,
                TaskFinanceDoc.planned_amount,
            ),
        ):
            due_col = getattr(model, "due_date", None)
            columns = [model.id, amount_col]
            if due_col is not None:
                columns.append(due_col)
            r = await db.execute(
                select(*columns).where(
                    model.is_deleted == 0, model.status == FIN_REVIEWED,
                )
            )
            for row in r.all():
                if f"{kind}:{int(row[0])}" in taken:
                    continue
                amount = Decimal(str(row[1] or 0))
                if amount <= 0:
                    continue
                pending_count += 1
                pending_amount += amount
                due = row[2] if len(row) > 2 else None
                if due and due < today:
                    overdue_count += 1

        r = await db.execute(
            select(
                func.count(PaymentBatch.id),
                func.coalesce(
                    func.sum(PaymentBatch.total_amount - PaymentBatch.paid_amount), 0
                ),
            ).where(
                PaymentBatch.is_deleted == 0,
                PaymentBatch.status.in_((FIN_REVIEWED, FIN_PARTIAL)),
            )
        )
        batch_count, batch_amount = r.one()
        return {
            "payablePendingCount": pending_count,
            "payablePendingAmount": float(pending_amount),
            "payableOverdueCount": overdue_count,
            "batchWaitingCount": int(batch_count or 0),
            "batchWaitingAmount": float(batch_amount or 0),
        }

    @classmethod
    async def _receivable_stats(cls, db: AsyncSession) -> dict:
        """应收侧：已审批未收妥的结算单金额（出纳催收依据）。"""
        r = await db.execute(
            select(
                func.count(CustomerSettlement.id),
                func.coalesce(
                    func.sum(
                        CustomerSettlement.planned_amount
                        - CustomerSettlement.received_amount_total
                    ),
                    0,
                ),
            ).where(
                CustomerSettlement.is_deleted == 0,
                CustomerSettlement.status == FIN_REVIEWED,
            )
        )
        count, amount = r.one()
        return {
            "receivablePendingCount": int(count or 0),
            "receivablePendingAmount": float(amount or 0),
        }

    # ------------------------------------------------------------------
    # 资金流水
    # ------------------------------------------------------------------
    @classmethod
    async def flow_list(
        cls,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        direction: Optional[int] = None,
        bank_account_id: Optional[int] = None,
        date_from: Optional[ddate] = None,
        date_to: Optional[ddate] = None,
        keyword: Optional[str] = None,
    ) -> Tuple[List[dict], int, dict]:
        """收付款流水（收款单 + 打款批次明细合并，按时间倒序）。

        两个来源结构不同，先各查各的再在内存里合并分页：流水量按天算最多几百条，
        用 UNION 拼 SQL 反而更难维护。返回值第三项是当前筛选下的收付合计。
        """
        rows: List[dict] = []
        if direction in (None, FLOW_IN):
            rows.extend(await cls._inflow_rows(
                db, bank_account_id=bank_account_id,
                date_from=date_from, date_to=date_to, keyword=keyword,
            ))
        if direction in (None, FLOW_OUT):
            rows.extend(await cls._outflow_rows(
                db, bank_account_id=bank_account_id,
                date_from=date_from, date_to=date_to, keyword=keyword,
            ))
        rows.sort(key=lambda x: (x["occurredAt"] or datetime.min), reverse=True)

        summary = {
            "inAmount": float(sum(
                Decimal(str(x["amount"])) for x in rows
                if x["direction"] == FLOW_IN
            )),
            "outAmount": float(sum(
                Decimal(str(x["amount"])) for x in rows
                if x["direction"] == FLOW_OUT
            )),
        }
        summary["netAmount"] = round(
            summary["inAmount"] - summary["outAmount"], 2,
        )
        total = len(rows)
        start = (max(1, page) - 1) * page_size
        return rows[start:start + page_size], total, summary

    @classmethod
    async def _inflow_rows(
        cls,
        db: AsyncSession,
        *,
        bank_account_id: Optional[int],
        date_from: Optional[ddate],
        date_to: Optional[ddate],
        keyword: Optional[str],
    ) -> List[dict]:
        stmt = select(ReceiptVoucher).where(
            ReceiptVoucher.is_deleted == 0,
            ReceiptVoucher.status != FIN_CANCELLED,
        )
        if bank_account_id:
            stmt = stmt.where(ReceiptVoucher.bank_account_id == bank_account_id)
        if date_from:
            stmt = stmt.where(
                ReceiptVoucher.received_at
                >= datetime.combine(date_from, datetime.min.time())
            )
        if date_to:
            stmt = stmt.where(
                ReceiptVoucher.received_at
                <= datetime.combine(date_to, datetime.max.time())
            )
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                ReceiptVoucher.doc_no.like(kw)
                | ReceiptVoucher.payer_name.like(kw)
                | ReceiptVoucher.customer_name.like(kw)
                | ReceiptVoucher.bank_serial_no.like(kw)
            )
        r = await db.execute(stmt.order_by(ReceiptVoucher.received_at.desc()))
        return [
            {
                "flowId": f"receipt:{int(x.id)}",
                "direction": FLOW_IN,
                "docKind": "receipt_voucher",
                "docKindLabel": "收款到账",
                "docId": int(x.id),
                "docNo": x.doc_no,
                "counterparty": x.customer_name or x.payer_name,
                "amount": float(x.planned_amount or 0),
                "method": int(x.receive_method or 0) or None,
                "methodLabel": ReceiveMethod.LABELS.get(int(x.receive_method or 0)),
                "bankAccountId": x.bank_account_id,
                "bankAccountLabel": x.bank_account_label,
                "bankSerialNo": x.bank_serial_no,
                "occurredAt": x.received_at,
                "status": int(x.status or 0),
                "remark": x.remark,
            }
            for x in r.scalars().all()
        ]

    @classmethod
    async def _outflow_rows(
        cls,
        db: AsyncSession,
        *,
        bank_account_id: Optional[int],
        date_from: Optional[ddate],
        date_to: Optional[ddate],
        keyword: Optional[str],
    ) -> List[dict]:
        stmt = (
            select(PaymentBatchItem, PaymentBatch)
            .join(PaymentBatch, PaymentBatch.id == PaymentBatchItem.batch_id)
            .where(
                PaymentBatchItem.is_deleted == 0,
                PaymentBatchItem.exec_status == BatchExecStatus.SUCCESS,
                PaymentBatch.is_deleted == 0,
            )
        )
        if bank_account_id:
            stmt = stmt.where(PaymentBatch.bank_account_id == bank_account_id)
        if date_from:
            stmt = stmt.where(
                PaymentBatchItem.paid_at
                >= datetime.combine(date_from, datetime.min.time())
            )
        if date_to:
            stmt = stmt.where(
                PaymentBatchItem.paid_at
                <= datetime.combine(date_to, datetime.max.time())
            )
        if keyword:
            kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                PaymentBatchItem.doc_no.like(kw)
                | PaymentBatchItem.payee_name.like(kw)
                | PaymentBatchItem.bank_serial_no.like(kw)
                | PaymentBatch.doc_no.like(kw)
            )
        r = await db.execute(stmt.order_by(PaymentBatchItem.paid_at.desc()))
        return [
            {
                "flowId": f"batch_item:{int(item.id)}",
                "direction": FLOW_OUT,
                "docKind": item.doc_kind,
                "docKindLabel": PayableDocKind.LABELS.get(item.doc_kind, "对外付款"),
                "docId": int(item.doc_id),
                "docNo": item.doc_no,
                "batchId": int(batch.id),
                "batchDocNo": batch.doc_no,
                "counterparty": item.payee_name,
                "amount": float(item.amount or 0),
                "method": int(item.pay_method or 0) or None,
                "methodLabel": PayMethod.LABELS.get(int(item.pay_method or 0)),
                "bankAccountId": batch.bank_account_id,
                "bankAccountLabel": batch.bank_account_label,
                "bankSerialNo": item.bank_serial_no,
                "occurredAt": item.paid_at,
                "status": FIN_PAID,
                "remark": item.remark,
            }
            for item, batch in r.all()
        ]

    @classmethod
    async def _flow_total(
        cls,
        db: AsyncSession,
        *,
        direction: int,
        date_from: Optional[ddate] = None,
        date_to: Optional[ddate] = None,
    ) -> Decimal:
        _, _, summary = await cls.flow_list(
            db, page=1, page_size=1, direction=direction,
            date_from=date_from, date_to=date_to,
        )
        key = "inAmount" if direction == FLOW_IN else "outAmount"
        return Decimal(str(summary[key]))

    # ------------------------------------------------------------------
    # 日历
    # ------------------------------------------------------------------
    @classmethod
    async def pay_calendar(
        cls, db: AsyncSession, *, days: int = 14,
    ) -> List[dict]:
        """未来若干天的付款计划（按批次计划付款日与结算单到期日聚合）。

        看的是「哪天要准备多少钱」，所以到期日已过的单全部并到今天这一格——它们是
        今天就该处理的事，散在过去的日期里没人会往回翻。
        """
        today = ddate.today()
        end = today + timedelta(days=max(1, int(days)))
        buckets: Dict[ddate, Dict[str, Any]] = {}

        def bucket(day: Optional[ddate]) -> Dict[str, Any]:
            key = today if (day is None or day < today) else day
            if key > end:
                key = end
            return buckets.setdefault(key, {
                "date": key,
                "batchAmount": Decimal("0"),
                "batchCount": 0,
                "docAmount": Decimal("0"),
                "docCount": 0,
            })

        r = await db.execute(
            select(PaymentBatch).where(
                PaymentBatch.is_deleted == 0,
                PaymentBatch.status.in_((FIN_REVIEWED, FIN_PARTIAL)),
            )
        )
        for batch in r.scalars().all():
            slot = bucket(batch.plan_pay_date)
            slot["batchCount"] += 1
            slot["batchAmount"] += (
                Decimal(str(batch.total_amount or 0))
                - Decimal(str(batch.paid_amount or 0))
            )

        taken = await PaymentBatchService._taken_doc_keys(db)
        r2 = await db.execute(
            select(CarrierSettlementDoc).where(
                CarrierSettlementDoc.is_deleted == 0,
                CarrierSettlementDoc.status == FIN_REVIEWED,
                CarrierSettlementDoc.is_offset_only == 0,
            )
        )
        for settle in r2.scalars().all():
            if f"{PayableDocKind.CARRIER_SETTLE}:{int(settle.id)}" in taken:
                continue
            slot = bucket(settle.due_date)
            slot["docCount"] += 1
            slot["docAmount"] += Decimal(str(settle.planned_amount or 0))

        return [
            {
                "date": k,
                "batchCount": v["batchCount"],
                "batchAmount": float(v["batchAmount"]),
                "docCount": v["docCount"],
                "docAmount": float(v["docAmount"]),
                "totalAmount": float(v["batchAmount"] + v["docAmount"]),
            }
            for k, v in sorted(buckets.items())
        ]
