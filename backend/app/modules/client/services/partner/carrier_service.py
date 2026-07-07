"""
承运商主体档案服务（租户库）
- CRUD
- 创建时联动写 settlements
- 列表分页/筛选
- 选择器（含默认结算账户）
"""

from typing import List, Optional, Tuple

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.schemas.partner.carrier import (
    CarrierCreate, CarrierUpdate,
)
from app.modules.client.services.partner.carrier_settlement_service import (
    CarrierSettlementService,
)


class CarrierService:

    @staticmethod
    async def _check_unique_code(
        db: AsyncSession, code: Optional[str], exclude_id: Optional[int] = None
    ) -> None:
        if not code:
            return
        stmt = select(Carrier.id).where(
            Carrier.carrier_code == code,
            Carrier.is_deleted == 0,
        )
        if exclude_id is not None:
            stmt = stmt.where(Carrier.id != exclude_id)
        r = await db.execute(stmt.limit(1))
        if r.scalar_one_or_none() is not None:
            raise BizException(f"承运商编码 {code} 已存在")

    @staticmethod
    async def _check_phone_conflict(
        db: AsyncSession, phone: str, exclude_id: Optional[int] = None
    ) -> None:
        """同租户内不允许重复联系电话（互联激活语义要求唯一）"""
        if not phone:
            return
        stmt = select(Carrier.id).where(
            Carrier.contact_phone == phone,
            Carrier.is_deleted == 0,
        )
        if exclude_id is not None:
            stmt = stmt.where(Carrier.id != exclude_id)
        r = await db.execute(stmt.limit(1))
        if r.scalar_one_or_none() is not None:
            raise BizException(f"联系电话 {phone} 已被其他承运商使用")

    @staticmethod
    async def get_or_404(db: AsyncSession, carrier_id: int) -> Carrier:
        r = await db.execute(
            select(Carrier).where(
                Carrier.id == carrier_id,
                Carrier.is_deleted == 0,
            )
        )
        c = r.scalar_one_or_none()
        if not c:
            raise BizException("承运商不存在")
        return c

    @staticmethod
    async def list_page(
        db: AsyncSession,
        keyword: Optional[str] = None,
        carrier_type: Optional[int] = None,
        status: Optional[int] = None,
        invite_status: Optional[int] = None,
        linked_only: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Carrier], int]:
        base = select(Carrier).where(Carrier.is_deleted == 0)
        cnt = select(func.count(Carrier.id)).where(Carrier.is_deleted == 0)

        if keyword:
            kw = f"%{keyword}%"
            cond = or_(
                Carrier.carrier_name.like(kw),
                Carrier.short_name.like(kw),
                Carrier.carrier_code.like(kw),
                Carrier.contact_person.like(kw),
                Carrier.contact_phone.like(kw),
            )
            base = base.where(cond)
            cnt = cnt.where(cond)
        if carrier_type is not None:
            base = base.where(Carrier.carrier_type == carrier_type)
            cnt = cnt.where(Carrier.carrier_type == carrier_type)
        if status is not None:
            base = base.where(Carrier.status == status)
            cnt = cnt.where(Carrier.status == status)
        if invite_status is not None:
            base = base.where(Carrier.invite_status == invite_status)
            cnt = cnt.where(Carrier.invite_status == invite_status)
        if linked_only is True:
            base = base.where(Carrier.linked_tenant_code.is_not(None))
            cnt = cnt.where(Carrier.linked_tenant_code.is_not(None))
        elif linked_only is False:
            base = base.where(Carrier.linked_tenant_code.is_(None))
            cnt = cnt.where(Carrier.linked_tenant_code.is_(None))

        total_r = await db.execute(cnt)
        total = int(total_r.scalar() or 0)

        offset = max(0, (page - 1) * page_size)
        items_r = await db.execute(
            base.order_by(Carrier.created_at.desc(), Carrier.id.desc())
            .offset(offset).limit(page_size)
        )
        return list(items_r.scalars().all()), total

    @staticmethod
    async def create(
        db: AsyncSession, data: CarrierCreate
    ) -> Carrier:
        await CarrierService._check_unique_code(db, data.carrierCode)
        await CarrierService._check_phone_conflict(db, data.contactPhone)

        carrier = Carrier(
            carrier_code=data.carrierCode,
            carrier_name=data.carrierName,
            short_name=data.shortName,
            enterprise_id=data.enterpriseId,
            carrier_type=data.carrierType or 0,
            credit_code=data.creditCode,
            id_card_no=data.idCardNo,
            legal_person=data.legalPerson,
            contact_person=data.contactPerson,
            contact_phone=data.contactPhone,
            contact_email=data.contactEmail,
            province=data.province,
            city=data.city,
            district=data.district,
            address=data.address,
            cooperation_start_date=data.cooperationStartDate,
            status=data.status if data.status is not None else 1,
            invite_status=0,
            remark=data.remark,
        )
        db.add(carrier)
        await db.flush()

        # 联动创建结算账户（保证至多 1 条 is_default=1）
        if data.settlements:
            default_seen = False
            for idx, s in enumerate(data.settlements):
                if s.isDefault == 1 and default_seen:
                    s.isDefault = 0
                if s.isDefault == 1:
                    default_seen = True
                await CarrierSettlementService.create(db, carrier.id, s)

        await db.refresh(carrier)
        return carrier

    @staticmethod
    async def update(
        db: AsyncSession, carrier_id: int, data: CarrierUpdate
    ) -> Carrier:
        carrier = await CarrierService.get_or_404(db, carrier_id)
        if data.carrierCode is not None and data.carrierCode != carrier.carrier_code:
            await CarrierService._check_unique_code(
                db, data.carrierCode, exclude_id=carrier_id
            )
        if data.contactPhone is not None and data.contactPhone != carrier.contact_phone:
            # 已激活互联的承运商联系电话不可改（避免联系人和已链接 B 不一致）
            if carrier.linked_tenant_code:
                raise BizException("承运商已激活互联，联系电话不可修改")
            await CarrierService._check_phone_conflict(
                db, data.contactPhone, exclude_id=carrier_id
            )

        field_map = {
            "carrierCode": "carrier_code",
            "carrierName": "carrier_name",
            "shortName": "short_name",
            "enterpriseId": "enterprise_id",
            "carrierType": "carrier_type",
            "creditCode": "credit_code",
            "idCardNo": "id_card_no",
            "legalPerson": "legal_person",
            "contactPerson": "contact_person",
            "contactPhone": "contact_phone",
            "contactEmail": "contact_email",
            "province": "province",
            "city": "city",
            "district": "district",
            "address": "address",
            "cooperationStartDate": "cooperation_start_date",
            "status": "status",
            "remark": "remark",
        }
        for sf, mf in field_map.items():
            v = getattr(data, sf, None)
            if v is not None:
                setattr(carrier, mf, v)

        await db.flush()
        await db.refresh(carrier)
        return carrier

    @staticmethod
    async def delete(db: AsyncSession, carrier_id: int) -> None:
        carrier = await CarrierService.get_or_404(db, carrier_id)
        if carrier.linked_tenant_code:
            raise BizException("已激活互联的承运商需先解除互联再删除")
        # 远期：若被运单引用则禁止删除
        carrier.is_deleted = 1
        await CarrierSettlementService.cascade_soft_delete(db, carrier_id)
        await db.flush()

    @staticmethod
    async def select_for_picker(
        db: AsyncSession,
        keyword: Optional[str] = None,
        limit: int = 50,
    ) -> List[Carrier]:
        """运单/合同等场景的承运商选择器（仅返回正常状态）"""
        stmt = select(Carrier).where(
            Carrier.is_deleted == 0, Carrier.status == 1
        )
        if keyword:
            kw = f"%{keyword}%"
            stmt = stmt.where(or_(
                Carrier.carrier_name.like(kw),
                Carrier.short_name.like(kw),
                Carrier.carrier_code.like(kw),
            ))
        stmt = stmt.order_by(Carrier.carrier_name.asc()).limit(limit)
        r = await db.execute(stmt)
        return list(r.scalars().all())
