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
from app.modules.client.models.role.biz_menu import BizMenu
from app.modules.client.models.organization.biz_department import BizDepartment
from app.modules.client.models.user.biz_user_role import BizUserRole
from app.modules.client.models.role.biz_role_menu import BizRoleMenu
from app.modules.client.models.region.biz_region import BizRegion
from app.modules.client.models.biz_operation_log import BizOperationLog
from app.modules.client.models.biz_dict import BizDict, BizDictItem

# ---- Tier 2: Business (版本开通时创建) ----
from app.modules.client.models.vehicle import Vehicle
from app.modules.client.models.vehicle_ext import VehicleExt
from app.modules.client.models.trailer import Trailer
from app.modules.client.models.trailer_ext import TrailerExt
from app.modules.client.models.driver import Driver
from app.modules.client.models.order import Order
from app.modules.client.models.route import Route
from app.modules.client.models.customer import Customer

__all__ = [
    # Core
    "BizUser",
    "BizRole",
    "BizMenu",
    "BizDepartment",
    "BizUserRole",
    "BizRoleMenu",
    "BizRegion",
    "BizOperationLog",
    "BizDict",
    "BizDictItem",
    # Business
    "Vehicle",
    "VehicleExt",
    "Trailer",
    "TrailerExt",
    "Driver",
    "Order",
    "Route",
    "Customer",
]
