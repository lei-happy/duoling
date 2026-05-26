"""
社会运力池 Schema - 主体（含车辆/司机详情合并提交）

前端提交时把基础信息 + 车辆信息 + 司机信息合并在一个请求体中，
后端 Service 层负责拆分写入 biz_social_capacity / _vehicle / _driver 三张表。
结算账户通过独立接口管理。
"""

from typing import Optional, Any, List
from datetime import date, datetime
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# 子结构：车辆信息 / 司机信息
# ---------------------------------------------------------------------------
class SocialCapacityVehicleInfo(BaseModel):
    """车辆信息（与 biz_social_capacity_vehicle 对应）"""

    plateNumber: str
    plateCategory: Optional[str] = "YELLOW"
    vehicleType: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    engineNo: Optional[str] = None
    loadCapacity: Optional[float] = None
    volumeCapacity: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    axleCount: Optional[int] = None
    hasTrailer: Optional[int] = 0
    trailerPlate: Optional[str] = None
    trailerType: Optional[str] = None
    trailerLoadCapacity: Optional[float] = None
    registrationDate: Optional[date] = None
    inspectionExpire: Optional[date] = None
    insuranceExpire: Optional[date] = None
    transportLicenseNo: Optional[str] = None
    transportLicenseExpire: Optional[date] = None
    vehicleLicensePhoto: Optional[str] = None
    vehicleLicenseBackPhoto: Optional[str] = None
    transportLicensePhoto: Optional[str] = None
    vehiclePhoto: Optional[str] = None


class SocialCapacityDriverInfo(BaseModel):
    """司机信息（与 biz_social_capacity_driver 对应）"""

    name: str
    gender: Optional[int] = 0
    phone: str
    idCard: Optional[str] = None
    birthDate: Optional[date] = None
    avatar: Optional[str] = None
    licenseType: Optional[str] = None
    licenseNo: Optional[str] = None
    licenseIssueDate: Optional[date] = None
    licenseExpire: Optional[date] = None
    licenseClass: Optional[str] = None
    qualificationNo: Optional[str] = None
    qualificationExpire: Optional[date] = None
    licensePhoto: Optional[str] = None
    qualificationPhoto: Optional[str] = None
    idCardFrontPhoto: Optional[str] = None
    idCardBackPhoto: Optional[str] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    homeAddress: Optional[str] = None


# ---------------------------------------------------------------------------
# Create / Update
# ---------------------------------------------------------------------------
class SocialCapacityCreate(BaseModel):
    """创建社会运力（基础 + 车辆 + 司机）"""

    source: Optional[str] = None
    sourceRemark: Optional[str] = None
    referrerUserId: Optional[int] = None
    remark: Optional[str] = None
    vehicle: SocialCapacityVehicleInfo
    driver: SocialCapacityDriverInfo


class SocialCapacityUpdate(BaseModel):
    """更新社会运力（按审核状态控制可改字段，由 Service 层兜底校验）"""

    source: Optional[str] = None
    sourceRemark: Optional[str] = None
    referrerUserId: Optional[int] = None
    remark: Optional[str] = None
    vehicle: Optional[SocialCapacityVehicleInfo] = None
    driver: Optional[SocialCapacityDriverInfo] = None


# ---------------------------------------------------------------------------
# 状态动作 Schema
# ---------------------------------------------------------------------------
class SocialCapacityStatusUpdate(BaseModel):
    """启用 / 停用 / 黑名单切换"""

    status: int
    remark: Optional[str] = None


class SocialCapacityApproveAction(BaseModel):
    """审核通过"""

    remark: Optional[str] = None


class SocialCapacityRejectAction(BaseModel):
    """审核驳回（理由必填）"""

    remark: str


class SocialCapacitySubmitAction(BaseModel):
    """提交审核 / 撤回提交（备注可选）"""

    remark: Optional[str] = None


# ---------------------------------------------------------------------------
# 输出
# ---------------------------------------------------------------------------
class SocialCapacityAccountBrief(BaseModel):
    """主表输出中默认结算账户摘要"""

    id: int
    accountType: int
    accountLabel: Optional[str] = None
    accountName: str
    accountNo: str
    bankName: Optional[str] = None
    isDefault: int
    status: int


class SocialCapacityAuditBrief(BaseModel):
    """主表输出中最近一次审核 / 状态流水摘要"""

    id: int
    action: int
    beforeStatus: Optional[int] = None
    afterStatus: Optional[int] = None
    operatorUserId: int
    operatorName: Optional[str] = None
    remark: Optional[str] = None
    createdAt: datetime


class SocialCapacityListItem(BaseModel):
    """列表行（精简字段）"""

    id: int
    socialCode: str
    driverName: str
    driverPhone: str
    plateNumber: str
    plateCategory: Optional[str] = "YELLOW"
    vehicleTypeLabel: Optional[str] = None
    source: Optional[str] = None
    approvalStatus: int
    status: int
    ratingScore: Optional[float] = None
    ratingLevel: Optional[int] = None
    defaultAccount: Optional[SocialCapacityAccountBrief] = None
    createdAt: datetime
    updatedAt: datetime


class SocialCapacityDetail(BaseModel):
    """详情（含主体 + 车辆 + 司机 + 账户列表 + 最近一条流水）"""

    id: int
    socialCode: str
    driverName: str
    driverPhone: str
    driverIdCard: Optional[str] = None
    plateNumber: str
    vehicleTypeLabel: Optional[str] = None
    source: Optional[str] = None
    sourceRemark: Optional[str] = None
    referrerUserId: Optional[int] = None
    approvalStatus: int
    approvalUserId: Optional[int] = None
    approvalTime: Optional[datetime] = None
    approvalRemark: Optional[str] = None
    status: int
    statusRemark: Optional[str] = None
    ratingScore: Optional[float] = None
    ratingLevel: Optional[int] = None
    lastEvaluatedAt: Optional[datetime] = None
    evaluationSummary: Optional[Any] = None
    orderCount: int = 0
    lastDispatchedAt: Optional[datetime] = None
    createdUserId: Optional[int] = None
    updatedUserId: Optional[int] = None
    remark: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime
    vehicle: Optional[SocialCapacityVehicleInfo] = None
    driver: Optional[SocialCapacityDriverInfo] = None
    accounts: List[SocialCapacityAccountBrief] = []
    lastAudit: Optional[SocialCapacityAuditBrief] = None


class SocialCapacitySelectItem(BaseModel):
    """调度选择器输出（仅返回已通过 + 正常）"""

    id: int
    socialCode: str
    driverName: str
    driverPhone: str
    plateNumber: str
    vehicleType: Optional[str] = None
    loadCapacity: Optional[float] = None
    ratingLevel: Optional[int] = None
    defaultAccount: Optional[SocialCapacityAccountBrief] = None
