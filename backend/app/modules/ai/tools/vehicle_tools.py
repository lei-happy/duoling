"""
车辆 / 驾驶员 相关工具
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.modules.ai.tools.base import ToolContext, ToolResult
from app.modules.ai.tools.registry import register_tool
from app.modules.client.services.capacity.self_capacity.vehicle_service import VehicleService


class VehicleSearchParams(BaseModel):
    keyword: Optional[str] = Field(
        None, description="模糊关键词，匹配车牌号 / 品牌 / 型号"
    )
    vehicle_type: Optional[str] = Field(None, description="车辆类型字典")
    status: Optional[int] = Field(
        None, description="状态 0-停用 1-正常 2-维修中"
    )
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=50)


@register_tool(
    code="vehicle.search",
    name="查询车辆",
    category="vehicle",
    description=(
        "按关键词、车辆类型、状态分页查询当前租户的车辆列表。"
        "返回车牌号、品牌、型号、状态等信息。"
    ),
    params_schema=VehicleSearchParams,
    permission="capacity:self_capacity:vehicle:list",
    risk_level="low",
)
async def search_vehicle(ctx: ToolContext, **kwargs) -> ToolResult:
    params = VehicleSearchParams(**kwargs)
    data = await VehicleService.page_vehicles(
        ctx.db,
        page=params.page,
        page_size=params.page_size,
        keyword=params.keyword,
        vehicle_type=params.vehicle_type,
        status=params.status,
    )
    return ToolResult(
        success=True,
        data=data,
        message=f"共找到 {data.get('total', 0)} 辆车",
    )
