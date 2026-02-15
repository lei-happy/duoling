"""
客户端业务模块路由汇总
Client 端的 API，服务于客户端产品（Web + 小程序）
"""

from fastapi import APIRouter

from app.modules.client.api.auth import router as auth_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["客户端-认证"])

# 后续在此处注册更多业务路由
# router.include_router(vehicle_router, prefix="/vehicle", tags=["客户端-车辆管理"])
# router.include_router(driver_router, prefix="/driver", tags=["客户端-驾驶员管理"])
# router.include_router(order_router, prefix="/order", tags=["客户端-运单管理"])
