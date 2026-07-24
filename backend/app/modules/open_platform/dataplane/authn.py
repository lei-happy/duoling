"""数据面鉴权

- API 通道：HMAC-SHA256 签名（X-Zt-Key/Timestamp/Nonce/Sign），验签需服务端解密密钥
- MCP 通道：Bearer Token（access_key.token），哈希比对

统一校验：凭证有效性、有效期、IP 白名单、时间戳窗口、nonce 防重放、scope、限流。
"""

import time
from typing import Optional, Tuple

from fastapi import Request

from app.core.config import get_settings

from app.modules.open_platform.auth.resolver import (
    CredentialView,
    resolve_by_access_key,
)
from app.modules.open_platform.capabilities.context import OpenContext
from app.modules.open_platform.security import keygen, signing, ratelimit
from app.modules.open_platform.dataplane import errors


def _timestamp_window() -> int:
    return int(getattr(get_settings(), "OPEN_TIMESTAMP_WINDOW_SEC", 300))


def _rate_limit_per_min() -> int:
    return int(getattr(get_settings(), "OPEN_RATE_LIMIT_PER_MIN", 600))


def client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else ""


def _check_ip(cred: CredentialView, ip: str) -> None:
    wl = (cred.ip_whitelist or "").strip()
    if not wl:
        return
    allowed = {x.strip() for x in wl.split(",") if x.strip()}
    if ip not in allowed:
        raise errors.forbidden_ip()


def _check_rate_limit(cred: CredentialView) -> None:
    if ratelimit.hit_rate_limit(f"cred:{cred.id}", _rate_limit_per_min(), 60):
        raise errors.rate_limited()


def ensure_scope(cred: CredentialView, capability_code: str) -> None:
    if capability_code not in (cred.scope or []):
        raise errors.forbidden_scope(capability_code)


async def authenticate_api(
    request: Request, body: bytes
) -> Tuple[CredentialView, OpenContext]:
    """校验 API 签名，返回 (凭证视图, 上下文)。"""
    key = request.headers.get("x-zt-key")
    ts = request.headers.get("x-zt-timestamp")
    nonce = request.headers.get("x-zt-nonce")
    sign = request.headers.get("x-zt-sign")
    if not all([key, ts, nonce, sign]):
        raise errors.unauthorized("缺少签名头，请检查接入配置")

    cred = await resolve_by_access_key(key)
    if not cred or cred.cred_type != "api" or not cred.is_active():
        raise errors.unauthorized()

    ip = client_ip(request)
    _check_ip(cred, ip)

    # 时间戳窗口
    try:
        skew = abs(int(time.time()) - int(ts))
    except (TypeError, ValueError):
        raise errors.replay()
    if skew > _timestamp_window():
        raise errors.replay()

    # nonce 防重放（ttl 取 2 倍窗口）
    if ratelimit.seen_nonce(f"{key}:{nonce}", _timestamp_window() * 2):
        raise errors.replay()

    # 验签（解密取回明文密钥）
    try:
        secret = keygen.decrypt_secret(cred.secret_store)
    except Exception:
        raise errors.unauthorized()
    ok = signing.verify_signature(
        secret,
        sign,
        method=request.method,
        path=request.url.path,
        query=dict(request.query_params),
        body=body,
        timestamp=ts,
        nonce=nonce,
    )
    if not ok:
        raise errors.unauthorized("签名校验失败，请检查密钥与签名算法")

    _check_rate_limit(cred)

    ctx = OpenContext(
        tenant_code=cred.tenant_code,
        channel="api",
        app_id=cred.app_id,
        credential_id=cred.id,
        request_id=request.headers.get("x-request-id") or nonce,
        scope=list(cred.scope or []),
        client_ip=ip,
        user_agent=request.headers.get("user-agent", "")[:255],
    )
    return cred, ctx


async def authenticate_mcp(
    request: Request, expected_credential_id: Optional[int] = None
) -> Tuple[CredentialView, OpenContext]:
    """校验 MCP Bearer Token，返回 (凭证视图, 上下文)。"""
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise errors.unauthorized("缺少 Authorization: Bearer 令牌")
    raw = auth[7:].strip()
    if "." not in raw:
        raise errors.unauthorized()
    key, token = raw.split(".", 1)

    cred = await resolve_by_access_key(key)
    if not cred or cred.cred_type != "mcp" or not cred.is_active():
        raise errors.unauthorized()
    if expected_credential_id is not None and cred.id != expected_credential_id:
        raise errors.unauthorized()
    if not keygen.verify_secret(token, cred.secret_store):
        raise errors.unauthorized()

    ip = client_ip(request)
    _check_ip(cred, ip)
    _check_rate_limit(cred)

    ctx = OpenContext(
        tenant_code=cred.tenant_code,
        channel="mcp",
        app_id=cred.app_id,
        credential_id=cred.id,
        request_id=request.headers.get("x-request-id") or f"mcp-{int(time.time()*1000)}",
        scope=list(cred.scope or []),
        client_ip=ip,
        user_agent=request.headers.get("user-agent", "")[:255],
    )
    return cred, ctx
