"""AI 数字人（client）· 日志脱敏（纯逻辑，零 DB）测试

AI 工具调用日志需对手机号 / 身份证 / 银行卡脱敏，敏感 key（password/token 等）
整体屏蔽，避免明文落库。

对应需求：项目文档/02.需求文档/02.企业端/11.AI数字员工/**
对应代码：backend/app/modules/ai/security/desensitize.py
覆盖用例：TC-CLI-AI-001 ~ TC-CLI-AI-012
"""

from __future__ import annotations

from app.modules.ai.security.desensitize import (
    desensitize_obj,
    desensitize_text,
)


class TestDesensitizeText:
    def test_phone_masked(self):
        assert desensitize_text("联系 13812345678 请回电") == "联系 138****5678 请回电"

    def test_id_card_masked(self):
        out = desensitize_text("身份证 110101199001011234 已核验")
        assert "110101********1234" in out
        assert "199001011234" not in out

    def test_bank_card_masked(self):
        out = desensitize_text("卡号 6222021234567890123")
        assert out.startswith("卡号 6222")
        assert out.endswith("0123")
        assert "1234567890" not in out

    def test_empty_passthrough(self):
        assert desensitize_text("") == ""

    def test_plain_text_unchanged(self):
        assert desensitize_text("今天天气不错") == "今天天气不错"


class TestDesensitizeObj:
    def test_sensitive_keys_hidden(self):
        obj = {"password": "abc123", "token": "xyz", "name": "张三"}
        out = desensitize_obj(obj)
        assert out["password"] == "***"
        assert out["token"] == "***"
        assert out["name"] == "张三"

    def test_nested_structures(self):
        obj = {
            "user": {"phone": "13812345678", "pwd": "secret"},
            "cards": ["6222021234567890123"],
        }
        out = desensitize_obj(obj)
        assert out["user"]["phone"] == "138****5678"
        assert out["user"]["pwd"] == "***"
        assert out["cards"][0].startswith("6222") and out["cards"][0].endswith("0123")

    def test_non_str_passthrough(self):
        assert desensitize_obj(123) == 123
        assert desensitize_obj(None) is None
        assert desensitize_obj(True) is True
