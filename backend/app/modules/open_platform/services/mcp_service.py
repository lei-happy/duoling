"""MCP 配置管理服务（平台库）

创建一条 MCP 配置时，同时签发一个 mcp 类型凭证（Bearer Token），并生成可复制配置。
Token 只展示一次；改名不影响连接（slug/token 不变）。
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.core.config import get_settings
from app.modules.open_platform.models.platform.open_credential import OpenCredential
from app.modules.open_platform.models.platform.open_mcp_config import OpenMcpConfig
from app.modules.open_platform.services.app_service import AppService
from app.modules.open_platform.services.credential_service import _validate_scope
from app.modules.open_platform.security import keygen
from app.modules.open_platform.auth.resolver import invalidate_credential_cache


def _base_url() -> str:
    return getattr(get_settings(), "OPEN_PLATFORM_BASE_URL", "") or "https://openapi.example.com"


def _mcp_url(slug: str) -> str:
    return f"{_base_url().rstrip('/')}/mcp/{slug}"


def _build_config_json(display_name: str, url: str, token: str) -> dict:
    return {
        "mcpServers": {
            display_name: {
                "url": url,
                "headers": {"Authorization": f"Bearer {token}"},
            }
        }
    }


class McpService:
    @staticmethod
    def _to_out(cfg: OpenMcpConfig) -> dict:
        return {
            "id": cfg.id,
            "display_name": cfg.display_name,
            "server_slug": cfg.server_slug,
            "enabled_capabilities": list(cfg.enabled_capabilities or []),
            "status": cfg.status,
            "url": _mcp_url(cfg.server_slug),
            "created_at": cfg.created_at,
        }

    @staticmethod
    async def list_configs(db: AsyncSession, tenant_code: str, app_id: int) -> list[dict]:
        await AppService.get_app(db, tenant_code, app_id)
        rows = (
            await db.execute(
                select(OpenMcpConfig)
                .where(
                    OpenMcpConfig.app_id == app_id,
                    OpenMcpConfig.is_deleted == 0,
                )
                .order_by(OpenMcpConfig.id.desc())
            )
        ).scalars().all()
        return [McpService._to_out(c) for c in rows]

    @staticmethod
    async def create_config(
        db: AsyncSession,
        tenant_code: str,
        app_id: int,
        *,
        display_name: str,
        enabled_capabilities: List[str],
        user_id: Optional[int],
    ) -> dict:
        await AppService.get_app(db, tenant_code, app_id)
        caps = _validate_scope(enabled_capabilities)

        # 1) 签发 mcp 凭证
        access_key = keygen.gen_mcp_key()
        token = keygen.gen_mcp_token()
        cred = OpenCredential(
            app_id=app_id,
            tenant_code=tenant_code,
            cred_type="mcp",
            access_key=access_key,
            secret_store=keygen.hash_secret(token),
            scope=caps,
            status="enabled",
            created_by=user_id,
        )
        db.add(cred)
        await db.flush()

        # 2) 建配置
        slug = keygen.gen_server_slug()
        cfg = OpenMcpConfig(
            app_id=app_id,
            tenant_code=tenant_code,
            credential_id=cred.id,
            server_slug=slug,
            display_name=display_name,
            enabled_capabilities=caps,
            status="enabled",
            created_by=user_id,
        )
        db.add(cfg)
        await db.flush()
        await db.refresh(cfg)  # 回填 server_default 的 created_at，避免异步下惰性刷新报错

        url = _mcp_url(slug)
        out = McpService._to_out(cfg)
        # MCP Token 在 URL 之外单独下发；此处 token 即上面的 mcp_token
        out["token"] = f"{access_key}.{token}"
        out["config_json"] = _build_config_json(display_name, url, out["token"])
        return out

    @staticmethod
    async def _get_owned(
        db: AsyncSession, tenant_code: str, config_id: int
    ) -> OpenMcpConfig:
        cfg = await db.scalar(
            select(OpenMcpConfig).where(
                OpenMcpConfig.id == config_id,
                OpenMcpConfig.tenant_code == tenant_code,
                OpenMcpConfig.is_deleted == 0,
            )
        )
        if not cfg:
            raise BizException("MCP 配置不存在")
        return cfg

    @staticmethod
    async def update_config(
        db: AsyncSession,
        tenant_code: str,
        config_id: int,
        *,
        display_name: Optional[str] = None,
        enabled_capabilities: Optional[List[str]] = None,
        status: Optional[str] = None,
    ) -> dict:
        cfg = await McpService._get_owned(db, tenant_code, config_id)
        if display_name is not None:
            cfg.display_name = display_name  # 仅展示，不动 slug/token
        if enabled_capabilities is not None:
            caps = _validate_scope(enabled_capabilities)
            cfg.enabled_capabilities = caps
            cred = await db.scalar(
                select(OpenCredential).where(OpenCredential.id == cfg.credential_id)
            )
            if cred:
                cred.scope = caps
                invalidate_credential_cache(cred.access_key)
        if status is not None:
            if status not in ("enabled", "disabled"):
                raise BizException("状态取值不合法")
            cfg.status = status
            cred = await db.scalar(
                select(OpenCredential).where(OpenCredential.id == cfg.credential_id)
            )
            if cred:
                cred.status = status
                invalidate_credential_cache(cred.access_key)
        await db.flush()
        return McpService._to_out(cfg)

    @staticmethod
    async def revoke(db: AsyncSession, tenant_code: str, config_id: int) -> None:
        cfg = await McpService._get_owned(db, tenant_code, config_id)
        cfg.status = "disabled"
        cred = await db.scalar(
            select(OpenCredential).where(OpenCredential.id == cfg.credential_id)
        )
        if cred:
            cred.status = "revoked"
            invalidate_credential_cache(cred.access_key)
        cfg.is_deleted = 1
        await db.flush()
