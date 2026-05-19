"""
任务单财务费用单 Service

职责：
1. 费用单 CRUD（带费用项明细子表）
2. 状态机：草稿 → 待审批 → 已审批 → 已支付，及 → 已撤销
3. 收款人 / 收款账户校验
4. 主表冗余聚合（prepaid / supplement / settled / finance_doc_count）
5. 结算单 is_final + 已支付 时把 task.status 推进到 6
"""

from datetime import datetime, date as ddate, time as dtime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.models.capacity.self_capacity.driver.driver_account import (
    DriverAccount,
)
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.models.partner.carrier_settlement import CarrierSettlement
from app.modules.client.models.task.task import Task
from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
from app.modules.client.models.task.task_finance_item import TaskFinanceItem
from app.modules.client.schemas.task.task_finance_doc import (
    TaskFinanceDocCancelRequest,
    TaskFinanceDocCreate,
    TaskFinanceDocPayRequest,
    TaskFinanceDocUpdate,
)
from app.modules.client.schemas.task.task_finance_item import TaskFinanceItemIn


_FIN_STATUS_LABELS = {
    0: "草稿", 1: "待审批", 2: "已审批", 3: "已支付", 4: "已撤销",
}

# 费用单状态机：合法跳转
_FIN_VALID_TRANS = {
    0: {1, 4},     # 草稿 → 待审批 / 已撤销
    1: {2, 4},     # 待审批 → 已审批 / 已撤销
    2: {3, 4},     # 已审批 → 已支付 / 已撤销
    3: set(),      # 已支付：不可变更
    4: set(),      # 已撤销：不可变更
}

# doc_type → 主表冗余字段
_DOC_TYPE_TO_AGG = {
    1: "prepaid_amount",
    2: "supplement_amount",
    3: "settled_amount",
}


def _mask_bank_account(no: Optional[str]) -> Optional[str]:
    if not no:
        return None
    s = str(no).strip()
    if len(s) <= 8:
        return s
    return s[:4] + "****" + s[-4:]


