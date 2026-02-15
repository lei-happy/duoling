"""
开放接口模块路由汇总
无需认证的公开 API
"""

from fastapi import APIRouter

from app.modules.open.api.register import router as register_router
from app.modules.open.api.product import router as product_router

router = APIRouter()

router.include_router(register_router, prefix="/register", tags=["开放-企业注册"])
router.include_router(product_router, prefix="/product", tags=["开放-产品信息"])
