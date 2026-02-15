"""
管理后台模块路由汇总
Console 端的所有 API（操作 zt_platform 库）
"""

from fastapi import APIRouter

from app.modules.console.api.auth import router as auth_router
from app.modules.console.api.tenant import router as tenant_router
from app.modules.console.api.user import router as user_router
from app.modules.console.api.product_version import router as product_version_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["管理后台-认证"])
router.include_router(tenant_router, prefix="/tenant", tags=["管理后台-租户管理"])
router.include_router(user_router, prefix="/user", tags=["管理后台-用户管理"])
router.include_router(product_version_router, prefix="/product-version", tags=["管理后台-产品版本"])

# 后续在此处注册更多管理后台路由
# router.include_router(role_router, prefix="/role", tags=["管理后台-角色管理"])
# router.include_router(menu_router, prefix="/menu", tags=["管理后台-菜单管理"])
# router.include_router(organization_router, prefix="/organization", tags=["管理后台-组织架构"])
# router.include_router(dict_router, prefix="/dict", tags=["管理后台-数据字典"])
# router.include_router(log_router, prefix="/log", tags=["管理后台-操作日志"])
