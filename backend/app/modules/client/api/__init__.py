"""
客户端业务模块路由汇总
Client 端的 API，服务于客户端产品（Web + 小程序）
"""

from fastapi import APIRouter, Depends

from app.core.permissions import require_feature
from app.modules.client.api.auth import router as auth_router
from app.modules.client.api.organization import router as dept_router
from app.modules.client.api.organization import (
    business_entity_router as business_entity_router,
)
from app.modules.client.api.user import router as user_router
from app.modules.client.api.role import router as role_router
from app.modules.client.api.dict import router as dict_router
from app.modules.client.api.dict_data import router as dict_data_router
from app.modules.client.api.capacity.self_capacity.vehicle import router as self_vehicle_router
from app.modules.client.api.capacity.self_capacity.trailer import router as self_trailer_router
from app.modules.client.api.capacity.self_capacity.driver import router as self_driver_router
from app.modules.client.api.capacity.self_capacity.list import router as self_capacity_list_router
from app.modules.client.api.capacity.self_capacity.log import router as self_capacity_log_router
from app.modules.client.api.capacity.carrier_capacity.list import router as carrier_capacity_list_router
from app.modules.client.api.capacity.carrier_capacity.approval import router as carrier_capacity_approval_router
from app.modules.client.api.capacity.social_capacity.list import router as social_capacity_list_router
from app.modules.client.api.capacity.social_capacity.approval import router as social_capacity_approval_router
from app.modules.client.api.capacity.compliance.alerts import router as compliance_alert_router
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
from app.modules.client.api.workbench.activities import router as workbench_activities_router
from app.modules.client.api.workbench.banner import router as workbench_banner_router
from app.modules.client.api.workbench.changelog import router as workbench_changelog_router
from app.modules.client.api.system_config import router as system_config_router
from app.modules.client.api.partner.customer import router as partner_customer_router
from app.modules.client.api.partner.carrier import router as partner_carrier_router
from app.modules.client.api.partner.carrier_inbound import router as partner_inbound_router
from app.modules.client.api.billing.freight_contract import router as freight_contract_router
from app.modules.client.api.billing.freight_rate import router as freight_rate_router
from app.modules.client.api.billing.calculate import router as freight_calc_router
from app.modules.client.api.billing.freight_engine import (
    task_router as freight_calc_task_router,
    exception_router as freight_calc_exception_router,
    region_alias_router as basic_data_region_alias_router,
    vehicle_alias_router as basic_data_vehicle_alias_router,
    regression_router as freight_calc_regression_router,
)
from app.modules.client.api.billing.cost_policy import router as cost_policy_router
from app.modules.client.api.billing.cost_rule import router as cost_rule_router
from app.modules.client.api.billing.task_cost import router as task_cost_router
from app.modules.client.api.billing.cost_engine import (
    task_router as cost_calc_task_router,
    exception_router as cost_calc_exception_router,
)
from app.modules.client.api.billing.carrier_contract import (
    router as carrier_contract_router,
)
from app.modules.client.api.billing.carrier_rate import (
    router as carrier_rate_router,
)
from app.modules.client.api.billing.carrier_freight import (
    router as carrier_freight_router,
)
from app.modules.client.api.billing.carrier_freight_engine import (
    task_router as carrier_freight_task_router,
    exception_router as carrier_freight_exception_router,
)
from app.modules.client.api.waybill.waybill import router as waybill_router
from app.modules.client.api.task import (
    task_router,
    task_finance_router,
    smart_stowage_router,
)
from app.modules.client.api.insight.cockpit import router as insight_cockpit_router
from app.modules.client.api.insight.profit import router as insight_profit_router
from app.modules.client.api.approval import router as approval_router
from app.modules.ai.api.client import router as ai_client_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["客户端-认证"])
router.include_router(dept_router, prefix="/system/organization", tags=["客户端-组织架构"])
router.include_router(
    business_entity_router,
    prefix="/system/business-entity",
    tags=["客户端-经营主体"],
)
router.include_router(user_router, prefix="/system/user", tags=["客户端-员工管理"])
router.include_router(role_router, prefix="/system/role", tags=["客户端-角色管理"])
router.include_router(dict_router, prefix="/system/dictionary", tags=["客户端-数据字典"])
router.include_router(dict_data_router, prefix="/system/dictionary-data", tags=["客户端-字典数据"])
router.include_router(
    self_capacity_list_router,
    prefix="/capacity/self_capacity/list",
    tags=["客户端-自有运力-运力列表"],
    dependencies=[Depends(require_feature("capacity_self_list"))],
)
router.include_router(
    self_capacity_log_router,
    prefix="/capacity/self_capacity/log",
    tags=["客户端-自有运力-变更记录"],
    dependencies=[Depends(require_feature("capacity_self_log"))],
)
router.include_router(
    self_vehicle_router,
    prefix="/capacity/self_capacity/vehicle",
    tags=["客户端-自有运力-车辆管理"],
    dependencies=[Depends(require_feature("capacity_self_vehicle"))],
)
router.include_router(
    self_trailer_router,
    prefix="/capacity/self_capacity/trailer",
    tags=["客户端-自有运力-挂车管理"],
    dependencies=[Depends(require_feature("capacity_self_trailer"))],
)
router.include_router(
    self_driver_router,
    prefix="/capacity/self_capacity/driver",
    tags=["客户端-自有运力-驾驶员管理"],
    dependencies=[Depends(require_feature("capacity_self_driver"))],
)
router.include_router(
    carrier_capacity_list_router,
    prefix="/capacity/carrier_capacity/list",
    tags=["客户端-承运商运力-列表"],
    dependencies=[Depends(require_feature("capacity_carrier_list"))],
)
router.include_router(
    carrier_capacity_approval_router,
    prefix="/capacity/carrier_capacity/approval",
    tags=["客户端-承运商运力-审批"],
    dependencies=[Depends(require_feature("capacity_carrier_approval"))],
)
router.include_router(
    social_capacity_list_router,
    prefix="/capacity/social_capacity/list",
    tags=["客户端-社会运力池-档案"],
    dependencies=[Depends(require_feature("capacity_social_list"))],
)
router.include_router(
    social_capacity_approval_router,
    prefix="/capacity/social_capacity/approval",
    tags=["客户端-社会运力池-审批"],
    dependencies=[Depends(require_feature("capacity_social_approval"))],
)
router.include_router(
    compliance_alert_router,
    prefix="/capacity/compliance/alerts",
    tags=["客户端-证照监控-到期预警"],
    dependencies=[Depends(require_feature("fleet_compliance"))],
)
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
router.include_router(
    workbench_activities_router,
    prefix="/workbench/activities",
    tags=["客户端-工作台最新动态"],
)
router.include_router(
    workbench_banner_router,
    prefix="/workbench/banner",
    tags=["客户端-工作台推广位Banner"],
)
router.include_router(
    workbench_changelog_router,
    prefix="/workbench/changelog",
    tags=["客户端-工作台版本升级说明"],
)
router.include_router(system_config_router, prefix="/system/config", tags=["客户端-系统配置"])
router.include_router(partner_customer_router, prefix="/partner/customer", tags=["客户端-合作伙伴-客户"])
router.include_router(partner_carrier_router, prefix="/partner/carrier", tags=["客户端-合作伙伴-承运商"])
router.include_router(partner_inbound_router, prefix="/partner/inbound", tags=["客户端-合作伙伴-合作客户(反向)"])
router.include_router(freight_contract_router, prefix="/billing/contract", tags=["客户端-运价合同"])
router.include_router(freight_rate_router, prefix="/billing/rate", tags=["客户端-运价费率"])
router.include_router(freight_calc_router, prefix="/billing/calculate", tags=["客户端-运费计算"])
router.include_router(
    freight_calc_task_router,
    prefix="/billing/freight-calc/tasks",
    tags=["客户端-计费引擎-任务"],
)
router.include_router(
    freight_calc_exception_router,
    prefix="/billing/freight-calc/exceptions",
    tags=["客户端-计费引擎-异常"],
)
router.include_router(
    basic_data_region_alias_router,
    prefix="/basic-data/region-alias",
    tags=["客户端-基础数据-地名别名"],
)
router.include_router(
    basic_data_vehicle_alias_router,
    prefix="/basic-data/vehicle-alias",
    tags=["客户端-基础数据-车型别名"],
)
router.include_router(
    freight_calc_regression_router,
    prefix="/billing/freight-calc/regression",
    tags=["客户端-计费引擎-双引擎回归"],
)
router.include_router(
    cost_policy_router,
    prefix="/billing/cost-policy",
    tags=["客户端-成本政策"],
    dependencies=[Depends(require_feature("billing_cost_rule"))],
)
router.include_router(
    cost_rule_router,
    prefix="/billing/cost-rule",
    tags=["客户端-成本费用规则"],
    dependencies=[Depends(require_feature("billing_cost_rule"))],
)
router.include_router(
    task_cost_router,
    prefix="/billing",
    tags=["客户端-任务成本计算"],
    dependencies=[Depends(require_feature("billing_cost_rule"))],
)
router.include_router(
    cost_calc_task_router,
    prefix="/billing/cost-calc/tasks",
    tags=["客户端-成本引擎-任务"],
    dependencies=[Depends(require_feature("billing_cost_rule"))],
)
router.include_router(
    cost_calc_exception_router,
    prefix="/billing/cost-calc/exceptions",
    tags=["客户端-成本引擎-异常"],
    dependencies=[Depends(require_feature("billing_cost_rule"))],
)
router.include_router(
    carrier_contract_router,
    prefix="/billing/carrier-contract",
    tags=["客户端-承运商合同"],
    dependencies=[Depends(require_feature("billing_carrier_freight"))],
)
router.include_router(
    carrier_rate_router,
    prefix="/billing/carrier-rate",
    tags=["客户端-承运价规则"],
    dependencies=[Depends(require_feature("billing_carrier_freight"))],
)
router.include_router(
    carrier_freight_router,
    prefix="/billing",
    tags=["客户端-承运商运费计算"],
    dependencies=[Depends(require_feature("billing_carrier_freight"))],
)
router.include_router(
    carrier_freight_task_router,
    prefix="/billing/carrier-freight-calc/tasks",
    tags=["客户端-承运运费引擎-任务"],
    dependencies=[Depends(require_feature("billing_carrier_freight"))],
)
router.include_router(
    carrier_freight_exception_router,
    prefix="/billing/carrier-freight-calc/exceptions",
    tags=["客户端-承运运费引擎-异常"],
    dependencies=[Depends(require_feature("billing_carrier_freight"))],
)
router.include_router(waybill_router, prefix="/business/waybill", tags=["客户端-运单管理V2"])
router.include_router(task_router, prefix="/business/task", tags=["客户端-运输任务单"])
router.include_router(
    task_finance_router,
    prefix="/business/task-finance",
    tags=["客户端-任务单财务费用"],
)
router.include_router(
    smart_stowage_router,
    prefix="/business/smart-stowage",
    tags=["客户端-智能配载"],
    dependencies=[Depends(require_feature("smart_stowage"))],
)
router.include_router(
    insight_cockpit_router,
    prefix="/insight/cockpit",
    tags=["客户端-数据洞察-经营驾驶舱"],
)
router.include_router(
    insight_profit_router,
    prefix="/insight/cockpit/profit",
    tags=["客户端-数据洞察-利润总览"],
)
router.include_router(approval_router, prefix="/approval", tags=["客户端-审批中心"])
router.include_router(ai_client_router, prefix="/ai", tags=["客户端-AI数字员工"])
