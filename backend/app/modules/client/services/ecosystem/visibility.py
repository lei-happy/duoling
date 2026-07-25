"""服务平台可见性内核（纯逻辑，零 DB）

**这是整个服务平台唯一允许决定字段可见性的地方。**

禁止在 Router / Service 里写 `if level >= 2: data["contactPhone"] = ...` 这类零散
判断。可见性逻辑分散一次，就等于埋下一个数据泄露入口。
规则来源：doc/02.需求文档/02.企业端/13.服务平台/08.接口契约.md §2。

本模块刻意做成纯函数 + 不可变数据类，不碰数据库：
  - 层级判定依赖的「查看方与该挂牌是否在洽谈/已成交」由
    ``EcoViewerContext`` 预先批量装入，避免列表页 N+1 查询；
  - 纯逻辑才能被穷举测试，而可见性正是最需要穷举测试的部分。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import IntEnum
from typing import Any, FrozenSet, Optional

from app.modules.console.models.ecosystem.constants import VisibilityLevel


class ViewerLevel(IntEnum):
    """查看方相对「某一条具体挂牌」的可见层级

    层级是**针对「查看方 × 具体挂牌」这一组合**计算的，不是租户的全局属性：
    同一个查看方对 A 挂牌可能是 NEGOTIATING，对 B 挂牌只是 CERTIFIED。
    """

    ANONYMOUS = 1     # 已登录，但所属租户未完成营业执照核验
    CERTIFIED = 2     # 所属租户已核验营业执照
    NEGOTIATING = 3   # 与该挂牌存在洽谈中及以后的意向（联系方式已双向解锁）
    DEALT = 4         # 与该挂牌存在有效成交单
    OWNER = 9         # 发布方本人（含同租户其他成员），可见全部字段


# 1~4 必须与 constants.VisibilityLevel 保持一致：挂牌上的
# visibility_level / contact_visibility 存的就是那套取值，两边错位会导致
# 「按挂牌配置放宽/收紧」的判断整体偏移一级，且不会报错。
assert ViewerLevel.ANONYMOUS == VisibilityLevel.ANONYMOUS
assert ViewerLevel.CERTIFIED == VisibilityLevel.CERTIFIED
assert ViewerLevel.NEGOTIATING == VisibilityLevel.NEGOTIATING
assert ViewerLevel.DEALT == VisibilityLevel.DEALT


# 任何层级、任何接口、对任何人都不返回的字段名。
# 见 08.接口契约.md §2.4。序列化器不读这些字段，本集合用于测试兜底断言，
# 以及未来若有人新增序列化路径时的自检。
NEVER_RETURN_FIELDS: FrozenSet[str] = frozenset({
    "driverName",       # 司机真实姓名：对外只给 driverDisplay
    "driver_name",
    "contactPhoneRaw",
    "vin",
    "customerName",     # 客户名称 / 货主单位绝对禁止进入平台库
    "ownerUnit",
})


@dataclass(frozen=True)
class EcoViewerContext:
    """查看方上下文

    ``negotiating_post_ids`` / ``dealt_post_ids`` 由 Service 层用一次批量查询
    装入（列表页整页一次、详情页单条一次），因此本类的层级判定是纯内存运算。

    ``is_platform_ops`` 为运营后台视角：能看到审核相关字段，但**不因此获得
    联系方式与司机姓名**——运营核查敏感信息走独立的调阅接口（一期不做）。
    """

    viewer_tenant_code: Optional[str]
    license_verified: bool = False
    is_platform_ops: bool = False
    negotiating_post_ids: FrozenSet[int] = field(default_factory=frozenset)
    dealt_post_ids: FrozenSet[int] = field(default_factory=frozenset)


def resolve_level(post: Any, viewer: EcoViewerContext) -> ViewerLevel:
    """计算查看方相对该挂牌的可见层级

    判定顺序不可调换：先判归属，再判成交，再判洽谈，最后才落到认证/匿名。
    """
    owner_code = getattr(post, "owner_tenant_code", None)
    if viewer.viewer_tenant_code and owner_code == viewer.viewer_tenant_code:
        return ViewerLevel.OWNER

    post_id = getattr(post, "id", None)
    if post_id is not None:
        if post_id in viewer.dealt_post_ids:
            return ViewerLevel.DEALT
        if post_id in viewer.negotiating_post_ids:
            return ViewerLevel.NEGOTIATING

    if viewer.license_verified:
        return ViewerLevel.CERTIFIED
    return ViewerLevel.ANONYMOUS


# ---------------------------------------------------------------------------
# 单项可见性判定
# ---------------------------------------------------------------------------

def can_see_owner_full_name(post: Any, level: ViewerLevel) -> bool:
    """企业全称是否可见

    默认 ``visibility_level = 2``（认证层起可见），此时匿名层看不到全称、
    只能看到脱敏名，与 §2.2 矩阵一致。发布方若显式设为 1，属于主动放开给
    匿名层，按其意愿放行。
    """
    required = getattr(post, "visibility_level", None) or VisibilityLevel.CERTIFIED
    return level >= required


def can_see_contact(post: Any, level: ViewerLevel) -> bool:
    """联系方式是否可见

    取挂牌配置与「认证层」的较严者：``contact_visibility`` 合法取值只有 2/3，
    因此匿名层永远看不到联系方式。即使数据异常写入了 1，这里也会兜到 2。
    """
    required = getattr(post, "contact_visibility", None) or VisibilityLevel.NEGOTIATING
    required = max(int(required), int(VisibilityLevel.CERTIFIED))
    return level >= required


def can_see_full_plate(capacity: Any, level: ViewerLevel) -> bool:
    """完整车牌是否可见：洽谈层起可见；认证层仅当发布方勾选了完全公开。"""
    if level >= ViewerLevel.NEGOTIATING:
        return True
    if level == ViewerLevel.CERTIFIED:
        return int(getattr(capacity, "plate_public", 0) or 0) == 1
    return False


def can_see_certified_detail(level: ViewerLevel) -> bool:
    """区县、详细地名、结算方式、其他要求、浏览/意向数等「认证层可见」字段。"""
    return level >= ViewerLevel.CERTIFIED


def can_see_owner_private(level: ViewerLevel) -> bool:
    """仅发布方可见：热度反馈、源单信息、屏蔽配置。"""
    return level == ViewerLevel.OWNER


def can_see_audit(level: ViewerLevel, viewer: EcoViewerContext) -> bool:
    """审核状态与驳回原因：发布方本人，或运营后台。"""
    return level == ViewerLevel.OWNER or viewer.is_platform_ops


# ---------------------------------------------------------------------------
# 脱敏与降精度
# ---------------------------------------------------------------------------

def mask_plate(plate: Optional[str]) -> Optional[str]:
    """车牌打码：``浙A88888`` → ``浙A·**·88``

    保留省份简称 + 字母（判断车辆归属地，是撮合时的有效信息），隐藏中间号段，
    保留末两位便于双方电话核对时确认是同一台车。
    """
    if not plate:
        return None
    s = str(plate).strip().replace("·", "").replace(" ", "")
    if len(s) <= 4:
        # 异常短车牌：只保留首字，其余打码，避免反而暴露全量
        return (s[0] + "*" * (len(s) - 1)) if s else None
    return f"{s[:2]}·**·{s[-2:]}"


# 行业关键词，按长度倒序匹配，保证「供应链」不被「链」之类的短词抢先命中
_INDUSTRY_WORDS = (
    "供应链", "物流", "运输", "货运", "汽运", "仓储", "贸易",
    "科技", "实业", "集团", "汽车", "商贸", "服务",
)

# 企业名后缀，脱敏时先剥掉：它们对识别企业毫无帮助，只占位置
_LEGAL_SUFFIXES = (
    "股份有限公司", "有限责任公司", "有限公司", "分公司", "公司", "厂", "店",
)


def mask_company_name(name: Optional[str]) -> str:
    """企业名脱敏：``杭州速达物流有限公司`` → ``杭州**物流``

    脱敏名出现在每一张大厅卡片上，目标是「能判断对方大概是哪儿的、做什么的，
    但认不出是哪一家」——保留地名前缀与行业词，遮住中间的字号部分。

    结果是**固化存储**的（``sys_eco_post.owner_masked_name``），不在读取时计算：
    大厅列表一页几十条卡片，实时算太贵。
    """
    if not name:
        return ""
    core = " ".join(str(name).split())
    for suffix in _LEGAL_SUFFIXES:
        if core.endswith(suffix) and len(core) - len(suffix) >= 2:
            core = core[: -len(suffix)]
            break
    if not core:
        return ""
    if len(core) <= 2:
        # 太短，遮一个字已经是能做的极限
        return core[0] + "*"

    for word in _INDUSTRY_WORDS:
        idx = core.rfind(word)
        # idx > 2 才有字可遮：等于 2 时「速达物流」会原样输出，等于没脱敏
        if idx > 2:
            return f"{core[:2]}**{word}"

    if len(core) <= 4:
        return f"{core[0]}**{core[-1]}"
    return f"{core[:2]}**{core[-2:]}"


def coarse_day(value: Optional[datetime]) -> Optional[str]:
    """时间降精度到日：匿名层只能看到哪天装车，看不到具体时刻。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return str(value)


