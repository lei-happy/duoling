"""
日志脱敏工具

用于工具调用日志中的参数 / 结果摘要的脱敏，避免敏感信息（手机号、身份证、银行卡）
明文落库。
"""

from __future__ import annotations

import re
from typing import Any

_PHONE = re.compile(r"(?<!\d)(1\d{2})\d{4}(\d{4})(?!\d)")
_ID_CARD = re.compile(r"(?<!\w)(\d{6})\d{8}(\d{4})(?!\w)")
_BANK_CARD = re.compile(r"(?<!\d)(\d{4})\d{8,12}(\d{4})(?!\d)")
_SENSITIVE_KEYS = {"password", "passwd", "pwd", "api_key", "apikey", "token", "secret"}


def desensitize_text(text: str) -> str:
    if not text:
        return text
    text = _PHONE.sub(r"\1****\2", text)
    text = _ID_CARD.sub(r"\1********\2", text)
    text = _BANK_CARD.sub(r"\1****\2", text)
    return text


def desensitize_obj(obj: Any) -> Any:
    """递归脱敏任意 JSON-like 对象"""
    if isinstance(obj, str):
        return desensitize_text(obj)
    if isinstance(obj, dict):
        out: dict[str, Any] = {}
        for k, v in obj.items():
            if isinstance(k, str) and k.lower() in _SENSITIVE_KEYS:
                out[k] = "***"
            else:
                out[k] = desensitize_obj(v)
        return out
    if isinstance(obj, list):
        return [desensitize_obj(x) for x in obj]
    return obj
