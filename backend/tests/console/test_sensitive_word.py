"""运营后台 · 敏感词库（纯逻辑，零 DB）测试

覆盖两处容易出错的地方：

1. **缓存失效范围**：``scope=all`` 的词被所有范围引用，改它必须清空全部缓存，
   只清 ``all`` 这一个键会让 ecosystem 继续用旧词库直到 TTL 到期。
2. **录入校验**：单字词会大面积误伤，必须挡在入库前。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.3
对应代码：backend/app/modules/console/services/system/sensitive_word_service.py
"""

from __future__ import annotations

import pytest

from app.common.exceptions import BizException
from app.modules.console.models.system.sensitive_word import (
    SensitiveWordAction,
    SensitiveWordCategory,
    SensitiveWordScope,
)
from app.modules.console.services.system.sensitive_word_service import (
    _word_cache,
    SensitiveWordService,
    invalidate_sensitive_word_cache,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    _word_cache.clear()
    yield
    _word_cache.clear()


class TestCacheInvalidation:
    def _fill(self):
        _word_cache["all"] = (9e18, ())
        _word_cache["ecosystem"] = (9e18, ())

    def test_invalidate_specific_scope(self):
        self._fill()
        invalidate_sensitive_word_cache(SensitiveWordScope.ECOSYSTEM)
        assert "ecosystem" not in _word_cache
        assert "all" in _word_cache

    def test_invalidate_all_scope_clears_everything(self):
        """scope=all 的词被所有范围引用，改它必须清空全部缓存。

        只清 all 这一个键，ecosystem 会继续用含旧词的缓存直到 TTL 到期——
        运营在界面上删掉一个误伤词，却发现还在拦，这类问题极难排查。
        """
        self._fill()
        invalidate_sensitive_word_cache(SensitiveWordScope.ALL)
        assert _word_cache == {}

    def test_invalidate_none_clears_everything(self):
        self._fill()
        invalidate_sensitive_word_cache()
        assert _word_cache == {}

    def test_invalidate_missing_scope_is_safe(self):
        invalidate_sensitive_word_cache("not_exist")


class TestCleanWord:
    def test_trims_whitespace(self):
        assert SensitiveWordService._clean_word("  走私  ") == "走私"

    @pytest.mark.parametrize("bad", ["", "   ", None])
    def test_empty_rejected(self, bad):
        with pytest.raises(BizException, match="不能为空"):
            SensitiveWordService._clean_word(bad)

    def test_single_char_rejected(self):
        """单字词会大面积误伤正常内容，运营很容易手滑录入。"""
        with pytest.raises(BizException, match="至少要 2 个字"):
            SensitiveWordService._clean_word("枪")

    def test_too_long_rejected(self):
        with pytest.raises(BizException, match="太长"):
            SensitiveWordService._clean_word("词" * 65)

    def test_max_length_accepted(self):
        assert len(SensitiveWordService._clean_word("词" * 64)) == 64


class TestValidate:
    def test_valid_values_pass(self):
        SensitiveWordService._validate(
            category=SensitiveWordCategory.CONTRABAND,
            action=SensitiveWordAction.REVIEW,
            scope=SensitiveWordScope.ECOSYSTEM,
        )

    def test_bad_category(self):
        with pytest.raises(BizException, match="分类"):
            SensitiveWordService._validate(category=99)

    def test_bad_action(self):
        with pytest.raises(BizException, match="处置"):
            SensitiveWordService._validate(action=99)

    def test_bad_scope(self):
        with pytest.raises(BizException, match="适用范围"):
            SensitiveWordService._validate(scope="whatever")

    def test_none_values_skipped(self):
        SensitiveWordService._validate()


class TestErrorMessagesAreHumanReadable:
    """面向运营的提示不能出现字段名、错误码等技术语言。"""

    @pytest.mark.parametrize(
        "call",
        [
            lambda: SensitiveWordService._clean_word(""),
            lambda: SensitiveWordService._clean_word("枪"),
            lambda: SensitiveWordService._validate(category=99),
            lambda: SensitiveWordService._validate(action=99),
            lambda: SensitiveWordService._validate(scope="x"),
        ],
    )
    def test_no_technical_jargon(self, call):
        with pytest.raises(BizException) as exc:
            call()
        msg = exc.value.message
        for bad in ("category", "action", "scope", "word", "None", "null", "ERR"):
            assert bad not in msg, f"提示里出现技术词「{bad}」：{msg}"
