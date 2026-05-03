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
from app.modules.client.api.operation_record import router as operation_record_router
from app.modules.client.api.login_record import router as login_record_router
from app.modules.client.api.region import router as region_router
from app.modules.client.api.basicdata import (
    vehicle_brand_router,
    vehicle_series_router,
    dealer_router,
)
from app.modules.client.api.enterprise import router as enterprise_router
from app.modules.client.api.file import router as file_router
from app.modules.client.api.workbench.todo import router as workbench_todo_router
from app.modules.client.api.system_config import router as system_config_router
from app.modules.client.api.partner.customer import router as partner_customer_router
from app.modules.client.api.billing.freight_contract import router as freight_contract_router
from app.modules.client.api.billing.freight_rate import router as freight_rate_router
from app.modules.client.api.billing.calculate import router as freight_calc_router
from app.modules.client.api.waybill.waybill import router as waybill_router
from app.modules.client.api.capacity import router as capacity_router
from app.modules.ai.api.client import router as ai_client_router

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
router.include_router(
    operation_record_router,
    prefix="/logcenter/operation-record",
    tags=["客户端-日志中心-操作记录"],
)
router.include_router(
    login_record_router,
    prefix="/logcenter/login-record",
    tags=["客户端-日志中心-登录记录"],
)
router.include_router(region_router, prefix="/basic-data/region", tags=["客户端-地区数据"])
router.include_router(
    vehicle_brand_router, prefix="/basic-data/vehicle-brand", tags=["客户端-品牌"]
)
router.include_router(
    vehicle_series_router, prefix="/basic-data/vehicle-series", tags=["客户端-车系"]
)
router.include_router(
    dealer_router, prefix="/basic-data/dealer", tags=["客户端-经销商"]
)
router.include_router(enterprise_router, prefix="/enterprise", tags=["客户端-企业管理"])
router.include_router(file_router, prefix="/file", tags=["客户端-文件管理"])
router.include_router(workbench_todo_router, prefix="/workbench/todo", tags=["客户端-工作台待办"])
router.include_router(system_config_router, prefix="/system/config", tags=["客户端-系统配置"])
router.include_router(partner_customer_router, prefix="/partner/customer", tags=["客户端-合作伙伴-客户"])
router.include_router(freight_contract_router, prefix="/billing/contract", tags=["客户端-运价合同"])
router.include_router(freight_rate_router, prefix="/billing/rate", tags=["客户端-运价费率"])
router.include_router(freight_calc_router, prefix="/billing/calculate", tags=["客户端-运费计算"])
router.include_router(waybill_router, prefix="/business/waybill", tags=["客户端-运单管理V2"])
router.include_router(capacity_router, prefix="/capacity", tags=["客户端-运力管理"])
router.include_router(ai_client_router, prefix="/ai", tags=["客户端-AI数字员工"])
