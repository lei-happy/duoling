"""
驾驶员管理 API 路由汇总
"""

from app.modules.client.api.driver.driver import router
from app.modules.client.api.driver.driver_account import router as _account_router
from app.modules.client.api.driver.driver_route import router as _route_router

router.include_router(_account_router)
router.include_router(_route_router)
