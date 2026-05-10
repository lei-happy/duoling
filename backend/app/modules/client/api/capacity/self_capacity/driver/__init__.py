"""
自有运力-驾驶员管理 API 路由汇总
"""

from app.modules.client.api.capacity.self_capacity.driver.driver import router
from app.modules.client.api.capacity.self_capacity.driver.driver_account import (
    router as _account_router,
)
from app.modules.client.api.capacity.self_capacity.driver.driver_route import (
    router as _route_router,
)

router.include_router(_account_router)
router.include_router(_route_router)
