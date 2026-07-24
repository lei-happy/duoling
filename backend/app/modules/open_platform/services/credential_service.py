"""接入凭证管理服务（平台库）

生成/重置时返回一次性明文 secret；库内只存哈希。任何状态变更主动失效数据面缓存。
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BizException
from app.modules.open_platform.models.platform.open_credential import OpenCredential
from app.modules.open_platform.services.app_service import AppService
from app.modules.open_platform.security import keygen
from app.modules.open_platform.auth.resolver import invalidate_credential_cache
from app.modules.open_platform.capabilities.registry import get_capability


def _validate_scope(scope: List[str]) -> List[str]:
    """只允许已注册且支持 api 通道的能力码进入 scope。"""
    cleaned = []
    for code in scope or []:
        spec = get_capability(code)
        if spec is None:
            raise BizException(f"能力不存在：{code}")
        cleaned.append(code)
    return cleaned


class CredentialService:
    @staticmethod
    def _to_out(cred: OpenCredential) -> dict:
        return {
            "id": cred.id,
            "app_id": cred.app_id,
            "cred_type": cred.cred_type,
            "access_key": cred.access_key,
            "scope": list(cred.scope or []),
            "ip_whitelist": cred.ip_whitelist or "",
            "status": cred.status,
            "expires_at": cred.expires_at,
            "last_used_at": cred.last_used_at,
            "created_at": cred.created_at,
        }

    @staticmethod
    async def list_credentials(
        db: AsyncSession, tenant_code: str, app_id: int
    ) -> list[dict]:
        await AppService.get_app(db, tenant_code, app_id)
        rows = (
            await db.execute(
                select(OpenCredential)
                .where(
                    OpenCredential.app_id == app_id,
                    OpenCredential.cred_type == "api",
                    OpenCredential.is_deleted == 0,
                )
                .order_by(OpenCredential.id.desc())
            )
        ).scalars().all()
        return [CredentialService._to_out(c) for c in rows]

    @staticmethod
    async def create_credential(
        db: AsyncSession,
        tenant_code: str,
        app_id: int,
        *,
        scope: List[str],
        ip_whitelist: str,
        expires_at: Optional[datetime],
        user_id: Optional[int],
    ) -> dict:
        await AppService.get_app(db, tenant_code, app_id)
        scope = _validate_scope(scope)

        access_key = keygen.gen_app_key()
        secret = keygen.gen_app_secret()
        cred = OpenCredential(
            app_id=app_id,
            tenant_code=tenant_code,
            cred_type="api",
            access_key=access_key,
            secret_store=keygen.encrypt_secret(secret),
            scope=scope,
            ip_whitelist=ip_whitelist or "",
            status="enabled",
            expires_at=expires_at,
            created_by=user_id,
        )
        db.add(cred)
        await db.flush()
        await db.refresh(cred)  # 回填 server_default 的 created_at，避免异步下惰性刷新报错
        out = CredentialService._to_out(cred)
        out["secret"] = secret  # 仅此一次返回明文
        return out

    @staticmethod
    async def _get_owned(
        db: AsyncSession, tenant_code: str, credential_id: int, cred_type: str = "api"
    ) -> OpenCredential:
        cred = await db.scalar(
            select(OpenCredential).where(
                OpenCredential.id == credential_id,
                OpenCredential.tenant_code == tenant_code,
                OpenCredential.cred_type == cred_type,
                OpenCredential.is_deleted == 0,
            )
        )
        if not cred:
            raise BizException("凭证不存在")
        return cred

    @staticmethod
    async def update_scope(
        db: AsyncSession,
        tenant_code: str,
        credential_id: int,
        *,
        scope: Optional[List[str]],
        ip_whitelist: Optional[str],
    ) -> dict:
        cred = await CredentialService._get_owned(db, tenant_code, credential_id)
        if scope is not None:
            cred.scope = _validate_scope(scope)
        if ip_whitelist is not None:
            cred.ip_whitelist = ip_whitelist
        await db.flush()
        invalidate_credential_cache(cred.access_key)
        return CredentialService._to_out(cred)

    @staticmethod
    async def reset_secret(
        db: AsyncSession, tenant_code: str, credential_id: int
    ) -> dict:
        cred = await CredentialService._get_owned(db, tenant_code, credential_id)
        secret = keygen.gen_app_secret()
        cred.secret_store = keygen.encrypt_secret(secret)
        cred.status = "enabled"
        await db.flush()
        invalidate_credential_cache(cred.access_key)
        out = CredentialService._to_out(cred)
        out["secret"] = secret
        return out

    @staticmethod
    async def revoke(db: AsyncSession, tenant_code: str, credential_id: int) -> None:
        cred = await CredentialService._get_owned(db, tenant_code, credential_id)
        cred.status = "revoked"
        await db.flush()
        invalidate_credential_cache(cred.access_key)
