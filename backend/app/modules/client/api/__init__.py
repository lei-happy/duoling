"""
客户端业务模块路由汇总
Client 端的 API，服务于客户端产品（Web + 小程序）
"""

from fastapi import APIRouter

from app.modules.client.api.auth import router as auth_router
from app.modules.client.api.organization import router as dept_router
from app.modules.client.api.user import router as user_router
from app.modules.client.api.role import router as role_router
from app.modules.client.api.dict import router as dict_router
from app.modules.client.api.dict_data import router as dict_data_router
from app.modules.client.api.vehicle import router as vehicle_router
from app.modules.client.api.trailer import router as trailer_router
from app.modules.client.api.driver import router as driver_router
from app.modules.client.api.customer import router as customer_router
from app.modules.client.api.route import router as route_router
from app.modules.client.api.order import router as order_router
from app.modules.client.api.operation_record import router as operation_record_router
from app.modules.client.api.region import router as region_router
from app.modules.client.api.enterprise import router as enterprise_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["客户端-认证"])
router.include_router(dept_router, prefix="/system/organization", tags=["客户端-组织架构"])
router.include_router(user_router, prefix="/system/user", tags=["客户端-员工管理"])
router.include_router(role_router, prefix="/system/role", tags=["客户端-角色管理"])
router.include_router(dict_router, prefix="/system/dictionary", tags=["客户端-数据字典"])
router.include_router(dict_data_router, prefix="/system/dictionary-data", tags=["客户端-字典数据"])
router.include_router(vehicle_router, prefix="/resource/vehicle", tags=["客户端-车辆管理"])
router.include_router(trailer_router, prefix="/resource/trailer", tags=["客户端-挂车管理"])
router.include_router(driver_router, prefix="/resource/driver", tags=["客户端-驾驶员管理"])
router.include_router(customer_router, prefix="/resource/customer", tags=["客户端-客户管理"])
router.include_router(route_router, prefix="/resource/route", tags=["客户端-路线管理"])
router.include_router(order_router, prefix="/business/order", tags=["客户端-运单管理"])
router.include_router(operation_record_router, prefix="/system/operation-record", tags=["客户端-操作记录"])
router.include_router(region_router, prefix="/basic-data/region", tags=["客户端-地区数据"])
router.include_router(enterprise_router, prefix="/enterprise", tags=["客户端-企业管理"])
