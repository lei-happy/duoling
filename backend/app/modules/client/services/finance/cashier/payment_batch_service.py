"""打款批次 Service（文档 10 §二）

批次是「一次银行付款动作」，不是新的应付义务：钱该不该付、付多少，已经由承运商结算
单 / 司机工资单 / 任务费用单表达完了。批次只解决「把这 N 笔已审批的钱一次付出去」。

四条口径：

1. **只收已审批未入批的单**：草稿与待审批的单不能入批（钱还没批准就打出去是最不能
   出的错），已入批的单靠明细 ``dedup_key`` 挡住二次入批。
2. **金额跟单不跟人填**：明细金额取单据应付额，出纳只能整笔或不入批，不能改数——要
   改金额回到原单调整，留在原单的痕迹里。
3. **逐笔登记结果**：银行退票是常态，所以执行是「按笔标记成功/失败」，成功笔立刻驱动
   原单进入已支付（连带锁任务、回写对账进度），失败笔留在批次里可重试。
4. **有失败就是部分失败**：批次状态 6 表示还有笔没打成，别让它显示成「已执行」——
   出纳第二天就找不到该补打的那几笔了。
"""

from datetime import date as ddate, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.finance.bank_account import BankAccount
from app.modules.client.models.finance.carrier_settlement_doc import (
    CarrierSettlementDoc,
)
from app.modules.client.models.finance.driver_payroll import DriverPayroll
from app.modules.client.models.finance.payment_batch import (
    PAYMENT_BATCH_DOC_KIND,
    PaymentBatch,
    PaymentBatchItem,
)
from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
from app.modules.client.services.finance.base.constants import (
    BatchExecStatus,
    FinanceDirection,
    PayableDocKind,
    PayeeType,
    PayMethod,
)
from app.modules.client.services.finance.base.finance_doc_event_writer import (
    FinanceDocEventWriter,
    FinanceEventType,
)
from app.modules.client.services.finance.base.finance_doc_service import (
    FinanceDocService,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    FIN_CANCELLED,
    FIN_DRAFT,
    FIN_PAID,
    FIN_PARTIAL,
    FIN_PENDING_REVIEW,
    FIN_REVIEWED,
    label as status_label,
)
from app.modules.client.services.finance.cashier.bank_account_service import (
    BankAccountService,
)
from app.modules.client.services.finance.carrier.carrier_settlement_doc_service import (  # noqa: E501
    CarrierSettlementDocService,
)
from app.modules.client.services.finance.driver.driver_payroll_service import (
    DriverPayrollService,
)

_CENT = Decimal("0.01")
AMOUNT_TOLERANCE = Decimal("0.01")

# 三类应付单据的取数配置：模型 + 收款方字段，避免在候选与入批处各写一遍分支
_DOC_MODELS: Dict[str, Any] = {
    PayableDocKind.CARRIER_SETTLE: CarrierSettlementDoc,
    PayableDocKind.DRIVER_PAYROLL: DriverPayroll,
    PayableDocKind.TASK_FINANCE: TaskFinanceDoc,
}


