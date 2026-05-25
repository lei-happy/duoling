"""
社会运力主体服务（租户库）

核心职责：
  - 主表 + 司机详情 + 车辆详情 + 默认结算账户 的联查 / 联写 / 联删
  - 审核状态机：草稿(0) ↔ 待审核(1) ↔ 已通过(2) / 已驳回(3)
  - 启用状态机：仅在 approval_status=2 时才可调整 status (0→1 / 1↔2 / 1↔3 / 2↔3)
  - 编辑权限矩阵：1 不可编；2 仅可改账户与备注；0 / 3 全字段可编
  - 唯一性校验：driver_phone / plate_number 在租户内（非已驳回 / 非草稿）唯一
  - 调度选择器：仅返回 approval_status=2 AND status=1
  - 与 SocialCapacityAuditService / SocialCapacityAccountService 协作
"""

from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, func, and_, asc, desc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.capacity.social_capacity.social_capacity import (
    SocialCapacity,
)
from app.modules.client.models.capacity.social_capacity.social_capacity_driver import (
    SocialCapacityDriver,
)
from app.modules.client.models.capacity.social_capacity.social_capacity_vehicle import (
    SocialCapacityVehicle,
)
from app.modules.client.models.capacity.social_capacity.social_capacity_account import (
    SocialCapacityAccount,
)
from app.modules.client.schemas.capacity.social_capacity.social_capacity import (
    SocialCapacityCreate,
    SocialCapacityUpdate,
    SocialCapacityVehicleInfo,
    SocialCapacityDriverInfo,
    SocialCapacityListItem,
    SocialCapacityDetail,
    SocialCapacitySelectItem,
    SocialCapacityAccountBrief,
    SocialCapacityAuditBrief,
)
from app.modules.client.services.capacity.social_capacity.social_capacity_audit_service import (
    SocialCapacityAuditService,
    ACTION_SUBMIT,
    ACTION_APPROVE,
    ACTION_REJECT,
    ACTION_ENABLE,
    ACTION_DISABLE,
    ACTION_BLACKLIST,
    ACTION_UNBLACKLIST,
    ACTION_WITHDRAW,
)


# ------------------------- 常量 -------------------------
APPROVAL_DRAFT = 0
APPROVAL_PENDING = 1
APPROVAL_APPROVED = 2
APPROVAL_REJECTED = 3

STATUS_INACTIVE = 0
STATUS_ACTIVE = 1
STATUS_DISABLED = 2
STATUS_BLACKLIST = 3


# ------------------------- 排序 -------------------------
_LIST_SORT_COLUMNS = {
    "createdAt": SocialCapacity.created_at,
    "approvalTime": SocialCapacity.approval_time,
    "ratingScore": SocialCapacity.rating_score,
}


def _list_order_clauses(sort: Optional[str], order: Optional[str]):
    col = _LIST_SORT_COLUMNS.get(sort or "")
    if col is None:
        return [desc(SocialCapacity.created_at), desc(SocialCapacity.id)]
    raw = (order or "desc").strip().lower()
    if raw in ("descending",):
        direction = "desc"
    elif raw in ("ascending",):
        direction = "asc"
    elif raw in ("asc", "desc"):
        direction = raw
    else:
        direction = "desc"
    primary = asc(col) if direction == "asc" else desc(col)
    return [primary, desc(SocialCapacity.id)]


