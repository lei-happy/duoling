"""运营后台-服务平台路由汇总"""

from app.modules.console.api.ecosystem.audit import router as eco_audit_router
from app.modules.console.api.ecosystem.whitelist import (
    router as eco_whitelist_router,
)

__all__ = ["eco_audit_router", "eco_whitelist_router"]
