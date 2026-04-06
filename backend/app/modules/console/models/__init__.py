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
from app.modules.console.models.changelog.changelog import Changelog
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
from app.modules.console.models.system.platform_setting import PlatformSetting

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
    "PlatformSetting",
]