# ------------------------- Service -------------------------
class SocialCapacityService:
    """社会运力主体服务"""

    # =====================================================
    # 私有：编号 / 唯一性 / 默认账户摘要
    # =====================================================
    @staticmethod
    async def _generate_social_code(db: AsyncSession) -> str:
        """S{YYYY}{NNNNN}，同租户自增。"""
        year = datetime.now().strftime("%Y")
        prefix = f"S{year}"
        result = await db.execute(
            select(func.count()).select_from(
                select(SocialCapacity.id)
                .where(SocialCapacity.social_code.like(f"{prefix}%"))
                .subquery()
            )
        )
        count = (result.scalar() or 0) + 1
        return f"{prefix}{count:05d}"

    @staticmethod
    async def _check_unique_phone(
        db: AsyncSession, phone: str, exclude_id: Optional[int] = None
    ) -> None:
        """driver_phone 在 (草稿 / 待审核 / 已通过) 状态下唯一；已驳回不占名。"""
        q = select(SocialCapacity.id).where(
            SocialCapacity.driver_phone == phone,
            SocialCapacity.is_deleted == 0,
            SocialCapacity.approval_status.in_(
                [APPROVAL_DRAFT, APPROVAL_PENDING, APPROVAL_APPROVED]
            ),
        )
        if exclude_id is not None:
            q = q.where(SocialCapacity.id != exclude_id)
        if (await db.execute(q)).first():
            raise BizException(f"手机号 {phone} 已被其他社会运力档案占用")

    @staticmethod
    async def _check_unique_plate(
        db: AsyncSession, plate: str, exclude_id: Optional[int] = None
    ) -> None:
        q = select(SocialCapacity.id).where(
            SocialCapacity.plate_number == plate,
            SocialCapacity.is_deleted == 0,
            SocialCapacity.approval_status.in_(
                [APPROVAL_DRAFT, APPROVAL_PENDING, APPROVAL_APPROVED]
            ),
        )
        if exclude_id is not None:
            q = q.where(SocialCapacity.id != exclude_id)
        if (await db.execute(q)).first():
            raise BizException(f"车牌号 {plate} 已被其他社会运力档案占用")

    @staticmethod
    async def _load_default_account_brief(
        db: AsyncSession, social_capacity_id: int
    ) -> Optional[SocialCapacityAccountBrief]:
        result = await db.execute(
            select(SocialCapacityAccount).where(
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
                SocialCapacityAccount.is_default == 1,
            )
        )
        acc = result.scalar_one_or_none()
        if not acc:
            return None
        return SocialCapacityAccountBrief(
            id=acc.id,
            accountType=acc.account_type,
            accountLabel=acc.account_label,
            accountName=acc.account_name,
            accountNo=acc.account_no,
            bankName=acc.bank_name,
            isDefault=acc.is_default,
            status=acc.status,
        )

    # =====================================================
    # 私有：拷贝 vehicle / driver 字段
    # =====================================================
    _VEHICLE_FIELD_MAP = {
        "plateNumber": "plate_number",
        "plateCategory": "plate_category",
        "vehicleType": "vehicle_type",
        "brand": "brand",
        "model": "model",
        "color": "color",
        "vin": "vin",
        "engineNo": "engine_no",
        "loadCapacity": "load_capacity",
        "volumeCapacity": "volume_capacity",
        "length": "length",
        "width": "width",
        "height": "height",
        "axleCount": "axle_count",
        "hasTrailer": "has_trailer",
        "trailerPlate": "trailer_plate",
        "trailerType": "trailer_type",
        "trailerLoadCapacity": "trailer_load_capacity",
        "registrationDate": "registration_date",
        "inspectionExpire": "inspection_expire",
        "insuranceExpire": "insurance_expire",
        "transportLicenseNo": "transport_license_no",
        "transportLicenseExpire": "transport_license_expire",
        "vehicleLicensePhoto": "vehicle_license_photo",
        "vehicleLicenseBackPhoto": "vehicle_license_back_photo",
        "transportLicensePhoto": "transport_license_photo",
        "vehiclePhoto": "vehicle_photo",
    }

    _DRIVER_FIELD_MAP = {
        "name": "name",
        "gender": "gender",
        "phone": "phone",
        "idCard": "id_card",
        "birthDate": "birth_date",
        "avatar": "avatar",
        "licenseType": "license_type",
        "licenseNo": "license_no",
        "licenseIssueDate": "license_issue_date",
        "licenseExpire": "license_expire",
        "licenseClass": "license_class",
        "qualificationNo": "qualification_no",
        "qualificationExpire": "qualification_expire",
        "licensePhoto": "license_photo",
        "qualificationPhoto": "qualification_photo",
        "idCardFrontPhoto": "id_card_front_photo",
        "idCardBackPhoto": "id_card_back_photo",
        "emergencyContact": "emergency_contact",
        "emergencyPhone": "emergency_phone",
        "homeAddress": "home_address",
    }

    @staticmethod
    def _apply_vehicle(model: SocialCapacityVehicle, info: SocialCapacityVehicleInfo, full: bool) -> None:
        data = info.model_dump(exclude_unset=not full)
        for schema_f, model_f in SocialCapacityService._VEHICLE_FIELD_MAP.items():
            if schema_f in data:
                setattr(model, model_f, data[schema_f])

    @staticmethod
    def _apply_driver(model: SocialCapacityDriver, info: SocialCapacityDriverInfo, full: bool) -> None:
        data = info.model_dump(exclude_unset=not full)
        for schema_f, model_f in SocialCapacityService._DRIVER_FIELD_MAP.items():
            if schema_f in data:
                setattr(model, model_f, data[schema_f])

    # =====================================================
    # 列表 / 详情
    # =====================================================
    @staticmethod
    async def page(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        approval_status: Optional[int] = None,
        status: Optional[int] = None,
        source: Optional[str] = None,
        rating_level: Optional[int] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> dict:
        base_filter = [SocialCapacity.is_deleted == 0]
        if keyword:
            base_filter.append(
                or_(
                    SocialCapacity.social_code.contains(keyword),
                    SocialCapacity.driver_name.contains(keyword),
                    SocialCapacity.driver_phone.contains(keyword),
                    SocialCapacity.plate_number.contains(keyword),
                )
            )
        if approval_status is not None:
            base_filter.append(SocialCapacity.approval_status == approval_status)
        if status is not None:
            base_filter.append(SocialCapacity.status == status)
        if source is not None:
            base_filter.append(SocialCapacity.source == source)
        if rating_level is not None:
            base_filter.append(SocialCapacity.rating_level == rating_level)

        count_q = select(func.count()).select_from(
            select(SocialCapacity.id).where(*base_filter).subquery()
        )
        total = (await db.execute(count_q)).scalar() or 0

        order_clauses = _list_order_clauses(sort, order)

        result = await db.execute(
            select(SocialCapacity)
            .where(*base_filter)
            .order_by(*order_clauses)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.scalars().all()

        items: List[dict] = []
        for r in rows:
            default_acc = await SocialCapacityService._load_default_account_brief(db, r.id)
            items.append(
                SocialCapacityListItem(
                    id=r.id,
                    socialCode=r.social_code,
                    driverName=r.driver_name,
                    driverPhone=r.driver_phone,
                    plateNumber=r.plate_number,
                    vehicleTypeLabel=r.vehicle_type_label,
                    source=r.source,
                    approvalStatus=r.approval_status,
                    status=r.status,
                    ratingScore=float(r.rating_score) if r.rating_score is not None else None,
                    ratingLevel=r.rating_level,
                    defaultAccount=default_acc,
                    createdAt=r.created_at,
                    updatedAt=r.updated_at,
                ).model_dump()
            )

        return {
            "list": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    @staticmethod
    async def list_for_dispatch(
        db: AsyncSession, keyword: Optional[str] = None, limit: int = 50
    ) -> List[dict]:
        """调度选择器：仅返回 approval_status=2 AND status=1。"""
        base_filter = [
            SocialCapacity.is_deleted == 0,
            SocialCapacity.approval_status == APPROVAL_APPROVED,
            SocialCapacity.status == STATUS_ACTIVE,
        ]
        if keyword:
            base_filter.append(
                or_(
                    SocialCapacity.social_code.contains(keyword),
                    SocialCapacity.driver_name.contains(keyword),
                    SocialCapacity.driver_phone.contains(keyword),
                    SocialCapacity.plate_number.contains(keyword),
                )
            )

        q = (
            select(SocialCapacity, SocialCapacityVehicle)
            .outerjoin(
                SocialCapacityVehicle,
                and_(
                    SocialCapacityVehicle.social_capacity_id == SocialCapacity.id,
                    SocialCapacityVehicle.is_deleted == 0,
                ),
            )
            .where(*base_filter)
            .order_by(desc(SocialCapacity.rating_score), desc(SocialCapacity.id))
            .limit(limit)
        )
        rows = (await db.execute(q)).all()

        items: List[dict] = []
        for cap, veh in rows:
            default_acc = await SocialCapacityService._load_default_account_brief(db, cap.id)
            items.append(
                SocialCapacitySelectItem(
                    id=cap.id,
                    socialCode=cap.social_code,
                    driverName=cap.driver_name,
                    driverPhone=cap.driver_phone,
                    plateNumber=cap.plate_number,
                    vehicleType=veh.vehicle_type if veh else None,
                    loadCapacity=float(veh.load_capacity) if veh and veh.load_capacity is not None else None,
                    ratingLevel=cap.rating_level,
                    defaultAccount=default_acc,
                ).model_dump()
            )
        return items

    @staticmethod
    async def get_detail(
        db: AsyncSession, social_capacity_id: int
    ) -> SocialCapacityDetail:
        result = await db.execute(
            select(SocialCapacity, SocialCapacityDriver, SocialCapacityVehicle)
            .outerjoin(
                SocialCapacityDriver,
                and_(
                    SocialCapacityDriver.social_capacity_id == SocialCapacity.id,
                    SocialCapacityDriver.is_deleted == 0,
                ),
            )
            .outerjoin(
                SocialCapacityVehicle,
                and_(
                    SocialCapacityVehicle.social_capacity_id == SocialCapacity.id,
                    SocialCapacityVehicle.is_deleted == 0,
                ),
            )
            .where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        row = result.one_or_none()
        if not row:
            raise BizException("社会运力不存在")
        cap, drv, veh = row

        # 账户列表
        acc_result = await db.execute(
            select(SocialCapacityAccount)
            .where(
                SocialCapacityAccount.social_capacity_id == cap.id,
                SocialCapacityAccount.is_deleted == 0,
            )
            .order_by(
                SocialCapacityAccount.is_default.desc(),
                asc(SocialCapacityAccount.created_at),
                asc(SocialCapacityAccount.id),
            )
        )
        accounts = [
            SocialCapacityAccountBrief(
                id=a.id,
                accountType=a.account_type,
                accountLabel=a.account_label,
                accountName=a.account_name,
                accountNo=a.account_no,
                bankName=a.bank_name,
                isDefault=a.is_default,
                status=a.status,
            )
            for a in acc_result.scalars().all()
        ]

        # 最近一条流水
        latest = await SocialCapacityAuditService.latest(db, cap.id)
        last_audit_brief = None
        if latest:
            last_audit_brief = SocialCapacityAuditBrief(
                id=latest.id,
                action=latest.action,
                beforeStatus=latest.before_status,
                afterStatus=latest.after_status,
                operatorUserId=latest.operator_user_id,
                operatorName=latest.operator_name,
                remark=latest.remark,
                createdAt=latest.created_at,
            )

        return SocialCapacityDetail(
            id=cap.id,
            socialCode=cap.social_code,
            driverName=cap.driver_name,
            driverPhone=cap.driver_phone,
            driverIdCard=cap.driver_id_card,
            plateNumber=cap.plate_number,
            vehicleTypeLabel=cap.vehicle_type_label,
            source=cap.source,
            sourceRemark=cap.source_remark,
            referrerUserId=cap.referrer_user_id,
            approvalStatus=cap.approval_status,
            approvalUserId=cap.approval_user_id,
            approvalTime=cap.approval_time,
            approvalRemark=cap.approval_remark,
            status=cap.status,
            statusRemark=cap.status_remark,
            ratingScore=float(cap.rating_score) if cap.rating_score is not None else None,
            ratingLevel=cap.rating_level,
            lastEvaluatedAt=cap.last_evaluated_at,
            evaluationSummary=cap.evaluation_summary,
            orderCount=cap.order_count,
            lastDispatchedAt=cap.last_dispatched_at,
            createdUserId=cap.created_user_id,
            updatedUserId=cap.updated_user_id,
            remark=cap.remark,
            createdAt=cap.created_at,
            updatedAt=cap.updated_at,
            vehicle=(
                SocialCapacityVehicleInfo(**{
                    schema_f: getattr(veh, model_f)
                    for schema_f, model_f in SocialCapacityService._VEHICLE_FIELD_MAP.items()
                    if hasattr(veh, model_f)
                }) if veh else None
            ),
            driver=(
                SocialCapacityDriverInfo(**{
                    schema_f: getattr(drv, model_f)
                    for schema_f, model_f in SocialCapacityService._DRIVER_FIELD_MAP.items()
                    if hasattr(drv, model_f)
                }) if drv else None
            ),
            accounts=accounts,
            lastAudit=last_audit_brief,
        )

    # =====================================================
    # 新增 / 编辑 / 删除
    # =====================================================
    @staticmethod
    async def create(
        db: AsyncSession,
        data: SocialCapacityCreate,
        current_user_id: Optional[int] = None,
    ) -> SocialCapacityDetail:
        await SocialCapacityService._check_unique_phone(db, data.driver.phone)
        await SocialCapacityService._check_unique_plate(db, data.vehicle.plateNumber)

        social_code = await SocialCapacityService._generate_social_code(db)

        capacity = SocialCapacity(
            social_code=social_code,
            driver_name=data.driver.name,
            driver_phone=data.driver.phone,
            driver_id_card=data.driver.idCard,
            plate_number=data.vehicle.plateNumber,
            vehicle_type_label=data.vehicle.vehicleType,
            source=data.source,
            source_remark=data.sourceRemark,
            referrer_user_id=data.referrerUserId,
            approval_status=APPROVAL_DRAFT,
            status=STATUS_INACTIVE,
            order_count=0,
            created_user_id=current_user_id,
            updated_user_id=current_user_id,
            remark=data.remark,
        )
        db.add(capacity)
        await db.flush()
        await db.refresh(capacity)

        vehicle = SocialCapacityVehicle(social_capacity_id=capacity.id)
        SocialCapacityService._apply_vehicle(vehicle, data.vehicle, full=True)
        db.add(vehicle)

        driver = SocialCapacityDriver(social_capacity_id=capacity.id)
        SocialCapacityService._apply_driver(driver, data.driver, full=True)
        db.add(driver)

        await db.flush()
        return await SocialCapacityService.get_detail(db, capacity.id)

    @staticmethod
    async def update(
        db: AsyncSession,
        social_capacity_id: int,
        data: SocialCapacityUpdate,
        current_user_id: Optional[int] = None,
    ) -> SocialCapacityDetail:
        result = await db.execute(
            select(SocialCapacity).where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("社会运力不存在")

        # 编辑权限矩阵
        if capacity.approval_status == APPROVAL_PENDING:
            raise BizException("待审核状态不可编辑，请先撤回审核")

        update = data.model_dump(exclude_unset=True)
        approved = capacity.approval_status == APPROVAL_APPROVED

        # 已通过：仅可改 备注，不允许改基础信息 / 车辆 / 司机
        if approved:
            forbidden = {"source", "sourceRemark", "referrerUserId", "vehicle", "driver"}
            if any(k in update for k in forbidden):
                raise BizException("已通过的运力档案仅可修改结算账户与备注")

        # 唯一性预检查（如果更新了 phone / plate）
        if data.driver and data.driver.phone:
            await SocialCapacityService._check_unique_phone(
                db, data.driver.phone, exclude_id=capacity.id
            )
        if data.vehicle and data.vehicle.plateNumber:
            await SocialCapacityService._check_unique_plate(
                db, data.vehicle.plateNumber, exclude_id=capacity.id
            )

        if "source" in update:
            capacity.source = update["source"]
        if "sourceRemark" in update:
            capacity.source_remark = update["sourceRemark"]
        if "referrerUserId" in update:
            capacity.referrer_user_id = update["referrerUserId"]
        if "remark" in update:
            capacity.remark = update["remark"]
        capacity.updated_user_id = current_user_id

        if data.vehicle:
            veh_result = await db.execute(
                select(SocialCapacityVehicle).where(
                    SocialCapacityVehicle.social_capacity_id == capacity.id,
                    SocialCapacityVehicle.is_deleted == 0,
                )
            )
            vehicle = veh_result.scalar_one_or_none()
            if not vehicle:
                vehicle = SocialCapacityVehicle(social_capacity_id=capacity.id)
                db.add(vehicle)
                await db.flush()
            SocialCapacityService._apply_vehicle(vehicle, data.vehicle, full=False)
            if data.vehicle.plateNumber:
                capacity.plate_number = data.vehicle.plateNumber
            if data.vehicle.vehicleType:
                capacity.vehicle_type_label = data.vehicle.vehicleType

        if data.driver:
            drv_result = await db.execute(
                select(SocialCapacityDriver).where(
                    SocialCapacityDriver.social_capacity_id == capacity.id,
                    SocialCapacityDriver.is_deleted == 0,
                )
            )
            driver = drv_result.scalar_one_or_none()
            if not driver:
                driver = SocialCapacityDriver(
                    social_capacity_id=capacity.id,
                    name=data.driver.name,
                    phone=data.driver.phone,
                )
                db.add(driver)
                await db.flush()
            SocialCapacityService._apply_driver(driver, data.driver, full=False)
            if data.driver.name:
                capacity.driver_name = data.driver.name
            if data.driver.phone:
                capacity.driver_phone = data.driver.phone
            if data.driver.idCard is not None:
                capacity.driver_id_card = data.driver.idCard

        await db.flush()
        return await SocialCapacityService.get_detail(db, capacity.id)

    @staticmethod
    async def delete(db: AsyncSession, social_capacity_id: int) -> None:
        result = await db.execute(
            select(SocialCapacity).where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("社会运力不存在")

        # 已通过 + 正常 状态禁止直接删除
        if (
            capacity.approval_status == APPROVAL_APPROVED
            and capacity.status == STATUS_ACTIVE
        ):
            raise BizException("已启用的社会运力不可删除，请先停用")

        # TODO: 接入运单 / 任务单后补真实引用校验
        # if await _has_active_reference(db, capacity.id):
        #     raise BizException("已被运单引用的社会运力不可删除")

        capacity.is_deleted = 1

        veh_result = await db.execute(
            select(SocialCapacityVehicle).where(
                SocialCapacityVehicle.social_capacity_id == capacity.id,
                SocialCapacityVehicle.is_deleted == 0,
            )
        )
        for veh in veh_result.scalars().all():
            veh.is_deleted = 1

        drv_result = await db.execute(
            select(SocialCapacityDriver).where(
                SocialCapacityDriver.social_capacity_id == capacity.id,
                SocialCapacityDriver.is_deleted == 0,
            )
        )
        for drv in drv_result.scalars().all():
            drv.is_deleted = 1

        acc_result = await db.execute(
            select(SocialCapacityAccount).where(
                SocialCapacityAccount.social_capacity_id == capacity.id,
                SocialCapacityAccount.is_deleted == 0,
            )
        )
        for acc in acc_result.scalars().all():
            acc.is_deleted = 1

        await db.flush()

    # =====================================================
    # 状态机：审核
    # =====================================================
    @staticmethod
    async def submit(
        db: AsyncSession,
        social_capacity_id: int,
        operator_user_id: int,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> SocialCapacityDetail:
        result = await db.execute(
            select(SocialCapacity).where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("社会运力不存在")
        if capacity.approval_status not in (APPROVAL_DRAFT, APPROVAL_REJECTED):
            raise BizException("仅草稿 / 已驳回 状态可提交审核")

        # 必填校验
        await SocialCapacityService._validate_for_submit(db, capacity.id)

        before = capacity.approval_status
        capacity.approval_status = APPROVAL_PENDING
        await db.flush()

        await SocialCapacityAuditService.write(
            db=db,
            social_capacity_id=capacity.id,
            action=ACTION_SUBMIT,
            before_status=before,
            after_status=APPROVAL_PENDING,
            operator_user_id=operator_user_id,
            operator_name=operator_name,
            remark=remark,
        )
        return await SocialCapacityService.get_detail(db, capacity.id)

    @staticmethod
    async def withdraw(
        db: AsyncSession,
        social_capacity_id: int,
        operator_user_id: int,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> SocialCapacityDetail:
        result = await db.execute(
            select(SocialCapacity).where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("社会运力不存在")
        if capacity.approval_status != APPROVAL_PENDING:
            raise BizException("仅待审核状态可撤回")

        capacity.approval_status = APPROVAL_DRAFT
        await db.flush()

        await SocialCapacityAuditService.write(
            db=db,
            social_capacity_id=capacity.id,
            action=ACTION_WITHDRAW,
            before_status=APPROVAL_PENDING,
            after_status=APPROVAL_DRAFT,
            operator_user_id=operator_user_id,
            operator_name=operator_name,
            remark=remark,
        )
        return await SocialCapacityService.get_detail(db, capacity.id)

    @staticmethod
    async def approve(
        db: AsyncSession,
        social_capacity_id: int,
        operator_user_id: int,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> SocialCapacityDetail:
        result = await db.execute(
            select(SocialCapacity).where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("社会运力不存在")
        if capacity.approval_status != APPROVAL_PENDING:
            raise BizException("仅待审核状态可审核通过")

        capacity.approval_status = APPROVAL_APPROVED
        capacity.approval_user_id = operator_user_id
        capacity.approval_time = datetime.now()
        capacity.approval_remark = remark
        # 自动 0 -> 1
        if capacity.status == STATUS_INACTIVE:
            capacity.status = STATUS_ACTIVE
        await db.flush()

        await SocialCapacityAuditService.write(
            db=db,
            social_capacity_id=capacity.id,
            action=ACTION_APPROVE,
            before_status=APPROVAL_PENDING,
            after_status=APPROVAL_APPROVED,
            operator_user_id=operator_user_id,
            operator_name=operator_name,
            remark=remark,
        )
        return await SocialCapacityService.get_detail(db, capacity.id)

    @staticmethod
    async def reject(
        db: AsyncSession,
        social_capacity_id: int,
        operator_user_id: int,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> SocialCapacityDetail:
        if not remark:
            raise BizException("驳回必须填写理由")
        result = await db.execute(
            select(SocialCapacity).where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("社会运力不存在")
        if capacity.approval_status != APPROVAL_PENDING:
            raise BizException("仅待审核状态可驳回")

        capacity.approval_status = APPROVAL_REJECTED
        capacity.approval_user_id = operator_user_id
        capacity.approval_time = datetime.now()
        capacity.approval_remark = remark
        await db.flush()

        await SocialCapacityAuditService.write(
            db=db,
            social_capacity_id=capacity.id,
            action=ACTION_REJECT,
            before_status=APPROVAL_PENDING,
            after_status=APPROVAL_REJECTED,
            operator_user_id=operator_user_id,
            operator_name=operator_name,
            remark=remark,
        )
        return await SocialCapacityService.get_detail(db, capacity.id)

    # =====================================================
    # 状态机：启用 / 停用 / 黑名单
    # =====================================================
    _STATUS_ACTION_MAP = {
        # (from_status, to_status) -> action_code
        (STATUS_INACTIVE, STATUS_ACTIVE): ACTION_ENABLE,
        (STATUS_DISABLED, STATUS_ACTIVE): ACTION_ENABLE,
        (STATUS_BLACKLIST, STATUS_ACTIVE): ACTION_UNBLACKLIST,
        (STATUS_ACTIVE, STATUS_DISABLED): ACTION_DISABLE,
        (STATUS_BLACKLIST, STATUS_DISABLED): ACTION_DISABLE,
        (STATUS_INACTIVE, STATUS_DISABLED): ACTION_DISABLE,
        (STATUS_ACTIVE, STATUS_BLACKLIST): ACTION_BLACKLIST,
        (STATUS_DISABLED, STATUS_BLACKLIST): ACTION_BLACKLIST,
    }

    @staticmethod
    async def update_status(
        db: AsyncSession,
        social_capacity_id: int,
        target_status: int,
        operator_user_id: int,
        operator_name: Optional[str] = None,
        remark: Optional[str] = None,
    ) -> SocialCapacityDetail:
        result = await db.execute(
            select(SocialCapacity).where(
                SocialCapacity.id == social_capacity_id,
                SocialCapacity.is_deleted == 0,
            )
        )
        capacity = result.scalar_one_or_none()
        if not capacity:
            raise BizException("社会运力不存在")

        if capacity.approval_status != APPROVAL_APPROVED:
            raise BizException("仅审核通过的社会运力可调整启用状态")
        if target_status not in (
            STATUS_INACTIVE,
            STATUS_ACTIVE,
            STATUS_DISABLED,
            STATUS_BLACKLIST,
        ):
            raise BizException("非法的目标状态")
        if target_status == STATUS_INACTIVE:
            raise BizException("已审核通过的运力不可回到未生效状态")
        if capacity.status == target_status:
            raise BizException("当前状态与目标状态相同")

        action = SocialCapacityService._STATUS_ACTION_MAP.get(
            (capacity.status, target_status)
        )
        if action is None:
            raise BizException("不支持的状态切换")

        before = capacity.status
        capacity.status = target_status
        capacity.status_remark = remark
        await db.flush()

        await SocialCapacityAuditService.write(
            db=db,
            social_capacity_id=capacity.id,
            action=action,
            before_status=before,
            after_status=target_status,
            operator_user_id=operator_user_id,
            operator_name=operator_name,
            remark=remark,
        )
        return await SocialCapacityService.get_detail(db, capacity.id)

    # =====================================================
    # 提交审核前的必填校验
    # =====================================================
    @staticmethod
    async def _validate_for_submit(
        db: AsyncSession, social_capacity_id: int
    ) -> None:
        # 至少一条结算账户
        acc_q = await db.execute(
            select(SocialCapacityAccount.id).where(
                SocialCapacityAccount.social_capacity_id == social_capacity_id,
                SocialCapacityAccount.is_deleted == 0,
            )
        )
        if acc_q.first() is None:
            raise BizException("至少需要登记 1 条结算账户后才能提交审核")

    # =====================================================
    # 审批中心专用：分页 + 统计
    # =====================================================
    @staticmethod
    async def page_for_approval(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        keyword: Optional[str] = None,
        approval_status: Optional[int] = APPROVAL_PENDING,
    ) -> dict:
        return await SocialCapacityService.page(
            db=db,
            page=page,
            page_size=page_size,
            keyword=keyword,
            approval_status=approval_status,
        )

    @staticmethod
    async def pending_count(db: AsyncSession) -> int:
        result = await db.execute(
            select(func.count()).select_from(
                select(SocialCapacity.id)
                .where(
                    SocialCapacity.is_deleted == 0,
                    SocialCapacity.approval_status == APPROVAL_PENDING,
                )
                .subquery()
            )
        )
        return result.scalar() or 0