class TaskFinanceService:

    # ------------------------------------------------------------------
    # 单号生成
    # ------------------------------------------------------------------
    @staticmethod
    async def generate_doc_no(db: AsyncSession, doc_type: int) -> str:
        prefix_map = {1: "FY", 2: "FB", 3: "FS"}
        today = ddate.today().strftime("%Y%m%d")
        prefix = f"{prefix_map.get(doc_type, 'F')}{today}"
        like = f"{prefix}%"
        r = await db.execute(
            select(func.count(TaskFinanceDoc.id)).where(
                TaskFinanceDoc.doc_no.like(like),
            )
        )
        cnt = int(r.scalar() or 0) + 1
        return f"{prefix}{cnt:04d}"

    @staticmethod
    async def get_or_404(db: AsyncSession, doc_id: int) -> TaskFinanceDoc:
        r = await db.execute(
            select(TaskFinanceDoc).where(
                TaskFinanceDoc.id == doc_id,
                TaskFinanceDoc.is_deleted == 0,
            )
        )
        d = r.scalar_one_or_none()
        if not d:
            raise BizException("费用单不存在")
        return d

    # ------------------------------------------------------------------
    # 收款人/账户解析
    # ------------------------------------------------------------------
    @staticmethod
    async def _resolve_payee_snapshot(
        db: AsyncSession,
        payee_type: int,
        payee_id: Optional[int],
        payee_account_type: Optional[int],
        payee_account_id: Optional[int],
        payee_name: Optional[str] = None,
        payee_bank_name: Optional[str] = None,
        payee_bank_account_masked: Optional[str] = None,
    ) -> dict:
        out = {
            "payee_type": payee_type,
            "payee_id": payee_id,
            "payee_name": payee_name,
            "payee_account_type": payee_account_type,
            "payee_account_id": payee_account_id,
            "payee_bank_name": payee_bank_name,
            "payee_bank_account_masked": payee_bank_account_masked,
        }

        if payee_type == 1 and payee_id:
            r = await db.execute(
                select(Driver).where(
                    Driver.id == payee_id, Driver.is_deleted == 0
                )
            )
            d = r.scalar_one_or_none()
            if not d:
                raise BizException(f"司机不存在 (id={payee_id})")
            if not out["payee_name"]:
                out["payee_name"] = d.name
            if payee_account_id:
                r = await db.execute(
                    select(DriverAccount).where(
                        DriverAccount.id == payee_account_id,
                        DriverAccount.driver_id == payee_id,
                        DriverAccount.is_deleted == 0,
                    )
                )
                acc = r.scalar_one_or_none()
                if not acc:
                    raise BizException(
                        f"司机账户不存在 (account_id={payee_account_id})"
                    )
                out["payee_account_type"] = 1
                out["payee_bank_account_masked"] = (
                    out["payee_bank_account_masked"]
                    or _mask_bank_account(acc.account_no)
                )

        elif payee_type == 2 and payee_id:
            r = await db.execute(
                select(Carrier).where(
                    Carrier.id == payee_id, Carrier.is_deleted == 0
                )
            )
            c = r.scalar_one_or_none()
            if not c:
                raise BizException(f"承运商不存在 (id={payee_id})")
            if not out["payee_name"]:
                out["payee_name"] = c.carrier_name
            if payee_account_id:
                r = await db.execute(
                    select(CarrierSettlement).where(
                        CarrierSettlement.id == payee_account_id,
                        CarrierSettlement.carrier_id == payee_id,
                        CarrierSettlement.is_deleted == 0,
                    )
                )
                acc = r.scalar_one_or_none()
                if not acc:
                    raise BizException(
                        f"承运商结算账户不存在 (account_id={payee_account_id})"
                    )
                out["payee_account_type"] = 2
                if not out["payee_bank_name"]:
                    out["payee_bank_name"] = acc.bank_name
                if not out["payee_bank_account_masked"]:
                    out["payee_bank_account_masked"] = _mask_bank_account(
                        acc.bank_account
                    )
        elif payee_type == 3:
            # 自由文本：要求至少有 payee_name
            if not out["payee_name"]:
                raise BizException("自由文本收款人必须填写名称")
            if out["payee_account_type"] is None:
                out["payee_account_type"] = 3

        return out

    # ------------------------------------------------------------------
    # items 子表
    # ------------------------------------------------------------------
    @staticmethod
    def _validate_item_amounts(items_in: List[TaskFinanceItemIn]) -> None:
        for it in items_in:
            if it.amount <= 0:
                raise BizException("费用项金额必须大于 0")
            # quantity * unit_price 与 amount 一致性校验（允许 0.01 误差）
            if it.quantity is not None and it.unitPrice is not None:
                expected = round(float(it.quantity) * float(it.unitPrice), 2)
                if abs(expected - float(it.amount)) > 0.01:
                    raise BizException(
                        f"费用项「{it.itemType}」数量×单价 ({expected}) 与金额 "
                        f"({it.amount}) 不一致"
                    )

    @staticmethod
    async def _replace_items(
        db: AsyncSession,
        doc: TaskFinanceDoc,
        items_in: List[TaskFinanceItemIn],
    ) -> None:
        TaskFinanceService._validate_item_amounts(items_in)
        # 软删旧
        old = await TaskFinanceService.list_items(db, doc.id)
        for it in old:
            it.is_deleted = 1
        await db.flush()
        for idx, it in enumerate(items_in):
            row = TaskFinanceItem(
                finance_doc_id=doc.id,
                item_type=it.itemType,
                item_name=it.itemName,
                quantity=it.quantity,
                unit=it.unit,
                unit_price=it.unitPrice,
                amount=Decimal(str(it.amount)),
                sort_order=int(it.sortOrder or idx),
                remark=it.remark,
            )
            db.add(row)
        await db.flush()

    @staticmethod
    async def list_items(
        db: AsyncSession, doc_id: int
    ) -> List[TaskFinanceItem]:
        r = await db.execute(
            select(TaskFinanceItem).where(
                TaskFinanceItem.finance_doc_id == doc_id,
                TaskFinanceItem.is_deleted == 0,
            ).order_by(TaskFinanceItem.sort_order.asc(), TaskFinanceItem.id.asc())
        )
        return list(r.scalars().all())

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @staticmethod
    async def create_doc(
        db: AsyncSession,
        task_id: int,
        data: TaskFinanceDocCreate,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        # 取任务单存在 + 一些联动校验
        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, task_id)

        if data.docType not in (1, 2, 3):
            raise BizException("非法 docType")
        if data.isFinal == 1 and data.docType != 3:
            raise BizException("仅结算单 (docType=3) 可标记为最终结算")

        # 校验金额合理性
        if data.plannedAmount <= 0:
            raise BizException("计划金额必须大于 0")

        snap = await TaskFinanceService._resolve_payee_snapshot(
            db,
            payee_type=data.payeeType,
            payee_id=data.payeeId,
            payee_account_type=data.payeeAccountType,
            payee_account_id=data.payeeAccountId,
            payee_name=data.payeeName,
            payee_bank_name=data.payeeBankName,
            payee_bank_account_masked=data.payeeBankAccountMasked,
        )

        doc_no = await TaskFinanceService.generate_doc_no(db, data.docType)
        doc = TaskFinanceDoc(
            task_id=task.id,
            doc_no=doc_no,
            doc_type=data.docType,
            is_final=int(data.isFinal or 0),
            planned_amount=Decimal(str(data.plannedAmount)),
            currency=data.currency or "CNY",
            pay_method=data.payMethod,
            planned_pay_time=data.plannedPayTime,
            status=0,
            created_by=current_user_id,
            remark=data.remark,
            **snap,
        )
        db.add(doc)
        await db.flush()

        if data.items:
            await TaskFinanceService._replace_items(db, doc, data.items)

        await TaskFinanceService._refresh_task_finance_aggregates(db, task)
        await db.refresh(doc)
        return doc

    @staticmethod
    async def update_doc(
        db: AsyncSession,
        doc_id: int,
        data: TaskFinanceDocUpdate,
    ) -> TaskFinanceDoc:
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        if int(doc.status) not in (0, 1):
            raise BizException(
                f"费用单状态「{_FIN_STATUS_LABELS.get(doc.status)}」不允许编辑"
            )

        # 收款人/账户重新解析（若任一字段被更新）
        if any(v is not None for v in [
            data.payeeType, data.payeeId, data.payeeAccountType,
            data.payeeAccountId, data.payeeName, data.payeeBankName,
            data.payeeBankAccountMasked,
        ]):
            payee_type = data.payeeType if data.payeeType is not None else doc.payee_type
            snap = await TaskFinanceService._resolve_payee_snapshot(
                db,
                payee_type=payee_type,
                payee_id=data.payeeId if data.payeeId is not None else doc.payee_id,
                payee_account_type=(
                    data.payeeAccountType
                    if data.payeeAccountType is not None
                    else doc.payee_account_type
                ),
                payee_account_id=(
                    data.payeeAccountId
                    if data.payeeAccountId is not None
                    else doc.payee_account_id
                ),
                payee_name=(
                    data.payeeName
                    if data.payeeName is not None else doc.payee_name
                ),
                payee_bank_name=(
                    data.payeeBankName
                    if data.payeeBankName is not None else doc.payee_bank_name
                ),
                payee_bank_account_masked=(
                    data.payeeBankAccountMasked
                    if data.payeeBankAccountMasked is not None
                    else doc.payee_bank_account_masked
                ),
            )
            for k, v in snap.items():
                setattr(doc, k, v)

        if data.plannedAmount is not None:
            if data.plannedAmount <= 0:
                raise BizException("计划金额必须大于 0")
            doc.planned_amount = Decimal(str(data.plannedAmount))
        if data.payMethod is not None:
            doc.pay_method = data.payMethod
        if data.plannedPayTime is not None:
            doc.planned_pay_time = data.plannedPayTime
        if data.isFinal is not None:
            if data.isFinal == 1 and doc.doc_type != 3:
                raise BizException("仅结算单 (docType=3) 可标记为最终结算")
            doc.is_final = int(data.isFinal)
        if data.remark is not None:
            doc.remark = data.remark

        if data.items is not None:
            await TaskFinanceService._replace_items(db, doc, data.items)

        await db.flush()
        await db.refresh(doc)
        return doc

    @staticmethod
    async def delete_doc(db: AsyncSession, doc_id: int) -> None:
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        if int(doc.status) not in (0, 4):
            raise BizException(
                f"费用单状态「{_FIN_STATUS_LABELS.get(doc.status)}」不允许删除"
            )
        # 软删 items
        for it in await TaskFinanceService.list_items(db, doc_id):
            it.is_deleted = 1
        doc.is_deleted = 1
        await db.flush()

        # 联动主表冗余（理论上撤销过的不会算金额，但保守起见刷新）
        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, doc.task_id)
        await TaskFinanceService._refresh_task_finance_aggregates(db, task)

    # ------------------------------------------------------------------
    # 状态机
    # ------------------------------------------------------------------
    @staticmethod
    async def _change_status(
        db: AsyncSession,
        doc: TaskFinanceDoc,
        new_status: int,
        current_user_id: Optional[int] = None,
    ) -> None:
        old = int(doc.status)
        if new_status not in _FIN_VALID_TRANS.get(old, set()):
            raise BizException(
                f"费用单状态从「{_FIN_STATUS_LABELS.get(old)}」"
                f"不能直接跳转到「{_FIN_STATUS_LABELS.get(new_status, new_status)}」"
            )
        doc.status = new_status
        if new_status == 2:
            doc.reviewed_by = current_user_id
            doc.reviewed_at = datetime.now()
        elif new_status == 3:
            doc.paid_by = current_user_id

    @staticmethod
    async def submit_doc(
        db: AsyncSession, doc_id: int,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        await TaskFinanceService._change_status(db, doc, 1, current_user_id)
        await db.flush()
        return doc

    @staticmethod
    async def approve_doc(
        db: AsyncSession, doc_id: int,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        await TaskFinanceService._change_status(db, doc, 2, current_user_id)
        await db.flush()
        return doc

    @staticmethod
    async def pay_doc(
        db: AsyncSession,
        doc_id: int,
        data: TaskFinanceDocPayRequest,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        if int(doc.status) != 2:
            raise BizException(
                f"仅「已审批」状态的费用单可支付（当前：{_FIN_STATUS_LABELS.get(doc.status)}）"
            )
        if data.actualAmount <= 0:
            raise BizException("实际支付金额必须大于 0")
        doc.actual_amount = Decimal(str(data.actualAmount))
        doc.pay_method = data.payMethod
        doc.actual_pay_time = data.actualPayTime
        doc.pay_voucher_url = data.payVoucherUrl
        if data.remark:
            existing = (doc.remark or "").rstrip()
            doc.remark = (existing + "\n" if existing else "") + data.remark
        await TaskFinanceService._change_status(db, doc, 3, current_user_id)
        await db.flush()

        # 主表冗余 + 结算联动
        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, doc.task_id)
        await TaskFinanceService._refresh_task_finance_aggregates(db, task)

        if doc.doc_type == 3 and int(doc.is_final or 0) == 1:
            # 最终结算单已支付 → 推进任务单到 6 已结算（仅当已签收）
            if int(task.status) == 5:
                task.status = 6
                await db.flush()

        await db.refresh(doc)
        return doc

    @staticmethod
    async def cancel_doc(
        db: AsyncSession,
        doc_id: int,
        data: TaskFinanceDocCancelRequest,
    ) -> TaskFinanceDoc:
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        was_final_paid = (
            doc.doc_type == 3
            and int(doc.is_final or 0) == 1
            and int(doc.status) == 3
        )
        await TaskFinanceService._change_status(db, doc, 4)
        if data.reason:
            existing = (doc.remark or "").rstrip()
            doc.remark = (
                (existing + "\n" if existing else "")
                + f"[撤销原因] {data.reason}"
            )
        await db.flush()

        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, doc.task_id)
        await TaskFinanceService._refresh_task_finance_aggregates(db, task)

        # 反向联动：已支付的最终结算单被撤销 → task 6 回退到 5
        if was_final_paid and int(task.status) == 6:
            from app.modules.client.services.state_machine.task_state_machine import (
                TaskStateMachine,
            )
            TaskStateMachine.assert_revert(6, 5)
            task.status = 5
            actor = "system"
            existing = (task.remark or "").rstrip()
            task.remark = (
                (existing + "\n" if existing else "")
                + f"[结算撤销] 由最终结算单 {doc.doc_no} 撤销触发，"
                f"by {actor}：{(data.reason or '').strip() or '未填写原因'}"
            )
            await db.flush()

        await db.refresh(doc)
        return doc

    @staticmethod
    async def cancel_all_unpaid_docs(
        db: AsyncSession,
        task_id: int,
        reason: str,
    ) -> List[TaskFinanceDoc]:
        """任务被取消时调用：把所有未支付（status<3）的费用单批量撤销。

        已支付（status=3）不动；调用方应在用户确认后再行单独操作。
        返回受影响的费用单列表。
        """
        r = await db.execute(
            select(TaskFinanceDoc).where(
                TaskFinanceDoc.task_id == task_id,
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.status < 3,
            )
        )
        docs = list(r.scalars().all())
        for d in docs:
            await TaskFinanceService._change_status(db, d, 4)
            existing = (d.remark or "").rstrip()
            d.remark = (
                (existing + "\n" if existing else "")
                + f"[随任务取消] {reason or '任务单被取消'}"
            )
        if docs:
            await db.flush()
            from app.modules.client.services.task.task_service import TaskService
            task = await TaskService.get_or_404(db, task_id)
            await TaskFinanceService._refresh_task_finance_aggregates(db, task)
        return docs

    # ------------------------------------------------------------------
    # 主表冗余聚合
    # ------------------------------------------------------------------
    @staticmethod
    async def _refresh_task_finance_aggregates(
        db: AsyncSession, task: Task,
    ) -> None:
        """重算 task 的 prepaid/supplement/settled 金额与 finance_doc_count"""
        # 总单数（除已撤销）
        cnt_res = await db.execute(
            select(func.count(TaskFinanceDoc.id)).where(
                TaskFinanceDoc.task_id == task.id,
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.status != 4,
            )
        )
        task.finance_doc_count = int(cnt_res.scalar() or 0)

        # 三类已支付金额（status=3）
        for doc_type, field in _DOC_TYPE_TO_AGG.items():
            res = await db.execute(
                select(func.coalesce(
                    func.sum(TaskFinanceDoc.actual_amount), 0
                )).where(
                    TaskFinanceDoc.task_id == task.id,
                    TaskFinanceDoc.is_deleted == 0,
                    TaskFinanceDoc.doc_type == doc_type,
                    TaskFinanceDoc.status == 3,
                )
            )
            setattr(task, field, Decimal(str(res.scalar() or 0)))
        await db.flush()

    # ------------------------------------------------------------------
    # 列表
    # ------------------------------------------------------------------
    @staticmethod
    async def list_docs_by_task(
        db: AsyncSession, task_id: int,
    ) -> List[TaskFinanceDoc]:
        r = await db.execute(
            select(TaskFinanceDoc).where(
                TaskFinanceDoc.task_id == task_id,
                TaskFinanceDoc.is_deleted == 0,
            ).order_by(
                TaskFinanceDoc.doc_type.asc(),
                TaskFinanceDoc.created_at.asc(),
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def page_docs(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        task_id: Optional[int] = None,
        doc_type: Optional[int] = None,
        status: Optional[int] = None,
        payee_type: Optional[int] = None,
        created_at_start: Optional[ddate] = None,
        created_at_end: Optional[ddate] = None,
    ) -> Tuple[List[TaskFinanceDoc], int]:
        base = select(TaskFinanceDoc).where(TaskFinanceDoc.is_deleted == 0)
        cnt = select(func.count(TaskFinanceDoc.id)).where(
            TaskFinanceDoc.is_deleted == 0
        )
        if keyword:
            kw = f"%{keyword.strip()}%"
            cond = or_(
                TaskFinanceDoc.doc_no.like(kw),
                TaskFinanceDoc.payee_name.like(kw),
            )
            base = base.where(cond)
            cnt = cnt.where(cond)
        if task_id is not None:
            base = base.where(TaskFinanceDoc.task_id == task_id)
            cnt = cnt.where(TaskFinanceDoc.task_id == task_id)
        if doc_type is not None:
            base = base.where(TaskFinanceDoc.doc_type == doc_type)
            cnt = cnt.where(TaskFinanceDoc.doc_type == doc_type)
        if status is not None:
            base = base.where(TaskFinanceDoc.status == status)
            cnt = cnt.where(TaskFinanceDoc.status == status)
        if payee_type is not None:
            base = base.where(TaskFinanceDoc.payee_type == payee_type)
            cnt = cnt.where(TaskFinanceDoc.payee_type == payee_type)
        if created_at_start is not None:
            start_dt = datetime.combine(created_at_start, dtime.min)
            base = base.where(TaskFinanceDoc.created_at >= start_dt)
            cnt = cnt.where(TaskFinanceDoc.created_at >= start_dt)
        if created_at_end is not None:
            end_dt = datetime.combine(created_at_end, dtime.max)
            base = base.where(TaskFinanceDoc.created_at <= end_dt)
            cnt = cnt.where(TaskFinanceDoc.created_at <= end_dt)

        total = int((await db.execute(cnt)).scalar() or 0)
        offset = max(0, (page - 1) * page_size)
        r = await db.execute(
            base.order_by(
                TaskFinanceDoc.created_at.desc(),
                TaskFinanceDoc.id.desc(),
            ).offset(offset).limit(page_size)
        )
        return list(r.scalars().all()), total

    # ------------------------------------------------------------------
    # 工作台聚合 + 批量动作
    # ------------------------------------------------------------------
    @staticmethod
    async def workbench_stats(db: AsyncSession) -> dict:
        """返回各状态计数 + 待审批/待支付金额合计 + 今日已支付金额"""
        # 各状态计数
        r = await db.execute(
            select(TaskFinanceDoc.status, func.count(TaskFinanceDoc.id))
            .where(TaskFinanceDoc.is_deleted == 0)
            .group_by(TaskFinanceDoc.status)
        )
        status_counts: dict[int, int] = {int(s): int(c) for s, c in r.all()}

        # 待审批合计（status=1，按 planned_amount）
        r_pending_review = await db.execute(
            select(func.coalesce(func.sum(TaskFinanceDoc.planned_amount), 0))
            .where(
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.status == 1,
            )
        )
        pending_review_amt = float(r_pending_review.scalar() or 0)

        # 待支付合计（status=2，按 planned_amount）
        r_pending_pay = await db.execute(
            select(func.coalesce(func.sum(TaskFinanceDoc.planned_amount), 0))
            .where(
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.status == 2,
            )
        )
        pending_pay_amt = float(r_pending_pay.scalar() or 0)

        # 今日已支付合计（status=3 且 actual_pay_time 在今日）
        today = ddate.today()
        today_start = datetime.combine(today, dtime.min)
        today_end = datetime.combine(today, dtime.max)
        r_today_paid = await db.execute(
            select(func.coalesce(func.sum(TaskFinanceDoc.actual_amount), 0))
            .where(
                TaskFinanceDoc.is_deleted == 0,
                TaskFinanceDoc.status == 3,
                TaskFinanceDoc.actual_pay_time >= today_start,
                TaskFinanceDoc.actual_pay_time <= today_end,
            )
        )
        today_paid_amt = float(r_today_paid.scalar() or 0)

        return {
            "statusCounts": status_counts,
            "totals": {
                "draft": status_counts.get(0, 0),
                "pendingReview": status_counts.get(1, 0),
                "pendingPay": status_counts.get(2, 0),
                "paid": status_counts.get(3, 0),
                "cancelled": status_counts.get(4, 0),
            },
            "amounts": {
                "pendingReviewAmount": pending_review_amt,
                "pendingPayAmount": pending_pay_amt,
                "todayPaidAmount": today_paid_amt,
            },
        }

    @staticmethod
    async def batch_action(
        db: AsyncSession,
        ids: List[int],
        action: str,
        current_user_id: Optional[int] = None,
        pay_payload: Optional[TaskFinanceDocPayRequest] = None,
        cancel_reason: Optional[str] = None,
    ) -> dict:
        """批量执行 approve / pay / cancel / submit。
        - approve: 1 → 2
        - pay   : 2 → 3 （需要 pay_payload）
        - cancel: 0/1/2 → 4
        - submit: 0 → 1
        """
        if action not in ("approve", "pay", "cancel", "submit"):
            raise BizException(f"非法批量动作: {action}")
        if action == "pay" and pay_payload is None:
            raise BizException("批量支付需要 pay 详情")

        success = 0
        failures: List[dict] = []
        for doc_id in ids:
            try:
                if action == "submit":
                    await TaskFinanceService.submit_doc(
                        db, int(doc_id), current_user_id
                    )
                elif action == "approve":
                    await TaskFinanceService.approve_doc(
                        db, int(doc_id), current_user_id
                    )
                elif action == "pay":
                    await TaskFinanceService.pay_doc(
                        db, int(doc_id), pay_payload, current_user_id
                    )
                elif action == "cancel":
                    await TaskFinanceService.cancel_doc(
                        db,
                        int(doc_id),
                        TaskFinanceDocCancelRequest(reason=cancel_reason),
                    )
                success += 1
            except Exception as e:  # noqa: BLE001
                failures.append({"id": int(doc_id), "error": str(e)})
        return {
            "success": success,
            "failed": len(failures),
            "failures": failures,
        }
