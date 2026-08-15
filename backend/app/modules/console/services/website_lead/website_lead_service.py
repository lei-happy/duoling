"""
官网线索管理服务（Console）
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.console.models.system.user import User
from app.modules.console.schemas.website_lead.website_lead import (
    WebsiteLeadFollowIn,
    WebsiteLeadOut,
)
from app.modules.open.models.website_lead import WebsiteLead

# 已联系及之后的状态都算"接触过"，用于补首次联系时间
_CONTACTED_STATUSES = {1, 2}


def _parse_profile(raw: Optional[str]) -> Optional[Dict[str, str]]:
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return None
    return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else None


def _to_out(row: WebsiteLead) -> WebsiteLeadOut:
    return WebsiteLeadOut(
        id=row.id,
        company_name=row.company_name,
        contact_person=row.contact_person,
        contact_phone=row.contact_phone,
        fleet_size=row.fleet_size,
        pain_point=row.pain_point,
        profile_answers=_parse_profile(row.profile_answers),
        stage_band=row.stage_band,
        stage_name=row.stage_name,
        total_score=row.total_score,
        dim_a=row.dim_a,
        dim_b=row.dim_b,
        dim_c=row.dim_c,
        dim_d=row.dim_d,
        source_page=row.source_page,
        referrer=row.referrer,
        client_ip=row.client_ip,
        status=row.status,
        follow_remark=row.follow_remark,
        handler_id=row.handler_id,
        handler_name=row.handler_name,
        contacted_at=row.contacted_at,
        converted_tenant_code=row.converted_tenant_code,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


class WebsiteLeadService:
    """运营端官网线索服务"""

    @staticmethod
    def _base_query() -> Select:
        return select(WebsiteLead).where(WebsiteLead.is_deleted == 0)

    @staticmethod
    async def get_by_id(db: AsyncSession, lead_id: int) -> Optional[WebsiteLead]:
        result = await db.execute(
            select(WebsiteLead).where(
                WebsiteLead.id == lead_id,
                WebsiteLead.is_deleted == 0,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_leads(
        db: AsyncSession,
        *,
        page: int = 1,
        limit: int = 20,
        status: Optional[int] = None,
        stage_band: Optional[str] = None,
        fleet_size: Optional[str] = None,
        keyword: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
    ) -> Tuple[List[WebsiteLeadOut], int]:
        query = WebsiteLeadService._base_query()
        if status is not None:
            query = query.where(WebsiteLead.status == status)
        if stage_band:
            query = query.where(WebsiteLead.stage_band == stage_band)
        if fleet_size:
            query = query.where(WebsiteLead.fleet_size == fleet_size)
        if keyword:
            like = f"%{keyword.strip()}%"
            query = query.where(
                or_(
                    WebsiteLead.company_name.like(like),
                    WebsiteLead.contact_person.like(like),
                    WebsiteLead.contact_phone.like(like),
                )
            )
        if created_from is not None:
            query = query.where(WebsiteLead.created_at >= created_from)
        if created_to is not None:
            query = query.where(WebsiteLead.created_at <= created_to)

        total = (
            await db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0

        rows = list(
            (
                await db.execute(
                    query.order_by(WebsiteLead.id.desc())
                    .offset((page - 1) * limit)
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        return [_to_out(r) for r in rows], total

    @staticmethod
    async def get_detail(db: AsyncSession, lead_id: int) -> WebsiteLeadOut:
        row = await WebsiteLeadService.get_by_id(db, lead_id)
        if not row:
            raise BizException("找不到这条线索")
        return _to_out(row)

    @staticmethod
    async def follow_lead(
        db: AsyncSession,
        lead_id: int,
        data: WebsiteLeadFollowIn,
        *,
        handler_id: int,
        handler_name: Optional[str],
    ) -> WebsiteLeadOut:
        row = await WebsiteLeadService.get_by_id(db, lead_id)
        if not row:
            raise BizException("找不到这条线索")

        row.status = int(data.status)
        if data.follow_remark is not None:
            row.follow_remark = (data.follow_remark or "").strip() or None
        if data.converted_tenant_code is not None:
            row.converted_tenant_code = (
                data.converted_tenant_code or ""
            ).strip() or None

        # 第一次标为已联系时补上时间，之后再改状态不覆盖
        if row.status in _CONTACTED_STATUSES and row.contacted_at is None:
            row.contacted_at = datetime.now()

        row.handler_id = int(handler_id)
        row.handler_name = (handler_name or "").strip() or None

        await db.flush()
        await db.refresh(row)
        return _to_out(row)

    @staticmethod
    async def resolve_handler_name(db: AsyncSession, user_id: int) -> Optional[str]:
        result = await db.execute(
            select(User.real_name, User.phone).where(
                User.id == user_id,
                User.is_deleted == 0,
            )
        )
        pair = result.one_or_none()
        if not pair:
            return None
        real_name, phone = pair
        return (real_name or "").strip() or phone
