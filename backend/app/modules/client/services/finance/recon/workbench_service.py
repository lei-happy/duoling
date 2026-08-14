"""对账工作台聚合（文档 08 §3.2）

工作台只做「筛待办 + 触发动作」，本服务因此只提供**读聚合**：KPI 卡与四个状态池
Tab 的计数由一次 ``summary`` 给全，Tab 列表则复用各自台账的分页接口，不在这里再
造一套 CRUD。

第 2 期只覆盖客户侧；承运商侧（``carrier_recon``）第 3 期接入时，把本文件的查询
按 ``recon_kind`` 参数化即可，KPI 结构不变。
"""

from datetime import date, datetime, time as dtime
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.finance.customer_recon import CustomerRecon
from app.modules.client.models.finance.recon_diff import ReconDiff
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.services.finance.base.finance_state_machine import (
    FIN_CANCELLED,
    FIN_DRAFT,
    FIN_REVIEWED,
)
from app.modules.client.services.finance.linkage.waybill_to_finance import (
    WAYBILL_RECONCILABLE_STATUSES,
)
from app.modules.client.services.finance.recon.consistency_checker import (
    ConsistencyChecker,
)
from app.modules.client.services.finance.recon.diff_constants import (
    DiffSeverity,
    DiffStatus,
    ReconKind,
)


