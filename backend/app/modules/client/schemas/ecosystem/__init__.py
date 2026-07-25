"""服务平台相关 Schemas 统一导出"""

from app.modules.client.schemas.ecosystem.post import (
    CapacityFormRequest,
    CapacityPreviewRequest,
    CapacityPublishRequest,
    CargoFormRequest,
    CargoPreviewRequest,
    CargoPublishRequest,
    PostDelistRequest,
    PostExtendRequest,
    PostSubmitRequest,
)

__all__ = [
    "CargoFormRequest",
    "CargoPublishRequest",
    "CargoPreviewRequest",
    "CapacityFormRequest",
    "CapacityPublishRequest",
    "CapacityPreviewRequest",
    "PostDelistRequest",
    "PostSubmitRequest",
    "PostExtendRequest",
]
