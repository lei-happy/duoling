"""
管理后台模块路由汇总
Console 端的所有 API（操作 zt_platform 库）
"""

from fastapi import APIRouter

from app.modules.console.api.auth import router as auth_router
from app.modules.console.api.tenant import router as tenant_router
from app.modules.console.api.system.user import router as user_router
from app.modules.console.api.system.menu import router as menu_router
from app.modules.console.api.system.role import router as role_router
from app.modules.console.api.system.role_menu import router as role_menu_router
from app.modules.console.api.system.organization import router as org_router
from app.modules.console.api.product.product_version import router as product_version_router
from app.modules.console.api.changelog import router as changelog_router
from app.modules.console.api.dictionary.dict import router as dict_router
from app.modules.console.api.dictionary.dict_data import router as dict_data_router
from app.modules.console.api.product.product_feature import router as product_feature_router
from app.modules.console.api.product.client_menu import router as client_menu_router
from app.modules.console.api.sms import router as sms_code_router
from app.modules.console.api.log_center import router as log_center_router
from app.modules.console.api.region import router as region_router
from app.modules.console.api.basicdata import (
    vehicle_brand_router,
    vehicle_series_router,
    dealer_router,
)
from app.modules.console.api.workbench.todo import router as workbench_todo_router
from app.modules.console.api.file import router as file_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["管理后台-认证"])
router.include_router(file_router, prefix="/file", tags=["管理后台-文件上传"])
router.include_router(tenant_router, prefix="/tenant", tags=["管理后台-租户管理"])
router.include_router(menu_router, prefix="/system/menu", tags=["菜单管理"])
router.include_router(user_router, prefix="/system/user", tags=["用户管理"])
router.include_router(role_router, prefix="/system/role", tags=["角色管理"])
router.include_router(role_menu_router, prefix="/system/role-menu", tags=["角色菜单"])
router.include_router(org_router, prefix="/system/organization", tags=["组织架构"])
router.include_router(product_version_router, prefix="/product-version", tags=["管理后台-产品版本"])
router.include_router(product_feature_router, prefix="/product-feature", tags=["管理后台-功能清单"])
router.include_router(changelog_router, prefix="/changelog", tags=["管理后台-更新记录"])
router.include_router(dict_router, prefix="/system/dictionary", tags=["数据字典"])
router.include_router(dict_data_router, prefix="/system/dictionary-data", tags=["字典数据"])
router.include_router(client_menu_router, prefix="/system/client-menu", tags=["客户端菜单管理"])
router.include_router(sms_code_router, prefix="/system/sms-code", tags=["短信验证码"])
router.include_router(log_center_router, prefix="/log-center", tags=["日志中心"])
router.include_router(region_router, prefix="/basic-data/region", tags=["管理后台-地区数据"])
router.include_router(
    vehicle_brand_router, prefix="/basic-data/vehicle-brand", tags=["管理后台-品牌"]
)
router.include_router(
    vehicle_series_router, prefix="/basic-data/vehicle-series", tags=["管理后台-车系"]
)
router.include_router(dealer_router, prefix="/basic-data/dealer", tags=["管理后台-经销商"])
router.include_router(workbench_todo_router, prefix="/workbench/todo", tags=["管理后台-待办查询"])
