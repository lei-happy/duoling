"""
枚举常量定义
"""

from enum import IntEnum, Enum
from typing import Iterable, List, Optional, Sequence, Union


class StatusEnum(IntEnum):
    """通用状态"""
    DISABLED = 0
    ENABLED = 1


class TenantStatusEnum(IntEnum):
    """租户状态"""
    DISABLED = 0       # 停用
    ENABLED = 1        # 正常
    PENDING = 2        # 待审核
    EXPIRED = 3        # 已过期


class UserTypeEnum(IntEnum):
    """用户类型"""
    PLATFORM_ADMIN = 0   # 平台管理员
    TENANT_ADMIN = 1     # 租户管理员
    TENANT_USER = 2      # 租户普通用户
    DRIVER = 3           # 驾驶员


class RolePersonaEnum(str, Enum):
    """小程序岗位视图。挂在 biz_role 上，只决定首页先看什么，不参与鉴权。"""

    DISPATCH = "dispatch"
    BOSS = "boss"
    FINANCE = "finance"
    CAPTAIN = "captain"


ROLE_PERSONA_VALUES = frozenset(item.value for item in RolePersonaEnum)
ROLE_PERSONA_ORDER = tuple(item.value for item in RolePersonaEnum)
ROLE_PERSONA_LABELS = {
    RolePersonaEnum.DISPATCH.value: "调度",
    RolePersonaEnum.BOSS.value: "老板",
    RolePersonaEnum.FINANCE.value: "财务",
    RolePersonaEnum.CAPTAIN.value: "车队长",
}
ADMIN_DEFAULT_PERSONA = RolePersonaEnum.BOSS.value


def normalize_role_personas(
    raw: Optional[Union[str, Sequence[object]]],
) -> List[str]:
    """把角色上的岗位字段收成有序去重列表；非法值丢弃。"""
    if raw is None:
        return []
    if isinstance(raw, str):
        values: Iterable[object] = [raw]
    elif isinstance(raw, (list, tuple)):
        values = raw
    else:
        return []
    seen = {
        item
        for item in values
        if isinstance(item, str) and item in ROLE_PERSONA_VALUES
    }
    return [key for key in ROLE_PERSONA_ORDER if key in seen]


class GenderEnum(IntEnum):
    """性别"""
    UNKNOWN = 0
    MALE = 1
    FEMALE = 2


class ProductVersionEnum(str, Enum):
    """产品版本"""
    BASIC = "basic"           # 基础版
    STANDARD = "standard"     # 标准版
    PROFESSIONAL = "pro"      # 专业版
    ENTERPRISE = "enterprise" # 企业版


class FeedbackStatusEnum(IntEnum):
    """意见反馈状态"""
    PENDING = 0     # 待处理
    PROCESSING = 1  # 处理中
    RESOLVED = 2    # 已解决
    CLOSED = 3      # 已关闭


class FeedbackTypeEnum(IntEnum):
    """意见反馈类型"""
    SUGGESTION = 0  # 建议
    BUG = 1         # 缺陷
    COMPLAINT = 2   # 投诉
    OTHER = 3       # 其他
