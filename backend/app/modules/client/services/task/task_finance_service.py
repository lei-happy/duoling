"""
任务单财务费用单 Service

职责：
1. 费用单 CRUD（带费用项明细子表）
2. 状态机：草稿 → 待审批 → 已审批 → 已支付，及 → 已撤销
3. 收款人 / 收款账户校验
4. 主表冗余聚合（prepaid / supplement / settled / finance_doc_count）

注：财务单据与 ``task.status`` 已彻底解耦。
- 任务 5 已交车 = item 全交车聚合驱动；
- "已结算" 不再是任务状态机的一部分，财务侧只维护 ``task.settled_amount`` 等冗余金额。
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
from app.modules.client.models.task.constants import CarrierType
from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
from app.modules.client.models.task.task_finance_item import TaskFinanceItem
from app.modules.client.schemas.task.task_finance_doc import (
    TaskFinanceDocCancelRequest,
    TaskFinanceDocCreate,
    TaskFinanceDocPayRequest,
    TaskFinanceDocUpdate,
)
from app.modules.client.schemas.task.task_finance_item import TaskFinanceItemIn
from app.modules.client.services.finance.base.constants import (
    DocType,
    PayeeType,
    PayMethod,
)
from app.modules.client.services.finance.base.finance_doc_event_writer import (
    FinanceDocEventWriter,
    FinanceEventType,
)
from app.modules.client.services.finance.base.finance_state_machine import (
    FIN_CANCELLED,
    FIN_PAID,
    FIN_STATUS_LABELS,
    FinanceStateMachine,
)
from app.modules.client.services.finance.linkage.lock_orchestrator import (
    LockOrchestrator,
)


# 本单据在通用基座中的 doc_kind 常量
_DOC_KIND = "task_finance"

# 状态标签复用通用状态机（避免与 FIN_STATUS_LABELS 重复维护）
_FIN_STATUS_LABELS = FIN_STATUS_LABELS

# 撤销 / 撤销支付 / 强制撤销原因最小长度（对齐 Schema 层）
_CANCEL_REASON_MIN_LEN = 5

# doc_type → 主表冗余字段
_DOC_TYPE_TO_AGG = {
    DocType.PREPAY: "prepaid_amount",
    DocType.SUPPLEMENT: "supplement_amount",
    DocType.SETTLE: "settled_amount",
    DocType.CONTRACTED: "contracted_amount",
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
        prefix_map = {
            DocType.PREPAY: "FY",
            DocType.SUPPLEMENT: "FB",
            DocType.SETTLE: "FS",
            DocType.CONTRACTED: "FC",
        }
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

        if payee_type == PayeeType.DRIVER and payee_id:
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
                out["payee_account_type"] = PayeeType.DRIVER
                out["payee_bank_account_masked"] = (
                    out["payee_bank_account_masked"]
                    or _mask_bank_account(acc.account_no)
                )

        elif payee_type == PayeeType.CARRIER and payee_id:
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
                out["payee_account_type"] = PayeeType.CARRIER
                if not out["payee_bank_name"]:
                    out["payee_bank_name"] = acc.bank_name
                if not out["payee_bank_account_masked"]:
                    out["payee_bank_account_masked"] = _mask_bank_account(
                        acc.bank_account
                    )
        elif payee_type == PayeeType.OTHER:
            # 自由文本：要求至少有 payee_name
            if not out["payee_name"]:
                raise BizException("自由文本收款人必须填写名称")
            if out["payee_account_type"] is None:
                out["payee_account_type"] = PayeeType.OTHER

        return out

    # ------------------------------------------------------------------
    # 业务规则校验（承包单 / 社会运力）
    # ------------------------------------------------------------------
    @staticmethod
    async def _validate_contracted_payee(
        db: AsyncSession,
        task_id: int,
        payee_type: int,
        period_start: Optional[datetime],
        period_end: Optional[datetime],
        exclude_doc_id: Optional[int] = None,
    ) -> None:
        """承包单（doc_type=4）业务规则：
        - 收款人必须是司机（payee_type=1）；
        - 必填结算周期，且起 < 止；
        - 与结算单互斥：同一任务下不允许并存未撤销的结算单（doc_type=3）。
        """
        if payee_type != PayeeType.DRIVER:
            raise BizException("承包单收款人必须为司机（payeeType=1）")
        if period_start is None or period_end is None:
            raise BizException("承包单必须填写结算周期起止")
        if period_start >= period_end:
            raise BizException("承包单结算周期起必须早于周期止")

        # 与结算单互斥（同周期不重复结算，本期简化为同任务级互斥）
        conflict = select(func.count(TaskFinanceDoc.id)).where(
            TaskFinanceDoc.task_id == task_id,
            TaskFinanceDoc.is_deleted == 0,
            TaskFinanceDoc.doc_type == DocType.SETTLE,
            TaskFinanceDoc.status != FIN_CANCELLED,
        )
        if exclude_doc_id is not None:
            conflict = conflict.where(TaskFinanceDoc.id != exclude_doc_id)
        if int((await db.execute(conflict)).scalar() or 0) > 0:
            raise BizException("该任务已存在有效结算单，承包单与结算单互斥，不可重复结算")

    @staticmethod
    async def _validate_social_capacity(
        task: Task,
        snap: dict,
    ) -> None:
        """社会运力预付/尾款合规校验：
        当 ``task.carrier_type=3``（社会运力）且收款人为其他（payeeType=3）时，
        强制填写收款人名称与脱敏银行账号（合规留痕）。
        """
        if int(getattr(task, "carrier_type", 0) or 0) != CarrierType.SOCIAL:
            return
        if int(snap.get("payee_type") or 0) != PayeeType.OTHER:
            return
        if not snap.get("payee_name"):
            raise BizException("社会运力付款必须填写收款人名称")
        if not snap.get("payee_bank_account_masked"):
            raise BizException("社会运力付款必须填写收款银行账号")

    @staticmethod
    def _assert_voucher_for_pay_method(
        pay_method: Optional[int],
        pay_voucher_url: Optional[str],
    ) -> None:
        """现金/微信/支付宝（4/5/6）支付必须上传凭证。"""
        if int(pay_method or 0) in PayMethod.VOUCHER_REQUIRED and not (
            pay_voucher_url or ""
        ).strip():
            raise BizException("现金 / 微信 / 支付宝支付方式必须上传支付凭证")

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

    @staticmethod
    async def list_events(db: AsyncSession, doc_id: int) -> list:
        """返回该费用单的审计事件流（时间倒序）。"""
        # 确认单据存在（软删单据仍可查历史事件）
        await TaskFinanceService.get_or_404(db, doc_id)
        return await FinanceDocEventWriter.list_by_doc(db, _DOC_KIND, doc_id)

    # ------------------------------------------------------------------
    # 发起节点规则（租户级配置）
    # ------------------------------------------------------------------
    @staticmethod
    async def _load_stage_rules(db: AsyncSession):
        """读取租户「费用单发起节点规则」配置，返回 ``(enforce, rules)``。"""
        from app.modules.client.services.finance.base.finance_stage_rules import (
            STAGE_RULES_CONFIG_KEY,
            parse_stage_rules,
        )
        from app.modules.client.services.system_config_service import (
            SystemConfigService,
        )

        raw = await SystemConfigService.get_by_key(db, STAGE_RULES_CONFIG_KEY)
        return parse_stage_rules(raw)

    @staticmethod
    async def _assert_creatable_at_stage(
        db: AsyncSession, task: Task, doc_type: int
    ) -> None:
        """校验当前任务节点是否允许发起该类费用单（enforce=True 才硬拦截）。"""
        from app.modules.client.services.finance.base.finance_stage_rules import (
            assert_stage_allowed,
        )

        enforce, rules = await TaskFinanceService._load_stage_rules(db)
        assert_stage_allowed(doc_type, int(task.status or 0), enforce, rules)

    @staticmethod
    async def creatable_doc_types(db: AsyncSession, task_id: int) -> dict:
        """返回某任务当前节点可发起的单据类型集合，供前端入口显隐 / 下拉过滤。"""
        from app.modules.client.services.finance.base.finance_stage_rules import (
            creatable_doc_types,
        )
        from app.modules.client.services.task.task_service import TaskService

        task = await TaskService.get_or_404(db, task_id)
        enforce, rules = await TaskFinanceService._load_stage_rules(db)
        status = int(task.status or 0)
        return {
            "taskStatus": status,
            "enforce": enforce,
            "docTypes": creatable_doc_types(status, rules),
        }

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

        if data.docType not in DocType.ALL:
            raise BizException("非法 docType")
        if data.isFinal == 1 and data.docType != DocType.SETTLE:
            raise BizException("仅结算单 (docType=3) 可标记为最终结算")

        # 发起节点校验：按租户配置判断当前任务节点是否允许发起该类费用单
        await TaskFinanceService._assert_creatable_at_stage(db, task, data.docType)

        # 校验金额合理性
        if data.plannedAmount <= 0:
            raise BizException("计划金额必须大于 0")

        period_start = getattr(data, "periodStart", None)
        period_end = getattr(data, "periodEnd", None)

        # 承包单（doc_type=4）业务规则
        if data.docType == DocType.CONTRACTED:
            await TaskFinanceService._validate_contracted_payee(
                db,
                task_id=task.id,
                payee_type=data.payeeType,
                period_start=period_start,
                period_end=period_end,
            )

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

        # 社会运力预付/尾款合规校验
        await TaskFinanceService._validate_social_capacity(task, snap)

        doc_no = await TaskFinanceService.generate_doc_no(db, data.docType)
        doc = TaskFinanceDoc(
            task_id=task.id,
            # 经营主体：费用单归属继承自任务，保证分主体对账口径一致
            enterprise_id=getattr(task, "enterprise_id", None),
            doc_no=doc_no,
            doc_type=data.docType,
            doc_kind=_DOC_KIND,
            direction=2,
            is_final=int(data.isFinal or 0),
            planned_amount=Decimal(str(data.plannedAmount)),
            currency=data.currency or "CNY",
            period_start=period_start,
            period_end=period_end,
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

        await FinanceDocEventWriter.write(
            db,
            doc_kind=_DOC_KIND,
            doc_id=doc.id,
            event_type=FinanceEventType.CREATE,
            to_status=0,
            direction=2,
            occurred_amount=doc.planned_amount,
            operator_id=current_user_id,
        )

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
        if getattr(data, "periodStart", None) is not None:
            doc.period_start = data.periodStart
        if getattr(data, "periodEnd", None) is not None:
            doc.period_end = data.periodEnd
        if doc.doc_type == DocType.CONTRACTED and doc.period_start and doc.period_end:
            if doc.period_start >= doc.period_end:
                raise BizException("承包单结算周期起必须早于周期止")
        if data.payMethod is not None:
            doc.pay_method = data.payMethod
        if data.plannedPayTime is not None:
            doc.planned_pay_time = data.plannedPayTime
        if data.isFinal is not None:
            if data.isFinal == 1 and doc.doc_type != DocType.SETTLE:
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
        *,
        event_type: int,
        current_user_id: Optional[int] = None,
        reason: Optional[str] = None,
        occurred_amount: Optional[Decimal] = None,
    ) -> None:
        """通用状态切换：走 FinanceStateMachine 校验 + 写审计事件。

        - 校验合法跳转（含撤销/撤销支付强制 reason）；
        - 按目标状态补齐 submitted / reviewed / paid / cancelled 操作人与时间；
        - append 一条 biz_finance_doc_event。
        """
        old = int(doc.status)
        has_reason = bool(reason and reason.strip())
        FinanceStateMachine.assert_not_locked(getattr(doc, "is_locked", 0))
        FinanceStateMachine.assert_transition(
            _DOC_KIND, old, new_status, has_reason=has_reason,
        )
        doc.status = new_status
        now = datetime.now()
        if new_status == 1:
            doc.submitted_by = current_user_id
            doc.submitted_at = now
        elif new_status == 2:
            doc.reviewed_by = current_user_id
            doc.reviewed_at = now
        elif new_status == 3:
            doc.paid_by = current_user_id
        elif new_status == 4:
            doc.cancelled_by = current_user_id
            doc.cancelled_at = now
            if reason:
                doc.cancel_reason = reason.strip()

        await FinanceDocEventWriter.write(
            db,
            doc_kind=_DOC_KIND,
            doc_id=doc.id,
            event_type=event_type,
            from_status=old,
            to_status=new_status,
            direction=int(getattr(doc, "direction", 2) or 2),
            occurred_amount=occurred_amount,
            operator_id=current_user_id,
            reason=reason.strip() if reason else None,
        )

    @staticmethod
    def _assert_cancel_reason(reason: Optional[str]) -> str:
        if not reason or len(reason.strip()) < _CANCEL_REASON_MIN_LEN:
            raise BizException(
                f"撤销原因必须填写且不少于 {_CANCEL_REASON_MIN_LEN} 个字"
            )
        return reason.strip()

    @staticmethod
    async def submit_doc(
        db: AsyncSession, doc_id: int,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        await TaskFinanceService._change_status(
            db, doc, 1,
            event_type=FinanceEventType.SUBMIT,
            current_user_id=current_user_id,
            occurred_amount=doc.planned_amount,
        )
        await db.flush()
        return doc

    @staticmethod
    async def approve_doc(
        db: AsyncSession, doc_id: int,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        await TaskFinanceService._change_status(
            db, doc, 2,
            event_type=FinanceEventType.APPROVE,
            current_user_id=current_user_id,
            occurred_amount=doc.planned_amount,
        )
        await db.flush()
        return doc

    @staticmethod
    async def withdraw_to_draft(
        db: AsyncSession, doc_id: int,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        """退回草稿：待审批(1) / 已审批(2) → 草稿(0)，供录错后修改。"""
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        if int(doc.status) not in (1, 2):
            raise BizException(
                f"仅「待审批 / 已审批」可退回草稿（当前：{_FIN_STATUS_LABELS.get(doc.status)}）"
            )
        await TaskFinanceService._change_status(
            db, doc, 0,
            event_type=FinanceEventType.WITHDRAW,
            current_user_id=current_user_id,
        )
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
        # 现金 / 微信 / 支付宝支付强制凭证（社会运力尾款合规）
        TaskFinanceService._assert_voucher_for_pay_method(
            data.payMethod, data.payVoucherUrl,
        )
        doc.actual_amount = Decimal(str(data.actualAmount))
        doc.pay_method = data.payMethod
        doc.actual_pay_time = data.actualPayTime
        doc.pay_voucher_url = data.payVoucherUrl
        if data.remark:
            existing = (doc.remark or "").rstrip()
            doc.remark = (existing + "\n" if existing else "") + data.remark
        await TaskFinanceService._change_status(
            db, doc, 3,
            event_type=FinanceEventType.PAY,
            current_user_id=current_user_id,
            occurred_amount=doc.actual_amount,
        )
        await db.flush()

        # 主表冗余刷新；财务支付与 task.status 已彻底解耦，
        # 不再驱动 task.status 5→6（"已结算"枚举已从状态机中移除）。
        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, doc.task_id)

        # 最终结算单（doc_type=3 且 is_final=1）支付后锁定任务成本字段（不改 task.status）
        locked = await LockOrchestrator.lock_task_if_final(
            db, task=task, doc_type=doc.doc_type,
            is_final=doc.is_final, by_doc_id=doc.id,
        )
        if locked:
            doc.is_locked = 1
            doc.locked_at = datetime.now()
            doc.locked_by_doc_id = doc.id
            await FinanceDocEventWriter.write(
                db,
                doc_kind=_DOC_KIND,
                doc_id=doc.id,
                event_type=FinanceEventType.LOCK,
                to_status=doc.status,
                direction=int(getattr(doc, "direction", 2) or 2),
                operator_id=current_user_id,
                reason="最终结算单支付，锁定任务成本",
            )

        await TaskFinanceService._refresh_task_finance_aggregates(db, task)

        # 联动：司机预付单支付 → 写资金账户「预付登记」流水
        from app.modules.client.services.finance.linkage.driver_fund_orchestrator import (
            DriverFundOrchestrator,
        )
        await DriverFundOrchestrator.on_finance_doc_paid(db, doc, current_user_id)

        await db.refresh(doc)
        return doc

    @staticmethod
    async def cancel_doc(
        db: AsyncSession,
        doc_id: int,
        data: TaskFinanceDocCancelRequest,
    ) -> TaskFinanceDoc:
        """撤销未支付费用单（草稿/待审批/已审批 → 已撤销）。已支付需走强制撤销。"""
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        if int(doc.status) == 3:
            raise BizException("已支付费用单请走「强制撤销」（高权限）")
        reason = TaskFinanceService._assert_cancel_reason(data.reason)
        await TaskFinanceService._change_status(
            db, doc, 4,
            event_type=FinanceEventType.CANCEL,
            reason=reason,
        )
        await db.flush()

        # 仅刷新冗余金额；财务侧已与 task.status 解耦，撤销结算单不再触发 6→5 回退。
        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, doc.task_id)
        await TaskFinanceService._refresh_task_finance_aggregates(db, task)

        await db.refresh(doc)
        return doc

    @staticmethod
    async def cancel_payment(
        db: AsyncSession,
        doc_id: int,
        data: TaskFinanceDocCancelRequest,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        """撤销支付（高权限）：已支付(3) → 已审批(2)，解锁任务并刷新冗余。"""
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        if int(doc.status) != 3:
            raise BizException(
                f"仅「已支付」可撤销支付（当前：{_FIN_STATUS_LABELS.get(doc.status)}）"
            )
        reason = TaskFinanceService._assert_cancel_reason(data.reason)

        # 已支付会置 is_locked=1，需先临时放行状态机的锁定校验
        await TaskFinanceService._unlock_task_and_doc(db, doc, current_user_id)
        await TaskFinanceService._change_status(
            db, doc, 2,
            event_type=FinanceEventType.CANCEL_PAY,
            current_user_id=current_user_id,
            reason=reason,
            occurred_amount=(
                -doc.actual_amount if doc.actual_amount is not None else None
            ),
        )
        existing = (doc.remark or "").rstrip()
        doc.remark = (
            (existing + "\n" if existing else "") + f"[撤销支付] {reason}"
        )
        await db.flush()

        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, doc.task_id)
        await TaskFinanceService._refresh_task_finance_aggregates(db, task)

        # 联动：撤销司机预付单支付 → 冲正资金账户「预付登记」
        from app.modules.client.services.finance.linkage.driver_fund_orchestrator import (
            DriverFundOrchestrator,
        )
        await DriverFundOrchestrator.on_finance_doc_payment_reversed(
            db, doc, current_user_id
        )

        await db.refresh(doc)
        return doc

    @staticmethod
    async def force_cancel(
        db: AsyncSession,
        doc_id: int,
        data: TaskFinanceDocCancelRequest,
        current_user_id: Optional[int] = None,
    ) -> TaskFinanceDoc:
        """强制撤销（高权限）：已支付(3) → 已撤销(4)，解锁任务并刷新冗余。"""
        doc = await TaskFinanceService.get_or_404(db, doc_id)
        if int(doc.status) != 3:
            raise BizException(
                f"仅「已支付」可强制撤销（当前：{_FIN_STATUS_LABELS.get(doc.status)}）"
            )
        reason = TaskFinanceService._assert_cancel_reason(data.reason)

        await TaskFinanceService._unlock_task_and_doc(db, doc, current_user_id)
        await TaskFinanceService._change_status(
            db, doc, 4,
            event_type=FinanceEventType.FORCE_CANCEL,
            current_user_id=current_user_id,
            reason=reason,
            occurred_amount=(
                -doc.actual_amount if doc.actual_amount is not None else None
            ),
        )
        await db.flush()

        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, doc.task_id)
        await TaskFinanceService._refresh_task_finance_aggregates(db, task)

        # 联动：强制撤销司机预付单（已支付）→ 冲正资金账户「预付登记」
        from app.modules.client.services.finance.linkage.driver_fund_orchestrator import (
            DriverFundOrchestrator,
        )
        await DriverFundOrchestrator.on_finance_doc_payment_reversed(
            db, doc, current_user_id
        )

        await db.refresh(doc)
        return doc

    @staticmethod
    async def _unlock_task_and_doc(
        db: AsyncSession,
        doc: TaskFinanceDoc,
        current_user_id: Optional[int] = None,
    ) -> None:
        """撤销已支付的最终结算单前：解锁任务成本字段与本单据锁定标记。"""
        if int(getattr(doc, "is_locked", 0) or 0) != 1:
            return
        from app.modules.client.services.task.task_service import TaskService
        task = await TaskService.get_or_404(db, doc.task_id)
        unlocked = await LockOrchestrator.unlock_task(
            db, task=task, by_doc_id=doc.id,
        )
        doc.is_locked = 0
        doc.locked_at = None
        doc.locked_by_doc_id = None
        if unlocked:
            await FinanceDocEventWriter.write(
                db,
                doc_kind=_DOC_KIND,
                doc_id=doc.id,
                event_type=FinanceEventType.UNLOCK,
                to_status=doc.status,
                direction=int(getattr(doc, "direction", 2) or 2),
                operator_id=current_user_id,
                reason="撤销最终结算单支付，解锁任务成本",
            )

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
                TaskFinanceDoc.status < FIN_PAID,
            )
        )
        docs = list(r.scalars().all())
        cancel_reason = reason or "任务单被取消"
        for d in docs:
            await TaskFinanceService._change_status(
                db, d, 4,
                event_type=FinanceEventType.CANCEL,
                reason=f"[随任务取消] {cancel_reason}",
            )
            existing = (d.remark or "").rstrip()
            d.remark = (
                (existing + "\n" if existing else "")
                + f"[随任务取消] {cancel_reason}"
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
                TaskFinanceDoc.status != FIN_CANCELLED,
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
                    TaskFinanceDoc.status == FIN_PAID,
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
                TaskFinanceDoc.status == FIN_PAID,
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
