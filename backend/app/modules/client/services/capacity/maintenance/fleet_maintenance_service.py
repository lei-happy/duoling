"""
车辆资产 - 维修保养服务

工单闭环 + 保养计划 + 看板；开工/完工联动车辆与运力状态。
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.maintenance.maintain_plan import FleetMaintainPlan
from app.modules.client.models.capacity.maintenance.part import FleetPart
from app.modules.client.models.capacity.maintenance.work_order import FleetWorkOrder
from app.modules.client.models.capacity.maintenance.work_order_line import (
    FleetWorkOrderLine,
)
from app.modules.client.models.capacity.self_capacity.capacity import Capacity
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.schemas.capacity.maintenance import (
    MaintainPlanCreate,
    MaintainPlanOut,
    MaintainPlanUpdate,
    WorkOrderCompleteBody,
    WorkOrderCreate,
    WorkOrderLineIn,
    WorkOrderLineOut,
    WorkOrderOut,
    WorkOrderUpdate,
)
from app.modules.client.services.capacity.maintenance.fleet_parts_service import (
    FleetPartsService,
)
from app.modules.client.services.capacity.self_capacity.capacity_service import (
    CapacityService,
)
from app.modules.client.services.capacity.self_capacity.vehicle_status_service import (
    VehicleStatusService,
)

ORDER_TYPES = {"repair", "maintenance"}
WO_STATUSES = {"draft", "in_progress", "completed", "cancelled"}
CYCLE_TYPES = {"time", "mileage", "either"}
LINE_TYPES = {"labor", "part", "other"}
FAULT_CATEGORIES = {
    "engine",
    "brake",
    "electrical",
    "body",
    "tire",
    "routine",
    "other",
}
MILEAGE_REMIND_BUFFER = 500
_ZERO = Decimal("0")
_CENT = Decimal("0.01")


class FleetMaintenanceService:

    # ---------- 序列化 ----------

    @staticmethod
    def _line_out(line: FleetWorkOrderLine) -> dict[str, Any]:
        return WorkOrderLineOut(
            id=line.id,
            workOrderId=line.work_order_id,
            lineType=line.line_type,
            partId=line.part_id,
            title=line.title,
            qty=line.qty,
            unitPrice=line.unit_price,
            laborHours=line.labor_hours,
            amount=line.amount,
            sortOrder=line.sort_order,
        ).model_dump(mode="json")

    @staticmethod
    def _wo_out(
        row: FleetWorkOrder,
        lines: Optional[list[FleetWorkOrderLine]] = None,
    ) -> dict[str, Any]:
        return WorkOrderOut(
            id=row.id,
            workOrderNo=row.work_order_no,
            vehicleId=row.vehicle_id,
            plateNumber=row.plate_number,
            orderType=row.order_type,
            planId=row.plan_id,
            title=row.title,
            description=row.description,
            odometer=row.odometer,
            faultCategory=row.fault_category,
            workshopId=row.workshop_id,
            workshop=row.workshop,
            expectFinishDate=row.expect_finish_date,
            laborAmount=row.labor_amount,
            partsAmount=row.parts_amount,
            costAmount=row.cost_amount,
            costRemark=row.cost_remark,
            status=row.status,
            startedAt=row.started_at,
            finishedAt=row.finished_at,
            capacityId=row.capacity_id,
            remark=row.remark,
            lines=[FleetMaintenanceService._line_out(x) for x in lines]
            if lines is not None
            else None,
            createdAt=row.created_at,
            updatedAt=row.updated_at,
        ).model_dump(mode="json")

    @staticmethod
    async def _load_lines(
        db: AsyncSession, wo_id: int
    ) -> list[FleetWorkOrderLine]:
        return list(
            (
                await db.execute(
                    select(FleetWorkOrderLine)
                    .where(
                        FleetWorkOrderLine.work_order_id == wo_id,
                        FleetWorkOrderLine.is_deleted == 0,
                    )
                    .order_by(
                        FleetWorkOrderLine.sort_order.asc(),
                        FleetWorkOrderLine.id.asc(),
                    )
                )
            ).scalars().all()
        )

    @staticmethod
    async def _wo_out_with_lines(db: AsyncSession, row: FleetWorkOrder) -> dict:
        lines = await FleetMaintenanceService._load_lines(db, row.id)
        return FleetMaintenanceService._wo_out(row, lines)

    @staticmethod
    def _calc_line_amount(line: WorkOrderLineIn) -> Decimal:
        if line.amount is not None:
            return Decimal(str(line.amount)).quantize(_CENT)
        qty = Decimal(str(line.qty or 1))
        price = Decimal(str(line.unitPrice or 0))
        return (qty * price).quantize(_CENT)

    @staticmethod
    async def _replace_lines(
        db: AsyncSession,
        wo: FleetWorkOrder,
        lines: Optional[list[WorkOrderLineIn]],
    ) -> None:
        existing = await FleetMaintenanceService._load_lines(db, wo.id)
        for e in existing:
            e.is_deleted = 1

        labor_sum = _ZERO
        parts_sum = _ZERO
        if lines:
            for idx, item in enumerate(lines):
                if item.lineType not in LINE_TYPES:
                    raise BizException("明细行类型不正确")
                title = (item.title or "").strip()
                if not title:
                    raise BizException("请填写明细行名称")
                qty = Decimal(str(item.qty or 1))
                if qty <= 0:
                    raise BizException("明细数量须大于 0")
                part_id = item.partId
                if item.lineType == "part":
                    if not part_id:
                        raise BizException("备件行请选择备件")
                    part = (
                        await db.execute(
                            select(FleetPart).where(
                                FleetPart.id == part_id,
                                FleetPart.is_deleted == 0,
                            )
                        )
                    ).scalar_one_or_none()
                    if not part or part.status != 1:
                        raise BizException(f"备件「{title}」不可用，请重新选择")
                    title = part.part_name
                    if item.unitPrice is None and part.ref_price is not None:
                        item.unitPrice = part.ref_price
                amount = FleetMaintenanceService._calc_line_amount(item)
                db.add(
                    FleetWorkOrderLine(
                        work_order_id=wo.id,
                        line_type=item.lineType,
                        part_id=part_id if item.lineType == "part" else None,
                        title=title,
                        qty=qty,
                        unit_price=item.unitPrice,
                        labor_hours=item.laborHours,
                        amount=amount,
                        sort_order=item.sortOrder if item.sortOrder else idx,
                    )
                )
                if item.lineType == "part":
                    parts_sum += amount
                else:
                    labor_sum += amount

        wo.labor_amount = labor_sum
        wo.parts_amount = parts_sum
        wo.cost_amount = labor_sum + parts_sum

    @staticmethod
    def _plan_out(row: FleetMaintainPlan, due_level: Optional[str] = None) -> dict:
        return MaintainPlanOut(
            id=row.id,
            vehicleId=row.vehicle_id,
            plateNumber=row.plate_number,
            name=row.name,
            cycleType=row.cycle_type,
            intervalDays=row.interval_days,
            intervalMileage=row.interval_mileage,
            lastMaintainDate=row.last_maintain_date,
            lastMaintainMileage=row.last_maintain_mileage,
            nextMaintainDate=row.next_maintain_date,
            nextMaintainMileage=row.next_maintain_mileage,
            remindDays=row.remind_days,
            enabled=row.enabled,
            dueLevel=due_level,
            createdAt=row.created_at,
            updatedAt=row.updated_at,
        ).model_dump(mode="json")

    # ---------- 车辆 ----------

    @staticmethod
    async def _get_vehicle(db: AsyncSession, vehicle_id: int) -> Vehicle:
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise BizException("车辆不存在")
        return vehicle

    @staticmethod
    async def _gen_work_order_no(db: AsyncSession) -> str:
        """按当日前缀取最大序号 +1（含软删，避免与 uk_fleet_wo_no 撞号）。"""
        prefix = f"WO{datetime.now().strftime('%Y%m%d')}"
        result = await db.execute(
            select(FleetWorkOrder.work_order_no)
            .where(FleetWorkOrder.work_order_no.like(f"{prefix}%"))
            .order_by(FleetWorkOrder.work_order_no.desc())
            .limit(1)
        )
        last = result.scalar_one_or_none()
        seq = 1
        if last and str(last).startswith(prefix):
            tail = str(last)[len(prefix) :]
            if tail.isdigit():
                seq = int(tail) + 1
        return f"{prefix}{seq:04d}"

    # ---------- 保养计划计算 ----------

    @staticmethod
    def _recalc_next(plan: FleetMaintainPlan) -> None:
        today = date.today()
        if plan.cycle_type in ("time", "either") and plan.interval_days:
            base = plan.last_maintain_date or today
            plan.next_maintain_date = base + timedelta(days=plan.interval_days)
        else:
            plan.next_maintain_date = None

        if plan.cycle_type in ("mileage", "either") and plan.interval_mileage:
            base_m = plan.last_maintain_mileage or 0
            plan.next_maintain_mileage = base_m + plan.interval_mileage
        else:
            plan.next_maintain_mileage = None

    @staticmethod
    def _plan_due_level(plan: FleetMaintainPlan) -> str:
        today = date.today()
        date_overdue = False
        date_soon = False
        mile_overdue = False
        mile_soon = False

        if plan.next_maintain_date:
            if plan.next_maintain_date <= today:
                date_overdue = True
            elif plan.next_maintain_date <= today + timedelta(days=plan.remind_days or 7):
                date_soon = True

        # 里程：无当前里程时仅按日期判断
        if plan.next_maintain_mileage is not None and plan.last_maintain_mileage is not None:
            # 无实时里程时，不做里程 overdue（避免误报）；仅在 either/mileage 且有上次里程时依赖日期
            pass

        if plan.cycle_type == "time":
            if date_overdue:
                return "overdue"
            if date_soon:
                return "due_soon"
            return "ok"
        if plan.cycle_type == "mileage":
            # 一期无实时里程：有下次里程则视为需关注 due_soon（保守），否则 ok
            if plan.next_maintain_mileage is not None and not plan.last_maintain_date:
                return "due_soon"
            if date_overdue:
                return "overdue"
            return "ok"
        # either
        if date_overdue or mile_overdue:
            return "overdue"
        if date_soon or mile_soon:
            return "due_soon"
        return "ok"

    @staticmethod
    def _validate_plan_input(
        cycle_type: str,
        interval_days: Optional[int],
        interval_mileage: Optional[int],
    ) -> None:
        if cycle_type not in CYCLE_TYPES:
            raise BizException("请选择正确的保养周期类型")
        if cycle_type in ("time", "either") and not interval_days:
            raise BizException("请填写时间间隔天数")
        if cycle_type in ("mileage", "either") and not interval_mileage:
            raise BizException("请填写里程间隔")

    # ---------- 工单 ----------

    @staticmethod
    async def page_work_orders(
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        order_type: Optional[str] = None,
        vehicle_id: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        query = select(FleetWorkOrder).where(FleetWorkOrder.is_deleted == 0)
        if status:
            query = query.where(FleetWorkOrder.status == status)
        if order_type:
            query = query.where(FleetWorkOrder.order_type == order_type)
        if vehicle_id:
            query = query.where(FleetWorkOrder.vehicle_id == vehicle_id)
        if keyword:
            like = f"%{keyword.strip()}%"
            query = query.where(
                or_(
                    FleetWorkOrder.plate_number.like(like),
                    FleetWorkOrder.work_order_no.like(like),
                    FleetWorkOrder.title.like(like),
                )
            )
        count_q = select(func.count()).select_from(query.subquery())
        total = int((await db.execute(count_q)).scalar() or 0)
        rows = (
            await db.execute(
                query.order_by(FleetWorkOrder.updated_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [FleetMaintenanceService._wo_out(r) for r in rows],
            "total": total,
            "page": page,
            "pageSize": page_size,
        }

    @staticmethod
    async def _get_wo(db: AsyncSession, wo_id: int) -> FleetWorkOrder:
        result = await db.execute(
            select(FleetWorkOrder).where(
                FleetWorkOrder.id == wo_id,
                FleetWorkOrder.is_deleted == 0,
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("工单不存在")
        return row

    @staticmethod
    async def create_work_order(
        db: AsyncSession,
        body: WorkOrderCreate,
        operator_user_id: Optional[int],
    ) -> dict:
        if body.orderType not in ORDER_TYPES:
            raise BizException("请选择正确的工单类型")
        if not (body.title or "").strip():
            raise BizException("请填写工单标题")
        if body.faultCategory and body.faultCategory not in FAULT_CATEGORIES:
            raise BizException("请选择正确的作业分类")
        vehicle = await FleetMaintenanceService._get_vehicle(db, body.vehicleId)
        if body.planId:
            await FleetMaintenanceService._get_plan(db, body.planId)

        workshop_name = body.workshop
        if body.workshopId:
            workshop_name = await FleetPartsService.get_workshop_name(
                db, body.workshopId
            ) or workshop_name

        row = FleetWorkOrder(
            work_order_no=await FleetMaintenanceService._gen_work_order_no(db),
            vehicle_id=vehicle.id,
            plate_number=vehicle.plate_number,
            order_type=body.orderType,
            plan_id=body.planId,
            title=body.title.strip(),
            description=body.description,
            odometer=body.odometer,
            fault_category=body.faultCategory,
            workshop_id=body.workshopId,
            workshop=workshop_name,
            expect_finish_date=body.expectFinishDate,
            cost_amount=body.costAmount,
            cost_remark=body.costRemark,
            status="draft",
            remark=body.remark,
            created_by=operator_user_id,
        )
        db.add(row)
        await db.flush()
        await FleetMaintenanceService._replace_lines(db, row, body.lines)
        await db.flush()
        await db.refresh(row)
        return await FleetMaintenanceService._wo_out_with_lines(db, row)

    @staticmethod
    async def update_work_order(
        db: AsyncSession, wo_id: int, body: WorkOrderUpdate
    ) -> dict:
        row = await FleetMaintenanceService._get_wo(db, wo_id)
        if row.status not in ("draft", "in_progress"):
            raise BizException("仅草稿或进行中的工单可以编辑")
        data = body.model_dump(exclude_unset=True)
        if "faultCategory" in data and data["faultCategory"]:
            if data["faultCategory"] not in FAULT_CATEGORIES:
                raise BizException("请选择正确的作业分类")
        mapping = {
            "title": "title",
            "description": "description",
            "odometer": "odometer",
            "faultCategory": "fault_category",
            "workshopId": "workshop_id",
            "workshop": "workshop",
            "expectFinishDate": "expect_finish_date",
            "costRemark": "cost_remark",
            "remark": "remark",
        }
        for k, attr in mapping.items():
            if k in data:
                val = data[k]
                if k == "title" and val is not None:
                    val = str(val).strip()
                    if not val:
                        raise BizException("请填写工单标题")
                setattr(row, attr, val)
        if "workshopId" in data:
            name = await FleetPartsService.get_workshop_name(db, row.workshop_id)
            if name:
                row.workshop = name
        if "lines" in data:
            await FleetMaintenanceService._replace_lines(db, row, body.lines)
        await db.flush()
        await db.refresh(row)
        return await FleetMaintenanceService._wo_out_with_lines(db, row)

    @staticmethod
    async def get_work_order(db: AsyncSession, wo_id: int) -> dict:
        row = await FleetMaintenanceService._get_wo(db, wo_id)
        return await FleetMaintenanceService._wo_out_with_lines(db, row)

    @staticmethod
    async def _count_in_progress(db: AsyncSession, vehicle_id: int) -> int:
        result = await db.execute(
            select(func.count())
            .select_from(FleetWorkOrder)
            .where(
                FleetWorkOrder.vehicle_id == vehicle_id,
                FleetWorkOrder.status == "in_progress",
                FleetWorkOrder.is_deleted == 0,
            )
        )
        return int(result.scalar() or 0)

    @staticmethod
    async def start_work_order(
        db: AsyncSession,
        wo_id: int,
        operator_user_id: Optional[int],
    ) -> dict:
        row = await FleetMaintenanceService._get_wo(db, wo_id)
        if row.status != "draft":
            raise BizException("仅草稿状态的工单可以开工")

        vehicle = await FleetMaintenanceService._get_vehicle(db, row.vehicle_id)
        if vehicle.status in (0, 9):
            raise BizException("当前车辆已停用或报废，无法开工")
        if vehicle.status == 3 and (vehicle.status_source or "") == "insurance":
            raise BizException("该车正在办理保险续期，请先完成续期登记")
        if vehicle.status == 2 and await FleetMaintenanceService._count_in_progress(
            db, vehicle.id
        ) > 0:
            raise BizException("该车已有进行中的维保工单，请先完成后再开工")

        cap_result = await db.execute(
            select(Capacity).where(
                Capacity.vehicle_id == vehicle.id,
                Capacity.status == 1,
                Capacity.is_deleted == 0,
            )
        )
        capacity = cap_result.scalar_one_or_none()
        if capacity and capacity.operation_status == 2:
            raise BizException(
                "该车运输任务尚未结束，请先完成任务再安排进厂"
            )

        if await FleetMaintenanceService._count_in_progress(db, vehicle.id) > 0:
            raise BizException("该车已有进行中的维保工单，请先完成后再开工")

        if vehicle.status != 1 and vehicle.status != 2:
            raise BizException("当前车辆状态不可开工")

        await VehicleStatusService.change_status(
            db, vehicle.id, 2, source="maintenance"
        )
        capacity_id = await CapacityService.set_operation_status_by_module(
            db,
            vehicle_id=vehicle.id,
            operation_status=5,
            source="maintenance",
            operator_user_id=operator_user_id,
            remark=f"维保工单 {row.work_order_no}",
        )

        row.status = "in_progress"
        row.started_at = datetime.now()
        row.capacity_id = capacity_id
        await db.flush()
        await db.refresh(row)
        return FleetMaintenanceService._wo_out(row)

    @staticmethod
    async def complete_work_order(
        db: AsyncSession,
        wo_id: int,
        body: Optional[WorkOrderCompleteBody],
        operator_user_id: Optional[int],
    ) -> dict:
        row = await FleetMaintenanceService._get_wo(db, wo_id)
        if row.status != "in_progress":
            raise BizException("仅进行中的工单可以完工")
        if body:
            if body.costRemark is not None:
                row.cost_remark = body.costRemark
            if body.odometer is not None:
                row.odometer = body.odometer
            if body.remark is not None:
                row.remark = body.remark

        lines = await FleetMaintenanceService._load_lines(db, row.id)
        # 按备件汇总数量后出库
        need: dict[int, Decimal] = {}
        unit_costs: dict[int, Optional[Decimal]] = {}
        for line in lines:
            if line.line_type != "part" or not line.part_id:
                continue
            pid = int(line.part_id)
            need[pid] = need.get(pid, _ZERO) + Decimal(str(line.qty or 0))
            if pid not in unit_costs:
                unit_costs[pid] = line.unit_price
        for pid, qty in need.items():
            await FleetPartsService.issue_for_work_order(
                db,
                part_id=pid,
                qty=qty,
                unit_cost=unit_costs.get(pid),
                work_order_id=row.id,
                operator_user_id=operator_user_id,
            )

        labor_sum = sum(
            (Decimal(str(x.amount or 0)) for x in lines if x.line_type != "part"),
            _ZERO,
        )
        parts_sum = sum(
            (Decimal(str(x.amount or 0)) for x in lines if x.line_type == "part"),
            _ZERO,
        )
        row.labor_amount = labor_sum
        row.parts_amount = parts_sum
        # 有明细时以行汇总为准；无明细时允许完工体传入费用
        if lines:
            row.cost_amount = labor_sum + parts_sum
        elif body and body.costAmount is not None:
            row.cost_amount = body.costAmount

        row.status = "completed"
        row.finished_at = datetime.now()
        await db.flush()

        if row.plan_id and row.order_type == "maintenance":
            plan = await FleetMaintenanceService._get_plan(db, row.plan_id)
            plan.last_maintain_date = date.today()
            if row.odometer is not None:
                plan.last_maintain_mileage = row.odometer
            FleetMaintenanceService._recalc_next(plan)

        await FleetMaintenanceService._release_vehicle_capacity(
            db, row, operator_user_id
        )
        await db.refresh(row)
        return await FleetMaintenanceService._wo_out_with_lines(db, row)

    @staticmethod
    async def cancel_work_order(
        db: AsyncSession,
        wo_id: int,
        operator_user_id: Optional[int],
    ) -> dict:
        row = await FleetMaintenanceService._get_wo(db, wo_id)
        if row.status not in ("draft", "in_progress"):
            raise BizException("当前状态的工单不可取消")
        was_progress = row.status == "in_progress"
        row.status = "cancelled"
        row.finished_at = datetime.now()
        await db.flush()
        if was_progress:
            await FleetMaintenanceService._release_vehicle_capacity(
                db, row, operator_user_id
            )
        await db.refresh(row)
        return FleetMaintenanceService._wo_out(row)

    @staticmethod
    async def _release_vehicle_capacity(
        db: AsyncSession,
        row: FleetWorkOrder,
        operator_user_id: Optional[int],
    ) -> None:
        if await FleetMaintenanceService._count_in_progress(db, row.vehicle_id) > 0:
            return

        vehicle = await FleetMaintenanceService._get_vehicle(db, row.vehicle_id)
        if vehicle.status == 2 and (vehicle.status_source or "") == "maintenance":
            await VehicleStatusService.change_status(
                db, vehicle.id, 1, source="maintenance"
            )

        cap_result = await db.execute(
            select(Capacity).where(
                Capacity.vehicle_id == row.vehicle_id,
                Capacity.status == 1,
                Capacity.is_deleted == 0,
                Capacity.operation_status == 5,
            )
        )
        if cap_result.scalar_one_or_none():
            await CapacityService.set_operation_status_by_module(
                db,
                vehicle_id=row.vehicle_id,
                operation_status=1,
                source="maintenance",
                operator_user_id=operator_user_id,
                remark=f"维保工单 {row.work_order_no} 结束",
            )

    # ---------- 保养计划 ----------

    @staticmethod
    async def _get_plan(db: AsyncSession, plan_id: int) -> FleetMaintainPlan:
        result = await db.execute(
            select(FleetMaintainPlan).where(
                FleetMaintainPlan.id == plan_id,
                FleetMaintainPlan.is_deleted == 0,
            )
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("保养计划不存在")
        return row

    @staticmethod
    async def page_plans(
        db: AsyncSession,
        *,
        page: int,
        page_size: int,
        vehicle_id: Optional[int] = None,
        enabled: Optional[int] = None,
        keyword: Optional[str] = None,
    ) -> dict:
        query = select(FleetMaintainPlan).where(FleetMaintainPlan.is_deleted == 0)
        if vehicle_id:
            query = query.where(FleetMaintainPlan.vehicle_id == vehicle_id)
        if enabled is not None:
            query = query.where(FleetMaintainPlan.enabled == enabled)
        if keyword:
            like = f"%{keyword.strip()}%"
            query = query.where(
                or_(
                    FleetMaintainPlan.plate_number.like(like),
                    FleetMaintainPlan.name.like(like),
                )
            )
        total = int(
            (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
            or 0
        )
        rows = (
            await db.execute(
                query.order_by(FleetMaintainPlan.updated_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        ).scalars().all()
        return {
            "list": [
                FleetMaintenanceService._plan_out(
                    r, FleetMaintenanceService._plan_due_level(r)
                )
                for r in rows
            ],
            "total": total,
            "page": page,
            "pageSize": page_size,
        }

    @staticmethod
    async def create_plan(
        db: AsyncSession,
        body: MaintainPlanCreate,
        operator_user_id: Optional[int],
    ) -> dict:
        FleetMaintenanceService._validate_plan_input(
            body.cycleType, body.intervalDays, body.intervalMileage
        )
        vehicle = await FleetMaintenanceService._get_vehicle(db, body.vehicleId)
        row = FleetMaintainPlan(
            vehicle_id=vehicle.id,
            plate_number=vehicle.plate_number,
            name=body.name.strip(),
            cycle_type=body.cycleType,
            interval_days=body.intervalDays,
            interval_mileage=body.intervalMileage,
            last_maintain_date=body.lastMaintainDate,
            last_maintain_mileage=body.lastMaintainMileage,
            remind_days=body.remindDays or 7,
            enabled=1 if body.enabled != 0 else 0,
            created_by=operator_user_id,
        )
        FleetMaintenanceService._recalc_next(row)
        db.add(row)
        await db.flush()
        await db.refresh(row)
        return FleetMaintenanceService._plan_out(
            row, FleetMaintenanceService._plan_due_level(row)
        )

    @staticmethod
    async def update_plan(
        db: AsyncSession, plan_id: int, body: MaintainPlanUpdate
    ) -> dict:
        row = await FleetMaintenanceService._get_plan(db, plan_id)
        data = body.model_dump(exclude_unset=True)
        if "name" in data and data["name"] is not None:
            row.name = str(data["name"]).strip()
        if "cycleType" in data and data["cycleType"] is not None:
            row.cycle_type = data["cycleType"]
        if "intervalDays" in data:
            row.interval_days = data["intervalDays"]
        if "intervalMileage" in data:
            row.interval_mileage = data["intervalMileage"]
        if "lastMaintainDate" in data:
            row.last_maintain_date = data["lastMaintainDate"]
        if "lastMaintainMileage" in data:
            row.last_maintain_mileage = data["lastMaintainMileage"]
        if "remindDays" in data and data["remindDays"] is not None:
            row.remind_days = data["remindDays"]
        if "enabled" in data and data["enabled"] is not None:
            row.enabled = data["enabled"]
        FleetMaintenanceService._validate_plan_input(
            row.cycle_type, row.interval_days, row.interval_mileage
        )
        FleetMaintenanceService._recalc_next(row)
        await db.flush()
        await db.refresh(row)
        return FleetMaintenanceService._plan_out(
            row, FleetMaintenanceService._plan_due_level(row)
        )

    @staticmethod
    async def delete_plan(db: AsyncSession, plan_id: int) -> None:
        row = await FleetMaintenanceService._get_plan(db, plan_id)
        row.is_deleted = 1
        await db.flush()

    @staticmethod
    async def generate_work_order_from_plan(
        db: AsyncSession,
        plan_id: int,
        operator_user_id: Optional[int],
    ) -> dict:
        plan = await FleetMaintenanceService._get_plan(db, plan_id)
        if plan.enabled != 1:
            raise BizException("该保养计划已停用，无法生成工单")
        return await FleetMaintenanceService.create_work_order(
            db,
            WorkOrderCreate(
                vehicleId=plan.vehicle_id,
                orderType="maintenance",
                title=f"保养：{plan.name}",
                planId=plan.id,
            ),
            operator_user_id,
        )

    # ---------- 看板 ----------

    @staticmethod
    async def board(db: AsyncSession) -> dict:
        plans = (
            await db.execute(
                select(FleetMaintainPlan).where(
                    FleetMaintainPlan.is_deleted == 0,
                    FleetMaintainPlan.enabled == 1,
                )
            )
        ).scalars().all()
        due_plans = []
        for p in plans:
            level = FleetMaintenanceService._plan_due_level(p)
            if level in ("overdue", "due_soon"):
                due_plans.append(FleetMaintenanceService._plan_out(p, level))

        in_progress = (
            await db.execute(
                select(FleetWorkOrder)
                .where(
                    FleetWorkOrder.is_deleted == 0,
                    FleetWorkOrder.status == "in_progress",
                )
                .order_by(FleetWorkOrder.started_at.desc())
                .limit(20)
            )
        ).scalars().all()

        week_start = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=datetime.now().weekday())
        completed_rows = (
            await db.execute(
                select(FleetWorkOrder).where(
                    FleetWorkOrder.is_deleted == 0,
                    FleetWorkOrder.status == "completed",
                    FleetWorkOrder.finished_at >= week_start,
                )
            )
        ).scalars().all()
        cost_sum = sum(
            (r.cost_amount or Decimal("0")) for r in completed_rows
        )

        low_stock = await FleetPartsService.low_stock_count(db)
        return {
            "duePlans": due_plans,
            "inProgressOrders": [
                FleetMaintenanceService._wo_out(r) for r in in_progress
            ],
            "weekSummary": {
                "completedCount": len(completed_rows),
                "costAmount": float(cost_sum),
            },
            "lowStockCount": low_stock,
        }
