"""服务平台（货源大厅 / 运力大厅）API"""

from app.modules.client.api.ecosystem.hall import (
    capacity_hall_router,
    cargo_hall_router,
)
from app.modules.client.api.ecosystem.my_posts import router as eco_my_posts_router
from app.modules.client.api.ecosystem.publish import router as eco_publish_router

__all__ = [
    "cargo_hall_router",
    "capacity_hall_router",
    "eco_publish_router",
    "eco_my_posts_router",
]
