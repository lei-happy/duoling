"""
分页工具
"""

from typing import Any, Callable, List, Optional

from fastapi import Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select


class PageParams:
    """分页参数依赖"""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=200, description="每页条数"),
    ):
        self.page = page
        self.page_size = page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


async def paginate(
    db: AsyncSession,
    stmt: Select,
    page: int = 1,
    limit: int = 20,
    order_by=None,
    serializer: Optional[Callable] = None,
) -> dict:
    """
    通用异步分页查询助手

    :param db: 数据库 Session
    :param stmt: SQLAlchemy Select 语句（不含 offset/limit）
    :param page: 页码（从1开始）
    :param limit: 每页条数
    :param order_by: 排序列（如 Model.id.desc()）
    :param serializer: 行序列化函数，接收 ORM 实例返回 dict；为 None 时返回原始对象列表
    :return: {"list": [...], "count": total}
    """
    count_q = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    if order_by is not None:
        if isinstance(order_by, (list, tuple)):
            stmt = stmt.order_by(*order_by)
        else:
            stmt = stmt.order_by(order_by)
    stmt = stmt.offset((page - 1) * limit).limit(limit)

    result = await db.execute(stmt)
    rows = result.scalars().all()

    if serializer:
        items = [serializer(r) for r in rows]
    else:
        items = list(rows)

    return {"list": items, "count": total}
