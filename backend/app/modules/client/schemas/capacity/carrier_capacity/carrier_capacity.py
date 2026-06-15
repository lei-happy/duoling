"""
承运商运力 Schema（含车辆 / 司机详情合并提交）

前端把基础信息 + 车辆 + 司机合并在一个请求体提交，Service 层拆分写入
biz_carrier_capacity / _vehicle / _driver 三张表。
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel


class CarrierCapacityVehicleInfo(BaseModel):
    """车辆信息（与 biz_carrier_capacity_vehicle 对应）"""

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


class CarrierCapacityDriverInfo(BaseModel):
    """司机信息（与 biz_carrier_capacity_driver 对应）"""

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


class CarrierCapacityCreate(BaseModel):
    """新增承运商运力"""

    carrierId: int
    source: Optional[str] = None
    sourceRemark: Optional[str] = None
    remark: Optional[str] = None
    vehicle: CarrierCapacityVehicleInfo
    driver: CarrierCapacityDriverInfo


class CarrierCapacityUpdate(BaseModel):
    """编辑承运商运力"""

    carrierId: Optional[int] = None
    source: Optional[str] = None
    sourceRemark: Optional[str] = None
    remark: Optional[str] = None
    vehicle: Optional[CarrierCapacityVehicleInfo] = None
    driver: Optional[CarrierCapacityDriverInfo] = None


class CarrierCapacityStatusUpdate(BaseModel):
    """启用状态变更"""

    status: int
    statusRemark: Optional[str] = None


class CarrierCapacityListItem(BaseModel):
    """列表项"""

    id: int
    carrierCapacityCode: str
    carrierId: int
    carrierName: Optional[str] = None
    driverName: str
    driverPhone: str
    plateNumber: str
    vehicleTypeLabel: Optional[str] = None
    approvalStatus: int
    status: int
    createdAt: Optional[datetime] = None


class CarrierCapacityDetail(BaseModel):
    """详情（含车辆 / 司机）"""

    id: int
    carrierCapacityCode: str
    carrierId: int
    carrierName: Optional[str] = None
    driverName: str
    driverPhone: str
    driverIdCard: Optional[str] = None
    plateNumber: str
    vehicleTypeLabel: Optional[str] = None
    source: Optional[str] = None
    sourceRemark: Optional[str] = None
    approvalStatus: int
    status: int
    statusRemark: Optional[str] = None
    remark: Optional[str] = None
    createdAt: Optional[datetime] = None
    vehicle: Optional[CarrierCapacityVehicleInfo] = None
    driver: Optional[CarrierCapacityDriverInfo] = None


class CarrierCapacityPage(BaseModel):
    list: List[CarrierCapacityListItem]
    total: int
    page: int
    page_size: int
