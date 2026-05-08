"""
开放接口模块路由汇总
无需认证的公开 API
"""

from fastapi import APIRouter

from app.modules.open.api.register import router as register_router
from app.modules.open.api.product import router as product_router
from app.modules.open.api.changelog import router as changelog_router
from app.modules.open.api.sms import router as sms_router
from app.modules.open.api.carrier_invite import router as carrier_invite_router

router = APIRouter()

router.include_router(register_router, prefix="/register", tags=["开放-企业注册"])
router.include_router(product_router, prefix="/product", tags=["开放-产品信息"])
router.include_router(changelog_router, prefix="/changelog", tags=["开放-更新记录"])
router.include_router(sms_router, prefix="/sms", tags=["开放-短信验证码"])
router.include_router(
    carrier_invite_router, prefix="/carrier-invite", tags=["开放-承运商邀请激活"]
)
