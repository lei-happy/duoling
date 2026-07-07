"""
经营主体管理服务（租户库）

职责：
- 经营主体 CRUD；
- 默认主体维护（租户内至多 1 条 is_default=1）；
- 启用 / 停用；
- 删除前关联校验（存在归属业务数据禁止删除，默认主体禁止删除）。
"""

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.organization.business_entity import BusinessEntity
from app.modules.client.schemas.organization.business_entity import (
    BusinessEntityCreate,
    BusinessEntityOption,
    BusinessEntityOut,
    BusinessEntityUpdate,
)

STATUS_NORMAL = 1
STATUS_DISABLED = 0

IS_DEFAULT = 1
NOT_DEFAULT = 0

_CODE_PREFIX = "ENT"
MAX_PAGE_SIZE = 100


class BusinessEntityService:
    """经营主体"""

    # ------------------------------------------------------------------
    # 编码生成
    # ------------------------------------------------------------------
    @staticmethod
    async def _generate_code(db: AsyncSession) -> str:
        cnt = int(
            (await db.execute(select(func.count(BusinessEntity.id)))).scalar() or 0
        )
        # 处理编码冲突（软删/历史占用）：递增直到不冲突
        seq = cnt + 1
        while True:
            code = f"{_CODE_PREFIX}{seq:04d}"
            exists = (
                await db.execute(
                    select(BusinessEntity.id).where(
                        BusinessEntity.entity_code == code
                    )
                )
            ).scalar_one_or_none()
            if not exists:
                return code
            seq += 1

    # ------------------------------------------------------------------
    # 查询
    # ------------------------------------------------------------------
    @staticmethod
    async def page(
        db: AsyncSession,
        *,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        status: Optional[int] = None,
    ) -> dict:
        base = select(BusinessEntity).where(BusinessEntity.is_deleted == 0)
        if keyword:
            kw = f"%{keyword.strip()}%"
            base = base.where(
                BusinessEntity.entity_name.like(kw)
                | BusinessEntity.entity_code.like(kw)
                | BusinessEntity.short_name.like(kw)
            )
        if status is not None:
            base = base.where(BusinessEntity.status == status)

        count = int(
            (await db.execute(
                select(func.count()).select_from(base.subquery())
            )).scalar() or 0
        )
        page = max(1, page)
        limit = max(1, min(limit, MAX_PAGE_SIZE))
        rows = (
            await db.execute(
                base.order_by(
                    BusinessEntity.is_default.desc(),
                    BusinessEntity.sort_order.asc(),
                    BusinessEntity.id.asc(),
                )
                .offset((page - 1) * limit)
                .limit(limit)
            )
        ).scalars().all()
        return {
            "list": [BusinessEntityOut.from_model(r).model_dump() for r in rows],
            "count": count,
        }

    @staticmethod
    async def options(db: AsyncSession) -> list[dict]:
        """下拉选项：仅正常状态，默认主体置顶。"""
        rows = (
            await db.execute(
                select(BusinessEntity)
                .where(
                    BusinessEntity.is_deleted == 0,
                    BusinessEntity.status == STATUS_NORMAL,
                )
                .order_by(
                    BusinessEntity.is_default.desc(),
                    BusinessEntity.sort_order.asc(),
                    BusinessEntity.id.asc(),
                )
            )
        ).scalars().all()
        return [BusinessEntityOption.from_model(r).model_dump() for r in rows]

    @staticmethod
    async def get_or_404(db: AsyncSession, entity_id: int) -> BusinessEntity:
        m = (
            await db.execute(
                select(BusinessEntity).where(
                    BusinessEntity.id == entity_id,
                    BusinessEntity.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if not m:
            raise BizException("经营主体不存在")
        return m

    @staticmethod
    async def get(db: AsyncSession, entity_id: int) -> BusinessEntityOut:
        return BusinessEntityOut.from_model(
            await BusinessEntityService.get_or_404(db, entity_id)
        )

    # ------------------------------------------------------------------
    # 默认主体
    # ------------------------------------------------------------------
    @staticmethod
    async def _has_any(db: AsyncSession) -> bool:
        r = await db.execute(
            select(BusinessEntity.id).where(BusinessEntity.is_deleted == 0).limit(1)
        )
        return r.scalar_one_or_none() is not None

    @staticmethod
    async def ensure_default(db: AsyncSession, *, entity_name: str = "默认经营主体") -> BusinessEntity:
        """确保存在一个默认主体；无任何主体时创建。供 seed / 兜底调用。"""
        existing_default = (
            await db.execute(
                select(BusinessEntity).where(
                    BusinessEntity.is_deleted == 0,
                    BusinessEntity.is_default == IS_DEFAULT,
                )
            )
        ).scalar_one_or_none()
        if existing_default:
            return existing_default
        if await BusinessEntityService._has_any(db):
            # 有主体但无默认：挑选排序最靠前的置为默认
            first = (
                await db.execute(
                    select(BusinessEntity)
                    .where(BusinessEntity.is_deleted == 0)
                    .order_by(BusinessEntity.sort_order.asc(), BusinessEntity.id.asc())
                    .limit(1)
                )
            ).scalar_one()
            first.is_default = IS_DEFAULT
            await db.flush()
            return first
        entity = BusinessEntity(
            entity_code=await BusinessEntityService._generate_code(db),
            entity_name=entity_name,
            invoice_title=entity_name,
            is_default=IS_DEFAULT,
            status=STATUS_NORMAL,
        )
        db.add(entity)
        await db.flush()
        return entity

    @staticmethod
    async def _clear_default(db: AsyncSession, keep_id: Optional[int] = None) -> None:
        rows = (
            await db.execute(
                select(BusinessEntity).where(
                    BusinessEntity.is_deleted == 0,
                    BusinessEntity.is_default == IS_DEFAULT,
                )
            )
        ).scalars().all()
        for r in rows:
            if keep_id is not None and r.id == keep_id:
                continue
            r.is_default = NOT_DEFAULT

    @staticmethod
    async def set_default(db: AsyncSession, entity_id: int) -> BusinessEntityOut:
        m = await BusinessEntityService.get_or_404(db, entity_id)
        if m.status != STATUS_NORMAL:
            raise BizException("停用的主体不可设为默认")
        await BusinessEntityService._clear_default(db, keep_id=entity_id)
        m.is_default = IS_DEFAULT
        await db.flush()
        await db.refresh(m)
        return BusinessEntityOut.from_model(m)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @staticmethod
    async def create(
        db: AsyncSession, data: BusinessEntityCreate
    ) -> BusinessEntityOut:
        code = (data.entityCode or "").strip() or await BusinessEntityService._generate_code(db)
        dup = (
            await db.execute(
                select(BusinessEntity.id).where(
                    BusinessEntity.entity_code == code,
                    BusinessEntity.is_deleted == 0,
                )
            )
        ).scalar_one_or_none()
        if dup:
            raise BizException(f"主体编码已存在：{code}")

        is_first = not await BusinessEntityService._has_any(db)
        entity = BusinessEntity(
            entity_code=code,
            entity_name=data.entityName,
            short_name=data.shortName,
            unified_credit_code=data.unifiedCreditCode,
            legal_person=data.legalPerson,
            registered_address=data.registeredAddress,
            contact_person=data.contactPerson,
            contact_phone=data.contactPhone,
            bank_name=data.bankName,
            bank_account=data.bankAccount,
            invoice_title=data.invoiceTitle or data.entityName,
            invoice_tax_no=data.invoiceTaxNo or data.unifiedCreditCode,
            sort_order=data.sortOrder or 0,
            remark=data.remark,
            # 首个主体自动成为默认
            is_default=IS_DEFAULT if is_first else NOT_DEFAULT,
            status=STATUS_NORMAL,
        )
        db.add(entity)
        await db.flush()
        await db.refresh(entity)
        return BusinessEntityOut.from_model(entity)

    @staticmethod
    async def update(
        db: AsyncSession, entity_id: int, data: BusinessEntityUpdate
    ) -> BusinessEntityOut:
        m = await BusinessEntityService.get_or_404(db, entity_id)
        field_map = {
            "entityName": "entity_name",
            "shortName": "short_name",
            "unifiedCreditCode": "unified_credit_code",
            "legalPerson": "legal_person",
            "registeredAddress": "registered_address",
            "contactPerson": "contact_person",
            "contactPhone": "contact_phone",
            "bankName": "bank_name",
            "bankAccount": "bank_account",
            "invoiceTitle": "invoice_title",
            "invoiceTaxNo": "invoice_tax_no",
            "sortOrder": "sort_order",
            "remark": "remark",
        }
        for schema_field, model_field in field_map.items():
            val = getattr(data, schema_field, None)
            if val is not None:
                setattr(m, model_field, val)
        await db.flush()
        await db.refresh(m)
        return BusinessEntityOut.from_model(m)

    @staticmethod
    async def toggle_status(
        db: AsyncSession, entity_id: int, status: int
    ) -> BusinessEntityOut:
        if status not in (STATUS_NORMAL, STATUS_DISABLED):
            raise BizException("非法状态值")
        m = await BusinessEntityService.get_or_404(db, entity_id)
        if status == STATUS_DISABLED and m.is_default == IS_DEFAULT:
            raise BizException("默认主体不可停用，请先切换默认主体")
        m.status = status
        await db.flush()
        await db.refresh(m)
        return BusinessEntityOut.from_model(m)

    @staticmethod
    async def delete(db: AsyncSession, entity_id: int) -> None:
        m = await BusinessEntityService.get_or_404(db, entity_id)
        if m.is_default == IS_DEFAULT:
            raise BizException("默认主体不可删除，请先切换默认主体")
        await BusinessEntityService._assert_no_reference(db, entity_id)
        m.is_deleted = 1
        await db.flush()

    @staticmethod
    async def _assert_no_reference(db: AsyncSession, entity_id: int) -> None:
        """存在归属业务数据时禁止删除。"""
        from app.modules.client.models.capacity.self_capacity.driver.driver import (
            Driver,
        )
        from app.modules.client.models.capacity.self_capacity.vehicle import Vehicle
        from app.modules.client.models.capacity.self_capacity.capacity import Capacity
        from app.modules.client.models.task.task import Task
        from app.modules.client.models.task.task_finance_doc import TaskFinanceDoc
        from app.modules.client.models.partner.customer import Customer
        from app.modules.client.models.partner.carrier import Carrier
        from app.modules.client.models.waybill.waybill import Waybill

        checks = [
            (Driver, "司机"),
            (Vehicle, "车辆"),
            (Capacity, "运力"),
            (Task, "任务"),
            (TaskFinanceDoc, "费用单"),
            (Customer, "客户"),
            (Carrier, "承运商"),
            (Waybill, "运单"),
        ]
        for model, label in checks:
            hit = (
                await db.execute(
                    select(model.id).where(
                        model.enterprise_id == entity_id,
                        model.is_deleted == 0,
                    ).limit(1)
                )
            ).scalar_one_or_none()
            if hit:
                raise BizException(f"该主体下存在关联{label}数据，无法删除")
