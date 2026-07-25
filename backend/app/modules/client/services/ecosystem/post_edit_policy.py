"""挂牌编辑分级：改了什么决定要不要重审（纯逻辑，零 DB）

对应 04.运营审核与风控设计.md §2.4。分两档：

| 档位 | 触发条件 | 处理 |
|------|---------|------|
| 快速复审 | 只改了描述与条件 | 只跑自动预检，通过即留在原状态，不离开大厅 |
| 完整重审 | 改动了这单生意本身 | 回到待审核队列，期间从大厅移出 |

## 分档的判据

不是「字段重不重要」，而是**改完之后，正在看这条信息的人是否被误导了**：

- 线路、时间、台数、货物、车型、车辆、司机 → 改了就是另一笔生意。
  同行按旧信息打过来会白跑，必须重审并先撤出大厅。
- 标题、备注、报价、联系人、结算、可见范围 → 改的是描述与条件，
  同行看到的仍是同一笔生意。让这些改动排两小时队，结果就是没人愿意维护
  信息准确性（`04` §2.4 原话）。

按这个判据，**标题归快速复审**。它是最显眼的文本、也最容易夹带引流内容，
但「其他要求」「服务承诺」同样是自由文本、同样被文档划进快速复审档，
单独把标题拔高一档并不能挡住什么，只会造成规则不自洽。自由文本的风险由
预检（联系方式硬拦 + 敏感词）加运营抽检兜底，不靠重审档位兜。

## 有效期不参与比对

``valid_from`` / ``valid_until`` 由「延长展示」单独负责。若让编辑顺手重算
有效期，用户反复保存就能无限续命，把展示天数上限绕空。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from app.modules.client.services.ecosystem.post_draft import PostDraft
from app.modules.console.models.ecosystem.constants import PostType


class ReauditTier:
    """重审档位。数值大小即严格程度，取多个字段的最大值即整体档位"""

    FAST = 1  # 快速复审
    FULL = 2  # 完整重审


@dataclass(frozen=True)
class FieldRule:
    """一个字段的展示名与档位

    ``label`` 允许多个字段共用（如 ``from_province`` / ``from_city`` 都叫
    「出发地」）。流水里写「改动了出发地」比罗列五个列名可读得多。
    """

    label: str
    tier: int


# ---------------------------------------------------------------------------
# 主表字段
# ---------------------------------------------------------------------------

MAIN_FIELDS: Dict[str, FieldRule] = {
    "title": FieldRule("标题", ReauditTier.FAST),
    # --- 线路 ---
    "from_province": FieldRule("出发地", ReauditTier.FULL),
    "from_city": FieldRule("出发地", ReauditTier.FULL),
    "from_district": FieldRule("出发地", ReauditTier.FULL),
    "from_region_code": FieldRule("出发地", ReauditTier.FULL),
    "from_name": FieldRule("出发地", ReauditTier.FULL),
    "to_province": FieldRule("目的地", ReauditTier.FULL),
    "to_city": FieldRule("目的地", ReauditTier.FULL),
    "to_district": FieldRule("目的地", ReauditTier.FULL),
    "to_region_code": FieldRule("目的地", ReauditTier.FULL),
    "to_name": FieldRule("目的地", ReauditTier.FULL),
    "any_direction": FieldRule("目的地", ReauditTier.FULL),
    # --- 时间窗 ---
    "window_start": FieldRule("时间安排", ReauditTier.FULL),
    "window_end": FieldRule("时间安排", ReauditTier.FULL),
    # --- 数量 ---
    "total_quantity": FieldRule("数量", ReauditTier.FULL),
    "quantity_unit": FieldRule("数量", ReauditTier.FULL),
    # --- 报价 ---
    "price_type": FieldRule("报价", ReauditTier.FAST),
    "price_amount": FieldRule("报价", ReauditTier.FAST),
    "price_include_tax": FieldRule("报价", ReauditTier.FAST),
    "price_negotiable": FieldRule("报价", ReauditTier.FAST),
    # --- 合作方式 ---
    "cooperation_type": FieldRule("合作方式", ReauditTier.FAST),
    "keep_listed_after_deal": FieldRule("合作方式", ReauditTier.FAST),
    # --- 联系方式 ---
    "contact_name": FieldRule("联系方式", ReauditTier.FAST),
    "contact_phone": FieldRule("联系方式", ReauditTier.FAST),
    "contact_backup": FieldRule("联系方式", ReauditTier.FAST),
    # --- 可见范围 ---
    "visibility_level": FieldRule("可见范围", ReauditTier.FAST),
    "contact_visibility": FieldRule("可见范围", ReauditTier.FAST),
    "apply_block_rule": FieldRule("可见范围", ReauditTier.FAST),
    "extra_block_tenants": FieldRule("可见范围", ReauditTier.FAST),
}

# 目的地子表（sys_eco_post_dest）作为一个整体比对
DEST_RULE = FieldRule("目的地", ReauditTier.FULL)

# ---------------------------------------------------------------------------
# 扩展表字段
# ---------------------------------------------------------------------------

CARGO_EXT_FIELDS: Dict[str, FieldRule] = {
    "via_points": FieldRule("线路", ReauditTier.FULL),
    "reference_mileage": FieldRule("线路", ReauditTier.FULL),
    "segment_count": FieldRule("线路", ReauditTier.FULL),
    "cargo_category": FieldRule("货物信息", ReauditTier.FULL),
    "cargo_items": FieldRule("货物信息", ReauditTier.FULL),
    "vehicle_condition": FieldRule("货物信息", ReauditTier.FULL),
    "cargo_name": FieldRule("货物信息", ReauditTier.FULL),
    "cargo_weight": FieldRule("货物信息", ReauditTier.FULL),
    "cargo_volume": FieldRule("货物信息", ReauditTier.FULL),
    "package_type": FieldRule("货物信息", ReauditTier.FULL),
    "require_truck_types": FieldRule("承运要求", ReauditTier.FULL),
    "require_slot_min": FieldRule("承运要求", ReauditTier.FULL),
    "require_slot_max": FieldRule("承运要求", ReauditTier.FULL),
    "allow_split": FieldRule("承运要求", ReauditTier.FULL),
    "arrive_time": FieldRule("时间安排", ReauditTier.FULL),
    "require_insurance": FieldRule("承运要求", ReauditTier.FAST),
    "other_requirements": FieldRule("其他要求", ReauditTier.FAST),
    "time_negotiable": FieldRule("时间安排", ReauditTier.FAST),
    "settle_type": FieldRule("结算方式", ReauditTier.FAST),
    "prepay_ratio": FieldRule("结算方式", ReauditTier.FAST),
    "freq_desc": FieldRule("货量频次", ReauditTier.FAST),
}

CAPACITY_EXT_FIELDS: Dict[str, FieldRule] = {
    "post_granularity": FieldRule("挂牌粒度", ReauditTier.FULL),
    "truck_type": FieldRule("车辆信息", ReauditTier.FULL),
    "slot_count": FieldRule("车辆信息", ReauditTier.FULL),
    "truck_length": FieldRule("车辆信息", ReauditTier.FULL),
    "rated_load": FieldRule("车辆信息", ReauditTier.FULL),
    "truck_quantity": FieldRule("车辆信息", ReauditTier.FULL),
    "plate_number": FieldRule("车辆信息", ReauditTier.FULL),
    "plate_masked": FieldRule("车辆信息", ReauditTier.FULL),
    "has_trailer": FieldRule("车辆信息", ReauditTier.FULL),
    "trailer_plate_number": FieldRule("车辆信息", ReauditTier.FULL),
    "driver_name": FieldRule("司机信息", ReauditTier.FULL),
    "driver_display": FieldRule("司机信息", ReauditTier.FULL),
    "departure_ready_at": FieldRule("时间安排", ReauditTier.FULL),
    "plate_public": FieldRule("车牌公开设置", ReauditTier.FAST),
    "driver_years": FieldRule("司机信息", ReauditTier.FAST),
    "driver_order_count": FieldRule("司机信息", ReauditTier.FAST),
    "pickup_radius": FieldRule("接货范围", ReauditTier.FAST),
    "good_at_categories": FieldRule("擅长货类", ReauditTier.FAST),
    "can_invoice": FieldRule("开票信息", ReauditTier.FAST),
    "invoice_type": FieldRule("开票信息", ReauditTier.FAST),
    "has_insurance": FieldRule("保险情况", ReauditTier.FAST),
    "service_promise": FieldRule("服务承诺", ReauditTier.FAST),
    "settle_require": FieldRule("结算要求", ReauditTier.FAST),
}

_EXT_FIELD_TABLES = {
    PostType.CARGO: CARGO_EXT_FIELDS,
    PostType.CAPACITY: CAPACITY_EXT_FIELDS,
}

# 表里没有的扩展字段按最严档处理：新增列时忘记登记，代价是多一次人工审核，
# 而不是悄悄放行一处未分级的改动。
_UNKNOWN_RULE = FieldRule("其他信息", ReauditTier.FULL)


# ---------------------------------------------------------------------------
# 差异
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ChangedField:
    """一处改动"""

    name: str
    label: str
    tier: int
    old: Any
    new: Any


@dataclass
class EditDiff:
    """整次编辑的改动集合"""

    changed: List[ChangedField] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.changed)

    @property
    def tier(self) -> int:
        """整体档位：取最严的一处。无改动时按快速复审处理"""
        if not self.changed:
            return ReauditTier.FAST
        return max(c.tier for c in self.changed)

    @property
    def requires_full_reaudit(self) -> bool:
        return self.tier == ReauditTier.FULL

    @property
    def labels(self) -> List[str]:
        """去重后的改动项名称，保持首次出现顺序，用于流水与提示文案"""
        seen: List[str] = []
        for c in self.changed:
            if c.label not in seen:
                seen.append(c.label)
        return seen

    @property
    def field_names(self) -> List[str]:
        return [c.name for c in self.changed]

    def to_audit_payload(self) -> Optional[dict]:
        """转成写进 ``sys_eco_post_audit.changed_fields`` 的结构

        流水里存新旧值，是给两个下游用的：审核员要判断「这次改动是修正还是
        偷换内容」——只看「修改了报价」看不出是从 1200 改到 1180 还是改到 120；
        洽谈方的「对方更新了信息」通知要说清改成了什么。只记字段名，两件事都做不了。

        值一律转成字符串再存：``Decimal`` 与 ``datetime`` 不是 JSON 原生类型，
        留着会在写库时炸在序列化上；而这份数据只用于展示与追溯，不参与计算。
        """
        if not self.changed:
            return None
        return {
            "tier": self.tier,
            "labels": self.labels,
            "items": [
                {
                    "field": c.name,
                    "label": c.label,
                    "tier": c.tier,
                    "old": _to_text(c.old),
                    "new": _to_text(c.new),
                }
                for c in self.changed[:_MAX_AUDIT_ITEMS]
            ],
        }


# 流水里最多记多少处改动。一次编辑改到几十项已经不是「编辑」而是「重写」，
# 再往后记也没有辅助判断的价值，只是把 JSON 列撑大
_MAX_AUDIT_ITEMS = 40
# 单个值的展示长度上限
_MAX_AUDIT_VALUE_LEN = 100


def _to_text(value: Any) -> Optional[str]:
    """把任意字段值转成流水里可读的短文本"""
    value = normalize(value)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, (list, tuple)):
        text = "、".join(_to_text(v) or "" for v in value)
    else:
        text = str(value)
    text = text.strip()
    if len(text) > _MAX_AUDIT_VALUE_LEN:
        return text[:_MAX_AUDIT_VALUE_LEN] + "…"
    return text or None


def normalize(value: Any) -> Any:
    """比对前归一化

    只做两件事，都是为了避免把「没改」判成「改了」：

    - 字符串去首尾空白，空串按空值处理。表单提交的 ``""`` 与库里的 ``NULL``
      是同一个意思，判成改动会让每次保存都触发一次重审。
    - 空列表按空值处理，理由同上（JSON 列上 ``[]`` 与 ``NULL`` 等价）。

    数字不做处理：``Decimal("10.00") == Decimal("10") == 10`` 在 Python 里
    本来就成立，额外规整反而可能改变精度语义。
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, (list, tuple)):
        return list(value) or None
    return value


