"""凭证生成与哈希

- AppKey：公开标识 ak_<随机>
- AppSecret：机密 sk_<高熵随机>，仅展示一次，库存哈希
- MCP Token：mcp_<高熵随机>，同样只存哈希
- server_slug：MCP 端点路径片段

哈希用 HMAC-SHA256(secret, key=APP_SECRET_KEY)，比对用 hmac.compare_digest 防时序攻击。
"""

import base64
import hashlib
import hmac
import secrets
from functools import lru_cache

from cryptography.fernet import Fernet

from app.core.config import get_settings


def _rand(nbytes: int = 24) -> str:
    return secrets.token_urlsafe(nbytes).rstrip("=")


def gen_app_key() -> str:
    return f"ak_{_rand(12)}"


def gen_app_secret() -> str:
    return f"sk_{_rand(24)}"


def gen_mcp_key() -> str:
    return f"mcp_{_rand(12)}"


def gen_mcp_token() -> str:
    return f"mcpt_{_rand(24)}"


def gen_server_slug() -> str:
    return secrets.token_hex(6)


def hash_secret(secret: str) -> str:
    """对 secret/token 做 HMAC 哈希（不可逆），用于落库。"""
    key = get_settings().APP_SECRET_KEY.encode("utf-8")
    return hmac.new(key, secret.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_secret(secret: str, secret_hash: str) -> bool:
    """恒定时间比对（用于 MCP Bearer Token：明文直传 + 哈希比对）。"""
    return hmac.compare_digest(hash_secret(secret), secret_hash or "")


# ---- API 密钥可逆加密（HMAC 签名校验需要服务端持有明文密钥） ----
# APP_SECRET_KEY 派生 Fernet 对称密钥；密钥轮换需配套重加密迁移。

@lru_cache()
def _fernet() -> Fernet:
    digest = hashlib.sha256(get_settings().APP_SECRET_KEY.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(secret: str) -> str:
    """加密 API AppSecret 落库（可解密，供签名校验时取回明文）。"""
    return _fernet().encrypt(secret.encode("utf-8")).decode("utf-8")


def decrypt_secret(ciphertext: str) -> str:
    """解密 API AppSecret。"""
    return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
