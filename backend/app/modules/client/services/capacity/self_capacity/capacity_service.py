"""
运力管理服务（租户库）

上车/下车绑定逻辑、分页查询、变动日志查询。
"""

from typing import Optional
from datetime import datetime

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.self_capacity.capacity import (
    Capacity, CapacityLog,
)
from app.modules.client.models.capacity.self_capacity.driver.driver import Driver
from app.modules.client.models.capacity.self_capacity.driver.driver_operation import (
    DriverOperation,
)
from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
from app.modules.client.models.capacity.self_capacity.vehicle_ext import VehicleExt
from app.modules.client.models.capacity.self_capacity.trailer import Trailer
from app.modules.client.models.organization.biz_department import BizDepartment
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.schemas.capacity.self_capacity.capacity import (
    CapacityOut, CapacityLogOut,
)
from app.modules.client.services.company_activity_service import CompanyActivityService


class CapacityService:

    @staticmethod
    async def bind(
        db: AsyncSession,
        driver_id: int,
        vehicle_id: int,
        operator_user_id: Optional[int] = None,
        remark: Optional[str] = None,
    ) -> CapacityOut:
        """上车：绑定司机与车辆"""
        driver = await CapacityService._get_active_driver(db, driver_id)
        vehicle = await CapacityService._get_active_vehicle(db, vehicle_id)

        existing_driver = await db.execute(
            select(Capacity).where(
                Capacity.driver_id == driver_id,
                Capacity.status == 1,
                Capacity.is_deleted == 0,
            )
        )
        if existing_driver.scalar_one_or_none():
            raise BizException(f"司机「{driver.name}」已绑定其他车辆，请先下车")

        existing_vehicle = await db.execute(
            select(Capacity).where(
                Capacity.vehicle_id == vehicle_id,
                Capacity.status == 1,
                Capacity.is_deleted == 0,
            )
        )
        if existing_vehicle.scalar_one_or_none():
            raise BizException(f"车辆「{vehicle.plate_number}」已绑定其他司机，请先下车")

        now = datetime.now()
        capacity = Capacity(
            driver_id=driver_id,
            driver_name=driver.name,
            driver_phone=driver.phone,
            # 运力归属继承自司机的经营主体（车辆缺省时兜底取司机主体）
            enterprise_id=(
                getattr(driver, "enterprise_id", None)
                or getattr(vehicle, "enterprise_id", None)
            ),
            vehicle_id=vehicle_id,
            plate_number=vehicle.plate_number,
            status=1,
            operation_status=1,
            bound_at=now,
            remark=remark,
        )
        db.add(capacity)
        await db.flush()
        await db.refresh(capacity)

        trailer_plate, trailer_cat = (
            await CapacityService._trailer_plates_for_vehicle(db, vehicle)
        )

        operator_name = await CapacityService._get_operator_name(
            db, operator_user_id
        )
        log = CapacityLog(
            capacity_id=capacity.id,
            driver_id=driver_id,
            driver_name=driver.name,
            vehicle_id=vehicle_id,
            plate_number=vehicle.plate_number,
            action=1,
            action_time=now,
            operator_id=operator_user_id,
            operator_name=operator_name,
            remark=remark,
        )
        db.add(log)
        await db.flush()

        op_label = operator_name or "用户"
        await CompanyActivityService.record(
            db,
            occurred_at=now,
            event_code="capacity.self_bind",
            summary=(
                f"{op_label} 为司机「{driver.name}」与车辆「{vehicle.plate_number}」"
                "执行了上车绑定"
            ),
            actor_user_id=operator_user_id,
            actor_display_name=operator_name,
            payload={
                "capacity_id": capacity.id,
                "driver_id": driver_id,
                "vehicle_id": vehicle_id,
                "plate_number": vehicle.plate_number,
            },
        )

        extras = await CapacityService._load_capacity_extras(
            db, driver_id, vehicle_id
        )
        return CapacityOut.from_model(
            capacity,
            vehicle.plate_category,
            trailer_plate,
            trailer_cat,
            **extras,
        )

    @staticmethod
    async def unbind(
        db: AsyncSession,
        capacity_id: int,
        operator_user_id: Optional[int] = None,
        remark: Optional[str] = None,
    ) -> CapacityOut:
        """下车：解绑司机与车辆"""
        result = await db.execute(
            select(Capacity).where(
                Capacity.id == capacity_id,
                Capacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("运力记录不存在")
        if capacity.status != 1:
            raise BizException("该运力已解绑，无需重复操作")

        now = datetime.now()
        capacity.status = 0
        capacity.unbound_at = now

        operator_name = await CapacityService._get_operator_name(
            db, operator_user_id
        )
        log = CapacityLog(
            capacity_id=capacity.id,
            driver_id=capacity.driver_id,
            driver_name=capacity.driver_name,
            vehicle_id=capacity.vehicle_id,
            plate_number=capacity.plate_number,
            action=2,
            action_time=now,
            operator_id=operator_user_id,
            operator_name=operator_name,
            remark=remark,
        )
        db.add(log)
        await db.flush()

        op_label = operator_name or "用户"
        await CompanyActivityService.record(
            db,
            occurred_at=now,
            event_code="capacity.self_unbind",
            summary=(
                f"{op_label} 对司机「{capacity.driver_name}」与车辆「{capacity.plate_number}」"
                "执行了下车解绑"
            ),
            actor_user_id=operator_user_id,
            actor_display_name=operator_name,
            payload={
                "capacity_id": capacity.id,
                "driver_id": capacity.driver_id,
                "vehicle_id": capacity.vehicle_id,
                "plate_number": capacity.plate_number,
            },
        )

        vr = await db.execute(
            select(Vehicle).where(
                Vehicle.id == capacity.vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        vehicle = vr.scalar_one_or_none()
        pc = (vehicle.plate_category if vehicle else None) or "YELLOW"
        trailer_plate, trailer_cat = (
            await CapacityService._trailer_plates_for_vehicle(db, vehicle)
        )

        extras = await CapacityService._load_capacity_extras(
            db, capacity.driver_id, capacity.vehicle_id
        )
        return CapacityOut.from_model(
            capacity,
            pc,
            trailer_plate,
            trailer_cat,
            **extras,
        )

    # 运力运营状态 1-空闲 2-运输中 3-休假 4-停运 5-维修保养
    OPERATION_STATUS_LABELS = {
        1: "空闲",
        2: "运输中",
        3: "休假",
        4: "停运",
        5: "维修保养中",
    }
    # 允许人工手动切换到的目标状态（运输中/维修保养由上游模块驱动，不允许手动置位）
    MANUAL_TARGET_STATUSES = {1, 3, 4}

    @staticmethod
    async def update_operation_status(
        db: AsyncSession,
        capacity_id: int,
        operation_status: int,
        operator_user_id: Optional[int] = None,
    ) -> CapacityOut:
        """变更运力运营状态（手动）"""
        if operation_status not in CapacityService.MANUAL_TARGET_STATUSES:
            raise BizException(
                "该状态由任务单或维修保养等模块自动管理，不支持手动切换"
            )

        result = await db.execute(
            select(Capacity).where(
                Capacity.id == capacity_id,
                Capacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("运力记录不存在")
        if capacity.status != 1:
            raise BizException("该运力已解绑，无法变更状态")

        prev_status = capacity.operation_status
        if prev_status == operation_status:
            raise BizException("运力当前已是该状态，无需变更")

        labels = CapacityService.OPERATION_STATUS_LABELS
        prev_label = labels.get(prev_status, "未知")
        next_label = labels.get(operation_status, "未知")

        now = datetime.now()
        capacity.operation_status = operation_status

        operator_name = await CapacityService._get_operator_name(
            db, operator_user_id
        )
        change_note = f"运力状态：{prev_label} → {next_label}"
        log = CapacityLog(
            capacity_id=capacity.id,
            driver_id=capacity.driver_id,
            driver_name=capacity.driver_name,
            vehicle_id=capacity.vehicle_id,
            plate_number=capacity.plate_number,
            action=3,
            action_time=now,
            operator_id=operator_user_id,
            operator_name=operator_name,
            remark=change_note,
        )
        db.add(log)
        await db.flush()

        op_label = operator_name or "用户"
        await CompanyActivityService.record(
            db,
            occurred_at=now,
            event_code="capacity.self_status_change",
            summary=(
                f"{op_label} 将司机「{capacity.driver_name}」与车辆"
                f"「{capacity.plate_number}」的运力状态从「{prev_label}」"
                f"调整为「{next_label}」"
            ),
            actor_user_id=operator_user_id,
            actor_display_name=operator_name,
            payload={
                "capacity_id": capacity.id,
                "driver_id": capacity.driver_id,
                "vehicle_id": capacity.vehicle_id,
                "plate_number": capacity.plate_number,
                "prev_status": prev_status,
                "next_status": operation_status,
            },
        )

        vr = await db.execute(
            select(Vehicle).where(
                Vehicle.id == capacity.vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        vehicle = vr.scalar_one_or_none()
        pc = (vehicle.plate_category if vehicle else None) or "YELLOW"
        trailer_plate, trailer_cat = (
            await CapacityService._trailer_plates_for_vehicle(db, vehicle)
        )

        extras = await CapacityService._load_capacity_extras(
            db, capacity.driver_id, capacity.vehicle_id
        )
        return CapacityOut.from_model(
            capacity,
            pc,
            trailer_plate,
            trailer_cat,
            **extras,
        )

    @staticmethod
    async def page_capacities(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        operation_status: Optional[int] = None,
        enterprise_id: Optional[int] = None,
    ) -> dict:
        """运力分页列表（仅当前绑定中的运力；已解绑请在变动记录中查看）"""
        query = (
            select(
                Capacity,
                Vehicle.plate_category,
                Trailer.plate_number.label("trailer_plate"),
                Trailer.plate_category.label("trailer_cat"),
                Driver.avatar.label("driver_avatar"),
                BizDepartment.dept_name.label("department_name"),
                DriverOperation.operation_status.label("driver_operation_status"),
                VehicleExt.vehicle_type.label("vehicle_type"),
            )
            .outerjoin(
                Vehicle,
                and_(Vehicle.id == Capacity.vehicle_id, Vehicle.is_deleted == 0),
            )
            .outerjoin(
                Trailer,
                and_(Trailer.id == Vehicle.trailer_id, Trailer.is_deleted == 0),
            )
            .outerjoin(
                Driver,
                and_(Driver.id == Capacity.driver_id, Driver.is_deleted == 0),
            )
            .outerjoin(
                DriverOperation,
                and_(
                    DriverOperation.driver_id == Driver.id,
                    DriverOperation.is_deleted == 0,
                ),
            )
            .outerjoin(
                BizDepartment,
                and_(
                    BizDepartment.id == DriverOperation.department_id,
                    BizDepartment.is_deleted == 0,
                ),
            )
            .outerjoin(
                VehicleExt,
                and_(
                    VehicleExt.vehicle_id == Vehicle.id,
                    VehicleExt.is_deleted == 0,
                ),
            )
            .where(
                Capacity.is_deleted == 0,
                Capacity.status == 1,
            )
        )

        if keyword:
            kw = f"%{keyword}%"
            query = query.where(
                or_(
                    Capacity.driver_name.like(kw),
                    Capacity.driver_phone.like(kw),
                    Capacity.plate_number.like(kw),
                    Trailer.plate_number.like(kw),
                )
            )

        if operation_status is not None:
            query = query.where(Capacity.operation_status == operation_status)

        if enterprise_id is not None:
            query = query.where(Capacity.enterprise_id == enterprise_id)

        count_q = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_q)).scalar() or 0

        result = await db.execute(
            query.order_by(Capacity.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.all()

        return {
            "list": [
                CapacityOut.from_model(
                    cap,
                    pc or "YELLOW",
                    tp,
                    tc,
                    driver_avatar=avatar,
                    department_name=dept_name,
                    driver_operation_status=op_status,
                    vehicle_type=vtype,
                ).model_dump()
                for cap, pc, tp, tc, avatar, dept_name, op_status, vtype in rows
            ],
            "total": total,
            "count": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def list_stats(
        db: AsyncSession,
        keyword: Optional[str] = None,
        enterprise_id: Optional[int] = None,
    ) -> dict:
        """运力列表 KPI：按运营状态分组计数（不含 operationStatus 自身筛选）。"""
        query = (
            select(Capacity.operation_status, func.count())
            .outerjoin(
                Vehicle,
                and_(Vehicle.id == Capacity.vehicle_id, Vehicle.is_deleted == 0),
            )
            .outerjoin(
                Trailer,
                and_(Trailer.id == Vehicle.trailer_id, Trailer.is_deleted == 0),
            )
            .where(
                Capacity.is_deleted == 0,
                Capacity.status == 1,
            )
        )

        if keyword:
            kw = f"%{keyword}%"
            query = query.where(
                or_(
                    Capacity.driver_name.like(kw),
                    Capacity.driver_phone.like(kw),
                    Capacity.plate_number.like(kw),
                    Trailer.plate_number.like(kw),
                )
            )

        if enterprise_id is not None:
            query = query.where(Capacity.enterprise_id == enterprise_id)

        result = await db.execute(query.group_by(Capacity.operation_status))
        counts = {int(s): int(c) for s, c in result.all() if s is not None}
        total = sum(counts.values())

        return {
            "total": total,
            "available": counts.get(1, 0),
            "inTransit": counts.get(2, 0),
            "resting": counts.get(3, 0),
            "stopped": counts.get(4, 0),
            "maintenance": counts.get(5, 0),
        }

    @staticmethod
    async def page_logs(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        action: Optional[int] = None,
        operator_name: Optional[str] = None,
        action_time_start: Optional[str] = None,
        action_time_end: Optional[str] = None,
    ) -> dict:
        """运力变动历史分页列表"""
        filters = [CapacityLog.is_deleted == 0]

        if keyword:
            kw = f"%{keyword}%"
            filters.append(
                or_(
                    CapacityLog.driver_name.like(kw),
                    CapacityLog.plate_number.like(kw),
                    Driver.phone.like(kw),
                )
            )
        if action is not None:
            filters.append(CapacityLog.action == action)
        if operator_name:
            filters.append(
                CapacityLog.operator_name.like(f"%{operator_name}%")
            )
        if action_time_start:
            filters.append(CapacityLog.action_time >= action_time_start)
        if action_time_end:
            filters.append(CapacityLog.action_time <= action_time_end)

        where_clause = and_(*filters)

        count_stmt = (
            select(func.count(CapacityLog.id))
            .select_from(CapacityLog)
            .outerjoin(Vehicle, Vehicle.id == CapacityLog.vehicle_id)
            .outerjoin(Driver, Driver.id == CapacityLog.driver_id)
            .where(where_clause)
        )
        total = (await db.execute(count_stmt)).scalar() or 0

        list_stmt = (
            select(
                CapacityLog,
                Vehicle.plate_category,
                Driver.driver_code,
                Driver.phone,
            )
            .outerjoin(Vehicle, Vehicle.id == CapacityLog.vehicle_id)
            .outerjoin(Driver, Driver.id == CapacityLog.driver_id)
            .where(where_clause)
            .order_by(CapacityLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(list_stmt)
        rows = result.all()

        return {
            "list": [
                CapacityLogOut.from_model(
                    log,
                    plate_category=pc,
                    driver_code=dcode,
                    driver_phone=dphone,
                ).model_dump()
                for log, pc, dcode, dphone in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def _load_capacity_extras(
        db: AsyncSession,
        driver_id: int,
        vehicle_id: int,
    ) -> dict:
        """加载卡片展示所需的关联字段"""
        driver_avatar = None
        department_name = None
        operation_status = None
        vehicle_type = None

        dr = await db.execute(
            select(Driver.avatar).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        driver_avatar = dr.scalar_one_or_none()

        op = await db.execute(
            select(
                DriverOperation.operation_status,
                BizDepartment.dept_name,
            )
            .outerjoin(
                BizDepartment,
                and_(
                    BizDepartment.id == DriverOperation.department_id,
                    BizDepartment.is_deleted == 0,
                ),
            )
            .where(
                DriverOperation.driver_id == driver_id,
                DriverOperation.is_deleted == 0,
            )
        )
        op_row = op.one_or_none()
        if op_row:
            operation_status, department_name = op_row

        ext = await db.execute(
            select(VehicleExt.vehicle_type).where(
                VehicleExt.vehicle_id == vehicle_id,
                VehicleExt.is_deleted == 0,
            )
        )
        vehicle_type = ext.scalar_one_or_none()

        return {
            "driver_avatar": driver_avatar,
            "department_name": department_name,
            "driver_operation_status": operation_status,
            "vehicle_type": vehicle_type,
        }

    @staticmethod
    async def _get_active_driver(db: AsyncSession, driver_id: int) -> Driver:
        result = await db.execute(
            select(Driver).where(
                Driver.id == driver_id,
                Driver.is_deleted == 0,
            )
        )
        driver = result.scalar_one_or_none()
        if not driver:
            raise BizException("司机不存在")
        if driver.status != 1:
            raise BizException("司机非在职状态，无法绑定")
        return driver

    @staticmethod
    async def _trailer_plates_for_vehicle(
        db: AsyncSession,
        vehicle: Optional[Vehicle],
    ) -> tuple[Optional[str], Optional[str]]:
        if not vehicle or not vehicle.trailer_id:
            return None, None
        result = await db.execute(
            select(Trailer.plate_number, Trailer.plate_category).where(
                Trailer.id == vehicle.trailer_id,
                Trailer.is_deleted == 0,
            )
        )
        row = result.one_or_none()
        if not row:
            return None, None
        return row[0], row[1]

    @staticmethod
    async def _get_active_vehicle(db: AsyncSession, vehicle_id: int) -> Vehicle:
        result = await db.execute(
            select(Vehicle).where(
                Vehicle.id == vehicle_id,
                Vehicle.is_deleted == 0,
            )
        )
        vehicle = result.scalar_one_or_none()
        if not vehicle:
            raise BizException("车辆不存在")
        if vehicle.status != 1:
            raise BizException("车辆非正常状态，无法绑定")
        return vehicle

    @staticmethod
    async def _get_operator_name(
        db: AsyncSession, user_id: Optional[int]
    ) -> Optional[str]:
        if not user_id:
            return None
        result = await db.execute(
            select(BizUser.real_name).where(BizUser.id == user_id)
        )
        return result.scalar_one_or_none()