class PaymentBatchService(FinanceDocService):
    """打款批次"""

    model = PaymentBatch
    doc_kind = PAYMENT_BATCH_DOC_KIND
    doc_label = "打款批次"
    doc_no_prefix = "PB"
    direction = FinanceDirection.PAY
    editable_statuses = (FIN_DRAFT, FIN_PENDING_REVIEW)
    deletable_statuses = (FIN_DRAFT, FIN_CANCELLED)

    # ------------------------------------------------------------------
    # 候选
    # ------------------------------------------------------------------
    @classmethod
    async def list_candidates(
        cls,
        db: AsyncSession,
        *,
        doc_kinds: Optional[Sequence[str]] = None,
        keyword: Optional[str] = None,
        due_before: Optional[ddate] = None,
        limit: int = 300,
    ) -> List[dict]:
        """可入批的应付单：已审批、未入批、金额大于 0。

        三类单据混在一个列表里返回，出纳按到期日挑就行——按单据类型分三个页签反而
        让人要来回切换才知道今天一共要付多少。
        """
        kinds = [
            k for k in (doc_kinds or PayableDocKind.ALL)
            if k in _DOC_MODELS
        ]
        taken = await cls._taken_doc_keys(db)
        out: List[dict] = []
        for kind in kinds:
            rows = await cls._query_payable(
                db, kind, keyword=keyword, due_before=due_before, limit=limit,
            )
            for row in rows:
                if f"{kind}:{int(row['docId'])}" in taken:
                    continue
                out.append(row)
        out.sort(key=lambda x: (x.get("dueDate") is None, x.get("dueDate")))
        return out[:max(1, int(limit))]

    # ------------------------------------------------------------------
    # 建批与明细
    # ------------------------------------------------------------------
    @classmethod
    async def create_batch(
        cls,
        db: AsyncSession,
        *,
        docs: Sequence[dict],
        bank_account_id: Optional[int] = None,
        enterprise_id: Optional[int] = None,
        pay_method: int = PayMethod.BANK_TRANSFER,
        plan_pay_date: Optional[ddate] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> PaymentBatch:
        """按选中的应付单建批次草稿。"""
        if not docs:
            raise BizException("请选择要打款的单据")
        account = None
        if bank_account_id:
            account = await BankAccountService.get_or_404(db, int(bank_account_id))
            cls._assert_account_payable(account)

        batch = PaymentBatch(
            doc_no=await cls.generate_doc_no(db),
            doc_kind=cls.doc_kind,
            direction=FinanceDirection.PAY,
            status=FIN_DRAFT,
            enterprise_id=(
                enterprise_id
                if enterprise_id is not None
                else (account.enterprise_id if account else None)
            ),
            bank_account_id=(account.id if account else None),
            bank_account_label=(account.display_label if account else None),
            pay_method=int(pay_method),
            plan_pay_date=plan_pay_date or ddate.today(),
            # 批次金额由明细汇总而来，先占位 0，add_items 后由 refresh_totals 回填
            planned_amount=Decimal("0"),
            created_by=operator_id,
            remark=remark,
        )
        db.add(batch)
        await db.flush()

        await cls.add_items(db, batch.id, docs, operator_id=operator_id)
        await FinanceDocEventWriter.write(
            db,
            doc_kind=cls.doc_kind,
            doc_id=batch.id,
            event_type=FinanceEventType.CREATE,
            to_status=FIN_DRAFT,
            direction=FinanceDirection.PAY,
            occurred_amount=batch.total_amount,
            operator_id=operator_id,
            reason=f"新建打款批次，含 {batch.item_count} 笔",
        )
        await db.flush()
        return batch

    @classmethod
    async def add_items(
        cls,
        db: AsyncSession,
        batch_id: int,
        docs: Sequence[dict],
        *,
        operator_id: Optional[int] = None,
    ) -> List[PaymentBatchItem]:
        """把应付单加入批次（金额取单据应付额，不接受手填）。"""
        batch = await cls.get_or_404(db, batch_id)
        cls.assert_editable(batch)
        if not docs:
            raise BizException("请选择要加入批次的单据")

        taken = await cls._taken_doc_keys(db)
        rows: List[PaymentBatchItem] = []
        for item in docs:
            kind = str(item.get("docKind") or "").strip()
            doc_id = int(item.get("docId") or 0)
            if kind not in _DOC_MODELS or doc_id <= 0:
                raise BizException("单据类型不支持，请刷新页面后重新选择")
            key = f"{kind}:{doc_id}"
            if key in taken:
                raise BizException(
                    f"{PayableDocKind.LABELS.get(kind, '单据')}已经在其他批次里了，"
                    "请先从那个批次移出"
                )
            info = await cls._load_payable(db, kind, doc_id)
            amount = _money(info["amount"])
            if amount <= 0:
                raise BizException(
                    f"{info['docNo']} 的应付金额为 0，不需要打款；"
                    "纯抵账单请直接在原单上登记"
                )
            row = PaymentBatchItem(
                batch_id=batch_id,
                doc_kind=kind,
                doc_id=doc_id,
                doc_no=info["docNo"],
                payee_type=info["payeeType"],
                payee_id=info["payeeId"],
                payee_name=info["payeeName"],
                payee_bank_name=info["payeeBankName"],
                payee_bank_account=info["payeeBankAccount"],
                amount=amount,
                pay_method=batch.pay_method,
                exec_status=BatchExecStatus.PENDING,
                dedup_key=PaymentBatchItem.build_dedup_key(kind, doc_id),
            )
            db.add(row)
            rows.append(row)
            taken.add(key)
        await db.flush()
        await cls._mark_docs_batch(db, rows, batch_id=batch_id)
        await cls.refresh_totals(db, batch_id)
        return rows

    @classmethod
    async def remove_item(
        cls,
        db: AsyncSession,
        batch_id: int,
        item_id: int,
        *,
        operator_id: Optional[int] = None,
    ) -> None:
        """把一笔移出批次（已成功的笔不许移，否则原单的付款记录会失去来源）。"""
        batch = await cls.get_or_404(db, batch_id)
        if int(batch.status) not in (FIN_DRAFT, FIN_PENDING_REVIEW, FIN_REVIEWED,
                                    FIN_PARTIAL):
            raise BizException(
                f"批次当前是「{cls.status_text(batch)}」，不能再调整明细"
            )
        item = await cls._get_item_or_404(db, batch_id, item_id)
        if int(item.exec_status) == BatchExecStatus.SUCCESS:
            raise BizException(
                "这笔已经打成功了，不能移出批次；如需退回请在原单撤销付款"
            )
        item.is_deleted = 1
        item.dedup_key = None
        await db.flush()
        await cls._clear_doc_batch(db, item.doc_kind, int(item.doc_id))
        await cls.refresh_totals(db, batch_id)

    @classmethod
    async def update_batch(
        cls,
        db: AsyncSession,
        batch_id: int,
        *,
        bank_account_id: Optional[int] = None,
        pay_method: Optional[int] = None,
        plan_pay_date: Optional[ddate] = None,
        remark: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> PaymentBatch:
        batch = await cls.get_or_404(db, batch_id)
        cls.assert_editable(batch)
        if bank_account_id is not None:
            account = await BankAccountService.get_or_404(db, int(bank_account_id))
            cls._assert_account_payable(account)
            batch.bank_account_id = account.id
            batch.bank_account_label = account.display_label
            if batch.enterprise_id is None:
                batch.enterprise_id = account.enterprise_id
        if pay_method is not None:
            batch.pay_method = int(pay_method)
        if plan_pay_date is not None:
            batch.plan_pay_date = plan_pay_date
        if remark is not None:
            batch.remark = remark
        await db.flush()
        return batch

    @classmethod
    async def refresh_totals(cls, db: AsyncSession, batch_id: int) -> PaymentBatch:
        """按明细重算笔数与金额（计划额含全部笔，实付额只含成功笔）。"""
        batch = await cls.get_or_404(db, batch_id)
        items = await cls.list_items(db, batch_id)
        total = sum((Decimal(str(x.amount or 0)) for x in items), Decimal("0"))
        paid = sum(
            (
                Decimal(str(x.amount or 0)) for x in items
                if int(x.exec_status) == BatchExecStatus.SUCCESS
            ),
            Decimal("0"),
        )
        batch.item_count = len(items)
        batch.success_count = len([
            x for x in items if int(x.exec_status) == BatchExecStatus.SUCCESS
        ])
        batch.fail_count = len([
            x for x in items if int(x.exec_status) == BatchExecStatus.FAILED
        ])
        batch.total_amount = _money(total)
        batch.planned_amount = _money(total)
        batch.paid_amount = _money(paid)
        await db.flush()
        return batch

    # ------------------------------------------------------------------
    # 状态流转
    # ------------------------------------------------------------------
    @classmethod
    async def submit(
        cls, db: AsyncSession, doc_id: int, operator_id: Optional[int] = None,
    ) -> PaymentBatch:
        """草稿 → 待审批（至少 1 笔、必须选好付款账户）。"""
        batch = await cls.get_or_404(db, doc_id)
        if int(batch.item_count or 0) <= 0:
            raise BizException("这个批次里还没有单据，请先添加要打款的单")
        if not batch.bank_account_id:
            raise BizException("请先选择付款账户")
        return await super().submit(db, doc_id, operator_id)

    @classmethod
    async def execute(
        cls,
        db: AsyncSession,
        batch_id: int,
        results: Optional[Sequence[dict]] = None,
        *,
        paid_at: Optional[datetime] = None,
        operator_id: Optional[int] = None,
    ) -> PaymentBatch:
        """执行批次：逐笔登记结果，成功笔驱动原单进入已支付。

        ``results`` 留空表示「全部打成功」（银行批量回单常见情形）；给了就按笔处理，
        没提到的笔保持原状，可以分几次登记。
        """
        batch = await cls.get_or_404(db, batch_id)
        if int(batch.status) not in (FIN_REVIEWED, FIN_PARTIAL):
            raise BizException(
                f"只有已审批或部分失败的批次可以执行"
                f"（当前：{cls.status_text(batch)}）"
            )
        items = await cls.list_items(db, batch_id)
        pending = [
            x for x in items
            if int(x.exec_status) != BatchExecStatus.SUCCESS
        ]
        if not pending:
            raise BizException("这个批次已经全部打款成功，无需再执行")

        by_id = {int(x.id): x for x in pending}
        plan: Dict[int, dict] = {}
        if results:
            for r in results:
                item_id = int(r.get("itemId") or 0)
                if item_id not in by_id:
                    raise BizException("批次明细不存在或已移出，请刷新后重试")
                plan[item_id] = r
        else:
            plan = {int(x.id): {"success": True} for x in pending}

        when = paid_at or datetime.now()
        if batch.exec_started_at is None:
            batch.exec_started_at = when
        paid_delta = Decimal("0")
        for item_id, r in plan.items():
            item = by_id[item_id]
            ok = bool(r.get("success", True))
            if ok:
                await cls._pay_source_doc(
                    db, item,
                    paid_at=(r.get("paidAt") or when),
                    pay_method=int(
                        r.get("payMethod") or item.pay_method
                        or batch.pay_method or PayMethod.BANK_TRANSFER
                    ),
                    account_label=batch.bank_account_label,
                    operator_id=operator_id,
                )
                item.exec_status = BatchExecStatus.SUCCESS
                item.paid_at = r.get("paidAt") or when
                item.bank_serial_no = r.get("bankSerialNo")
                item.fail_reason = None
                paid_delta += Decimal(str(item.amount or 0))
            else:
                reason = (r.get("failReason") or "").strip()
                if not reason:
                    raise BizException(
                        f"{item.doc_no} 标记为失败时要写失败原因，"
                        "方便第二天知道该怎么补打"
                    )
                item.exec_status = BatchExecStatus.FAILED
                item.fail_reason = reason
                # 失败笔释放占用，允许换个批次重新打
                item.dedup_key = None
                await cls._clear_doc_batch(db, item.doc_kind, int(item.doc_id))
                await FinanceDocEventWriter.write(
                    db,
                    doc_kind=cls.doc_kind,
                    doc_id=batch_id,
                    event_type=FinanceEventType.BATCH_ITEM_FAIL,
                    direction=FinanceDirection.PAY,
                    occurred_amount=item.amount,
                    operator_id=operator_id,
                    reason=f"{item.doc_no} 打款失败：{reason}",
                    payload_snapshot={
                        "itemId": int(item.id),
                        "docKind": item.doc_kind,
                        "docId": int(item.doc_id),
                    },
                )
            await db.flush()

        await cls.refresh_totals(db, batch_id)
        batch = await cls.get_or_404(db, batch_id)
        remaining = [
            x for x in await cls.list_items(db, batch_id)
            if int(x.exec_status) != BatchExecStatus.SUCCESS
        ]
        target = FIN_PARTIAL if remaining else FIN_PAID
        if target == FIN_PAID:
            batch.exec_finished_at = datetime.now()
        await db.flush()
        if int(batch.status) != target:
            await cls.change_status(
                db, batch, target,
                event_type=FinanceEventType.BATCH_PAY,
                operator_id=operator_id,
                occurred_amount=batch.paid_amount,
                payload_snapshot={
                    "successCount": batch.success_count,
                    "failCount": batch.fail_count,
                },
            )
        if paid_delta > 0:
            await BankAccountService.apply_delta(
                db, batch.bank_account_id, -paid_delta,
                reason=f"批次 {batch.doc_no} 打款 {batch.success_count} 笔",
                operator_id=operator_id,
            )
        return batch

    @classmethod
    async def cancel_batch(
        cls,
        db: AsyncSession,
        batch_id: int,
        reason: str,
        operator_id: Optional[int] = None,
    ) -> PaymentBatch:
        """撤销批次：把还没打成功的笔放回待付池。

        已有成功笔的批次不许撤：那些钱已经出去了，撤掉批次就查不到是哪一次付的。
        """
        batch = await cls.get_or_404(db, batch_id)
        if int(batch.status) == FIN_CANCELLED:
            raise BizException("这个批次已撤销，无需重复操作")
        if int(batch.success_count or 0) > 0:
            raise BizException(
                "批次里已经有打款成功的笔，不能撤销；"
                "如需退回请在对应单据上撤销付款"
            )
        text = cls.assert_reason(reason)
        for item in await cls.list_items(db, batch_id):
            item.is_deleted = 1
            item.dedup_key = None
            await cls._clear_doc_batch(db, item.doc_kind, int(item.doc_id))
        await db.flush()
        await cls.change_status(
            db, batch, FIN_CANCELLED,
            event_type=FinanceEventType.CANCEL,
            operator_id=operator_id,
            reason=text,
            skip_lock_check=True,
        )
        await cls.refresh_totals(db, batch_id)
        return batch

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    @classmethod
    async def page_list(
        cls,
        db: AsyncSession,
        *,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
        bank_account_id: Optional[int] = None,
        enterprise_id: Optional[int] = None,
        date_from: Optional[ddate] = None,
        date_to: Optional[ddate] = None,
    ) -> Tuple[List[PaymentBatch], int]:
        stmt = select(PaymentBatch).where(PaymentBatch.is_deleted == 0)
        if keyword:
            stmt = stmt.where(PaymentBatch.doc_no.like(f"%{keyword.strip()}%"))
        if status is not None:
            stmt = stmt.where(PaymentBatch.status == status)
        if bank_account_id:
            stmt = stmt.where(PaymentBatch.bank_account_id == bank_account_id)
        if enterprise_id:
            stmt = stmt.where(PaymentBatch.enterprise_id == enterprise_id)
        if date_from:
            stmt = stmt.where(PaymentBatch.plan_pay_date >= date_from)
        if date_to:
            stmt = stmt.where(PaymentBatch.plan_pay_date <= date_to)

        total = int((await db.execute(
            select(func.count()).select_from(stmt.subquery())
        )).scalar() or 0)
        r = await db.execute(
            stmt.order_by(PaymentBatch.id.desc())
            .offset((max(1, page) - 1) * page_size)
            .limit(page_size)
        )
        return list(r.scalars().all()), total

    @classmethod
    async def list_items(
        cls, db: AsyncSession, batch_id: int,
    ) -> List[PaymentBatchItem]:
        r = await db.execute(
            select(PaymentBatchItem)
            .where(
                PaymentBatchItem.batch_id == batch_id,
                PaymentBatchItem.is_deleted == 0,
            )
            .order_by(PaymentBatchItem.id.asc())
        )
        return list(r.scalars().all())

    @classmethod
    def status_text(cls, batch: Any) -> str:
        return status_label(int(batch.status or 0), cls.doc_kind)

    @classmethod
    def action_flags(cls, doc: Any) -> dict:
        flags = super().action_flags(doc)
        status = int(doc.status)
        flags.update({
            "canEdit": status in (FIN_DRAFT, FIN_PENDING_REVIEW),
            "canAddItem": status in (FIN_DRAFT, FIN_PENDING_REVIEW),
            "canExecute": status in (FIN_REVIEWED, FIN_PARTIAL),
            "canCancel": (
                status not in (FIN_CANCELLED, FIN_PAID)
                and int(doc.success_count or 0) == 0
            ),
            "canForceCancel": False,
            "canPay": False,
            "canCancelPay": False,
        })
        return flags

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------
    @staticmethod
    def _assert_account_payable(account: BankAccount) -> None:
        from app.modules.client.services.finance.base.constants import (
            AccountUsageScope,
        )

        if int(account.status or 0) != 1:
            raise BizException(
                f"付款账户「{account.display_label}」已停用，请换一个账户"
            )
        if int(account.usage_scope or 0) == AccountUsageScope.RECEIVE_ONLY:
            raise BizException(
                f"账户「{account.display_label}」只用于收款，不能作为付款账户"
            )

    @classmethod
    async def _get_item_or_404(
        cls, db: AsyncSession, batch_id: int, item_id: int,
    ) -> PaymentBatchItem:
        r = await db.execute(
            select(PaymentBatchItem).where(
                PaymentBatchItem.id == item_id,
                PaymentBatchItem.batch_id == batch_id,
                PaymentBatchItem.is_deleted == 0,
            )
        )
        item = r.scalar_one_or_none()
        if item is None:
            raise BizException("批次明细不存在或已移出")
        return item

    @staticmethod
    async def _taken_doc_keys(db: AsyncSession) -> set:
        """已被批次占用的单据键（未失败、未移出的明细）。"""
        r = await db.execute(
            select(PaymentBatchItem.doc_kind, PaymentBatchItem.doc_id).where(
                PaymentBatchItem.is_deleted == 0,
                PaymentBatchItem.dedup_key.isnot(None),
            )
        )
        return {f"{kind}:{int(doc_id)}" for kind, doc_id in r.all()}

    @classmethod
    async def _query_payable(
        cls,
        db: AsyncSession,
        kind: str,
        *,
        keyword: Optional[str],
        due_before: Optional[ddate],
        limit: int,
    ) -> List[dict]:
        """按单据大类查已审批待付的单，统一成候选行结构。"""
        model = _DOC_MODELS[kind]
        stmt = select(model).where(
            model.is_deleted == 0,
            model.status == FIN_REVIEWED,
        )
        if kind == PayableDocKind.CARRIER_SETTLE:
            stmt = stmt.where(model.is_offset_only == 0)
            if due_before:
                stmt = stmt.where(model.due_date <= due_before)
            if keyword:
                kw = f"%{keyword.strip()}%"
                stmt = stmt.where(model.doc_no.like(kw) | model.carrier_name.like(kw))
        elif kind == PayableDocKind.DRIVER_PAYROLL:
            stmt = stmt.where(model.net_amount > 0)
            if keyword:
                kw = f"%{keyword.strip()}%"
                stmt = stmt.where(model.doc_no.like(kw) | model.driver_name.like(kw))
        else:
            stmt = stmt.where(model.planned_amount > 0)
            if keyword:
                kw = f"%{keyword.strip()}%"
                stmt = stmt.where(model.doc_no.like(kw) | model.payee_name.like(kw))
        r = await db.execute(stmt.order_by(model.id.desc()).limit(max(1, int(limit))))
        return [cls._to_candidate(kind, x) for x in r.scalars().all()]

    @classmethod
    def _to_candidate(cls, kind: str, doc: Any) -> dict:
        info = cls._payee_of(kind, doc)
        return {
            "docKind": kind,
            "docKindLabel": PayableDocKind.LABELS.get(kind),
            "docId": int(doc.id),
            "docNo": doc.doc_no,
            "amount": float(info["amount"]),
            "payeeType": info["payeeType"],
            "payeeId": info["payeeId"],
            "payeeName": info["payeeName"],
            "payeeBankName": info["payeeBankName"],
            "payeeBankAccount": info["payeeBankAccount"],
            "dueDate": getattr(doc, "due_date", None),
            "reviewedAt": getattr(doc, "reviewed_at", None),
            "remark": getattr(doc, "remark", None),
        }

    @staticmethod
    def _payee_of(kind: str, doc: Any) -> dict:
        """把三类单据的收款方与金额抹平成同一结构。"""
        if kind == PayableDocKind.CARRIER_SETTLE:
            return {
                "amount": Decimal(str(doc.planned_amount or 0)),
                "payeeType": PayeeType.CARRIER,
                "payeeId": doc.carrier_id,
                "payeeName": doc.carrier_name,
                "payeeBankName": doc.bank_name,
                "payeeBankAccount": doc.bank_account_masked,
            }
        if kind == PayableDocKind.DRIVER_PAYROLL:
            return {
                "amount": Decimal(str(doc.net_amount or 0)),
                "payeeType": PayeeType.DRIVER,
                "payeeId": doc.driver_id,
                "payeeName": doc.driver_name,
                "payeeBankName": doc.account_name_snapshot,
                "payeeBankAccount": doc.account_no_masked,
            }
        return {
            "amount": Decimal(str(doc.planned_amount or 0)),
            "payeeType": int(doc.payee_type or PayeeType.OTHER),
            "payeeId": doc.payee_id,
            "payeeName": doc.payee_name,
            "payeeBankName": doc.payee_bank_name,
            "payeeBankAccount": doc.payee_bank_account_masked,
        }

    @classmethod
    async def _load_payable(
        cls, db: AsyncSession, kind: str, doc_id: int,
    ) -> dict:
        model = _DOC_MODELS[kind]
        r = await db.execute(
            select(model).where(model.id == doc_id, model.is_deleted == 0)
        )
        doc = r.scalar_one_or_none()
        if doc is None:
            raise BizException("要打款的单据不存在或已删除，请刷新后重试")
        if int(doc.status or 0) != FIN_REVIEWED:
            raise BizException(
                f"{doc.doc_no} 不是「已审批」状态，不能入批；"
                "请先在原单走完审批"
            )
        info = cls._payee_of(kind, doc)
        info["docNo"] = doc.doc_no
        return info

    @classmethod
    async def _mark_docs_batch(
        cls,
        db: AsyncSession,
        items: Sequence[PaymentBatchItem],
        *,
        batch_id: int,
    ) -> None:
        """回写承运商结算单的入批标记（入批后禁止改金额）。"""
        ids = [
            int(x.doc_id) for x in items
            if x.doc_kind == PayableDocKind.CARRIER_SETTLE
        ]
        if not ids:
            return
        r = await db.execute(
            select(CarrierSettlementDoc).where(
                CarrierSettlementDoc.id.in_(ids),
                CarrierSettlementDoc.is_deleted == 0,
            )
        )
        for settle in r.scalars().all():
            settle.batch_id = batch_id
            settle.batch_locked_at = datetime.now()
        await db.flush()

    @classmethod
    async def _clear_doc_batch(
        cls, db: AsyncSession, doc_kind: str, doc_id: int,
    ) -> None:
        if doc_kind != PayableDocKind.CARRIER_SETTLE:
            return
        r = await db.execute(
            select(CarrierSettlementDoc).where(
                CarrierSettlementDoc.id == doc_id,
                CarrierSettlementDoc.is_deleted == 0,
            )
        )
        settle = r.scalar_one_or_none()
        if settle is not None:
            settle.batch_id = None
            settle.batch_locked_at = None
            await db.flush()

    @classmethod
    async def _pay_source_doc(
        cls,
        db: AsyncSession,
        item: PaymentBatchItem,
        *,
        paid_at: datetime,
        pay_method: int,
        account_label: Optional[str],
        operator_id: Optional[int],
    ) -> None:
        """驱动原单进入已支付，连带原单自己的联动（锁任务、发薪标记等）。

        走各单据 service 而不是直接改 status：锁定与回写规则都在那里，绕过去会出现
        「批次显示付了、任务却没锁」这种半截状态。
        """
        kind = item.doc_kind
        amount = Decimal(str(item.amount or 0))
        if kind == PayableDocKind.CARRIER_SETTLE:
            await CarrierSettlementDocService.pay(
                db, int(item.doc_id),
                actual_amount=amount,
                paid_at=paid_at,
                pay_method=pay_method,
                operator_id=operator_id,
            )
        elif kind == PayableDocKind.DRIVER_PAYROLL:
            await DriverPayrollService.pay(
                db, int(item.doc_id),
                actual_amount=amount,
                paid_at=paid_at,
                pay_method=pay_method,
                operator_id=operator_id,
            )
        else:
            from app.modules.client.schemas.task.task_finance_doc import (
                TaskFinanceDocPayRequest,
            )
            from app.modules.client.services.task.task_finance_service import (
                TaskFinanceService,
            )

            await TaskFinanceService.pay_doc(
                db, int(item.doc_id),
                TaskFinanceDocPayRequest(
                    actualAmount=float(amount),
                    payMethod=pay_method,
                    actualPayTime=paid_at,
                    remark=f"打款批次执行（{account_label or '未指定账户'}）",
                ),
                operator_id,
            )


def _money(v: Any) -> Decimal:
    return Decimal(str(v)).quantize(_CENT, rounding=ROUND_HALF_UP)