class ReconWorkbenchService:
    """对账工作台的读聚合"""

    recon_kind = ReconKind.CUSTOMER

    # ------------------------------------------------------------------
    # KPI + Tab 计数
    # ------------------------------------------------------------------
    @classmethod
    async def summary(
        cls,
        db: AsyncSession,
        *,
        enterprise_id: Optional[int] = None,
    ) -> dict:
        """一次返回全部卡片与 Tab 角标，避免前端并发四五个统计请求。"""
        pending = await cls._pending_waybill_total(db, enterprise_id=enterprise_id)
        dirty_count = await cls._recon_count(db, dirty=True, enterprise_id=enterprise_id)
        diff = await cls._open_diff_total(db)
        pending_sign = await cls._pending_sign_total(db, enterprise_id=enterprise_id)
        confirmed = await cls._confirmed_this_month(db, enterprise_id=enterprise_id)
        return {
            "pendingWaybillCount": pending["count"],
            "pendingWaybillAmount": pending["amount"],
            "pendingCustomerCount": pending["customerCount"],
            "dirtyReconCount": dirty_count,
            "openDiffCount": diff["count"],
            "openDiffAmount": diff["amount"],
            "blockingDiffCount": diff["blockingCount"],
            "pendingSignCount": pending_sign["count"],
            "pendingSignAmount": pending_sign["amount"],
            "confirmedThisMonthCount": confirmed["count"],
            "confirmedThisMonthAmount": confirmed["amount"],
            "monthStart": confirmed["monthStart"],
        }

    # ------------------------------------------------------------------
    # 候选池：按客户聚合
    # ------------------------------------------------------------------
    @classmethod
    async def pending_waybill_groups(
        cls,
        db: AsyncSession,
        *,
        keyword: Optional[str] = None,
        enterprise_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[dict]:
        """待对账运单按客户归堆，点开某一堆再去台账建单。

        工作台先给「哪个客户攒够了单」，而不是直接铺几千条运单——对账岗的第一个
        决策是选客户与周期，不是挑运单。
        """
        stmt = (
            select(
                Waybill.customer_id,
                func.max(Waybill.customer_name),
                func.count(Waybill.id),
                func.coalesce(func.sum(Waybill.freight_amount), 0),
                func.max(Waybill.enterprise_id),
            )
            .where(*cls._pending_conditions(enterprise_id=enterprise_id))
            .group_by(Waybill.customer_id)
            .order_by(func.count(Waybill.id).desc())
            .limit(max(1, int(limit)))
        )
        if keyword:
            stmt = stmt.where(Waybill.customer_name.like(f"%{keyword.strip()}%"))
        rows = (await db.execute(stmt)).all()
        return [
            {
                "customerId": int(cid) if cid is not None else None,
                "customerName": name,
                "waybillCount": int(cnt or 0),
                "freightAmount": float(amount or 0),
                "enterpriseId": int(eid) if eid is not None else None,
            }
            for cid, name, cnt, amount, eid in rows
            if cid is not None
        ]

    # ------------------------------------------------------------------
    # 内部查询
    # ------------------------------------------------------------------
    @classmethod
    def _pending_conditions(cls, *, enterprise_id: Optional[int] = None) -> list:
        """待对账运单口径：已交车、未被结算锁定、未挂任何非撤销对账单。"""
        conds = [
            Waybill.is_deleted == 0,
            Waybill.status.in_(WAYBILL_RECONCILABLE_STATUSES),
            Waybill.is_locked == 0,
            Waybill.customer_id.isnot(None),
        ]
        bound = ConsistencyChecker.bound_biz_ids(cls.recon_kind)
        if bound is not None:
            conds.append(Waybill.id.notin_(bound))
        if enterprise_id:
            conds.append(Waybill.enterprise_id == enterprise_id)
        return conds

    @classmethod
    async def _pending_waybill_total(
        cls, db: AsyncSession, *, enterprise_id: Optional[int] = None,
    ) -> dict:
        row = (await db.execute(
            select(
                func.count(Waybill.id),
                func.coalesce(func.sum(Waybill.freight_amount), 0),
                func.count(func.distinct(Waybill.customer_id)),
            ).where(*cls._pending_conditions(enterprise_id=enterprise_id))
        )).one()
        return {
            "count": int(row[0] or 0),
            "amount": float(row[1] or 0),
            "customerCount": int(row[2] or 0),
        }

    @classmethod
    async def _recon_count(
        cls,
        db: AsyncSession,
        *,
        dirty: bool = False,
        enterprise_id: Optional[int] = None,
    ) -> int:
        stmt = select(func.count(CustomerRecon.id)).where(
            CustomerRecon.is_deleted == 0,
            CustomerRecon.status != FIN_CANCELLED,
        )
        if dirty:
            stmt = stmt.where(CustomerRecon.dirty_line_count > 0)
        if enterprise_id:
            stmt = stmt.where(CustomerRecon.enterprise_id == enterprise_id)
        return int((await db.execute(stmt)).scalar() or 0)

    @classmethod
    async def _open_diff_total(cls, db: AsyncSession) -> dict:
        row = (await db.execute(
            select(
                func.count(ReconDiff.id),
                func.coalesce(func.sum(ReconDiff.diff_amount), 0),
            ).where(
                ReconDiff.is_deleted == 0,
                ReconDiff.recon_kind == cls.recon_kind,
                ReconDiff.status == DiffStatus.OPEN,
            )
        )).one()
        blocking = int((await db.execute(
            select(func.count(ReconDiff.id)).where(
                ReconDiff.is_deleted == 0,
                ReconDiff.recon_kind == cls.recon_kind,
                ReconDiff.status == DiffStatus.OPEN,
                ReconDiff.severity == DiffSeverity.BLOCKING,
            )
        )).scalar() or 0)
        return {
            "count": int(row[0] or 0),
            "amount": float(row[1] or 0),
            "blockingCount": blocking,
        }

    @classmethod
    async def _pending_sign_total(
        cls, db: AsyncSession, *, enterprise_id: Optional[int] = None,
    ) -> dict:
        stmt = select(
            func.count(CustomerRecon.id),
            func.coalesce(func.sum(CustomerRecon.planned_amount), 0),
        ).where(
            CustomerRecon.is_deleted == 0,
            CustomerRecon.status == FIN_REVIEWED,
            CustomerRecon.confirmed_by_customer_at.is_(None),
        )
        if enterprise_id:
            stmt = stmt.where(CustomerRecon.enterprise_id == enterprise_id)
        row = (await db.execute(stmt)).one()
        return {"count": int(row[0] or 0), "amount": float(row[1] or 0)}

    @classmethod
    async def _confirmed_this_month(
        cls, db: AsyncSession, *, enterprise_id: Optional[int] = None,
    ) -> dict:
        month_start = date.today().replace(day=1)
        stmt = select(
            func.count(CustomerRecon.id),
            func.coalesce(func.sum(CustomerRecon.planned_amount), 0),
        ).where(
            CustomerRecon.is_deleted == 0,
            CustomerRecon.status.notin_((FIN_DRAFT, FIN_CANCELLED)),
            CustomerRecon.reviewed_at >= datetime.combine(month_start, dtime.min),
        )
        if enterprise_id:
            stmt = stmt.where(CustomerRecon.enterprise_id == enterprise_id)
        row = (await db.execute(stmt)).one()
        return {
            "count": int(row[0] or 0),
            "amount": float(row[1] or 0),
            "monthStart": month_start,
        }


__all__ = ["ReconWorkbenchService"]
