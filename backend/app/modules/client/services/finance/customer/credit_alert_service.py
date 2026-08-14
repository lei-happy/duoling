"""信用与账期预警 Service（文档 12 §四）

**只预警不拦截**：本 service 不抛业务异常、不阻断录单派车与结算提交，只负责把
「欠了多少、逾期多久、是否超额」算成一句人能看懂的话，外加高危级留痕。

留痕复用 ``biz_finance_doc_event``（append-only 的领域事实流水），用虚拟大类
``credit_alert`` + ``doc_id=customer_id``；只有高危级才写，否则事件表会被刷爆。
用途是事后追责：「这单派车时系统已经提示过客户逾期 15 万」。
"""

from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.services.finance.base.constants import (
    CreditStatus,
    FinanceDirection,
)
from app.modules.client.services.finance.base.finance_doc_event_writer import (
    FinanceDocEventWriter,
    FinanceEventType,
)
from app.modules.client.services.finance.customer.aging_service import AgingService

CREDIT_ALERT_DOC_KIND = "credit_alert"


class AlertLevel:
    """预警等级（文档 12 §4.3）"""

    NONE = 0      # 无逾期且未超额，前端不显示
    REMIND = 1    # 黄：轻度逾期
    WARN = 2      # 橙：中度逾期或已超额
    CRITICAL = 3  # 红：重度逾期或客户被暂停合作

    LABELS = {NONE: "正常", REMIND: "提醒", WARN: "警示", CRITICAL: "高危"}


# 触发场景（写进事件 reason，便于事后追溯是哪一步提示过）
class AlertScene:
    WAYBILL_CREATE = "waybill_create"
    TASK_DISPATCH = "task_dispatch"
    RECON_CONFIRM = "recon_confirm"
    SETTLE_SUBMIT = "settle_submit"

    LABELS = {
        WAYBILL_CREATE: "运单录入",
        TASK_DISPATCH: "任务派车",
        RECON_CONFIRM: "对账单确认",
        SETTLE_SUBMIT: "结算单提交审批",
    }


class CreditAlertService:
    """预警等级判定 + 高危留痕"""

    @classmethod
    def evaluate(cls, brief: dict, buckets: Sequence[int]) -> dict:
        """按摘要给出等级与文案（纯计算，不查库、不写库）。"""
        overdue_days = int(brief.get("maxOverdueDays") or 0)
        overdue_amount = float(brief.get("overdueAmount") or 0)
        exceeded = bool(brief.get("exceeded"))
        exceeded_amount = float(brief.get("exceededAmount") or 0)
        raw_status = brief.get("creditStatus")
        # 暂停合作是 0，不能用 or 兜底，否则最该报警的客户反而被当成正常
        credit_status = (
            int(raw_status) if raw_status is not None else CreditStatus.NORMAL
        )
        last_threshold = int(buckets[-1]) if buckets else 90
        first_threshold = int(buckets[0]) if buckets else 30

        level = AlertLevel.NONE
        if overdue_days >= 1:
            level = AlertLevel.REMIND
        if overdue_days > first_threshold or exceeded:
            level = AlertLevel.WARN
        if overdue_days > last_threshold or credit_status == CreditStatus.SUSPENDED:
            level = AlertLevel.CRITICAL
        # 重点关注的客户提示升一档，让业务多看一眼
        if credit_status == CreditStatus.WATCH and level == AlertLevel.REMIND:
            level = AlertLevel.WARN

        return {
            "alertLevel": level,
            "alertLevelLabel": AlertLevel.LABELS[level],
            "alertMessage": cls._message(
                level,
                overdue_days=overdue_days,
                overdue_amount=overdue_amount,
                exceeded=exceeded,
                exceeded_amount=exceeded_amount,
                credit_status=credit_status,
                last_threshold=last_threshold,
            ),
        }

    @classmethod
    async def brief_with_alert(
        cls,
        db: AsyncSession,
        customer_id: int,
        *,
        scene: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> dict:
        """摘要 + 预警，必要时留痕。

        ``scene`` 非空表示「这次是业务页面真的把提示展示给人看了」，此时高危级会
        写一条事件；纯查看账龄页不传 scene，不留痕。
        """
        brief = await AgingService.customer_brief(db, customer_id)
        brief.update(cls.evaluate(brief, brief.get("buckets") or []))
        if scene and brief["alertLevel"] == AlertLevel.CRITICAL:
            await cls._record(db, customer_id, brief, scene, operator_id)
        return brief

    # ------------------------------------------------------------------
    # 内部
    # ------------------------------------------------------------------
    @staticmethod
    async def _record(
        db: AsyncSession,
        customer_id: int,
        brief: dict,
        scene: str,
        operator_id: Optional[int],
    ) -> None:
        await FinanceDocEventWriter.write(
            db,
            doc_kind=CREDIT_ALERT_DOC_KIND,
            doc_id=customer_id,
            event_type=FinanceEventType.CREDIT_ALERT,
            direction=FinanceDirection.RECEIVE,
            occurred_amount=Decimal(str(brief.get("unpaidAmount") or 0)),
            operator_id=operator_id,
            reason=AlertScene.LABELS.get(scene, scene),
            payload_snapshot={
                "overdueAmount": brief.get("overdueAmount"),
                "maxOverdueDays": brief.get("maxOverdueDays"),
                "creditLimit": brief.get("creditLimit"),
                "exceededAmount": brief.get("exceededAmount"),
                "creditStatus": brief.get("creditStatus"),
            },
        )

    @staticmethod
    def _message(
        level: int,
        *,
        overdue_days: int,
        overdue_amount: float,
        exceeded: bool,
        exceeded_amount: float,
        credit_status: int,
        last_threshold: int,
    ) -> Optional[str]:
        if level == AlertLevel.NONE:
            return None
        parts = []
        if overdue_amount > 0 and overdue_days > 0:
            if overdue_days > last_threshold:
                parts.append(
                    f"该客户有 {_money(overdue_amount)}逾期超过 "
                    f"{last_threshold} 天"
                )
            else:
                parts.append(
                    f"该客户有 {_money(overdue_amount)}已逾期 {overdue_days} 天"
                )
        if exceeded and exceeded_amount > 0:
            parts.append(f"已超信用额度 {_money(exceeded_amount)}")
        if credit_status == CreditStatus.SUSPENDED:
            parts.append("客户信用状态为「暂停合作」")
        elif credit_status == CreditStatus.WATCH:
            parts.append("该客户已被标记为「重点关注」")

        if not parts:
            return None
        tail = (
            "请先与财务确认后再继续"
            if level == AlertLevel.CRITICAL
            else "请关注回款"
        )
        return "，".join(parts) + f"，{tail}"


def _money(amount: float) -> str:
    """金额口语化：上万说万元，避免长串数字看不清量级。"""
    value = float(amount or 0)
    if value >= 10000:
        return f"{value / 10000:.2f} 万元"
    return f"{value:.2f} 元"
