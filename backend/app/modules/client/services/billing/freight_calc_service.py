"""
运费计算编排服务（计费引擎 Phase 2 - 编排层）

职责：
  - 把数据库 ORM 加载、标准化、规则筛选与持久化串起来
  - 提供两种入口：
      1) preview_for_waybill : dry_run 试算（不写库），用于编辑时回显
      2) calculate_and_persist: 正式计算，写 result + result_detail，
         刷新 waybill.calc_status / freight_amount，写异常表
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, Optional

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.client.models.billing.freight_calc_exception import FreightCalcException
from app.modules.client.models.billing.freight_calc_result import (
    WaybillFreightResult,
    WaybillFreightResultDetail,
)
from app.modules.client.models.billing.freight_contract import FreightContract
from app.modules.client.models.billing.freight_rate import FreightRate
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.services.billing.freight_matcher import (
    CALC_ENGINE_VERSION,
    CargoInput,
    CargoMatchResult,
    FreightMatcher,
    WaybillContext,
)
from app.modules.client.services.billing.standardize_service import (
    REGION_LEVEL_LABEL,
    StandardizeService,
)


@dataclass
class WaybillCalcSummary:
    waybill_id: int
    waybill_version: int
    total_amount: Decimal
    calc_status: str  # success/partial/exception
    cargo_results: list[CargoMatchResult]
    error_message: Optional[str] = None
    persisted_result_id: Optional[int] = None


class FreightCalcService:

    # ---------- 数据加载 ----------

    @staticmethod
    async def _load_waybill(
        db: AsyncSession, waybill_id: int
    ) -> Optional[Waybill]:
        r = await db.execute(
            select(Waybill).where(
                Waybill.id == waybill_id, Waybill.is_deleted == 0,
            )
        )
        return r.scalar_one_or_none()

    @staticmethod
    async def _load_cargoes(
        db: AsyncSession, waybill_id: int
    ) -> list[WaybillCargo]:
        r = await db.execute(
            select(WaybillCargo).where(
                WaybillCargo.waybill_id == waybill_id,
                WaybillCargo.is_deleted == 0,
            ).order_by(WaybillCargo.sort_order, WaybillCargo.id)
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_active_contracts(
        db: AsyncSession, customer_id: int, billing_date: date
    ) -> list[FreightContract]:
        r = await db.execute(
            select(FreightContract).where(
                FreightContract.customer_id == customer_id,
                FreightContract.status == 1,
                FreightContract.is_deleted == 0,
                FreightContract.effective_date <= billing_date,
                FreightContract.expiry_date >= billing_date,
            )
        )
        return list(r.scalars().all())

    @staticmethod
    async def _load_active_rules(
        db: AsyncSession,
        customer_id: int,
        contract_ids: list[int],
        billing_date: date,
    ) -> list[FreightRate]:
        if not contract_ids:
            return []
        r = await db.execute(
            select(FreightRate).where(
                FreightRate.contract_id.in_(contract_ids),
                FreightRate.customer_id == customer_id,
                FreightRate.status == 1,
                FreightRate.is_deleted == 0,
            )
        )
        rules = [
            r0 for r0 in r.scalars().all()
            if (
                (r0.effective_date is None or r0.effective_date <= billing_date)
                and (r0.expiry_date is None or r0.expiry_date >= billing_date)
            )
        ]
        return rules

    @staticmethod
    async def _build_region_level_cache(
        db: AsyncSession, rules: list[FreightRate]
    ) -> dict[int, str]:
        ids = {r.origin_region_id for r in rules if r.origin_region_id}
        ids |= {r.destination_region_id for r in rules if r.destination_region_id}
        if not ids:
            return {}
        r = await db.execute(
            select(BizRegion).where(
                BizRegion.id.in_(ids), BizRegion.is_deleted == 0,
            )
        )
        return {
            row.id: REGION_LEVEL_LABEL.get(row.level, "custom")
            for row in r.scalars().all()
        }

    @staticmethod
    async def _hydrate_rules_region_ids_from_codes(
        db: AsyncSession, rules: list[FreightRate],
    ) -> None:
        """规则表 origin/destination_region_id 为空时，用国标码或名称反查 biz_region.id。

        仅填充内存中的 ORM 属性，供匹配使用；调用方应对 rule 做 expunge，避免 flush 误写回库。
        """
        for rule in rules:
            if rule.origin_region_id is None:
                oc = (rule.origin_code or "").strip() or None
                on = (rule.origin or "").strip() or None
                if oc or on:
                    res = await StandardizeService.resolve_region(
                        db, region_id=None, code=oc, raw_name=on,
                    )
                    if res.region_id is not None:
                        rule.origin_region_id = res.region_id
            if rule.destination_region_id is None:
                dc = (rule.destination_code or "").strip() or None
                dn = (rule.destination or "").strip() or None
                if dc or dn:
                    res = await StandardizeService.resolve_region(
                        db, region_id=None, code=dc, raw_name=dn,
                    )
                    if res.region_id is not None:
                        rule.destination_region_id = res.region_id

    @staticmethod
    def _detach_freight_rates_from_session(
        db: AsyncSession, rules: list[FreightRate],
    ) -> None:
        """将运价规则从会话中分离，防止后续 flush 把内存补全的 region_id 写回 biz_freight_rate。"""
        for rule in rules:
            db.expunge(rule)

    # ---------- 内部：单次计算（不写库） ----------

    @staticmethod
    async def _calculate_in_memory(
        db: AsyncSession,
        waybill: Waybill,
        cargoes: list[WaybillCargo],
        billing_date: Optional[date] = None,
    ) -> WaybillCalcSummary:
        billing_date = billing_date or (
            waybill.plan_issue_time.date()
            if waybill.plan_issue_time else date.today()
        )

        # 标准化：地区
        origin = await StandardizeService.resolve_region(
            db,
            region_id=waybill.origin_region_id,
            code=waybill.origin_code,
            raw_name=waybill.origin,
        )
        if waybill.origin_region_id is None and origin.region_id is not None:
            waybill.origin_region_id = origin.region_id
        destination = await StandardizeService.resolve_region(
            db,
            region_id=waybill.destination_region_id,
            code=waybill.destination_code,
            raw_name=waybill.destination,
        )
        if waybill.destination_region_id is None and destination.region_id is not None:
            waybill.destination_region_id = destination.region_id
        ctx = WaybillContext(
            customer_id=waybill.customer_id or 0,
            transport_date=billing_date,
            origin=origin,
            destination=destination,
        )

        # 标准化：货物明细的车型
        cargo_inputs: list[CargoInput] = []
        for c in cargoes:
            v = await StandardizeService.resolve_vehicle(
                db,
                brand_id=c.brand_id, series_id=c.series_id,
                raw_brand=c.vehicle_brand, raw_model=c.vehicle_model,
            )
            cargo_inputs.append(CargoInput(
                waybill_cargo_id=c.id,
                quantity=int(c.quantity or 0),
                vehicle=v,
            ))

        # 加载候选合同/规则
        if not waybill.customer_id:
            results = [
                CargoMatchResult(
                    waybill_cargo_id=ci.waybill_cargo_id,
                    error_type="CONTRACT_NOT_FOUND",
                    error_message="运单缺少客户信息",
                ) for ci in cargo_inputs
            ]
        else:
            contracts = await FreightCalcService._load_active_contracts(
                db, waybill.customer_id, billing_date,
            )
            if not contracts:
                results = [
                    CargoMatchResult(
                        waybill_cargo_id=ci.waybill_cargo_id,
                        error_type="CONTRACT_NOT_FOUND",
                        error_message="客户在该运输日期无生效合同",
                    ) for ci in cargo_inputs
                ]
            else:
                rules = await FreightCalcService._load_active_rules(
                    db,
                    waybill.customer_id,
                    [c.id for c in contracts],
                    billing_date,
                )
                await FreightCalcService._hydrate_rules_region_ids_from_codes(db, rules)
                FreightCalcService._detach_freight_rates_from_session(db, rules)
                contract_map = {c.id: c for c in contracts}
                region_cache = await FreightCalcService._build_region_level_cache(db, rules)

                results = [
                    FreightMatcher.match_one_cargo(
                        ctx=ctx,
                        cargo=ci,
                        candidate_rules=rules,
                        contract_map=contract_map,
                        region_level_cache=region_cache,
                    )
                    for ci in cargo_inputs
                ]

        # 整单价分摊（billing_mode=2）：多明细命中同一条整单价规则时，
        # 按 quantity 加权重新分摊金额，避免重复加总
        qty_by_cargo = {ci.waybill_cargo_id: ci.quantity for ci in cargo_inputs}
        FreightCalcService._reallocate_whole_trip_amount(results, qty_by_cargo)

        total = sum((r.amount for r in results if r.calc_status == "success"),
                    Decimal("0"))
        success_cnt = sum(1 for r in results if r.calc_status == "success")
        if success_cnt == len(results) and results:
            calc_status = "success"
        elif success_cnt == 0:
            calc_status = "exception"
        else:
            calc_status = "partial"

        return WaybillCalcSummary(
            waybill_id=waybill.id,
            waybill_version=waybill.waybill_version or 1,
            total_amount=total,
            calc_status=calc_status,
            cargo_results=results,
        )

    @staticmethod
    def _reallocate_whole_trip_amount(
        results: list[CargoMatchResult],
        qty_by_cargo: dict[int, int],
    ) -> None:
        """整单价规则的金额按 quantity 分摊；同一 rule_id 只算一次。"""
        groups: dict[int, list[CargoMatchResult]] = {}
        for r in results:
            if (
                r.calc_status == "success"
                and r.matched_rule is not None
                and r.billing_mode == 2
            ):
                groups.setdefault(r.matched_rule.id, []).append(r)

        for items in groups.values():
            if len(items) <= 1:
                continue
            unit_price = items[0].matched_rule.unit_price or Decimal("0")
            min_amount = items[0].matched_rule.min_amount
            base = unit_price
            if min_amount is not None and base < min_amount:
                base = min_amount
            qtys = [
                max(int(qty_by_cargo.get(it.waybill_cargo_id, 0) or 0), 0)
                for it in items
            ]
            total_qty = sum(qtys) or len(items)
            allocated = Decimal("0")
            shares: list[Decimal] = []
            for q in qtys[:-1]:
                share = (base * Decimal(q) / Decimal(total_qty)).quantize(Decimal("0.01"))
                shares.append(share)
                allocated += share
            shares.append((base - allocated).quantize(Decimal("0.01")))
            for it, share in zip(items, shares):
                it.amount = share

    # ---------- 公共入口 ----------

    @staticmethod
    async def preview_for_waybill(
        db: AsyncSession,
        waybill: Waybill,
        cargoes: list[WaybillCargo],
        billing_date: Optional[date] = None,
    ) -> WaybillCalcSummary:
        """试算（dry_run）：仅返回内存结果，不落库。"""
        return await FreightCalcService._calculate_in_memory(
            db, waybill, cargoes, billing_date,
        )

    @staticmethod
    async def calculate_and_persist(
        db: AsyncSession,
        waybill_id: int,
        *,
        triggered_by: str = "manual_recalc",
        triggered_user_id: Optional[int] = None,
        billing_date: Optional[date] = None,
    ) -> WaybillCalcSummary:
        """正式计算并落库：写 result + detail，更新 waybill 与异常表。"""
        waybill = await FreightCalcService._load_waybill(db, waybill_id)
        if not waybill:
            raise ValueError(f"运单不存在: {waybill_id}")

        if waybill.is_locked == 1:
            # 锁定运单不重算，但写一条异常便于追踪
            db.add(FreightCalcException(
                waybill_id=waybill.id,
                exception_type="WAYBILL_LOCKED",
                exception_message="运单已锁定，跳过重算",
                context_json={"triggered_by": triggered_by},
            ))
            await db.flush()
            return WaybillCalcSummary(
                waybill_id=waybill.id,
                waybill_version=waybill.waybill_version or 1,
                total_amount=waybill.freight_amount or Decimal("0"),
                calc_status="locked",
                cargo_results=[],
                error_message="运单已锁定",
            )

        # 标记 calculating
        waybill.calc_status = "calculating"
        await db.flush()

        cargoes = await FreightCalcService._load_cargoes(db, waybill_id)
        summary = await FreightCalcService._calculate_in_memory(
            db, waybill, cargoes, billing_date,
        )

        # 把上一条 result 标记为非活跃
        await db.execute(
            update(WaybillFreightResult)
            .where(
                WaybillFreightResult.waybill_id == waybill_id,
                WaybillFreightResult.is_active == 1,
                WaybillFreightResult.is_deleted == 0,
            )
            .values(is_active=0)
        )

        # 写 result 主表
        now = datetime.now()
        result = WaybillFreightResult(
            waybill_id=waybill.id,
            waybill_version=summary.waybill_version,
            is_active=1,
            total_amount=summary.total_amount,
            calc_status=summary.calc_status,
            calc_engine_version=CALC_ENGINE_VERSION,
            calc_time=now,
            error_message=(
                "存在异常明细，详见 result_detail" if summary.calc_status != "success" else None
            ),
            triggered_by=triggered_by,
            triggered_user_id=triggered_user_id,
        )
        db.add(result)
        await db.flush()

        # 写 result_detail 与异常
        cargo_index = {c.id: c for c in cargoes}
        for cr in summary.cargo_results:
            cargo = cargo_index.get(cr.waybill_cargo_id)
            db.add(WaybillFreightResultDetail(
                result_id=result.id,
                waybill_id=waybill.id,
                waybill_cargo_id=cr.waybill_cargo_id,
                brand_id=cargo.brand_id if cargo else None,
                series_id=cargo.series_id if cargo else None,
                vehicle_brand=cargo.vehicle_brand if cargo else None,
                vehicle_model=cargo.vehicle_model if cargo else None,
                quantity=int(cargo.quantity or 0) if cargo else 0,
                matched_contract_id=cr.matched_contract.id if cr.matched_contract else None,
                matched_rule_id=cr.matched_rule.id if cr.matched_rule else None,
                matched_rule_version=(cr.matched_rule.rule_version if cr.matched_rule else None),
                origin_match_region_id=cr.origin_match_region_id,
                origin_match_level=cr.origin_match_level,
                destination_match_region_id=cr.destination_match_region_id,
                destination_match_level=cr.destination_match_level,
                direction=cr.direction,
                model_match_type=cr.model_match_type,
                unit_price=cr.unit_price,
                billing_mode=cr.billing_mode,
                distance_km=cr.distance_km,
                amount=cr.amount,
                match_score=cr.score,
                match_trace_json=cr.match_trace,
                calc_status=cr.calc_status,
                error_type=cr.error_type,
                error_message=cr.error_message,
            ))

            if cr.error_type:
                db.add(FreightCalcException(
                    waybill_id=waybill.id,
                    waybill_cargo_id=cr.waybill_cargo_id,
                    exception_type=cr.error_type,
                    exception_message=cr.error_message or cr.error_type,
                    context_json={
                        "triggered_by": triggered_by,
                        "match_trace": cr.match_trace,
                    },
                ))

        # 刷运单字段
        if summary.calc_status == "success":
            waybill.calc_status = "calculated"
            waybill.freight_amount = summary.total_amount
            waybill.freight_source = 0  # 自动计算
        elif summary.calc_status == "partial":
            waybill.calc_status = "exception"
            # 部分命中也把已有金额写回，便于业务参考
            waybill.freight_amount = summary.total_amount
            waybill.freight_source = 0
        else:
            waybill.calc_status = "exception"
            waybill.freight_amount = None
        waybill.last_calc_at = now
        waybill.last_result_id = result.id

        # 命中的合同/运价回填到 waybill（用首条 success 行）
        first_hit = next(
            (r for r in summary.cargo_results if r.calc_status == "success"),
            None,
        )
        if first_hit and first_hit.matched_contract:
            waybill.contract_id = first_hit.matched_contract.id
            if first_hit.matched_rule:
                waybill.rate_id = first_hit.matched_rule.id

        await db.flush()
        summary.persisted_result_id = result.id
        return summary

    # ---------- 受影响运单查找 ----------

    @staticmethod
    async def find_affected_waybills_for_rule(
        db: AsyncSession,
        rule: FreightRate,
        *,
        only_unlocked: bool = True,
    ) -> list[int]:
        """规则变更后，找出可能受影响的运单 ID 列表。

        粗匹配（重算时还会再做精细评分）：
          - customer_id 相同
          - origin_region_id == rule.origin_region_id
            或 destination_region_id == rule.destination_region_id
            （含双向时反过来也算）
          - 运输日期与规则生效期有交集（缺少日期时不限）
        """
        conds = [
            Waybill.customer_id == rule.customer_id,
            Waybill.is_deleted == 0,
        ]
        if only_unlocked:
            conds.append(Waybill.is_locked == 0)

        if rule.origin_region_id and rule.destination_region_id:
            if rule.is_bidirectional == 1:
                line_cond = (
                    and_(
                        Waybill.origin_region_id == rule.origin_region_id,
                        Waybill.destination_region_id == rule.destination_region_id,
                    )
                    | and_(
                        Waybill.origin_region_id == rule.destination_region_id,
                        Waybill.destination_region_id == rule.origin_region_id,
                    )
                )
            else:
                line_cond = and_(
                    Waybill.origin_region_id == rule.origin_region_id,
                    Waybill.destination_region_id == rule.destination_region_id,
                )
            conds.append(line_cond)

        r = await db.execute(select(Waybill.id).where(*conds))
        return [row[0] for row in r.all()]

    @staticmethod
    async def find_affected_waybills_for_contract(
        db: AsyncSession,
        contract: FreightContract,
        *,
        only_unlocked: bool = True,
    ) -> list[int]:
        """合同变更后，按客户范围扫描受影响运单。"""
        conds = [
            Waybill.customer_id == contract.customer_id,
            Waybill.is_deleted == 0,
        ]
        if only_unlocked:
            conds.append(Waybill.is_locked == 0)
        r = await db.execute(select(Waybill.id).where(*conds))
        return [row[0] for row in r.all()]

    # ---------- 受影响运单的批量重算 ----------

    @staticmethod
    async def recalculate_many(
        db: AsyncSession,
        waybill_ids: Iterable[int],
        *,
        triggered_by: str,
        triggered_user_id: Optional[int] = None,
    ) -> list[WaybillCalcSummary]:
        """对若干运单同步重算（用于试运行、Worker 调度）。"""
        out: list[WaybillCalcSummary] = []
        for wid in waybill_ids:
            try:
                summary = await FreightCalcService.calculate_and_persist(
                    db, wid,
                    triggered_by=triggered_by,
                    triggered_user_id=triggered_user_id,
                )
                out.append(summary)
            except Exception as e:  # noqa: BLE001
                # 单条失败不影响其它
                out.append(WaybillCalcSummary(
                    waybill_id=wid,
                    waybill_version=0,
                    total_amount=Decimal("0"),
                    calc_status="exception",
                    cargo_results=[],
                    error_message=str(e),
                ))
        return out
