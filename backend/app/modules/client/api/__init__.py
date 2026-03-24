"""
客户端业务模块路由汇总
Client 端的 API，服务于客户端产品（Web + 小程序）
"""

from fastapi import APIRouter

from app.modules.client.api.auth import router as auth_router
from app.modules.client.api.department import router as dept_router
from app.modules.client.api.user import router as user_router
from app.modules.client.api.role import router as role_router
from app.modules.client.api.dict import router as dict_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["客户端-认证"])
router.include_router(dept_router, prefix="/system/organization", tags=["客户端-组织架构"])
router.include_router(user_router, prefix="/system/user", tags=["客户端-员工管理"])
router.include_router(role_router, prefix="/system/role", tags=["客户端-角色管理"])
router.include_router(dict_router, prefix="/system/dictionary", tags=["客户端-数据字典"])