def fmt_datetime(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return str(value)


def price_range(amount: Optional[Decimal]) -> Optional[str]:
    """价格区间：匿名层只给区间，不给精确报价

    分档步长在此处集中定义，产品若要调整只改这一个函数：
      - 1 万以下按 1000 一档
      - 1 万以上按 5000 一档
    这样既能让未认证用户判断「这单大概什么价位、值不值得认证」，
    又不至于让报价被批量抓取用于同行比价。
    """
    if amount is None:
        return None
    value = float(amount)
    if value <= 0:
        return None
    step = 1000 if value < 10000 else 5000
    low = int(value // step) * step
    high = low + step
    return f"{_fmt_money(low)}~{_fmt_money(high)}"


def _fmt_money(value: int) -> str:
    if value >= 10000:
        text = f"{value / 10000:.1f}".rstrip("0").rstrip(".")
        return f"{text}万"
    return str(value)


def brands_only(cargo_items: Optional[list]) -> Optional[list]:
    """商品车明细降级为「仅品牌」：匿名层看不到车系与分车型台数。

    车系 + 台数组合起来足以反推具体订单，属于可被同行利用的商业信息。
    """
    if not cargo_items:
        return None
    seen: list = []
    for item in cargo_items:
        if not isinstance(item, dict):
            continue
        brand = item.get("brand")
        if brand and brand not in seen:
            seen.append(brand)
    return [{"brand": b} for b in seen] or None
