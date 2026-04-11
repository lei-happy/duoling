"""
租户端经销商 Schemas（字段名对齐前端 camelCase）
"""

from app.common.schemas.dealer import (
    DealerCreateBase as DealerCreate,
    DealerOutBase as DealerOut,
    DealerUpdateBase as DealerUpdate,
)

__all__ = ["DealerCreate", "DealerUpdate", "DealerOut"]
