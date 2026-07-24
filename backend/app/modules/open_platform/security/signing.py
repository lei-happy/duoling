"""HMAC-SHA256 请求签名（API 凭证）

签名串：
    method + "\n" + path + "\n" + canonicalQuery + "\n" +
    sha256Hex(body) + "\n" + timestamp + "\n" + nonce

sign = HMAC_SHA256(stringToSign, AppSecret) 的十六进制。

服务端用同算法重算比对（compare_digest）。时间戳窗口 + nonce 去重防重放。
"""

import hashlib
import hmac
from typing import Mapping
from urllib.parse import urlencode


def _canonical_query(query: Mapping[str, str]) -> str:
    if not query:
        return ""
    items = sorted((str(k), str(v)) for k, v in query.items())
    return urlencode(items)


def build_string_to_sign(
    method: str,
    path: str,
    query: Mapping[str, str],
    body: bytes,
    timestamp: str,
    nonce: str,
) -> str:
    body_hash = hashlib.sha256(body or b"").hexdigest()
    return "\n".join(
        [
            method.upper(),
            path,
            _canonical_query(query),
            body_hash,
            str(timestamp),
            nonce,
        ]
    )


def sign(secret: str, string_to_sign: str) -> str:
    return hmac.new(
        secret.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def verify_signature(
    secret: str,
    provided_sign: str,
    *,
    method: str,
    path: str,
    query: Mapping[str, str],
    body: bytes,
    timestamp: str,
    nonce: str,
) -> bool:
    expected = sign(
        secret,
        build_string_to_sign(method, path, query, body, timestamp, nonce),
    )
    return hmac.compare_digest(expected, provided_sign or "")
