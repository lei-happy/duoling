"""
日志脱敏工具

用于工具调用日志中的参数 / 结果摘要的脱敏，避免敏感信息（手机号、身份证、银行卡）
明文落库。
"""

from __future__ import annotations

import re
from typing import Any

_PHONE = re.compile(r"(?<!\d)(1\d{2})\d{4}(\d{4})(?!\d)")
# 身份证反向断言统一用数字边界 `\d`（与手机号/银行卡一致）。
# 若用 `\w`，Unicode 下中文亦属 `\w`，身份证紧邻中文时会跳过本规则、
# 错误回退到银行卡掩码（BUG-CLI-002）。同时兼容 18 位与 15 位旧身份证。
_ID_CARD_18 = re.compile(r"(?<!\d)(\d{6})\d{8}(\d{4})(?!\d)")
_ID_CARD_15 = re.compile(r"(?<!\d)(\d{6})\d{5}(\d{4})(?!\d)")
_BANK_CARD = re.compile(r"(?<!\d)(\d{4})\d{8,12}(\d{4})(?!\d)")
_SENSITIVE_KEYS = {"password", "passwd", "pwd", "api_key", "apikey", "token", "secret"}


def desensitize_text(text: str) -> str:
    if not text:
        return text
    text = _PHONE.sub(r"\1****\2", text)
    # 先按身份证规则处理（18 位再 15 位），避免 18 位身份证被银行卡规则抢先命中。
    text = _ID_CARD_18.sub(r"\1********\2", text)
    text = _ID_CARD_15.sub(r"\1*****\2", text)
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
