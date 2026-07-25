"""服务平台 · 发布预检（纯逻辑，零 DB）测试

联系方式硬拦截是「不许绕过平台私下成交」的第一道闸门，用户一定会尝试规避写法，
因此这里重点覆盖各种变形；同时要保证不误伤正常文案——误拦一条真实货源的代价
远大于漏过一条。

敏感词不在代码里硬编码，规则由运营维护的词库注入，因此这里用构造的规则集测试
匹配与处置逻辑本身。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.3
对应代码：backend/app/modules/client/services/ecosystem/content_guard.py
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.modules.client.services.ecosystem.content_guard import (
    BlockFlag,
    PrecheckInput,
    SensitiveWordRule,
    SuspiciousFlag,
    find_contact_info,
    find_sensitive_words,
    normalize_for_scan,
    run_precheck,
    strip_noise,
)
from app.modules.console.models.system.sensitive_word import (
    SensitiveWordAction,
    SensitiveWordCategory,
)

NOW = datetime(2026, 7, 25, 12, 0, 0)

BLOCK_WORD = SensitiveWordRule(
    word="走私", category=SensitiveWordCategory.OTHER,
    action=SensitiveWordAction.BLOCK,
)
CONTRABAND_WORD = SensitiveWordRule(
    word="危化品", category=SensitiveWordCategory.CONTRABAND,
    action=SensitiveWordAction.BLOCK,
)
REVIEW_WORD = SensitiveWordRule(
    word="低价甩货", category=SensitiveWordCategory.OTHER,
    action=SensitiveWordAction.REVIEW,
)
ASCII_WORD = SensitiveWordRule(
    word="VX", category=SensitiveWordCategory.DIVERSION,
    action=SensitiveWordAction.BLOCK,
)

ALL_RULES = [BLOCK_WORD, CONTRABAND_WORD, REVIEW_WORD, ASCII_WORD]


class TestNormalize:
    def test_fullwidth_digits(self):
        assert "13812345678" in normalize_for_scan("１３８１２３４５６７８")

    def test_chinese_digits(self):
        assert "13812345678" in normalize_for_scan("一三八一二三四五六七八")

    def test_separators_between_digits_removed(self):
        assert normalize_for_scan("138-1234-5678") == "13812345678"
        assert normalize_for_scan("138 1234 5678") == "13812345678"
        assert normalize_for_scan("138.1234.5678") == "13812345678"

    def test_plain_text_untouched(self):
        assert normalize_for_scan("杭州到成都 8 台") == "杭州到成都 8 台"

    def test_empty(self):
        assert normalize_for_scan("") == ""
        assert normalize_for_scan(None) == ""


class TestStripNoise:
    def test_removes_word_splitting_chars(self):
        assert strip_noise("走*私") == "走私"
        assert strip_noise("代-开-发-票") == "代开发票"
        assert strip_noise("危 化 品") == "危化品"

    def test_keeps_sentence_punctuation(self):
        """句读不剔除：全量剔除标点会让相邻正常词拼成敏感词，造成跨词误伤。"""
        assert strip_noise("装车，卸货。") == "装车，卸货。"

    def test_empty(self):
        assert strip_noise("") == ""
        assert strip_noise(None) == ""


class TestFindContactInfo:
    @pytest.mark.parametrize(
        "text",
        [
            "有货联系 13812345678",
            "电话138-1234-5678",
            "手机 138 1234 5678",
            "联系一三八一二三四五六七八",
            "拨１３８１２３４５６７８",
            "微信 zhangsan_888",
            "vx:abc123456",
            "加v abc888888",
            "QQ 123456789",
            "扣扣：987654321",
            "详情看 www.example.com",
            "https://t.me/abc",
            "上 huoyuan.com 找我",
            "座机 057188889999",
        ],
    )
    def test_variants_detected(self, text):
        assert find_contact_info(text), f"未识别：{text}"

    @pytest.mark.parametrize(
        "text",
        [
            "杭州到成都 8 台商品车",
            "需要封闭板运输，能开专票",
            "微信同号",              # 只是说明，没给账号
            "月结 30 天",
            "要求 1-8 位轿运车",
            "总重 20 吨，长度 17.5 米",
            "2026-07-27 装车",
            "报价 12000 元",
            "",
        ],
    )
    def test_no_false_positive(self, text):
        assert find_contact_info(text) == [], f"误拦：{text}"

    def test_reports_which_kind(self):
        assert "手机号" in find_contact_info("联系 13812345678")
        assert "微信号" in find_contact_info("微信 zhangsan_888")
        assert "外部链接" in find_contact_info("看 www.abc.com")


class TestFindSensitiveWords:
    def test_plain_hit(self):
        assert find_sensitive_words("顺带走私货", ALL_RULES) == [BLOCK_WORD]

    def test_evasion_by_separator(self):
        assert find_sensitive_words("顺带走*私货", ALL_RULES) == [BLOCK_WORD]

    def test_ascii_case_insensitive(self):
        """运营录入 VX，用户写 vx 也要命中。"""
        assert find_sensitive_words("加vx联系", ALL_RULES) == [ASCII_WORD]

    def test_clean_text(self):
        assert find_sensitive_words("正常的商品车运输需求", ALL_RULES) == []

    def test_empty_library_matches_nothing(self):
        """词库为空时不该拦下任何东西。"""
        assert find_sensitive_words("顺带走私货", []) == []

    def test_empty_text(self):
        assert find_sensitive_words("", ALL_RULES) == []

    def test_blank_word_in_library_ignored(self):
        """脏数据（空词）不能变成「匹配一切」。"""
        rules = [SensitiveWordRule(word="   ")]
        assert find_sensitive_words("任意内容", rules) == []

    def test_multiple_hits(self):
        hits = find_sensitive_words("走私危化品", ALL_RULES)
        assert set(h.word for h in hits) == {"走私", "危化品"}


class TestSensitiveWordBlocking:
    def test_block_action_blocks(self):
        r = run_precheck(
            PrecheckInput(
                texts={"标题": "顺带走私货"}, sensitive_words=ALL_RULES, now=NOW
            )
        )
        assert r.blocked is True
        assert BlockFlag.SENSITIVE_WORD in r.block_flags
        assert "标题" in r.block_message

    def test_contraband_gets_its_own_message(self):
        """违禁品与其他敏感词的用户处境不同，提示不能混为一句。"""
        r = run_precheck(
            PrecheckInput(
                texts={"标题": "运输危化品"}, sensitive_words=ALL_RULES, now=NOW
            )
        )
        assert BlockFlag.FORBIDDEN_CARGO in r.block_flags
        assert "专门资质" in r.block_message

    def test_review_action_does_not_block(self):
        """运营对某个词没把握时设为「转人工」，不该阻断提交。"""
        r = run_precheck(
            PrecheckInput(
                texts={"备注": "低价甩货"}, sensitive_words=ALL_RULES, now=NOW
            )
        )
        assert r.blocked is False
        assert SuspiciousFlag.SENSITIVE_WORD_REVIEW in r.suspicious_flags
        assert "低价甩货" in r.suspicious_notes[0]

    def test_cargo_name_is_scanned(self):
        r = run_precheck(
            PrecheckInput(cargo_name="危化品", sensitive_words=ALL_RULES, now=NOW)
        )
        assert BlockFlag.FORBIDDEN_CARGO in r.block_flags

    def test_hit_words_recorded_for_stats(self):
        """命中词要回传，供 Service 回写 hit_count，让运营看出哪些词是死词。"""
        r = run_precheck(
            PrecheckInput(
                texts={"标题": "走私", "备注": "低价甩货"},
                sensitive_words=ALL_RULES,
                now=NOW,
            )
        )
        assert set(r.hit_words) == {"走私", "低价甩货"}

    def test_empty_library_does_not_block(self):
        r = run_precheck(
            PrecheckInput(texts={"标题": "顺带走私货"}, sensitive_words=[], now=NOW)
        )
        assert r.blocked is False


class TestHardBlocks:
    def test_contact_in_text_blocks_with_field_name(self):
        r = run_precheck(
            PrecheckInput(texts={"其他要求": "有货直接打 13812345678"}, now=NOW)
        )
        assert r.blocked is True
        assert BlockFlag.CONTACT_IN_TEXT in r.block_flags
        # 文案要指明是哪一栏、并说明为什么不让填
        assert "其他要求" in r.block_message
        assert "手机号" in r.block_message
        assert "自动互相看到联系方式" in r.block_message

    def test_expired_license_blocks_and_names_it(self):
        r = run_precheck(
            PrecheckInput(expired_licenses=["道路运输经营许可证"], now=NOW)
        )
        assert BlockFlag.LICENSE_EXPIRED in r.block_flags
        assert "道路运输经营许可证" in r.block_message
        assert "请先更新" in r.block_message

    def test_same_route_blocks(self):
        r = run_precheck(
            PrecheckInput(
                from_province="浙江省", from_city="杭州市",
                to_province="浙江省", to_city="杭州市", now=NOW,
            )
        )
        assert BlockFlag.SAME_ROUTE in r.block_flags

    def test_same_city_different_district_allowed(self):
        """同城不同区是真实的短途业务，不能拦。"""
        r = run_precheck(
            PrecheckInput(
                from_province="浙江省", from_city="杭州市", from_district="萧山区",
                to_province="浙江省", to_city="杭州市", to_district="余杭区", now=NOW,
            )
        )
        assert BlockFlag.SAME_ROUTE not in r.block_flags

    def test_missing_destination_not_treated_as_same_route(self):
        """运力可「接受任意流向」而不填目的地，此时不该报错。"""
        r = run_precheck(
            PrecheckInput(from_province="浙江省", from_city="杭州市", now=NOW)
        )
        assert BlockFlag.SAME_ROUTE not in r.block_flags

    def test_past_window_blocks(self):
        r = run_precheck(
            PrecheckInput(window_start=NOW - timedelta(hours=1), now=NOW)
        )
        assert BlockFlag.WINDOW_PASSED in r.block_flags

    def test_future_window_passes(self):
        r = run_precheck(
            PrecheckInput(window_start=NOW + timedelta(hours=1), now=NOW)
        )
        assert r.blocked is False

    def test_only_one_message_at_a_time(self):
        """同时命中多条时只给一条提示，避免一长串错误让人无从下手。"""
        r = run_precheck(
            PrecheckInput(
                texts={"标题": "打 13812345678"},
                sensitive_words=ALL_RULES,
                cargo_name="危化品",
                expired_licenses=["道路运输经营许可证"],
                from_province="浙江省", from_city="杭州市",
                to_province="浙江省", to_city="杭州市",
                window_start=NOW - timedelta(days=1),
                now=NOW,
            )
        )
        assert len(r.block_flags) == 1
        assert r.block_flags[0] == BlockFlag.CONTACT_IN_TEXT

    def test_clean_post_passes(self):
        r = run_precheck(
            PrecheckInput(
                texts={
                    "标题": "杭州 → 成都 商品车 8 台",
                    "其他要求": "需要封闭板运输，月结 30 天",
                },
                sensitive_words=ALL_RULES,
                from_province="浙江省", from_city="杭州市",
                to_province="四川省", to_city="成都市",
                window_start=NOW + timedelta(days=2),
                cargo_name="商品车",
                now=NOW,
            )
        )
        assert r.blocked is False
        assert r.block_message is None
        assert r.suspicious_flags == []


class TestSuspiciousRules:
    def test_too_many_posts_flags_but_not_blocks(self):
        r = run_precheck(PrecheckInput(posts_last_24h=25, now=NOW))
        assert r.blocked is False
        assert SuspiciousFlag.TOO_MANY_POSTS in r.suspicious_flags
        assert "25" in r.suspicious_notes[0]

    def test_at_threshold_not_flagged(self):
        r = run_precheck(PrecheckInput(posts_last_24h=20, now=NOW))
        assert SuspiciousFlag.TOO_MANY_POSTS not in r.suspicious_flags

    def test_duplicate_like_flagged(self):
        r = run_precheck(PrecheckInput(similar_post_no="HY202607200001", now=NOW))
        assert SuspiciousFlag.DUPLICATE_LIKE in r.suspicious_flags
        assert "HY202607200001" in r.suspicious_notes[0]

    def test_new_tenant_first_post_flagged(self):
        r = run_precheck(
            PrecheckInput(tenant_age_days=10, is_first_post=True, now=NOW)
        )
        assert SuspiciousFlag.NEW_TENANT in r.suspicious_flags

    def test_new_tenant_later_post_not_flagged(self):
        r = run_precheck(
            PrecheckInput(tenant_age_days=10, is_first_post=False, now=NOW)
        )
        assert SuspiciousFlag.NEW_TENANT not in r.suspicious_flags

    def test_old_tenant_not_flagged(self):
        r = run_precheck(
            PrecheckInput(tenant_age_days=400, is_first_post=True, now=NOW)
        )
        assert SuspiciousFlag.NEW_TENANT not in r.suspicious_flags

    @pytest.mark.parametrize("ratio", [0.3, 4.0])
    def test_price_anomaly_flagged(self, ratio):
        r = run_precheck(PrecheckInput(price_ratio_to_baseline=ratio, now=NOW))
        assert SuspiciousFlag.PRICE_ABNORMAL in r.suspicious_flags

    @pytest.mark.parametrize("ratio", [0.5, 1.0, 3.0])
    def test_price_within_range_not_flagged(self, ratio):
        r = run_precheck(PrecheckInput(price_ratio_to_baseline=ratio, now=NOW))
        assert SuspiciousFlag.PRICE_ABNORMAL not in r.suspicious_flags

    def test_price_rule_off_when_no_baseline(self):
        """一期成交样本不足，Service 不传基线，该规则应自然关闭。"""
        r = run_precheck(PrecheckInput(price_ratio_to_baseline=None, now=NOW))
        assert SuspiciousFlag.PRICE_ABNORMAL not in r.suspicious_flags

    def test_suspicious_does_not_prevent_submit(self):
        r = run_precheck(
            PrecheckInput(
                texts={"备注": "低价甩货"},
                sensitive_words=ALL_RULES,
                posts_last_24h=99,
                tenant_age_days=1,
                is_first_post=True,
                similar_post_no="HY1",
                price_ratio_to_baseline=0.1,
                now=NOW,
            )
        )
        assert r.blocked is False
        assert len(r.suspicious_flags) == 5
