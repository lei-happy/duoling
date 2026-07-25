from app.modules.console.models.tenant.tenant import Tenant
from app.modules.console.models.system.user import User
from app.modules.console.models.system.user_tenant import UserTenant
from app.modules.console.models.system.role import Role
from app.modules.console.models.system.menu import Menu
from app.modules.console.models.system.permission import RoleMenu
from app.modules.console.models.system.user_role import UserRole
from app.modules.console.models.product.product_version import ProductVersion
from app.modules.console.models.tenant.tenant_product import TenantProduct
from app.modules.console.models.product.product_feature import ProductFeature, VersionFeature
from app.modules.console.models.changelog.changelog import Changelog, ChangelogRead
from app.modules.console.models.dictionary.dict_model import Dict, DictItem
from app.modules.console.models.common.feedback import Feedback
from app.modules.console.models.common.operation_log import OperationLog
from app.modules.console.models.sms.sms_code import SmsCode
from app.modules.console.models.region.sys_region import SysRegion
from app.modules.console.models.basicdata.basicdata_brand import BasicdataBrand
from app.modules.console.models.basicdata.basicdata_car_series import BasicdataCarSeries
from app.modules.console.models.basicdata.basicdata_dealer_info import BasicdataDealerInfo
from app.modules.console.models.todo.sys_todo_task import SysTodoTask
from app.modules.console.models.ops.autohome_sync_job import AutohomeSyncJob
from app.modules.console.models.ops.region_sync_job import RegionSyncJob
from app.modules.console.models.system.platform_setting import PlatformSetting
from app.modules.console.models.system.sensitive_word import SensitiveWord
from app.modules.console.models.driver.sys_driver import SysDriver
from app.modules.console.models.capacity.sys_capacity import SysCapacity
from app.modules.console.models.promotion.banner import (
    PromotionBanner,
    PromotionBannerEvent,
)

# ---- 服务平台（生态）撮合内核 ----
from app.modules.console.models.ecosystem import (
    SysEcoPost,
    SysEcoPostDest,
    SysEcoCargoPost,
    SysEcoCapacityPost,
    SysEcoPostAudit,
    SysEcoPostView,
    SysEcoIntent,
    SysEcoIntentMessage,
    SysEcoDeal,
    SysEcoDealMilestone,
    SysEcoEvaluation,
    SysEcoTenantProfile,
    SysEcoTenantCredit,
    SysEcoBlockRule,
    SysEcoSubscription,
    SysEcoReport,
)

# ---- AI 数字员工平台库元数据 ----
from app.modules.ai.models.platform.ai_employee import AiEmployee
from app.modules.ai.models.platform.ai_tool import AiTool
from app.modules.ai.models.platform.ai_employee_tool import AiEmployeeTool
from app.modules.ai.models.platform.ai_prompt_template import AiPromptTemplate
from app.modules.ai.models.platform.ai_model_provider import AiModelProvider

__all__ = [
    "Tenant",
    "User",
    "UserTenant",
    "Role",
    "Menu",
    "RoleMenu",
    "UserRole",
    "ProductVersion",
    "TenantProduct",
    "ProductFeature",
    "VersionFeature",
    "Changelog",
    "ChangelogRead",
    "Dict",
    "DictItem",
    "Feedback",
    "OperationLog",
    "SmsCode",
    "SysRegion",
    "BasicdataBrand",
    "BasicdataCarSeries",
    "BasicdataDealerInfo",
    "SysTodoTask",
    "AutohomeSyncJob",
    "RegionSyncJob",
    "PlatformSetting",
    "SensitiveWord",
    "SysDriver",
    "SysCapacity",
    "PromotionBanner",
    "PromotionBannerEvent",
    # 服务平台（生态）
    "SysEcoPost",
    "SysEcoPostDest",
    "SysEcoCargoPost",
    "SysEcoCapacityPost",
    "SysEcoPostAudit",
    "SysEcoPostView",
    "SysEcoIntent",
    "SysEcoIntentMessage",
    "SysEcoDeal",
    "SysEcoDealMilestone",
    "SysEcoEvaluation",
    "SysEcoTenantProfile",
    "SysEcoTenantCredit",
    "SysEcoBlockRule",
    "SysEcoSubscription",
    "SysEcoReport",
    # AI 数字员工
    "AiEmployee",
    "AiTool",
    "AiEmployeeTool",
    "AiPromptTemplate",
    "AiModelProvider",
]
