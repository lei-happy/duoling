"""审批中心 - 流程模板配置 API

完整前缀：/api/client/approval/flow
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_tenant_db
from app.core.security import TokenData
from app.modules.client.schemas.approval.flow import FlowCreate, FlowUpdate
from app.modules.client.services.approval import ApprovalFlowService

router = APIRouter()


@router.get("")
async def page_flows(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=200),
    bizType: Optional[str] = None,
    status: Optional[int] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await ApprovalFlowService.page_flows(
        db, page=page, page_size=page_size, biz_type=bizType, status=status, keyword=keyword,
    )
    return success(data=data)


@router.get("/{flow_id}")
async def get_flow(
    flow_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    data = await ApprovalFlowService.get_flow(db, flow_id)
    return success(data=data.model_dump())


@router.post("")
@operation_log(module="审批流程配置", action="新增", description="新增审批流程模板")
async def create_flow(
    request: Request,
    data: FlowCreate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    flow = await ApprovalFlowService.create_flow(db, data, operator_id=current_user.user_id)
    return success(data=flow.model_dump())


@router.put("/{flow_id}")
@operation_log(module="审批流程配置", action="修改", description="修改审批流程模板")
async def update_flow(
    request: Request,
    flow_id: int,
    data: FlowUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    current_user: TokenData = Depends(get_current_user),
):
    flow = await ApprovalFlowService.update_flow(db, flow_id, data, operator_id=current_user.user_id)
    return success(data=flow.model_dump())


@router.post("/{flow_id}/publish")
@operation_log(module="审批流程配置", action="发布", description="发布审批流程模板")
async def publish_flow(
    request: Request,
    flow_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    flow = await ApprovalFlowService.publish_flow(db, flow_id)
    return success(data=flow.model_dump())


@router.post("/{flow_id}/disable")
@operation_log(module="审批流程配置", action="停用", description="停用审批流程模板")
async def disable_flow(
    request: Request,
    flow_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    flow = await ApprovalFlowService.disable_flow(db, flow_id)
    return success(data=flow.model_dump())


@router.delete("/{flow_id}")
@operation_log(module="审批流程配置", action="删除", description="删除审批流程模板")
async def delete_flow(
    request: Request,
    flow_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _=Depends(get_current_user),
):
    await ApprovalFlowService.delete_flow(db, flow_id)
    return success(message="删除成功")
