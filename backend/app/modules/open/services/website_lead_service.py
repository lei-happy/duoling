"""
官网留资服务

留资的价值就在低门槛，所以这里不加短信验证码——加了等于用转化率换防刷。
改成三层轻量防护：蜜罐字段、同手机号 24 小时限流、同 IP 1 小时限流。
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Optional

from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.open.models.website_lead import WebsiteLead
from app.modules.open.schemas.website_lead import LeadSubmitRequest

# 同一个手机号 24 小时内最多留几条：正常人改口重填一两次，脚本不止
_PHONE_LIMIT = 3
_PHONE_WINDOW_HOURS = 24

# 同一个出口 IP 1 小时内最多几条：照顾同公司多人从一个出口提交的情况
_IP_LIMIT = 10
_IP_WINDOW_HOURS = 1


class WebsiteLeadService:
    """官网留资写入"""

    @staticmethod
    async def _count_since(
        db: AsyncSession, column, value: str, hours: int
    ) -> int:
        since = datetime.now() - timedelta(hours=hours)
        result = await db.execute(
            select(func.count())
            .select_from(WebsiteLead)
            .where(column == value, WebsiteLead.created_at >= since)
        )
        return int(result.scalar() or 0)

    @staticmethod
    async def submit(
        db: AsyncSession,
        data: LeadSubmitRequest,
        *,
        client_ip: Optional[str],
        user_agent: Optional[str],
        referrer: Optional[str],
    ) -> bool:
        """
        写入一条线索。

        返回 False 表示被限流或判定为脚本提交。调用方对这两种情况和成功一样
        回「已收到」——把拦截逻辑告诉对方，等于教他怎么绕过去。
        """
        if (data.website or "").strip():
            logger.info("官网留资命中蜜罐，已丢弃 ip={}", client_ip)
            return False

        phone_count = await WebsiteLeadService._count_since(
            db, WebsiteLead.contact_phone, data.contact_phone, _PHONE_WINDOW_HOURS
        )
        if phone_count >= _PHONE_LIMIT:
            logger.info("官网留资手机号超频 phone={}", data.contact_phone)
            return False

        if client_ip:
            ip_count = await WebsiteLeadService._count_since(
                db, WebsiteLead.client_ip, client_ip, _IP_WINDOW_HOURS
            )
            if ip_count >= _IP_LIMIT:
                logger.info("官网留资 IP 超频 ip={}", client_ip)
                return False

        lead = WebsiteLead(
            company_name=data.company_name,
            contact_person=data.contact_person,
            contact_phone=data.contact_phone,
            fleet_size=data.fleet_size,
            pain_point=(data.pain_point or "").strip() or None,
            profile_answers=(
                json.dumps(data.profile_answers, ensure_ascii=False)
                if data.profile_answers
                else None
            ),
            stage_band=data.stage_band,
            stage_name=data.stage_name,
            total_score=data.total_score,
            dim_a=data.dim_a,
            dim_b=data.dim_b,
            dim_c=data.dim_c,
            dim_d=data.dim_d,
            source_page=data.source_page,
            referrer=(referrer or "")[:255] or None,
            client_ip=client_ip,
            user_agent=(user_agent or "")[:255] or None,
            status=0,
        )
        db.add(lead)
        await db.flush()
        logger.info(
            "官网留资已受理 id={} company={} stage={}",
            lead.id,
            lead.company_name,
            lead.stage_band,
        )
        return True
