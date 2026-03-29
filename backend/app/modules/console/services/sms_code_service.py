"""
短信验证码记录查询（管理后台）
"""

from datetime import datetime, timedelta
from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.console.models.sms_code import SmsCode
from app.modules.console.schemas.sms_code import SmsCodeOut


def _fmt_dt(value: Optional[datetime]) -> str:
    if value is None:
        return ""
    return value.strftime("%Y-%m-%d %H:%M:%S")


def _parse_date_ymd(value: Optional[str]) -> Optional[datetime]:
    """兼容 YYYY-MM-DD 与带时间的字符串，取日期部分"""
    if not value or not value.strip():
        return None
    day = value.strip()[:10]
    return datetime.strptime(day, "%Y-%m-%d")


class SmsCodeService:
    """短信验证码查询"""

    @staticmethod
    def _to_out(row: SmsCode) -> SmsCodeOut:
        return SmsCodeOut(
            id=row.id,
            phone=row.phone,
            code=row.code,
            purpose=row.purpose,
            status=row.status,
            expireAt=_fmt_dt(row.expire_at),
            clientIp=row.client_ip,
            createdAt=_fmt_dt(row.created_at),
        )

    @staticmethod
    def _apply_filters(
        query,
        phone: Optional[str],
        purpose: Optional[int],
        status: Optional[int],
        create_time_start: Optional[str],
        create_time_end: Optional[str],
    ):
        if phone:
            query = query.where(SmsCode.phone.contains(phone))
        if purpose is not None:
            query = query.where(SmsCode.purpose == purpose)
        if status is not None:
            query = query.where(SmsCode.status == status)
        start = _parse_date_ymd(create_time_start)
        if start is not None:
            query = query.where(SmsCode.created_at >= start)
        end = _parse_date_ymd(create_time_end)
        if end is not None:
            query = query.where(SmsCode.created_at < end + timedelta(days=1))
        return query

    @staticmethod
    async def page_sms_codes(
        db: AsyncSession,
        page: int = 1,
        limit: int = 20,
        phone: Optional[str] = None,
        purpose: Optional[int] = None,
        status: Optional[int] = None,
        createTimeStart: Optional[str] = None,
        createTimeEnd: Optional[str] = None,
    ) -> dict:
        """分页查询"""
        query = select(SmsCode)
        query = SmsCodeService._apply_filters(
            query, phone, purpose, status, createTimeStart, createTimeEnd
        )

        count_q = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_q)
        count = total_result.scalar() or 0

        query = query.order_by(SmsCode.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        rows = result.scalars().all()

        return {
            "list": [SmsCodeService._to_out(r).model_dump() for r in rows],
            "count": count,
        }

    @staticmethod
    async def list_sms_codes(
        db: AsyncSession,
        phone: Optional[str] = None,
        purpose: Optional[int] = None,
        status: Optional[int] = None,
        createTimeStart: Optional[str] = None,
        createTimeEnd: Optional[str] = None,
        max_rows: int = 10000,
    ) -> List[SmsCodeOut]:
        """列表（导出等），最多 max_rows 条"""
        query = select(SmsCode)
        query = SmsCodeService._apply_filters(
            query, phone, purpose, status, createTimeStart, createTimeEnd
        )
        query = query.order_by(SmsCode.created_at.desc())
        query = query.limit(max_rows)
        result = await db.execute(query)
        rows = result.scalars().all()
        return [SmsCodeService._to_out(r) for r in rows]
