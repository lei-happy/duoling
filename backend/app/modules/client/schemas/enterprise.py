"""
企业管理相关 Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UpdateSystemNameRequest(BaseModel):
    """更新系统自定义名称"""
    systemName: Optional[str] = Field(
        default=None, max_length=12,
        description="系统自定义名称，最多12个字符，为空时恢复显示企业名称"
    )


class VersionInfo(BaseModel):
    """版本信息"""
    versionName: Optional[str] = Field(default=None, description="版本名称")
    versionCode: Optional[str] = Field(default=None, description="版本编码")
    maxUsers: Optional[int] = Field(default=None, description="最大用户数")
    maxVehicles: Optional[int] = Field(default=None, description="最大车辆数")
    startTime: Optional[datetime] = Field(default=None, description="授权开始时间")
    endTime: Optional[datetime] = Field(default=None, description="授权到期时间")


class EnterpriseInfoOut(BaseModel):
    """企业信息输出"""
    tenantName: str = Field(description="企业名称")
    systemName: Optional[str] = Field(default=None, description="系统自定义名称")
    contactPerson: Optional[str] = Field(default=None, description="联系人")
    contactPhone: Optional[str] = Field(default=None, description="联系电话")
    version: Optional[VersionInfo] = Field(default=None, description="当前版本信息")
