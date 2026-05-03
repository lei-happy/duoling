"""
对称加密工具

用于 AiModelProvider.api_key 加密存储。
密钥来自 Settings.APP_SECRET_KEY，沿用现有配置避免新增环境变量。
"""

from __future__ import annotations

import base64
import hashlib

from app.core.config import get_settings


def _fernet_key() -> bytes:
    """从 APP_SECRET_KEY 派生 Fernet 兼容的 32 字节 base64 key"""
    settings = get_settings()
    raw = (settings.APP_SECRET_KEY or "zhitu-default-secret").encode("utf-8")
    digest = hashlib.sha256(raw).digest()
    return base64.urlsafe_b64encode(digest)


def _get_fernet():
    try:
        from cryptography.fernet import Fernet
    except ImportError as e:
        raise RuntimeError(
            "未安装 cryptography 包，请执行 `pip install cryptography>=42.0.0`"
        ) from e
    return Fernet(_fernet_key())


_PREFIX = "enc::"


def encrypt_api_key(plaintext: str) -> str:
    """加密 api_key；返回带 `enc::` 前缀的 base64 字符串"""
    if not plaintext:
        return ""
    if plaintext.startswith(_PREFIX):
        return plaintext  # 幂等
    f = _get_fernet()
    token = f.encrypt(plaintext.encode("utf-8"))
    return _PREFIX + token.decode("utf-8")


def decrypt_api_key(stored: str) -> str:
    """解密 api_key；若不带 `enc::` 前缀则视为明文（兼容老数据）"""
    if not stored:
        return ""
    if not stored.startswith(_PREFIX):
        return stored
    f = _get_fernet()
    return f.decrypt(stored[len(_PREFIX):].encode("utf-8")).decode("utf-8")


def mask_api_key(stored: str) -> str:
    """对外展示用：只露后 4 位"""
    try:
        plain = decrypt_api_key(stored) if stored else ""
    except Exception:
        plain = ""
    if not plain:
        return ""
    if len(plain) <= 8:
        return "****"
    return f"{plain[:4]}****{plain[-4:]}"
