"""运营后台：服务平台免审白名单

对应 08.接口契约.md §4.2。

  - GET  /                            白名单成员列表
  - GET  /{tenantCode}/eligibility    资格判定（逐条明细）
  - POST /                            授予
  - POST /{tenantCode}/revoke         移出（必填原因）

## 移出为什么用 POST 而不是 DELETE

移出必须带原因（写入 ``whitelist_revoke_reason``，并作为冷静期起点）。
DELETE 带请求体虽然协议上允许，但在网关、日志采集、前端请求库这几层都属于
少见路径，最容易出现的故障是「体被丢掉了、后端收到空原因」。
一个必须携带业务参数的处置动作，用 POST 表达更稳。

## 资格判定为什么单独一个接口

界面上运营点开某家企业时就要看到「还差什么」，不能等他点了授予再用报错
告诉他不行——报错只能说一句话，而这里要列七条。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import get_current_user, get_platform_db
from app.core.security import TokenData
from app.modules.console.models.ecosystem.constants import WhitelistSource
from app.modules.console.models.system.user import User
from app.modules.console.schemas.ecosystem import (
    WhitelistGrantRequest,
    WhitelistRevokeRequest,
)
from app.modules.console.services.ecosystem.audit_facade import EcoAuditFacade
from app.modules.console.services.ecosystem.audit_query_service import OpsContext
from app.modules.console.services.ecosystem.audit_serializer import EcoAuditSerializer
from app.modules.console.services.ecosystem.whitelist_service import (
    EcoWhitelistService,
)

MODULE = "服务平台审核"

router = APIRouter()


async def _ops(db: AsyncSession, current_user: TokenData) -> OpsContext:
    name = (
        await db.execute(select(User.real_name).where(User.id == current_user.user_id))
    ).scalar()
    return OpsContext(
        user_id=current_user.user_id, user_name=name or current_user.phone
    )


@router.get("")
async def page_whitelist(
    page: int = Query(1, ge=1),
    size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """白名单成员列表"""
    return success(
        data=await EcoAuditFacade.page_whitelist(
            db, keyword=keyword, page=page, size=size
        )
    )


@router.get("/{tenant_code}/eligibility")
async def check_eligibility(
    tenant_code: str = Path(..., min_length=1, max_length=32),
    db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """资格判定 + 该企业在服务平台的完整档案"""
    return success(data=await EcoAuditFacade.tenant_profile(db, tenant_code))


@router.post("")
@operation_log(module=MODULE, action="授予免审", description="加入免审白名单")
async def grant_whitelist(
    request: Request,
    data: WhitelistGrantRequest,
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """人工授予免审白名单

    人工授予只放行发布量、成交量、干净期这类可酌情条件；企业认证与大厅能力
    不满足时仍然拦下（理由见 04 §2.2）。
    """
    result = await EcoWhitelistService.grant(
        db,
        data.tenantCode,
        operator=await _ops(db, current_user),
        source=WhitelistSource.MANUAL,
    )
    return success(
        data=EcoAuditSerializer.whitelist_result(result), message=result.message
    )


@router.post("/{tenant_code}/revoke")
@operation_log(module=MODULE, action="移出免审", description="移出免审白名单")
async def revoke_whitelist(
    request: Request,
    data: WhitelistRevokeRequest,
    tenant_code: str = Path(..., min_length=1, max_length=32),
    db: AsyncSession = Depends(get_platform_db),
    current_user: TokenData = Depends(get_current_user),
):
    """移出免审白名单，之后发布的挂牌重新走人工审核"""
    result = await EcoWhitelistService.revoke(
        db,
        tenant_code,
        reason=data.reason,
        operator=await _ops(db, current_user),
    )
    return success(
        data=EcoAuditSerializer.whitelist_result(result), message=result.message
    )
