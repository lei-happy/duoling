"""
企业端承运商管理 API
- 主体 CRUD（含选择器）
- 结算账户子表 CRUD
- 邀请：触发 / 撤回 / 历史（路径 B 全链路）
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.common.operation_log import operation_log
from app.common.response import success
from app.core.dependencies import (
    get_tenant_db, get_platform_db, get_current_user, get_tenant_code,
)
from app.core.security import TokenData
from app.modules.client.schemas.partner.carrier import (
    CarrierCreate, CarrierUpdate, CarrierOut,
    CarrierListItemOut, CarrierSelectItem,
)
from app.modules.client.schemas.partner.carrier_settlement import (
    CarrierSettlementCreate, CarrierSettlementUpdate, CarrierSettlementOut,
)
from app.modules.client.schemas.partner.carrier_invitation import (
    CarrierInviteRequest, CarrierInviteResponse,
    CarrierRevokeRequest, CarrierInvitationOut,
    CarrierInvitePhoneCheckOut,
)
from app.modules.client.services.partner.carrier_service import CarrierService
from app.modules.client.services.partner.carrier_settlement_service import (
    CarrierSettlementService,
)
from app.modules.client.services.partner.carrier_invite_service import (
    CarrierInviteService,
)

router = APIRouter()


# ============================================================
# 主体 CRUD（6）
# ============================================================

@router.get("")
async def page_carriers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, alias="limit", ge=1, le=100),
    keyword: Optional[str] = None,
    carrierType: Optional[int] = None,
    status: Optional[int] = None,
    inviteStatus: Optional[int] = None,
    linkedOnly: Optional[bool] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """承运商分页列表（含默认结算摘要列）"""
    items, total = await CarrierService.list_page(
        db,
        keyword=keyword,
        carrier_type=carrierType,
        status=status,
        invite_status=inviteStatus,
        linked_only=linkedOnly,
        page=page,
        page_size=page_size,
    )
    default_map = await CarrierSettlementService.get_default_map(
        db, [c.id for c in items]
    )
    rows = [
        CarrierListItemOut.from_model(c, default_map.get(c.id)).model_dump()
        for c in items
    ]
    return success(data={
        "list": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/select")
async def select_carriers(
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """运单/合同等场景的承运商选择器"""
    carriers = await CarrierService.select_for_picker(db, keyword=keyword)
    default_map = await CarrierSettlementService.get_default_map(
        db, [c.id for c in carriers]
    )
    out = []
    for c in carriers:
        d = default_map.get(c.id)
        out.append(CarrierSelectItem(
            id=c.id,
            carrierCode=c.carrier_code,
            carrierName=c.carrier_name,
            shortName=c.short_name,
            carrierType=c.carrier_type,
            linked=bool(c.linked_tenant_code),
            linkedTenantCode=c.linked_tenant_code,
            defaultSettlement=(
                CarrierSettlementOut.from_model(d) if d else None
            ),
        ).model_dump())
    return success(data=out)


@router.get("/{carrier_id}")
async def get_carrier(
    carrier_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    """承运商详情（含 settlements 全量）"""
    carrier = await CarrierService.get_or_404(db, carrier_id)
    settlements = await CarrierSettlementService.list_by_carrier(db, carrier_id)
    default = next((s for s in settlements if s.is_default == 1), None)
    return success(data=CarrierOut.from_model(
        carrier, settlements=settlements, default_settlement=default
    ).model_dump())


@router.post("")
@operation_log(module="承运商管理", action="新增", description="新增承运商")
async def create_carrier(
    request: Request,
    data: CarrierCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    carrier = await CarrierService.create(db, data)
    settlements = await CarrierSettlementService.list_by_carrier(db, carrier.id)
    default = next((s for s in settlements if s.is_default == 1), None)
    return success(data=CarrierOut.from_model(
        carrier, settlements=settlements, default_settlement=default
    ).model_dump())


@router.put("/{carrier_id}")
@operation_log(module="承运商管理", action="编辑", description="编辑承运商")
async def update_carrier(
    request: Request,
    carrier_id: int,
    data: CarrierUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    carrier = await CarrierService.update(db, carrier_id, data)
    settlements = await CarrierSettlementService.list_by_carrier(db, carrier_id)
    default = next((s for s in settlements if s.is_default == 1), None)
    return success(data=CarrierOut.from_model(
        carrier, settlements=settlements, default_settlement=default
    ).model_dump())


@router.delete("/{carrier_id}")
@operation_log(module="承运商管理", action="删除", description="删除承运商")
async def delete_carrier(
    request: Request,
    carrier_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await CarrierService.delete(db, carrier_id)
    return success()


# ============================================================
# 结算账户子表（6）
# ============================================================

@router.get("/{carrier_id}/settlements")
async def list_settlements(
    carrier_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    settlements = await CarrierSettlementService.list_by_carrier(db, carrier_id)
    return success(data=[CarrierSettlementOut.from_model(s).model_dump()
                         for s in settlements])


@router.post("/{carrier_id}/settlements")
@operation_log(module="承运商管理", action="新增结算账户", description="新增承运商结算账户")
async def create_settlement(
    request: Request,
    carrier_id: int,
    data: CarrierSettlementCreate,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await CarrierService.get_or_404(db, carrier_id)
    s = await CarrierSettlementService.create(db, carrier_id, data)
    return success(data=CarrierSettlementOut.from_model(s).model_dump())


@router.put("/{carrier_id}/settlements/{settlement_id}")
@operation_log(module="承运商管理", action="编辑结算账户", description="编辑承运商结算账户")
async def update_settlement(
    request: Request,
    carrier_id: int,
    settlement_id: int,
    data: CarrierSettlementUpdate,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    s = await CarrierSettlementService.update(db, carrier_id, settlement_id, data)
    return success(data=CarrierSettlementOut.from_model(s).model_dump())


@router.put("/{carrier_id}/settlements/{settlement_id}/default")
@operation_log(module="承运商管理", action="设为默认", description="设置默认结算账户")
async def set_settlement_default(
    request: Request,
    carrier_id: int,
    settlement_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    s = await CarrierSettlementService.set_default(db, carrier_id, settlement_id)
    return success(data=CarrierSettlementOut.from_model(s).model_dump())


@router.put("/{carrier_id}/settlements/{settlement_id}/toggle-status")
@operation_log(module="承运商管理", action="切换状态", description="启用/停用结算账户")
async def toggle_settlement_status(
    request: Request,
    carrier_id: int,
    settlement_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    s = await CarrierSettlementService.toggle_status(db, carrier_id, settlement_id)
    return success(data=CarrierSettlementOut.from_model(s).model_dump())


@router.delete("/{carrier_id}/settlements/{settlement_id}")
@operation_log(module="承运商管理", action="删除结算账户", description="删除承运商结算账户")
async def delete_settlement(
    request: Request,
    carrier_id: int,
    settlement_id: int,
    db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    await CarrierSettlementService.delete(db, carrier_id, settlement_id)
    return success()


# ============================================================
# 邀请相关（4，路径 B）
# ============================================================

@router.get("/invite/check-phone")
async def check_invite_phone(
    phone: str = Query(..., description="承运商联系手机号", min_length=6, max_length=20),
    platform_db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    """弹框打开时，按手机号查询平台注册状态。

    - 未注册：可继续走路径 B 生成邀请链接
    - 已注册：返回所属租户名 + 一名管理员脱敏信息，前端提示请联系管理员

    路径刻意放在 `/invite/check-phone` 而非 `/check-invite-phone`，避免与
    `/{carrier_id}` 的单段 path 冲突。
    """
    res = await CarrierInviteService.check_phone(platform_db, phone.strip())
    return success(data=res.model_dump())


@router.post("/{carrier_id}/invite")
@operation_log(module="承运商管理", action="邀请激活", description="发起承运商互联邀请")
async def invite_carrier(
    request: Request,
    carrier_id: int,
    data: CarrierInviteRequest,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    tenant_code: str = Depends(get_tenant_code),
    user: TokenData = Depends(get_current_user),
):
    res = await CarrierInviteService.invite(
        tenant_db=tenant_db,
        platform_db=platform_db,
        source_tenant_code=tenant_code,
        operator_user_id=user.user_id,
        carrier_id=carrier_id,
        data=data,
    )
    return success(data=res.model_dump())


@router.post("/{carrier_id}/revoke-invite")
@operation_log(module="承运商管理", action="撤回邀请", description="撤回承运商互联邀请")
async def revoke_carrier_invite(
    request: Request,
    carrier_id: int,
    data: Optional[CarrierRevokeRequest] = None,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    platform_db: AsyncSession = Depends(get_platform_db),
    _: TokenData = Depends(get_current_user),
):
    await CarrierInviteService.revoke_invite(
        tenant_db=tenant_db,
        platform_db=platform_db,
        carrier_id=carrier_id,
        data=data,
    )
    return success()


@router.get("/{carrier_id}/invitations")
async def list_carrier_invitations(
    carrier_id: int,
    tenant_db: AsyncSession = Depends(get_tenant_db),
    _: TokenData = Depends(get_current_user),
):
    items = await CarrierInviteService.list_invitations(tenant_db, carrier_id)
    return success(data=[CarrierInvitationOut.from_model(i).model_dump()
                         for i in items])
