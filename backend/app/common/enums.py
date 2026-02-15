"""
枚举常量定义
"""

from enum import IntEnum, Enum


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
