"""能源中心单号 / 编码生成"""

from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def next_code(db: AsyncSession, model, field_name: str, prefix: str, width: int = 4) -> str:
    col = getattr(model, field_name)
    head = f"{prefix}{date.today().strftime('%Y%m%d')}"
    r = await db.execute(select(func.max(col)).where(col.like(f"{head}%")))
    last = r.scalar()
    seq = 1
    if last:
        try:
            seq = int(str(last)[len(head):]) + 1
        except (TypeError, ValueError):
            seq = 1
    return f"{head}{seq:0{width}d}"
