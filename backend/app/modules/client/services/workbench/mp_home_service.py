"""管理员小程序首页聚合 + 统一速查。"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.partner.customer import Customer
from app.modules.client.services.approval import ApprovalQueryService
from app.modules.client.services.capacity.self_capacity.capacity_service import (
    CapacityService,
)
from app.modules.client.services.compliance.compliance_alert_service import (
    ComplianceAlertService,
)
from app.modules.client.services.insight.cockpit_service import CockpitService
from app.modules.client.services.partner.carrier_service import CarrierService
from app.modules.client.services.partner.customer_service import CustomerService
from app.modules.client.services.task.task_finance_service import TaskFinanceService
from app.modules.client.services.task.task_service import TaskService
from sqlalchemy import select


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


class MpHomeService:
    @staticmethod
    async def home_summary(
        db: AsyncSession,
        *,
        user_id: int,
        persona: Optional[str],
    ) -> dict:
        key = (persona or "dispatch").strip() or "dispatch"
        inbox_count = 0
        try:
            inbox_count = await ApprovalQueryService.pending_count(db, user_id=user_id)
        except Exception:  # noqa: BLE001
            inbox_count = 0

        builders = {
            "dispatch": MpHomeService._dispatch,
            "boss": MpHomeService._boss,
            "finance": MpHomeService._finance,
            "captain": MpHomeService._captain,
        }
        builder = builders.get(key, MpHomeService._dispatch)
        try:
            view = await builder(db, user_id=user_id, pending_count=inbox_count)
        except Exception:  # noqa: BLE001
            view = {
                "kpis": [],
                "notice": "",
                "primaryAction": None,
                "extra": {},
            }
        view["persona"] = key
        view["inboxCount"] = inbox_count
        return view

    @staticmethod
    async def _dispatch(db: AsyncSession, **_kwargs) -> dict:
        stats = await TaskService.workbench_stats(db)
        totals = stats.get("totals") or {}
        alerts = stats.get("alerts") or {}
        overdue = _safe_int(alerts.get("overdueArrive"))
        pending_dispatch = _safe_int(totals.get("pendingDispatch"))
        notice = ""
        if overdue:
            notice = f"{overdue} 单已超过约定到货时间，先处理超时的。"
        elif pending_dispatch:
            notice = f"还有 {pending_dispatch} 单待派车。"
        return {
            "kpis": [
                {"label": "待派车", "value": pending_dispatch, "alert": False},
                {"label": "待装车", "value": _safe_int(totals.get("pendingLoad")), "alert": False},
                {"label": "在途", "value": _safe_int(totals.get("onWay")), "alert": False},
                {"label": "已超时", "value": overdue, "alert": overdue > 0},
            ],
            "notice": notice,
            "primaryAction": {"label": "去派车", "path": "/pages/dispatch/index?stage=1"},
            "extra": {"totals": totals, "alerts": alerts},
        }

    @staticmethod
    async def _boss(db: AsyncSession, pending_count: int = 0, **_kwargs) -> dict:
        now = datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        kpi = await CockpitService.kpi_summary(db, start, now)
        revenue = (kpi.get("revenue") or {}).get("todayValue") or 0
        waybills = (kpi.get("waybillCount") or {}).get("todayValue") or 0
        vehicles = (kpi.get("vehicleQuantity") or {}).get("todayValue") or 0
        notice = f"今日 {int(waybills)} 个计划，待你放行 {pending_count} 件。" if pending_count else ""
        return {
            "kpis": [
                {"label": "今日运费", "value": round(_safe_float(revenue) / 10000, 1), "suffix": "万", "alert": False},
                {"label": "今日计划", "value": _safe_int(waybills), "alert": False},
                {"label": "商品车", "value": _safe_int(vehicles), "suffix": "台", "alert": False},
                {"label": "待批", "value": pending_count, "alert": pending_count > 0},
            ],
            "notice": notice,
            "primaryAction": {"label": "去审批", "path": "/pages/approval/index"},
            "extra": {"kpi": kpi},
        }

    @staticmethod
    async def _finance(db: AsyncSession, **_kwargs) -> dict:
        stats = await TaskFinanceService.workbench_stats(db)
        totals = stats.get("totals") or {}
        amounts = stats.get("amounts") or {}
        pending_pay = _safe_int(totals.get("pendingPay"))
        pending_review = _safe_int(totals.get("pendingReview"))
        pay_amt = _safe_float(amounts.get("pendingPayAmount"))
        notice = f"{pending_pay} 张待付，合计 {round(pay_amt / 10000, 1)} 万。" if pending_pay else ""
        return {
            "kpis": [
                {"label": "待付", "value": round(pay_amt / 10000, 1), "suffix": "万", "alert": pending_pay > 0},
                {"label": "待审批单", "value": pending_review, "alert": False},
                {"label": "今日已付", "value": round(_safe_float(amounts.get("todayPaidAmount")) / 10000, 1), "suffix": "万", "alert": False},
                {"label": "待付张数", "value": pending_pay, "alert": pending_pay > 0},
            ],
            "notice": notice,
            "primaryAction": {"label": "标记支付", "path": "/pages/fee/index"},
            "extra": {"totals": totals, "amounts": amounts},
            "canSeeAmount": True,
        }

    @staticmethod
    async def _captain(db: AsyncSession, **_kwargs) -> dict:
        cap = await CapacityService.list_stats(db)
        on_way = _safe_int((cap or {}).get("inTransit"))
        idle = _safe_int((cap or {}).get("available"))
        license_warn = 0
        try:
            summary = await ComplianceAlertService.summary(db)
            if isinstance(summary, dict):
                license_warn = _safe_int(summary.get("total"))
        except Exception:  # noqa: BLE001
            license_warn = 0
        notice = f"{license_warn} 条证照预警，派车前先看一眼。" if license_warn else ""
        return {
            "kpis": [
                {"label": "在途车辆", "value": on_way, "alert": False},
                {"label": "证照临期", "value": license_warn, "alert": license_warn > 0},
                {"label": "今日可派", "value": idle, "alert": False},
                {"label": "待催司机", "value": 0, "alert": False},
            ],
            "notice": notice,
            "primaryAction": {"label": "催司机", "path": "/pages/track/index"},
            "extra": {"capacity": cap, "licenseWarn": license_warn},
        }

    @staticmethod
    async def lookup(db: AsyncSession, keyword: str) -> dict:
        kw = (keyword or "").strip()
        if not kw:
            return {"items": []}

        items: list[dict] = []

        customers = await CustomerService.select_customers(db, keyword=kw)
        customer_ids = [c["id"] for c in customers[:8]]
        phone_map: dict[int, str] = {}
        if customer_ids:
            rows = await db.execute(
                select(Customer.id, Customer.contact_phone).where(Customer.id.in_(customer_ids))
            )
            phone_map = {int(i): (p or "") for i, p in rows.all()}
        for c in customers[:8]:
            items.append({
                "type": "customer",
                "id": c["id"],
                "title": c.get("customerName") or c.get("shortName") or "",
                "subtitle": c.get("customerCode") or "客户",
                "phone": phone_map.get(int(c["id"]), ""),
            })

        carriers = await CarrierService.select_for_picker(db, keyword=kw)
        for c in carriers[:8]:
            items.append({
                "type": "carrier",
                "id": c.id,
                "title": c.carrier_name or c.short_name or "",
                "subtitle": c.carrier_code or "承运商",
                "phone": getattr(c, "contact_phone", "") or "",
            })

        caps = await CapacityService.page_capacities(
            db, page=1, page_size=8, keyword=kw
        )
        cap_items = caps.get("list") or caps.get("items") or []
        for row in cap_items[:8]:
            data = row if isinstance(row, dict) else (row.model_dump() if hasattr(row, "model_dump") else {})
            items.append({
                "type": "capacity",
                "id": data.get("id"),
                "title": data.get("plateNumber") or "",
                "subtitle": f"{data.get('driverName') or ''} · 自有运力".strip(" ·"),
                "phone": data.get("driverPhone") or "",
            })

        return {"items": items}
