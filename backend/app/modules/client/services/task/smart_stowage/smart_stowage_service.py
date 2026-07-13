"""
智能配载编排层

职责：
  - 拉取候选商品车（复用 TaskWaybillItemService.list_candidate_cargoes）
  - 调用纯算法引擎 SmartStowageEngine 生成方案
  - 落库 biz_smart_stowage_plan / _plan_item
  - 采纳方案 -> 复用 TaskService.create_task(source=2) 落为任务单

同步路径与异步 worker 共用 run_generation()。
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.task.smart_stowage import (
    PLAN_STATUS_ADOPTED,
    PLAN_STATUS_IGNORED,
    PLAN_STATUS_PENDING,
    SmartStowagePlan,
    SmartStowagePlanItem,
)
from app.modules.client.schemas.task.task import TaskCreate
from app.modules.client.schemas.task.task_waybill_item import TaskWaybillItemIn
from app.modules.client.services.task.smart_stowage.constants import (
    DEFAULT_CANDIDATE_LIMIT,
    DEFAULT_MAX_PLANS,
    DEFAULT_MIN_LOAD_RATE,
    DEFAULT_TARGET_SPOTS,
    DEFAULT_WEIGHTS,
)
from app.modules.client.services.task.smart_stowage.stowage_engine import (
    CargoCandidate,
    EngineParams,
    SmartStowageEngine,
)
from app.modules.client.services.task.smart_stowage.stowage_task_service import (
    SmartStowageTaskService,
)
from app.modules.client.services.task.task_service import TaskService
from app.modules.client.services.task.task_waybill_item_service import (
    TaskWaybillItemService,
)


class SmartStowageService:

    # ------------------------------------------------------------------
    # 生成（同步）：create -> claim -> run，一步产出方案
    # ------------------------------------------------------------------
    @staticmethod
    async def generate_sync(
        db: AsyncSession,
        *,
        filter_payload: dict[str, Any],
        params_payload: dict[str, Any],
        current_user_id: Optional[int] = None,
        user_name: Optional[str] = None,
    ) -> int:
        task = await SmartStowageTaskService.create_task(
            db,
            filter_payload=filter_payload,
            params_payload=params_payload,
            triggered_by_user_id=current_user_id,
            triggered_by_name=user_name,
        )
        await SmartStowageTaskService.claim_one(db, task.id)
        try:
            await SmartStowageService.run_generation(db, task.id)
        except Exception as e:  # noqa: BLE001
            await SmartStowageTaskService.mark_failed(db, task.id, repr(e))
            raise
        return task.id

    # ------------------------------------------------------------------
    # 生成核心（同步/异步共用）
    # ------------------------------------------------------------------
    @staticmethod
    async def run_generation(db: AsyncSession, task_id: int) -> None:
        task = await SmartStowageTaskService.get(db, task_id)
        if task is None:
            raise BizException("生成任务不存在")

        filter_payload = json.loads(task.filter_json or "{}")
        params_payload = json.loads(task.params_json or "{}")

        # 1. 拉候选商品车
        candidate_out = await TaskWaybillItemService.list_candidate_cargoes(
            db,
            keyword=filter_payload.get("keyword"),
            customer_id=filter_payload.get("customerId"),
            origin_keyword=filter_payload.get("originKeyword"),
            destination_keyword=filter_payload.get("destinationKeyword"),
            model_keyword=filter_payload.get("modelKeyword"),
            offset=0,
            limit=int(filter_payload.get("limit") or DEFAULT_CANDIDATE_LIMIT),
        )
        candidates = [
            CargoCandidate(
                waybill_id=c.waybillId,
                waybill_cargo_id=c.cargoId,
                quantity=c.remainingQuantity,
                waybill_no=c.waybillNo,
                customer_id=c.customerId,
                customer_name=c.customerName,
                vehicle_brand=c.vehicleBrand,
                vehicle_model=c.vehicleModel,
                vin=c.vin,
                origin=c.origin,
                destination=c.destination,
            )
            for c in candidate_out.items
            if c.remainingQuantity and c.remainingQuantity > 0
        ]

        # 2. 组装参数并跑算法
        engine_params = EngineParams(
            target_spots=int(params_payload.get("targetSpots") or DEFAULT_TARGET_SPOTS),
            occupy_overrides=params_payload.get("occupyOverrides") or {},
            weights=params_payload.get("weights") or dict(DEFAULT_WEIGHTS),
            min_load_rate=float(
                params_payload.get("minLoadRate", DEFAULT_MIN_LOAD_RATE)
            ),
            max_plans=int(params_payload.get("maxPlans") or DEFAULT_MAX_PLANS),
        )
        plans = SmartStowageEngine.generate(candidates, engine_params)

        # 3. 落库
        for pr in plans:
            plan = SmartStowagePlan(
                plan_task_id=task_id,
                plan_no=pr.plan_no,
                origin=pr.origin,
                destination=pr.destination,
                vehicle_count=pr.vehicle_count,
                occupied_spots=pr.occupied_spots,
                target_spots=pr.target_spots,
                load_rate=pr.load_rate,
                customer_count=pr.customer_count,
                waybill_count=pr.waybill_count,
                score=pr.score,
                reason=pr.reason,
                status=PLAN_STATUS_PENDING,
            )
            db.add(plan)
            await db.flush()
            for it in pr.items:
                db.add(SmartStowagePlanItem(
                    plan_id=plan.id,
                    waybill_id=it.waybill_id,
                    waybill_cargo_id=it.waybill_cargo_id,
                    quantity=it.quantity,
                    waybill_no=it.waybill_no,
                    customer_id=it.customer_id,
                    customer_name=it.customer_name,
                    vehicle_brand=it.vehicle_brand,
                    vehicle_model=it.vehicle_model,
                    vin=it.vin,
                    origin=it.origin,
                    destination=it.destination,
                    occupy_coefficient=it.occupy_coefficient,
                ))
        await db.flush()

        await SmartStowageTaskService.mark_success(
            db, task_id,
            candidate_count=len(candidates),
            plan_count=len(plans),
        )

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    @staticmethod
    async def list_plans(db: AsyncSession, plan_task_id: int) -> list[dict]:
        r = await db.execute(
            select(SmartStowagePlan)
            .where(
                SmartStowagePlan.plan_task_id == plan_task_id,
                SmartStowagePlan.is_deleted == 0,
            )
            .order_by(SmartStowagePlan.score.desc(), SmartStowagePlan.plan_no.asc())
        )
        plans = list(r.scalars().all())
        if not plans:
            return []
        plan_ids = [p.id for p in plans]
        ir = await db.execute(
            select(SmartStowagePlanItem)
            .where(
                SmartStowagePlanItem.plan_id.in_(plan_ids),
                SmartStowagePlanItem.is_deleted == 0,
            )
            .order_by(SmartStowagePlanItem.id.asc())
        )
        items_by_plan: dict[int, list] = {}
        for it in ir.scalars().all():
            items_by_plan.setdefault(it.plan_id, []).append(it)

        return [
            SmartStowageService._plan_to_dict(p, items_by_plan.get(p.id, []))
            for p in plans
        ]

    @staticmethod
    def _plan_to_dict(plan: SmartStowagePlan, items: list) -> dict:
        return {
            "id": plan.id,
            "planTaskId": plan.plan_task_id,
            "planNo": plan.plan_no,
            "origin": plan.origin,
            "destination": plan.destination,
            "vehicleCount": plan.vehicle_count,
            "occupiedSpots": float(plan.occupied_spots or 0),
            "targetSpots": plan.target_spots,
            "loadRate": float(plan.load_rate or 0),
            "customerCount": plan.customer_count,
            "waybillCount": plan.waybill_count,
            "score": float(plan.score or 0),
            "reason": plan.reason,
            "status": plan.status,
            "adoptedTaskId": plan.adopted_task_id,
            "adoptedAt": plan.adopted_at,
            "items": [
                {
                    "id": it.id,
                    "waybillId": it.waybill_id,
                    "waybillCargoId": it.waybill_cargo_id,
                    "quantity": it.quantity,
                    "waybillNo": it.waybill_no,
                    "customerName": it.customer_name,
                    "vehicleBrand": it.vehicle_brand,
                    "vehicleModel": it.vehicle_model,
                    "vin": it.vin,
                    "origin": it.origin,
                    "destination": it.destination,
                    "occupyCoefficient": float(it.occupy_coefficient or 1),
                }
                for it in items
            ],
        }

    # ------------------------------------------------------------------
    # 采纳 / 忽略
    # ------------------------------------------------------------------
    @staticmethod
    async def adopt_plan(
        db: AsyncSession,
        plan_id: int,
        *,
        remark: Optional[str] = None,
        current_user_id: Optional[int] = None,
        dispatcher_name: Optional[str] = None,
    ) -> int:
        plan = await SmartStowageService._get_plan_or_404(db, plan_id)
        if plan.status == PLAN_STATUS_ADOPTED:
            raise BizException("该方案已采纳，请勿重复操作")

        ir = await db.execute(
            select(SmartStowagePlanItem).where(
                SmartStowagePlanItem.plan_id == plan_id,
                SmartStowagePlanItem.is_deleted == 0,
            )
        )
        items = list(ir.scalars().all())
        if not items:
            raise BizException("方案明细为空，无法采纳")

        payload = TaskCreate(
            source=2,  # AI 智能配载
            remark=remark or plan.reason,
            waybillItems=[
                TaskWaybillItemIn(
                    waybillId=it.waybill_id,
                    waybillCargoId=it.waybill_cargo_id,
                    quantity=it.quantity,
                )
                for it in items
            ],
            segments=[],
            carrier=None,
        )
        task = await TaskService.create_task(
            db, payload,
            current_user_id=current_user_id,
            dispatcher_name=dispatcher_name,
        )

        plan.status = PLAN_STATUS_ADOPTED
        plan.adopted_task_id = task.id
        plan.adopted_at = datetime.now()
        await db.flush()
        await SmartStowageTaskService.incr_adopted(db, plan.plan_task_id)
        return task.id

    @staticmethod
    async def ignore_plan(db: AsyncSession, plan_id: int) -> None:
        plan = await SmartStowageService._get_plan_or_404(db, plan_id)
        if plan.status == PLAN_STATUS_ADOPTED:
            raise BizException("已采纳的方案不可忽略")
        plan.status = PLAN_STATUS_IGNORED
        await db.flush()

    @staticmethod
    async def _get_plan_or_404(
        db: AsyncSession, plan_id: int
    ) -> SmartStowagePlan:
        r = await db.execute(
            select(SmartStowagePlan).where(
                SmartStowagePlan.id == plan_id,
                SmartStowagePlan.is_deleted == 0,
            )
        )
        plan = r.scalar_one_or_none()
        if plan is None:
            raise BizException("配载方案不存在")
        return plan
