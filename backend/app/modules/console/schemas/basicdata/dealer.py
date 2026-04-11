"""
Console 平台经销商 Schemas
"""

from typing import Optional

from app.common.schemas.dealer import (
    DealerCreateBase,
    DealerOutBase,
    DealerUpdateBase as DealerUpdate,
)


class DealerCreate(DealerCreateBase):
    autohomeDealerId: Optional[int] = None


class DealerOut(DealerOutBase):
    autohomeDealerId: Optional[int] = None

    @classmethod
    def from_model(cls, m) -> "DealerOut":
        base = DealerOutBase.from_model(m)
        return cls(
            **base.model_dump(),
            autohomeDealerId=getattr(m, "autohome_dealer_id", None),
        )


__all__ = ["DealerCreate", "DealerUpdate", "DealerOut"]
