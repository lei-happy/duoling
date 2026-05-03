"""
客户相关工具
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.modules.ai.tools.base import ToolContext, ToolResult
from app.modules.ai.tools.registry import register_tool
from app.modules.client.services.partner.customer_service import CustomerService


class CustomerSearchParams(BaseModel):
    keyword: Optional[str] = Field(
        None, description="模糊关键词，匹配客户名 / 编码 / 联系人 / 联系电话"
    )
    customer_type: Optional[int] = Field(None, description="客户类型字典值")
    status: Optional[int] = Field(None, description="状态 0-停用 1-正常")
    page: int = Field(1, ge=1)
    page_size: int = Field(10, ge=1, le=50)


@register_tool(
    code="customer.search",
    name="查询客户",
    category="customer",
    description="按关键词、客户类型、状态分页查询当前租户的客户列表",
    params_schema=CustomerSearchParams,
    permission="partner:customer:list",
    risk_level="low",
)
async def search_customer(ctx: ToolContext, **kwargs) -> ToolResult:
    params = CustomerSearchParams(**kwargs)
    data = await CustomerService.page_customers(
        ctx.db,
        page=params.page,
        page_size=params.page_size,
        keyword=params.keyword,
        customer_type=params.customer_type,
        status=params.status,
    )
    return ToolResult(
        success=True,
        data=data,
        message=f"共找到 {data.get('total', 0)} 个客户",
    )
