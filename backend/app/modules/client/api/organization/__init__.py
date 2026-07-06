from app.modules.client.api.organization.department import router
from app.modules.client.api.organization.business_entity import (
    router as business_entity_router,
)

__all__ = ["router", "business_entity_router"]
