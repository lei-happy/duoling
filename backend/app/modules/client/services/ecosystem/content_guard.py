"""服务平台发布预检（纯逻辑，零 DB）

对应 04.运营审核与风控设计.md §2.3：挂牌提交时先跑自动预检，
命中硬拦截当场失败并告诉用户怎么改，命中可疑规则则转人工并标红。

两类结论的分工要分清：
  - **硬拦截**：内容明确违规或明显填错，让用户当场改，不占用人工审核时间。
  - **可疑**：不阻断提交，写进 ``precheck_flags`` 供审核员标红参考。
    可疑规则宁可多报也不能直接拦——误拦一条真实货源的代价远大于多审一条。

需要查库的事实（敏感词库、近 24 小时发布数、租户注册天数、相似挂牌等）由
Service 先准备好后装进 ``PrecheckInput``，本模块只做判定。这样规则可被穷举测试。

**敏感词库不在本模块硬编码**：词库存在 ``sys_sensitive_word``、由运营后台维护
（见 SensitiveWordService）。源码里留一份硬编码兜底看似更安全，实际会造成
两个真相源——某个词误伤时运营在界面上找不到它、也删不掉，只能等发版。

扫描范围只包含**自由文本字段**（标题、备注、其他要求、服务承诺等）。
结构化联系人字段（``contact_name`` / ``contact_phone``）不参与扫描——
那是系统按可见性规则受控展示的，不是违规夹带。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Sequence

from app.modules.console.models.system.sensitive_word import (
    SensitiveWordAction,
    SensitiveWordCategory,
    SensitiveWordRule,
)

# ---------------------------------------------------------------------------
# 阈值（应做成运营可配，见 04 §2.3 备注；此处为默认值）
# ---------------------------------------------------------------------------

MAX_POSTS_PER_24H = 20          # 超过则转人工（疑似刷屏）
NEW_TENANT_DAYS = 30            # 注册不足此天数的租户首次发布转人工
PRICE_LOW_RATIO = 0.5           # 低于同线路均价此比例 → 可疑
PRICE_HIGH_RATIO = 3.0          # 高于同线路均价此比例 → 可疑


# ---------------------------------------------------------------------------
# 标识与用户文案
# ---------------------------------------------------------------------------

class BlockFlag:
    CONTACT_IN_TEXT = "contact_in_text"
    SENSITIVE_WORD = "sensitive_word"
    FORBIDDEN_CARGO = "forbidden_cargo"
    LICENSE_EXPIRED = "license_expired"
    SAME_ROUTE = "same_route"
    WINDOW_PASSED = "window_passed"


class SuspiciousFlag:
    SENSITIVE_WORD_REVIEW = "sensitive_word_review"
    PRICE_ABNORMAL = "price_abnormal"
    TOO_MANY_POSTS = "too_many_posts"
    DUPLICATE_LIKE = "duplicate_like"
    NEW_TENANT = "new_tenant"
    # 保险过期：不硬拦（影响理赔而非上路合法性，且各家投保节奏差异大，
    # 硬拦会误伤大量正常运力），但必须让审核员看见——出事时它最影响追偿
    INSURANCE_EXPIRED = "insurance_expired"
    # 曾被平台强制下架后又重新上架。不拦——运营下架后用户改好内容再上是正当
    # 需求，硬拦只会逼他新发一条一模一样的，反而甩掉了这段处置历史
    WAS_FORCE_DELISTED = "was_force_delisted"


# 文案直接展示给用户，必须说清「为什么」和「怎么改」，不能只说「校验失败」
BLOCK_MESSAGES = {
    BlockFlag.CONTACT_IN_TEXT: (
        "为了保护双方，请不要在信息里直接留联系方式。"
        "同行对你的信息感兴趣时，你们会自动互相看到联系方式。"
    ),
    BlockFlag.SENSITIVE_WORD: "信息里有不能发布的内容，请修改后再提交",
    BlockFlag.FORBIDDEN_CARGO: "这类货物需要专门资质，暂不支持在大厅发布",
    BlockFlag.SAME_ROUTE: "起点和终点一样，请检查一下线路",
    BlockFlag.WINDOW_PASSED: "计划装车时间已经过了，请调整时间",
}


# ---------------------------------------------------------------------------
# 联系方式识别
# ---------------------------------------------------------------------------

# 常见的手动分隔/替换手段：用户会写「138-1234-5678」「壹38…」来绕过检测。
# 扫描前先归一化，比堆更多正则更有效。
_FULLWIDTH_DIGITS = str.maketrans("０１２３４５６７８９", "0123456789")
_CN_DIGITS = {
    "零": "0", "〇": "0", "一": "1", "壹": "1", "二": "2", "贰": "2",
    "两": "2", "三": "3", "叁": "3", "四": "4", "肆": "4", "五": "5",
    "伍": "5", "六": "6", "陆": "6", "七": "7", "柒": "7", "八": "8",
    "捌": "8", "九": "9", "玖": "9",
}
_SEP_BETWEEN_DIGITS = re.compile(r"(?<=\d)[\s\-—_.。、·+*#|/\\]+(?=\d)")

_RE_MOBILE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
_RE_LANDLINE = re.compile(r"(?<!\d)0\d{2,3}\d{7,8}(?!\d)")
# 微信 / QQ：识别「关键词 + 号码/账号」的组合，避免把「微信同号」这类
# 不含实际账号的表述也拦掉——那并没有泄露联系方式。
_RE_WECHAT = re.compile(
    r"(?:微信|weixin|wechat|vx|wx|v信|加v)\s*[:：=]?\s*([A-Za-z][A-Za-z0-9_-]{5,19}|\d{6,20})",
    re.IGNORECASE,
)
_RE_QQ = re.compile(r"(?:qq|扣扣|企鹅)\s*[:：=]?\s*(\d{5,13})", re.IGNORECASE)
_RE_URL = re.compile(
    r"(?:https?://|www\.)\S+|\S+\.(?:com|cn|net|org)(?:/\S*)?", re.IGNORECASE
)


def normalize_for_scan(text: str) -> str:
    """归一化文本，抵消常见的规避手段（仅用于联系方式识别）

    依次处理：全角数字 → 半角、中文数字 → 阿拉伯数字、去掉数字之间的分隔符。

    **不要用它做敏感词匹配**：中文数字转阿拉伯数字会把「一条龙」变成
    「1条龙」，含中文数字的词将永远匹配不上。敏感词匹配用 ``strip_noise``。
    """
    if not text:
        return ""
    s = str(text).translate(_FULLWIDTH_DIGITS)
    s = "".join(_CN_DIGITS.get(ch, ch) for ch in s)
    # 反复替换：一次替换后可能产生新的相邻数字对（如 "138-1234-5678"）
    prev = None
    while prev != s:
        prev = s
        s = _SEP_BETWEEN_DIGITS.sub("", s)
    return s


def find_contact_info(text: str) -> List[str]:
    """返回命中的联系方式类型描述（空列表表示干净）"""
    scan = normalize_for_scan(text)
    hits: List[str] = []
    if _RE_MOBILE.search(scan):
        hits.append("手机号")
    if _RE_LANDLINE.search(scan):
        hits.append("固定电话")
    if _RE_WECHAT.search(scan):
        hits.append("微信号")
    if _RE_QQ.search(scan):
        hits.append("QQ 号")
    if _RE_URL.search(str(text or "")):
        hits.append("外部链接")
    return hits


# ---------------------------------------------------------------------------
# 敏感词匹配
# ---------------------------------------------------------------------------

# 只剔除用户用来拆词的符号，不剔除句读（。，、等）。
# 全量剔除标点会让相邻的正常词拼成敏感词，产生跨词边界的误伤。
_EVASION_CHARS = re.compile(r"[\s*\-_.·~^|/\\+#]+")


def strip_noise(text: str) -> str:
    """剔除拆词符号，抵消「走*私」「代-开-发-票」这类规避写法"""
    if not text:
        return ""
    return _EVASION_CHARS.sub("", str(text))


def find_sensitive_words(
    text: str, rules: Sequence[SensitiveWordRule]
) -> List[SensitiveWordRule]:
    """返回命中的规则

    同时在原文与「剔除拆词符号后的文本」上匹配，两者取并集。
    ASCII 词大小写不敏感（运营录入 ``VX`` 时不该漏掉 ``vx``）。
    """
    if not text or not rules:
        return []
    raw = str(text).lower()
    stripped = strip_noise(raw)

    hits: List[SensitiveWordRule] = []
    for rule in rules:
        w = (rule.word or "").strip().lower()
        if not w:
            continue
        if w in raw or strip_noise(w) in stripped:
            hits.append(rule)
    return hits


def _block_message_for(rule: SensitiveWordRule, label: str) -> str:
    """按分类给出用户文案

    违禁品与其他敏感词的用户处境不同：前者是「这货我们不接」，
    后者是「这话不能这么写」。给同一句提示会让用户不知道该改什么。
    """
    if rule.category == SensitiveWordCategory.CONTRABAND:
        return BLOCK_MESSAGES[BlockFlag.FORBIDDEN_CARGO]
    return f"「{label}」里有不能发布的内容，请修改后再提交"


# ---------------------------------------------------------------------------
# 输入与结果
# ---------------------------------------------------------------------------

@dataclass
class PrecheckInput:
    """预检输入

    ``texts`` 形如 ``{"标题": "...", "其他要求": "..."}``：带上字段名是为了
    拦截时能明确告诉用户是哪一栏有问题，而不是让用户自己在表单里找。

    ``sensitive_words`` 由 ``SensitiveWordService.get_rules`` 提供（带缓存）。
    留空则敏感词规则自然关闭——词库为空时不该拦下任何东西。
    """

    texts: Dict[str, str] = field(default_factory=dict)
    sensitive_words: List[SensitiveWordRule] = field(default_factory=list)

    from_province: Optional[str] = None
    from_city: Optional[str] = None
    from_district: Optional[str] = None
    to_province: Optional[str] = None
    to_city: Optional[str] = None
    to_district: Optional[str] = None

    window_start: Optional[datetime] = None
    now: Optional[datetime] = None

    cargo_name: Optional[str] = None
    expired_licenses: List[str] = field(default_factory=list)
    # 已过期但不足以拦截的证照（当前只有车辆保险），交人工审核关注
    soft_expired_licenses: List[str] = field(default_factory=list)

    posts_last_24h: int = 0
    tenant_age_days: Optional[int] = None
    is_first_post: bool = False
    similar_post_no: Optional[str] = None
    price_ratio_to_baseline: Optional[float] = None


@dataclass
class PrecheckResult:
    """预检结论"""

    block_flags: List[str] = field(default_factory=list)
    block_message: Optional[str] = None
    suspicious_flags: List[str] = field(default_factory=list)
    suspicious_notes: List[str] = field(default_factory=list)
    # 命中的敏感词，供 Service 回写 hit_count，让运营看出哪些词是死词
    hit_words: List[str] = field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return bool(self.block_flags)


def run_precheck(data: PrecheckInput) -> PrecheckResult:
    """执行自动预检

    硬拦截按「用户最该先改的」顺序返回首条文案：内容违规 > 证照过期 >
    信息填错。一次只给一条提示，避免弹出一长串错误让人无从下手。
    """
    result = PrecheckResult()

    # --- 硬拦截：自由文本中的联系方式 ---
    for label, text in (data.texts or {}).items():
        hits = find_contact_info(text)
        if hits:
            result.block_flags.append(BlockFlag.CONTACT_IN_TEXT)
            result.block_message = (
                f"「{label}」里似乎写了{('、'.join(hits))}。"
                + BLOCK_MESSAGES[BlockFlag.CONTACT_IN_TEXT]
            )
            break

    # --- 敏感词：货物名称一并扫描，命中违禁品分类时给专门文案 ---
    scan_targets: Dict[str, str] = dict(data.texts or {})
    if data.cargo_name:
        scan_targets.setdefault("货物名称", data.cargo_name)

    for label, text in scan_targets.items():
        for rule in find_sensitive_words(text, data.sensitive_words):
            result.hit_words.append(rule.word)
            if rule.action == SensitiveWordAction.BLOCK:
                if not result.blocked:
                    flag = (
                        BlockFlag.FORBIDDEN_CARGO
                        if rule.category == SensitiveWordCategory.CONTRABAND
                        else BlockFlag.SENSITIVE_WORD
                    )
                    result.block_flags.append(flag)
                    result.block_message = _block_message_for(rule, label)
            elif SuspiciousFlag.SENSITIVE_WORD_REVIEW not in result.suspicious_flags:
                result.suspicious_flags.append(SuspiciousFlag.SENSITIVE_WORD_REVIEW)
                result.suspicious_notes.append(
                    f"「{label}」命中需人工确认的词：{rule.word}"
                )

    # --- 硬拦截：证照过期 ---
    if not result.blocked and data.expired_licenses:
        names = "、".join(data.expired_licenses)
        result.block_flags.append(BlockFlag.LICENSE_EXPIRED)
        result.block_message = f"{names}已过期，请先更新后再对外发布"

    # --- 硬拦截：起终点相同 ---
    if not result.blocked and _same_route(data):
        result.block_flags.append(BlockFlag.SAME_ROUTE)
        result.block_message = BLOCK_MESSAGES[BlockFlag.SAME_ROUTE]

    # --- 硬拦截：装车时间已过 ---
    if not result.blocked and data.window_start and data.now:
        if data.window_start < data.now:
            result.block_flags.append(BlockFlag.WINDOW_PASSED)
            result.block_message = BLOCK_MESSAGES[BlockFlag.WINDOW_PASSED]

    # --- 可疑规则：不阻断，只标红 ---
    if data.soft_expired_licenses:
        result.suspicious_flags.append(SuspiciousFlag.INSURANCE_EXPIRED)
        result.suspicious_notes.append(
            f"{'、'.join(data.soft_expired_licenses)}已过期，出事时影响追偿，请人工确认"
        )

    if data.posts_last_24h > MAX_POSTS_PER_24H:
        result.suspicious_flags.append(SuspiciousFlag.TOO_MANY_POSTS)
        result.suspicious_notes.append(
            f"该企业近 24 小时已发布 {data.posts_last_24h} 条，疑似重复刷屏"
        )

    if data.similar_post_no:
        result.suspicious_flags.append(SuspiciousFlag.DUPLICATE_LIKE)
        result.suspicious_notes.append(
            f"与近 7 天的挂牌 {data.similar_post_no} 高度相似"
        )

    if (
        data.is_first_post
        and data.tenant_age_days is not None
        and data.tenant_age_days < NEW_TENANT_DAYS
    ):
        result.suspicious_flags.append(SuspiciousFlag.NEW_TENANT)
        result.suspicious_notes.append(
            f"新注册企业（{data.tenant_age_days} 天）首次发布"
        )

    # 报价基线依赖历史成交数据，一期样本不足时 Service 不传该值，规则自然关闭
    ratio = data.price_ratio_to_baseline
    if ratio is not None and (ratio < PRICE_LOW_RATIO or ratio > PRICE_HIGH_RATIO):
        result.suspicious_flags.append(SuspiciousFlag.PRICE_ABNORMAL)
        result.suspicious_notes.append(
            f"报价为同线路均价的 {ratio:.0%}，偏离明显"
        )

    return result


def _same_route(data: PrecheckInput) -> bool:
    """起终点是否相同

    只有在目的地填写完整时才判定：运力挂牌可以「接受任意流向」而不填目的地，
    此时不该报错。比较到区县——同城不同区是真实存在的短途业务，不能拦。
    """
    if not data.to_province or not data.from_province:
        return False
    origin = (data.from_province, data.from_city, data.from_district)
    dest = (data.to_province, data.to_city, data.to_district)
    if not data.from_district and not data.to_district:
        return origin[:2] == dest[:2]
    return origin == dest
