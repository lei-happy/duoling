"""
租户业务库 ORM 模型

模型通过 __table_tier__ 属性标记所属层级：
  - "core"     : 注册即创建（基础设施层）
  - "business" : 版本开通时创建（业务表）
  - "premium"  : 高级版本开通时创建（版本功能表）
"""

# ---- Tier 1: Core (注册即创建) ----
from app.modules.client.models.user.biz_user import BizUser
from app.modules.client.models.role.biz_role import BizRole
from app.modules.client.models.organization.biz_department import BizDepartment
from app.modules.client.models.user.biz_user_role import BizUserRole
from app.modules.client.models.role.biz_role_menu import BizRoleMenu
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.vehicle_basic.biz_vehicle_brand import BizVehicleBrand
from app.modules.client.models.vehicle_basic.biz_vehicle_series import BizVehicleSeries
from app.modules.client.models.vehicle_basic.biz_dealer import BizDealer
from app.modules.client.models.biz_operation_log import BizOperationLog
from app.modules.client.models.biz_login_log import BizLoginLog
from app.modules.client.models.biz_dict import BizDict, BizDictItem
from app.modules.client.models.system_config import SystemConfig

# ---- Tier 2: Business (版本开通时创建) ----
from app.modules.client.models.workbench.company_activity import BizCompanyActivity
from app.modules.client.models.capacity.self_capacity import (
    Vehicle,
    VehicleExt,
    Trailer,
    TrailerExt,
    Capacity,
    CapacityLog,
    Driver,
    DriverLicense,
    DriverOperation,
    DriverAccount,
    DriverRoute,
)
from app.modules.client.models.capacity.social_capacity import (
    SocialCapacity,
    SocialCapacityDriver,
    SocialCapacityVehicle,
    SocialCapacityAccount,
    SocialCapacityAudit,
)
from app.modules.client.models.capacity.carrier_capacity import (
    CarrierCapacity,
    CarrierCapacityVehicle,
    CarrierCapacityDriver,
)
from app.modules.client.models.compliance import BizComplianceAlert
from app.modules.client.models.route import Route
from app.modules.client.models.partner.customer import Customer
from app.modules.client.models.partner.carrier import Carrier
from app.modules.client.models.partner.carrier_settlement import CarrierSettlement
from app.modules.client.models.partner.carrier_invitation import CarrierInvitation
from app.modules.client.models.billing.freight_contract import FreightContract
from app.modules.client.models.billing.freight_rate import FreightRate
from app.modules.client.models.billing.freight_calc_result import (
    WaybillFreightResult,
    WaybillFreightResultDetail,
)
from app.modules.client.models.billing.freight_calc_task import FreightCalcTask
from app.modules.client.models.billing.freight_calc_exception import FreightCalcException
from app.modules.client.models.billing.freight_rate_change_log import FreightRateChangeLog
from app.modules.client.models.billing.region_alias import RegionAlias
from app.modules.client.models.billing.vehicle_alias import VehicleAlias
from app.modules.client.models.waybill.waybill import Waybill
from app.modules.client.models.waybill.waybill_cargo import WaybillCargo
from app.modules.client.models.waybill.waybill_receipt import WaybillReceipt
from app.modules.client.models.waybill.waybill_import import (
    WaybillImportBatch,
    WaybillImportRow,
)
from app.modules.client.models.task import (
    Task,
    TaskDispatchOrder,
    TaskWaybillItem,
    TaskLoadingRecord,
    TaskLoadingRecordItem,
    TaskFinanceDoc,
    TaskFinanceItem,
)
from app.modules.client.models.approval import (
    ApprovalFlow,
    ApprovalFlowNode,
    ApprovalFlowVersionLog,
    ApprovalInstance,
    ApprovalInstanceNode,
    ApprovalTask,
    ApprovalRecord,
    ApprovalCc,
)

# ---- Tier 2: Business - AI 数字员工（biz_ai_*） ----
from app.modules.ai.models.tenant.biz_ai_session import BizAiSession
from app.modules.ai.models.tenant.biz_ai_message import BizAiMessage
from app.modules.ai.models.tenant.biz_ai_tool_call_log import BizAiToolCallLog
from app.modules.ai.models.tenant.biz_ai_context import BizAiContext

__all__ = [
    # Core
    "BizUser",
    "BizRole",
    "BizDepartment",
    "BizUserRole",
    "BizRoleMenu",
    "BizRegion",
    "BizVehicleBrand",
    "BizVehicleSeries",
    "BizDealer",
    "BizOperationLog",
    "BizLoginLog",
    "BizDict",
    "BizDictItem",
    "SystemConfig",
    # Business
    "Vehicle",
    "VehicleExt",
    "Trailer",
    "TrailerExt",
    "Driver",
    "DriverLicense",
    "DriverOperation",
    "DriverAccount",
    "DriverRoute",
    "Route",
    "Customer",
    "Carrier",
    "CarrierSettlement",
    "CarrierInvitation",
    "FreightContract",
    "FreightRate",
    "WaybillFreightResult",
    "WaybillFreightResultDetail",
    "FreightCalcTask",
    "FreightCalcException",
    "FreightRateChangeLog",
    "RegionAlias",
    "VehicleAlias",
    "Waybill",
    "WaybillCargo",
    "WaybillReceipt",
    "WaybillImportBatch",
    "WaybillImportRow",
    "Task",
    "TaskDispatchOrder",
    "TaskWaybillItem",
    "TaskLoadingRecord",
    "TaskLoadingRecordItem",
    "TaskFinanceDoc",
    "TaskFinanceItem",
    "ApprovalFlow",
    "ApprovalFlowNode",
    "ApprovalFlowVersionLog",
    "ApprovalInstance",
    "ApprovalInstanceNode",
    "ApprovalTask",
    "ApprovalRecord",
    "ApprovalCc",
    "Capacity",
    "CapacityLog",
    "SocialCapacity",
    "SocialCapacityDriver",
    "SocialCapacityVehicle",
    "SocialCapacityAccount",
    "SocialCapacityAudit",
    "CarrierCapacity",
    "CarrierCapacityVehicle",
    "CarrierCapacityDriver",
    "BizComplianceAlert",
    "BizCompanyActivity",
    # AI 数字员工（biz_ai_*）
    "BizAiSession",
    "BizAiMessage",
    "BizAiToolCallLog",
    "BizAiContext",
]