def _same(old: Any, new: Any) -> bool:
    a, b = normalize(old), normalize(new)
    if a is None or b is None:
        return a is None and b is None
    # Decimal 与 float 混比会走 Decimal.__eq__，精度语义正确；
    # 类型完全不可比时（如 list 与 str）Python 返回 False，正是我们要的结论
    try:
        return bool(a == b)
    except TypeError:  # pragma: no cover - 正常字段不会走到
        return False


def diff_main(post: Any, draft: PostDraft) -> List[ChangedField]:
    """比对主表字段

    ``PostDraft`` 的主表字段一律有值（dataclass 有默认值），所以缺省即 ``None``，
    含义是「清空」。这是刻意的：Builder 每次都从源单与表单完整重建草稿，
    半个草稿说明 Builder 有问题，不该被当成「保持原值」放过去。
    """
    changed: List[ChangedField] = []
    for name, rule in MAIN_FIELDS.items():
        old = getattr(post, name, None)
        new = getattr(draft, name, None)
        if not _same(old, new):
            changed.append(ChangedField(name, rule.label, rule.tier, old, new))
    return changed


def diff_ext(post_type: int, ext: Any, draft_ext: Optional[Dict[str, Any]]) -> List[
    ChangedField
]:
    """比对扩展表字段

    **只比对 ``draft_ext`` 里出现的键**，与主表规则相反。扩展表字段多且各
    Builder 只填自己关心的那些，若把缺键当成「清空」，一次编辑就会把
    Builder 没覆盖到的字段全抹掉。要清空某字段，显式传 ``None``。
    """
    if not draft_ext:
        return []
    table = _EXT_FIELD_TABLES.get(int(post_type), {})
    changed: List[ChangedField] = []
    for name, new in draft_ext.items():
        rule = table.get(name, _UNKNOWN_RULE)
        old = getattr(ext, name, None) if ext is not None else None
        if not _same(old, new):
            changed.append(ChangedField(name, rule.label, rule.tier, old, new))
    return changed


