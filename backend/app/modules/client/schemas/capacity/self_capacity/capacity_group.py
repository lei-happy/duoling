"""
运力分组 Schemas
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CapacityGroupCreate(BaseModel):
    """新建分组"""
    groupName: str = Field(..., max_length=50, description="分组名称")
    groupCode: Optional[str] = Field(None, max_length=50, description="分组编码（留空自动生成）")
    color: Optional[str] = Field(None, max_length=16, description="标签颜色")
    sortOrder: Optional[int] = Field(0, description="排序号")
    status: Optional[int] = Field(1, description="状态 0-停用 1-启用")
    enterpriseId: Optional[int] = Field(None, description="所属经营主体ID")
    remark: Optional[str] = Field(None, max_length=255, description="备注")


class CapacityGroupUpdate(CapacityGroupCreate):
    """编辑分组"""
    groupName: Optional[str] = Field(None, max_length=50, description="分组名称")


class CapacityGroupStatusUpdate(BaseModel):
    """启用/停用"""
    status: int = Field(..., description="状态 0-停用 1-启用")


class CapacityGroupMemberAdd(BaseModel):
    """批量添加成员（传绑定中的运力ID列表）"""
    capacityIds: list[int] = Field(..., description="运力ID列表（biz_capacity.id）")


class CapacityGroupMemberRemove(BaseModel):
    """批量移出成员"""
    memberIds: Optional[list[int]] = Field(None, description="成员关联记录ID列表")
    driverIds: Optional[list[int]] = Field(None, description="司机ID列表（二选一）")


class CapacityGroupOut(BaseModel):
    """分组响应"""
    id: int
    enterpriseId: Optional[int] = None
    groupName: str
    groupCode: Optional[str] = None
    color: Optional[str] = None
    sortOrder: int = 0
    status: int = 1
    remark: Optional[str] = None
    memberCount: int = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    @classmethod
    def from_model(cls, m, member_count: int = 0) -> "CapacityGroupOut":
        return cls(
            id=m.id,
            enterpriseId=m.enterprise_id,
            groupName=m.group_name,
            groupCode=m.group_code,
            color=m.color,
            sortOrder=m.sort_order,
            status=m.status,
            remark=m.remark,
            memberCount=member_count,
            createdAt=m.created_at,
            updatedAt=m.updated_at,
        )


class CapacityGroupOption(BaseModel):
    """分组精简项（供成本规则条件下拉）"""
    id: int
    groupName: str
    groupCode: Optional[str] = None
    color: Optional[str] = None


class CapacityGroupMemberOut(BaseModel):
    """分组成员响应（联查当前运力信息）"""
    id: int
    groupId: int
    driverId: int
    driverName: str
    driverPhone: Optional[str] = None
    capacityId: Optional[int] = None
    plateNumber: Optional[str] = None
    bound: bool = False
    createdAt: Optional[datetime] = None

    @classmethod
    def from_model(
        cls,
        m,
        driver_phone: Optional[str] = None,
        current_capacity_id: Optional[int] = None,
        current_plate: Optional[str] = None,
    ) -> "CapacityGroupMemberOut":
        return cls(
            id=m.id,
            groupId=m.group_id,
            driverId=m.driver_id,
            driverName=m.driver_name,
            driverPhone=driver_phone,
            capacityId=current_capacity_id if current_capacity_id is not None else m.capacity_id,
            plateNumber=current_plate if current_plate is not None else m.plate_number,
            bound=current_capacity_id is not None,
            createdAt=m.created_at,
        )
