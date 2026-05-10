"""
驾驶员管理 Schemas

前端提交时核心字段、资质字段和运营字段合并在一个请求体中，
后端 Service 层负责拆分写入 biz_driver / biz_driver_license / biz_driver_operation 三张表。
账户信息通过独立接口管理。
"""

from typing import Optional, Any
from datetime import date, datetime
from pydantic import BaseModel


class DriverCreate(BaseModel):
    """创建驾驶员（核心+资质+运营字段合并提交）"""
    # 核心身份
    name: str
    gender: Optional[int] = 0
    phone: str
    idCard: Optional[str] = None
    avatar: Optional[str] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    homeAddress: Optional[str] = None
    remark: Optional[str] = None
    # 资质信息
    licenseType: Optional[str] = None
    licenseNo: Optional[str] = None
    licenseExpire: Optional[date] = None
    qualificationNo: Optional[str] = None
    qualificationExpire: Optional[date] = None
    licensePhoto: Optional[str] = None
    qualificationPhoto: Optional[str] = None
    idCardFrontPhoto: Optional[str] = None
    idCardBackPhoto: Optional[str] = None
    # 运营属性
    departmentId: Optional[int] = None
    driverType: Optional[str] = None
    residentAreas: Optional[Any] = None
    commonRoutes: Optional[str] = None
    operationStatus: Optional[int] = 1


class DriverUpdate(BaseModel):
    """更新驾驶员"""
    # 核心身份
    name: Optional[str] = None
    gender: Optional[int] = None
    phone: Optional[str] = None
    idCard: Optional[str] = None
    avatar: Optional[str] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    homeAddress: Optional[str] = None
    status: Optional[int] = None
    remark: Optional[str] = None
    # 资质信息
    licenseType: Optional[str] = None
    licenseNo: Optional[str] = None
    licenseExpire: Optional[date] = None
    qualificationNo: Optional[str] = None
    qualificationExpire: Optional[date] = None
    licensePhoto: Optional[str] = None
    qualificationPhoto: Optional[str] = None
    idCardFrontPhoto: Optional[str] = None
    idCardBackPhoto: Optional[str] = None
    # 运营属性
    departmentId: Optional[int] = None
    driverType: Optional[str] = None
    residentAreas: Optional[Any] = None
    commonRoutes: Optional[str] = None
    operationStatus: Optional[int] = None


class DriverStatusUpdate(BaseModel):
    """人事状态变更"""
    status: int


class DriverOperationStatusUpdate(BaseModel):
    """运营状态变更"""
    operationStatus: int


class DriverOut(BaseModel):
    """驾驶员响应（核心+资质+运营合并输出）"""
    id: int
    driverCode: str
    userId: Optional[int] = None
    name: str
    gender: Optional[int] = None
    phone: str
    idCard: Optional[str] = None
    avatar: Optional[str] = None
    emergencyContact: Optional[str] = None
    emergencyPhone: Optional[str] = None
    homeAddress: Optional[str] = None
    status: int
    remark: Optional[str] = None
    # 资质信息
    licenseType: Optional[str] = None
    licenseNo: Optional[str] = None
    licenseExpire: Optional[date] = None
    qualificationNo: Optional[str] = None
    qualificationExpire: Optional[date] = None
    licensePhoto: Optional[str] = None
    qualificationPhoto: Optional[str] = None
    idCardFrontPhoto: Optional[str] = None
    idCardBackPhoto: Optional[str] = None
    # 运营属性
    departmentId: Optional[int] = None
    departmentName: Optional[str] = None
    driverType: Optional[str] = None
    residentAreas: Optional[Any] = None
    commonRoutes: Optional[str] = None
    operationStatus: Optional[int] = None
    # 时间
    createdAt: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_row(cls, driver, license_info=None, operation=None, dept_name=None) -> "DriverOut":
        """从核心表+资质表+运营表组装输出"""
        data = dict(
            id=driver.id,
            driverCode=driver.driver_code,
            userId=driver.user_id,
            name=driver.name,
            gender=driver.gender,
            phone=driver.phone,
            idCard=driver.id_card,
            avatar=driver.avatar,
            emergencyContact=driver.emergency_contact,
            emergencyPhone=driver.emergency_phone,
            homeAddress=driver.home_address,
            status=driver.status,
            remark=driver.remark,
            createdAt=driver.created_at,
        )
        if license_info:
            data.update(
                licenseType=license_info.license_type,
                licenseNo=license_info.license_no,
                licenseExpire=license_info.license_expire,
                qualificationNo=license_info.qualification_no,
                qualificationExpire=license_info.qualification_expire,
                licensePhoto=license_info.license_photo,
                qualificationPhoto=license_info.qualification_photo,
                idCardFrontPhoto=license_info.id_card_front_photo,
                idCardBackPhoto=license_info.id_card_back_photo,
            )
        if operation:
            data.update(
                departmentId=operation.department_id,
                departmentName=dept_name,
                driverType=operation.driver_type,
                residentAreas=operation.resident_areas,
                commonRoutes=operation.common_routes,
                operationStatus=operation.operation_status,
            )
        return cls(**data)
