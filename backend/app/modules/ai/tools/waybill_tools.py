"""
运单相关工具

首期：
- waybill.search        : 查询运单（低风险）
- waybill.get_detail    : 查询运单详情
- waybill.batch_create  : 批量创建运单（高风险，需用户确认）
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.common.exceptions import BizException
from app.modules.ai.tools.base import ToolContext, ToolResult
from app.modules.ai.tools.registry import register_tool
from app.modules.client.schemas.waybill.waybill import WaybillCreate, WaybillCargoLineIn
from app.modules.client.services.waybill.waybill_service import WaybillService


class WaybillSearchParams(BaseModel):
    keyword: Optional[str] = Field(
        None,
        description="模糊匹配运单号（客户请用 customer_id）",
    )
    customer_id: Optional[int] = Field(None, description="客户ID")
    status: Optional[int] = Field(
        None,
        description="状态 0-待确认 1-已确认 2-已调度 3-运输中 4-已送达 5-已完成 6-已取消",
    )
    page: int = Field(1, ge=1, description="页码，从1开始")
    page_size: int = Field(10, ge=1, le=50, description="每页大小")


@register_tool(
    code="waybill.search",
    name="查询运单",
    category="waybill",
    description=(
        "按运单号关键词、客户、状态分页查询当前租户的运单列表。"
        "返回运单号、客户、起讫地、状态、运费等概要信息。"
    ),
    params_schema=WaybillSearchParams,
    permission="biz:waybill:list",
    risk_level="low",
)
async def search_waybill(ctx: ToolContext, **kwargs) -> ToolResult:
    params = WaybillSearchParams(**kwargs)
    data = await WaybillService.page_waybills(
        ctx.db,
        page=params.page,
        page_size=params.page_size,
        keyword=params.keyword,
        customer_id=params.customer_id,
        status=params.status,
    )
    return ToolResult(
        success=True,
        data=data,
        message=f"共找到 {data.get('total', 0)} 条运单，当前返回第 {params.page} 页",
    )


class WaybillDetailParams(BaseModel):
    waybill_id: int = Field(..., description="运单ID")


@register_tool(
    code="waybill.get_detail",
    name="查询运单详情",
    category="waybill",
    description="按 ID 查询单条运单的详细信息",
    params_schema=WaybillDetailParams,
    permission="biz:waybill:list",
    risk_level="low",
)
async def get_waybill_detail(ctx: ToolContext, **kwargs) -> ToolResult:
    params = WaybillDetailParams(**kwargs)
    try:
        wb = await WaybillService.get_waybill(ctx.db, params.waybill_id)
    except BizException as e:
        return ToolResult(success=False, error=e.message)
    out = await WaybillService.waybill_to_out(ctx.db, wb)
    return ToolResult(success=True, data=out.model_dump())


class WaybillRow(BaseModel):
    """单条待录入的运单（与 WaybillCreate 字段对齐，但所有字段可选以适配 LLM 灵活输出）"""

    waybillNo: Optional[str] = Field(None, description="运单号（不传则系统生成）")
    customerId: Optional[int] = Field(None, description="客户ID")
    customerName: Optional[str] = Field(None, description="客户名称")
    origin: Optional[str] = Field(None, description="出发地")
    originCode: Optional[str] = Field(None, description="出发地编码")
    destination: Optional[str] = Field(None, description="目的地")
    destinationCode: Optional[str] = Field(None, description="目的地编码")
    vehicleBrand: Optional[str] = Field(None, description="车辆品牌（无 cargoes 时与 vehicleModel/quantity 生成一行明细）")
    vehicleModel: Optional[str] = Field(None, description="车型")
    quantity: Optional[int] = Field(None, description="数量，默认1")
    cargoes: Optional[list[WaybillCargoLineIn]] = Field(
        None, description="货物明细（多品牌车型）；优先于顶层 vehicleBrand/vehicleModel"
    )
    dealerName: Optional[str] = Field(None, description="经销商名称")
    dealerContact: Optional[str] = Field(None, description="经销商联系人")
    dealerPhone: Optional[str] = Field(None, description="经销商电话")
    dealerAddress: Optional[str] = Field(None, description="经销商地址")
    freightAmount: Optional[float] = Field(None, description="运费金额")
    remark: Optional[str] = Field(None, description="备注")


class WaybillBatchCreateParams(BaseModel):
    rows: list[WaybillRow] = Field(..., description="待录入的运单列表，建议一次不超过50条")


@register_tool(
    code="waybill.batch_create",
    name="批量录入运单",
    category="waybill",
    description=(
        "把已映射好的运单数据批量入库。"
        "调用前请先用 file.parse_excel 解析文件，并由用户确认字段映射。"
        "本工具属于高风险操作，必须经用户确认后才会执行。"
    ),
    params_schema=WaybillBatchCreateParams,
    permission="biz:waybill:add",
    risk_level="high",
    confirm_required=True,
)
async def batch_create_waybill(ctx: ToolContext, **kwargs) -> ToolResult:
    params = WaybillBatchCreateParams(**kwargs)
    if not params.rows:
        return ToolResult(success=False, error="待录入运单列表为空")

    success_count, failed_items = 0, []
    for idx, row in enumerate(params.rows):
        try:
            payload = WaybillCreate(**row.model_dump(exclude_none=True))
            await WaybillService.create_waybill(
                ctx.db, payload, current_user_id=ctx.user.user_id
            )
            success_count += 1
        except BizException as e:
            failed_items.append({"index": idx, "error": e.message})
        except Exception as e:  # noqa: BLE001
            failed_items.append({"index": idx, "error": str(e)})

    return ToolResult(
        success=True,
        data={
            "total": len(params.rows),
            "success": success_count,
            "failed": len(failed_items),
            "failed_items": failed_items[:20],  # 截断
        },
        message=f"批量录入完成：成功 {success_count} 条，失败 {len(failed_items)} 条",
    )
