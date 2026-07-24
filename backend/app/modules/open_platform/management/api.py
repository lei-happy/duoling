"""开放平台控制面 API（挂载于 /api/client/open-platform）

面向租户员工：管理接入应用、凭证、MCP 配置，查看能力目录与调用记录。
沿用企业端 JWT + RBAC；功能门控 open_platform 在 client/api/__init__.py 挂载处统一施加。
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.response import success
from app.common.exceptions import TenantException
from app.core.database import db_manager
from app.core.dependencies import get_current_user, get_platform_db, get_tenant_db
from app.core.security import TokenData
from app.modules.open_platform.schemas import (
    AppCreate,
    AppUpdate,
    CredentialCreate,
    CredentialScopeUpdate,
    McpConfigCreate,
    McpConfigUpdate,
)
from app.modules.open_platform.services import (
    AppService,
    CredentialService,
    McpService,
    CapabilityService,
    AuditService,
)

router = APIRouter()


def _tenant(current_user: TokenData) -> str:
    if not current_user.tenant_code:
        raise TenantException("请在企业账号下使用开放平台")
    return current_user.tenant_code


# ============================================================
# 能力目录
# ============================================================

@router.get("/capabilities")
async def list_capabilities(
    channel: Optional[str] = Query(None, description="api / mcp"),
    current_user: TokenData = Depends(get_current_user),
):
    """能力目录（读代码注册表，永远与实现一致）"""
    _tenant(current_user)
    return success(data=CapabilityService.list_for_display(channel))


# ============================================================
# 接入应用
# ============================================================

@router.get("/apps")
async def list_apps(
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """接入应用列表"""
    data = await AppService.list_apps(db, _tenant(current_user))
    return success(data=data)


@router.post("/apps")
async def create_app(
    body: AppCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """新建接入应用"""
    app = await AppService.create_app(
        db, _tenant(current_user), body.name, body.description, current_user.user_id
    )
    return success(data={"id": app.id}, message="已创建接入应用")


@router.put("/apps/{app_id}")
async def update_app(
    app_id: int,
    body: AppUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """编辑接入应用"""
    await AppService.update_app(
        db,
        _tenant(current_user),
        app_id,
        name=body.name,
        description=body.description,
        status=body.status,
    )
    return success(message="已保存")


# ============================================================
# 接入凭证（API 类型）
# ============================================================

@router.get("/apps/{app_id}/credentials")
async def list_credentials(
    app_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """应用下的 API 凭证列表"""
    data = await CredentialService.list_credentials(db, _tenant(current_user), app_id)
    return success(data=data)


@router.post("/apps/{app_id}/credentials")
async def create_credential(
    app_id: int,
    body: CredentialCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """签发 API 凭证（明文密钥仅返回一次）"""
    data = await CredentialService.create_credential(
        db,
        _tenant(current_user),
        app_id,
        scope=body.scope,
        ip_whitelist=body.ip_whitelist,
        expires_at=body.expires_at,
        user_id=current_user.user_id,
    )
    return success(data=data, message="密钥已生成，请立即复制保存，仅显示这一次")


@router.put("/credentials/{credential_id}/scope")
async def update_credential_scope(
    credential_id: int,
    body: CredentialScopeUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """调整凭证可用能力 / IP 白名单"""
    data = await CredentialService.update_scope(
        db,
        _tenant(current_user),
        credential_id,
        scope=body.scope,
        ip_whitelist=body.ip_whitelist,
    )
    return success(data=data, message="已保存")


@router.post("/credentials/{credential_id}/reset")
async def reset_credential(
    credential_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """重置密钥（旧密钥立即失效）"""
    data = await CredentialService.reset_secret(db, _tenant(current_user), credential_id)
    return success(data=data, message="新密钥已生成，请立即复制保存，仅显示这一次")


@router.post("/credentials/{credential_id}/revoke")
async def revoke_credential(
    credential_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """吊销凭证"""
    await CredentialService.revoke(db, _tenant(current_user), credential_id)
    return success(message="凭证已停用")


# ============================================================
# MCP 配置
# ============================================================

@router.get("/apps/{app_id}/mcp")
async def list_mcp(
    app_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """应用下的 MCP 连接列表"""
    data = await McpService.list_configs(db, _tenant(current_user), app_id)
    return success(data=data)


@router.post("/apps/{app_id}/mcp")
async def create_mcp(
    app_id: int,
    body: McpConfigCreate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """新建 MCP 连接（返回可复制配置与一次性 Token）"""
    data = await McpService.create_config(
        db,
        _tenant(current_user),
        app_id,
        display_name=body.display_name,
        enabled_capabilities=body.enabled_capabilities,
        user_id=current_user.user_id,
    )
    return success(data=data, message="连接已创建，请复制配置到你的 AI 工具，Token 仅显示一次")


@router.put("/mcp/{config_id}")
async def update_mcp(
    config_id: int,
    body: McpConfigUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """编辑 MCP 连接（改名不影响已配置的连接）"""
    data = await McpService.update_config(
        db,
        _tenant(current_user),
        config_id,
        display_name=body.display_name,
        enabled_capabilities=body.enabled_capabilities,
        status=body.status,
    )
    return success(data=data, message="已保存")


@router.delete("/mcp/{config_id}")
async def delete_mcp(
    config_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_platform_db),
):
    """删除 MCP 连接（关联 Token 立即失效）"""
    await McpService.revoke(db, _tenant(current_user), config_id)
    return success(message="连接已删除")


# ============================================================
# 调用记录（审计，租户库）
# ============================================================

@router.get("/logs")
async def list_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    capability_code: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    app_id: Optional[int] = Query(None),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    """调用记录分页"""
    tenant_code = _tenant(current_user)
    # 审计表按需建（老租户开通开放平台前无此表，首次查询即补齐）
    await db_manager.ensure_tenant_tables(tenant_code, ["biz_open_call_log"])
    data = await AuditService.page_logs(
        db,
        page=page,
        limit=limit,
        capability_code=capability_code,
        status=status,
        channel=channel,
        app_id=app_id,
    )
    return success(data=data)


@router.get("/logs/stats")
async def logs_stats(
    days: int = Query(1, ge=1, le=90),
    current_user: TokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_tenant_db),
):
    """调用概览统计"""
    tenant_code = _tenant(current_user)
    await db_manager.ensure_tenant_tables(tenant_code, ["biz_open_call_log"])
    data = await AuditService.stats(db, days=days)
    return success(data=data)
