"""挂牌标题自动生成（纯函数）

标题是大厅列表卡片的主视觉，也是关键词搜索的主要命中字段，所以由后端统一生成、
不让前端拼——否则同一条线路会出现十几种写法，搜索直接失效。用户可以改写，
改写后的内容要过发布预检（``content_guard``），防止把联系方式塞进标题。

格式（02.货源大厅设计.md §3、03.运力大厅设计.md §3.1）：

- 货源：``杭州→成都 20台 比亚迪``
- 运力：``成都→期望往华东 8位板车 可载8台``

运力标题刻意把**位置与流向放在最前面**：找车方真正关心的是「你的车现在在哪、
能不能顺路送到我要的地方」，车辆参数是次要的过滤条件。
"""

from __future__ import annotations

from typing import Optional, Sequence

# sys_eco_post.title 是 varchar(120)
MAX_TITLE_LENGTH = 120

# 简称映射：这几个的后缀不是简单截断能处理的
_SPECIAL_SHORT_NAMES = {
    "内蒙古自治区": "内蒙古",
    "广西壮族自治区": "广西",
    "西藏自治区": "西藏",
    "宁夏回族自治区": "宁夏",
    "新疆维吾尔自治区": "新疆",
    "香港特别行政区": "香港",
    "澳门特别行政区": "澳门",
    "北京市": "北京",
    "上海市": "上海",
    "天津市": "天津",
    "重庆市": "重庆",
}

_STRIP_SUFFIXES = ("特别行政区", "自治区", "自治州", "地区", "盟", "省", "市", "县", "区")

_UNKNOWN_PLACE = "待确认"


def short_place(name: Optional[str]) -> Optional[str]:
    """地名简称：``杭州市`` → ``杭州``

    卡片宽度有限，标题里塞满「省」「市」会把真正有信息量的内容挤掉。
    """
    if not name:
        return None
    name = name.strip()
    if not name:
        return None
    if name in _SPECIAL_SHORT_NAMES:
        return _SPECIAL_SHORT_NAMES[name]
    for suffix in _STRIP_SUFFIXES:
        if name.endswith(suffix) and len(name) - len(suffix) >= 2:
            return name[: -len(suffix)]
    return name


def place_label(
    province: Optional[str] = None,
    city: Optional[str] = None,
    district: Optional[str] = None,
) -> str:
    """取一个尽量精确的地名短标签：市 > 区县 > 省"""
    return short_place(city) or short_place(district) or short_place(province) or _UNKNOWN_PLACE


def main_brand(brands: Optional[Sequence[Optional[str]]]) -> Optional[str]:
    """从品牌列表里取主要品牌

    多品牌时标注「等」，让看板的人知道还有别的车型，避免按单一品牌误判。
    """
    unique = []
    for b in brands or ():
        b = (b or "").strip()
        if b and b not in unique:
            unique.append(b)
    if not unique:
        return None
    if len(unique) == 1:
        return unique[0]
    return f"{unique[0]}等{len(unique)}个品牌"


def build_cargo_title(
    *,
    from_province: Optional[str] = None,
    from_city: Optional[str] = None,
    from_district: Optional[str] = None,
    to_province: Optional[str] = None,
    to_city: Optional[str] = None,
    to_district: Optional[str] = None,
    total_quantity: Optional[int] = None,
    quantity_unit: str = "台",
    brands: Optional[Sequence[Optional[str]]] = None,
    cargo_name: Optional[str] = None,
) -> str:
    """货源挂牌标题：``杭州→成都 20台 比亚迪``"""
    origin = place_label(from_province, from_city, from_district)
    dest = place_label(to_province, to_city, to_district)
    parts = [f"{origin}→{dest}"]

    if total_quantity:
        parts.append(f"{total_quantity}{quantity_unit or '台'}")

    # 商品车看品牌，普货看货名
    subject = main_brand(brands) or (cargo_name or "").strip()
    if subject:
        parts.append(subject)

    return _clamp(" ".join(parts))


def build_capacity_title(
    *,
    from_province: Optional[str] = None,
    from_city: Optional[str] = None,
    from_district: Optional[str] = None,
    to_province: Optional[str] = None,
    to_city: Optional[str] = None,
    to_district: Optional[str] = None,
    any_direction: bool = False,
    truck_type_name: Optional[str] = None,
    slot_count: Optional[int] = None,
    total_quantity: Optional[int] = None,
    quantity_unit: str = "台",
) -> str:
    """运力挂牌标题：``成都→期望往华东 8位板车 可载8台``"""
    origin = place_label(from_province, from_city, from_district)
    if any_direction:
        dest = "不限流向"
    else:
        dest = place_label(to_province, to_city, to_district)
        if dest == _UNKNOWN_PLACE:
            # 既没勾「任意流向」又没填流向，说明发布方还没想清楚，
            # 标题里如实写「流向待定」，不要伪装成有明确线路
            dest = "流向待定"
    parts = [f"{origin}→{dest}"]

    spec = _truck_spec(truck_type_name, slot_count)
    if spec:
        parts.append(spec)

    if total_quantity:
        parts.append(f"可载{total_quantity}{quantity_unit or '台'}")

    return _clamp(" ".join(parts))


# ----------------------------------------------------------------------


def _truck_spec(truck_type_name: Optional[str], slot_count: Optional[int]) -> str:
    """车辆规格片段：``8位板车`` / ``板车`` / ``8位``"""
    name = (truck_type_name or "").strip()
    if slot_count and name:
        return f"{slot_count}位{name}"
    if slot_count:
        return f"{slot_count}位"
    return name


def _clamp(title: str) -> str:
    """截断到列宽上限

    宁可截断也不能超长：数据库层会直接报错，而报错发生在发布的最后一步，
    用户已经填完了整个表单。
    """
    title = " ".join(title.split())
    if len(title) <= MAX_TITLE_LENGTH:
        return title
    return title[: MAX_TITLE_LENGTH - 1] + "…"
