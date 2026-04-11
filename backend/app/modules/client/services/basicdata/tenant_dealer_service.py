"""
租户库经销商服务
"""

from typing import Optional, Tuple

from sqlalchemy import select, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.common.pagination import paginate
from app.common.utils import to_decimal
from app.modules.client.models.vehicle_basic.biz_dealer import BizDealer
from app.modules.client.schemas.basicdata.dealer import (
    DealerCreate,
    DealerUpdate,
    DealerOut,
)


class TenantDealerService:

    @staticmethod
    def _order_created_at_clause(
        sort: Optional[str], order: Optional[str]
    ) -> Tuple:
        """按创建时间排序：仅支持 createdAt，其它回退为创建时间倒序。"""
        if sort != "createdAt":
            return (BizDealer.created_at.desc(), BizDealer.dealer_id.desc())
        ol = (order or "descending").lower()
        if ol in ("asc", "ascending"):
            return (BizDealer.created_at.asc(), BizDealer.dealer_id.asc())
        return (BizDealer.created_at.desc(), BizDealer.dealer_id.desc())

    @staticmethod
    async def page_dealers(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        keyword: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> dict:
        stmt = select(BizDealer)
        if keyword:
            kw = keyword.strip()
            stmt = stmt.where(
                or_(
                    BizDealer.dealer_name.contains(kw),
                    BizDealer.province.contains(kw),
                    BizDealer.city.contains(kw),
                    BizDealer.main_brand.contains(kw),
                )
            )
        order_clause = TenantDealerService._order_created_at_clause(sort, order)
        return await paginate(
            db,
            stmt,
            page,
            limit,
            order_by=order_clause,
            serializer=lambda r: DealerOut.from_model(r).model_dump(),
        )

    @staticmethod
    async def get_dealer(db: AsyncSession, dealer_id: int) -> DealerOut:
        result = await db.execute(
            select(BizDealer).where(BizDealer.dealer_id == dealer_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("经销商不存在")
        return DealerOut.from_model(row)

    @staticmethod
    async def create_dealer(
        db: AsyncSession, data: DealerCreate
    ) -> BizDealer:
        row = BizDealer(
            dealer_name=data.dealerName,
            dealer_type=data.dealerType,
            main_brand=data.mainBrand,
            province=data.province,
            city=data.city,
            address_detail=data.addressDetail,
            longitude=to_decimal(data.longitude),
            latitude=to_decimal(data.latitude),
        )
        db.add(row)
        await db.flush()
        return row

    @staticmethod
    async def update_dealer(
        db: AsyncSession, dealer_id: int, data: DealerUpdate
    ) -> BizDealer:
        result = await db.execute(
            select(BizDealer).where(BizDealer.dealer_id == dealer_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("经销商不存在")
        if data.dealerName is not None:
            row.dealer_name = data.dealerName
        if data.dealerType is not None:
            row.dealer_type = data.dealerType
        if data.mainBrand is not None:
            row.main_brand = data.mainBrand
        if data.province is not None:
            row.province = data.province
        if data.city is not None:
            row.city = data.city
        if data.addressDetail is not None:
            row.address_detail = data.addressDetail
        if data.longitude is not None:
            row.longitude = to_decimal(data.longitude)
        if data.latitude is not None:
            row.latitude = to_decimal(data.latitude)
        await db.flush()
        return row

    @staticmethod
    async def delete_dealer(db: AsyncSession, dealer_id: int) -> None:
        result = await db.execute(
            select(BizDealer).where(BizDealer.dealer_id == dealer_id)
        )
        row = result.scalar_one_or_none()
        if not row:
            raise BizException("经销商不存在")
        await db.execute(
            delete(BizDealer).where(BizDealer.dealer_id == dealer_id)
        )