def _dest_key(province: Any, city: Any, region_code: Any) -> tuple:
    return (normalize(province), normalize(city), region_code)


def diff_destinations(
    dests: Sequence[Any], draft: PostDraft
) -> List[ChangedField]:
    """比对目的地子表

    按 ``sort_order`` 排序后整体比对：顺序本身有意义（第一项是主目的地，
    会冗余到主表 ``to_*``），换序确实是一次改动。
    """
    old_keys = [
        _dest_key(d.province, d.city, d.region_code)
        for d in sorted(dests or [], key=lambda d: getattr(d, "sort_order", 0) or 0)
    ]
    new_keys = [
        _dest_key(d.province, d.city, d.region_code)
        for d in sorted(draft.destinations or [], key=lambda d: d.sort_order or 0)
        if d.province
    ]
    if old_keys == new_keys:
        return []
    return [
        ChangedField(
            "destinations", DEST_RULE.label, DEST_RULE.tier, old_keys, new_keys
        )
    ]


def build_diff(
    *, post: Any, ext: Any, dests: Sequence[Any], draft: PostDraft
) -> EditDiff:
    """算出整次编辑的改动集合与重审档位"""
    changed = diff_main(post, draft)
    changed += diff_ext(int(draft.post_type), ext, draft.ext)
    changed += diff_destinations(dests, draft)
    return EditDiff(changed=changed)
