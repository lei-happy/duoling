"""凭证解析（数据面鉴权用）

用 access_key 一次平台库查询定位凭证 + 租户 + scope + 状态，供数据面鉴权。
带短 TTL Redis 缓存（多实例共享）；吊销/重置/停用时由控制面主动失效，保证秒级生效。
Redis 不可用时不缓存（每次查库），保证正确性优先。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select

from app.core.database import db_manager
from app.modules.open_platform.models.platform.open_credential import OpenCredential
from app.modules.open_platform.models.platform.open_app import OpenApp
from app.modules.open_platform.security import ratelimit

_CACHE_TTL = 60


@dataclass
class CredentialView:
    id: int
    app_id: int
    tenant_code: str
    cred_type: str
    secret_store: str
    scope: List[str]
    ip_whitelist: str
    status: str
    app_status: str
    expires_at: Optional[str] = None  # ISO 字符串，便于缓存序列化

    def is_active(self) -> bool:
        if self.status != "enabled" or self.app_status != "enabled":
            return False
        if self.expires_at:
            try:
                if datetime.fromisoformat(self.expires_at) < datetime.now():
                    return False
            except ValueError:
                pass
        return True


def _cache_key(access_key: str) -> str:
    return f"cred:{access_key}"


def invalidate_credential_cache(access_key: str) -> None:
    client = ratelimit._get_redis()
    if client is not None:
        try:
            client.delete(f"op:{_cache_key(access_key)}")
        except Exception:
            pass


def _cache_get(access_key: str) -> Optional[CredentialView]:
    client = ratelimit._get_redis()
    if client is None:
        return None
    try:
        raw = client.get(f"op:{_cache_key(access_key)}")
        if raw:
            return CredentialView(**json.loads(raw))
    except Exception:
        return None
    return None


async def resolve_by_access_key(access_key: str) -> Optional[CredentialView]:
    """按 access_key 解析凭证视图（含租户/scope/状态）。找不到返回 None。"""
    cached = _cache_get(access_key)
    if cached is not None:
        return cached

    async for db in db_manager.get_platform_session():
        cred = await db.scalar(
            select(OpenCredential).where(
                OpenCredential.access_key == access_key,
                OpenCredential.is_deleted == 0,
            )
        )
        if not cred:
            return None
        app = await db.scalar(select(OpenApp).where(OpenApp.id == cred.app_id))
        view = CredentialView(
            id=cred.id,
            app_id=cred.app_id,
            tenant_code=cred.tenant_code,
            cred_type=cred.cred_type,
            secret_store=cred.secret_store,
            scope=list(cred.scope or []),
            ip_whitelist=cred.ip_whitelist or "",
            status=cred.status,
            app_status=(app.status if app else "disabled"),
            expires_at=cred.expires_at.isoformat() if cred.expires_at else None,
        )
        _store_cache(view, access_key)
        return view
    return None


def _store_cache(view: CredentialView, access_key: str) -> None:
    client = ratelimit._get_redis()
    if client is None:
        return
    try:
        client.set(
            f"op:{_cache_key(access_key)}",
            json.dumps(asdict(view)),
            ex=_CACHE_TTL,
        )
    except Exception:
        pass
