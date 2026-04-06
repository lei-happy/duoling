"""
从汽车之家车型参配页 HTML 内嵌的 `var config` JSON 解析车系级常用字段。

说明：数据源为公开页面结构，若对方改版或启用强反爬，可能需调整解析或改用浏览器渲染。
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.modules.console.services.ops.autohome_crawl_runner import DEFAULT_USER_AGENT

logger = logging.getLogger(__name__)

# 与浏览器一致：主站 www 车系参配对比页（含多车型列）常带完整 embedded config；car 子域作兜底。
HOST_WWW = "https://www.autohome.com.cn"
HOST_CAR = "https://car.autohome.com.cn"
URL_CONFIG_SERIES_WWW = f"{HOST_WWW}/config/series/{{series_id}}.html"
URL_CONFIG_SERIES_CAR = f"{HOST_CAR}/config/series/{{series_id}}.html"
URL_CONFIG_SERIES_YEAR_WWW = (
    f"{HOST_WWW}/config/series/{{series_id}}-{{year_id}}.html"
)
URL_CONFIG_SERIES_YEAR_CAR = (
    f"{HOST_CAR}/config/series/{{series_id}}-{{year_id}}.html"
)
URL_CONFIG_SPEC_WWW = f"{HOST_WWW}/config/spec/{{spec_id}}.html"
URL_CONFIG_SPEC_CAR = f"{HOST_CAR}/config/spec/{{spec_id}}.html"

_RE_SPEC_ID = re.compile(r"/config/spec/(\d+)\.html", re.I)
_RE_SERIES_YEAR = re.compile(r"/config/series/(\d+)-(\d+)\.html", re.I)
# 参配页脚本：var/let config 或 window.config（部分页面）
_CONFIG_MARKERS = (
    r"(?:var|let)\s+config\s*=",
    r"window\.config\s*=",
)


@dataclass
class ParsedSeriesSpecs:
    energy_type: Optional[str] = None
    length_mm: Optional[int] = None
    width_mm: Optional[int] = None
    height_mm: Optional[int] = None
    wheelbase_mm: Optional[int] = None
    front_track_mm: Optional[int] = None
    rear_track_mm: Optional[int] = None
    approach_angle: Optional[Decimal] = None
    departure_angle: Optional[Decimal] = None
    curb_weight_kg: Optional[int] = None


def _strip_html_tags(s: str) -> str:
    t = re.sub(r"<[^>]+>", "", s or "")
    return t.replace("&nbsp;", " ").replace("\xa0", " ").strip()


def _extract_balanced_json_object(html: str, start_brace: int) -> Optional[str]:
    """从 html[start_brace]=='{' 起，做带引号逃逸的括号配对，截取 JSON 对象子串。"""
    n = len(html)
    if start_brace >= n or html[start_brace] != "{":
        return None
    depth = 0
    i = start_brace
    in_str = False
    esc = False
    quote = ""
    while i < n:
        c = html[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == quote:
                in_str = False
        else:
            if c in "\"'":
                in_str = True
                quote = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    return html[start_brace : i + 1]
        i += 1
    return None


def extract_config_dict_from_spec_html(html: str) -> Optional[Dict[str, Any]]:
    for pat in _CONFIG_MARKERS:
        m = re.search(pat, html, re.I | re.MULTILINE)
        if not m:
            continue
        pos = m.end()
        while pos < len(html) and html[pos] in " \t\n\r":
            pos += 1
        raw = _extract_balanced_json_object(html, pos)
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            logger.debug("config json decode: %s", e)
            continue
        if isinstance(data, dict):
            return data
    return None


def config_has_param_table(cfg: Optional[Dict[str, Any]]) -> bool:
    if not cfg:
        return False
    r = cfg.get("result")
    if not isinstance(r, dict):
        return False
    groups = r.get("paramtypeitems")
    if not isinstance(groups, list) or not groups:
        return False
    for g in groups:
        if not isinstance(g, dict):
            continue
        pis = g.get("paramitems")
        if isinstance(pis, list) and len(pis) > 0:
            return True
    return False


def _valueitems_first_nonempty(valueitems: Any) -> str:
    """对比表多列时，取第一个非空单元格（避免首列为「-」或占位导致车身参数丢失）。"""
    if not valueitems or not isinstance(valueitems, list):
        return ""
    for cell in valueitems:
        if not isinstance(cell, dict):
            continue
        v = cell.get("value")
        if v is None:
            continue
        s = _strip_html_tags(str(v))
        if s in ("", "-", "●", "—"):
            continue
        return s
    return ""


def _normalize_label(name: str) -> str:
    if not name:
        return ""
    x = name.replace("（", "(").replace("）", ")")
    return re.sub(r"\s+", "", x)


def _display_param_name(raw: Any) -> str:
    """参配行名常含反爬 span，需去标签后再匹配「轴距」等汉字。"""
    return _normalize_label(_strip_html_tags(str(raw or "")))


def _group_title_normalized(grp: Dict[str, Any]) -> str:
    return _display_param_name(grp.get("name") or "")


def _label_only_unit_mm(label: str) -> bool:
    """行名被脱敏后仅剩 (mm) 等形式。"""
    if not label:
        return True
    t = label.strip()
    return bool(re.fullmatch(r"[\(（]?mm[\)）]?", t, re.I))


def _label_only_unit_kg(label: str) -> bool:
    t = (label or "").strip()
    return bool(re.fullmatch(r"[\(（]?kg[\)）]?", t, re.I))


def iter_flat_param_rows(cfg: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    按页面顺序展开全部参配行：(规范化列名, 展示文本)。
    不合并去重，便于按「轴距(mm)」「整备质量(kg)」等文字逐行匹配（含「车身」分组）。
    """
    rows: List[Tuple[str, str]] = []
    result = cfg.get("result")
    if not isinstance(result, dict):
        return rows
    groups = result.get("paramtypeitems")
    if not isinstance(groups, list):
        return rows
    for grp in groups:
        if not isinstance(grp, dict):
            continue
        for it in grp.get("paramitems") or []:
            if not isinstance(it, dict):
                continue
            raw = it.get("name") or it.get("itemname") or ""
            label = _display_param_name(raw)
            if not label:
                continue
            text = _valueitems_first_nonempty(it.get("valueitems"))
            rows.append((label, text))
    return rows


# 车身表格常见顺序（与官网对比表一致）：长度、宽度、高度、轴距、前轮距、后轮距（其后多为角度等）
_BODY_MM_SLOT_ATTRS: Tuple[str, ...] = (
    "length_mm",
    "width_mm",
    "height_mm",
    "wheelbase_mm",
    "front_track_mm",
    "rear_track_mm",
)


def _fill_body_group_by_mm_row_order(cfg: Dict[str, Any], snap: ParsedSeriesSpecs) -> None:
    """
    车身分组中行名可能被脱敏为仅「(mm)」，无法文字匹配；按表格行序把数值填入未赋值的尺寸列。
    仅收集数值在合理车身尺寸范围内的单元格，避免车门数等小整数干扰。
    """
    result = cfg.get("result")
    if not isinstance(result, dict):
        return
    groups = result.get("paramtypeitems")
    if not isinstance(groups, list):
        return
    mm_row_values: List[int] = []
    for grp in groups:
        if not isinstance(grp, dict):
            continue
        if _group_title_normalized(grp) != "车身":
            continue
        for it in grp.get("paramitems") or []:
            if not isinstance(it, dict):
                continue
            raw_name = it.get("name") or it.get("itemname") or ""
            dlabel = _display_param_name(raw_name)
            text = _valueitems_first_nonempty(it.get("valueitems"))
            v = _parse_int_loose(text)
            if v is None:
                continue
            # 接近角、车门数等小整数；车身 mm 尺寸一般 >= 800
            if v < 800:
                continue
            if any(
                x in dlabel
                for x in (
                    "排量",
                    "油箱",
                    "容积",
                    "满载",
                    "总质量",
                    "整备",
                    "装备",
                )
            ):
                continue
            is_dim_row = _label_only_unit_mm(dlabel) or (
                "长" in dlabel
                or "宽" in dlabel
                or "高" in dlabel
                or "轴距" in dlabel
                or "轮距" in dlabel
            )
            if is_dim_row:
                mm_row_values.append(v)
        break
    for idx, attr in enumerate(_BODY_MM_SLOT_ATTRS):
        if idx >= len(mm_row_values):
            break
        if getattr(snap, attr) is None:
            setattr(snap, attr, mm_row_values[idx])


def _fill_curb_weight_from_basic_group(cfg: Dict[str, Any], snap: ParsedSeriesSpecs) -> None:
    """基本参数里整备质量行名可能被脱敏为仅 (kg)。"""
    if snap.curb_weight_kg is not None:
        return
    result = cfg.get("result")
    if not isinstance(result, dict):
        return
    groups = result.get("paramtypeitems")
    if not isinstance(groups, list):
        return
    for grp in groups:
        if not isinstance(grp, dict):
            continue
        gt = _group_title_normalized(grp)
        if "基本" not in gt or "参数" not in gt:
            continue
        for it in grp.get("paramitems") or []:
            if not isinstance(it, dict):
                continue
            dlabel = _display_param_name(it.get("name") or it.get("itemname") or "")
            text = _valueitems_first_nonempty(it.get("valueitems"))
            v = _parse_int_loose(text)
            if v is None or v < 400 or v > 8000:
                continue
            if "整备质量" in dlabel or "装备质量" in dlabel:
                snap.curb_weight_kg = v
                return
        for it in grp.get("paramitems") or []:
            if not isinstance(it, dict):
                continue
            dlabel = _display_param_name(it.get("name") or it.get("itemname") or "")
            text = _valueitems_first_nonempty(it.get("valueitems"))
            v = _parse_int_loose(text)
            if v is None or v < 800 or v > 4500:
                continue
            if _label_only_unit_kg(dlabel):
                snap.curb_weight_kg = v
                return
        break


def _parse_int_loose(s: str) -> Optional[int]:
    m = re.search(r"-?\d+", (s or "").replace(",", ""))
    if not m:
        return None
    try:
        return int(m.group(0))
    except ValueError:
        return None


def _parse_decimal_loose(s: str) -> Optional[Decimal]:
    m = re.search(r"-?\d+(?:\.\d+)?", s or "")
    if not m:
        return None
    try:
        return Decimal(m.group(0))
    except Exception:
        return None


def _parse_l_w_h(s: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    t = (s or "").replace("×", "*").replace("x", "*").replace("X", "*")
    parts = [p.strip() for p in t.split("*") if p.strip()]
    if len(parts) < 3:
        return None, None, None

    def head_int(x: str) -> Optional[int]:
        m = re.match(r"^(\d+)", x.strip())
        return int(m.group(1)) if m else None

    return head_int(parts[0]), head_int(parts[1]), head_int(parts[2])


def specs_from_config_dict(cfg: Dict[str, Any]) -> ParsedSeriesSpecs:
    """
    按参配表列名做文字匹配（与官网「基本参数 / 车身」等分组无关），
    同一字段多行命中时以后续成功解析为准。
    """
    snap = ParsedSeriesSpecs()
    for label, text in iter_flat_param_rows(cfg):
        if not text:
            continue
        # 能源类型
        if "能源类型" in label:
            snap.energy_type = text
        # 长*宽*高 合并列
        elif ("长" in label and "宽" in label and "高" in label) or "长*宽*高" in label:
            l, w, h = _parse_l_w_h(text)
            if l is not None:
                snap.length_mm = l
            if w is not None:
                snap.width_mm = w
            if h is not None:
                snap.height_mm = h
        # 分列：长度(mm) / 宽度(mm) / 高度(mm)（车身或基本参数里常见）
        elif "车长" in label or ("长度" in label and "mm" in label):
            v = _parse_int_loose(text)
            if v is not None:
                snap.length_mm = v
        elif "车宽" in label or ("宽度" in label and "mm" in label):
            v = _parse_int_loose(text)
            if v is not None:
                snap.width_mm = v
        elif "车高" in label or (
            "高度" in label and "mm" in label and "离地" not in label
        ):
            v = _parse_int_loose(text)
            if v is not None:
                snap.height_mm = v
        elif "轴距" in label:
            v = _parse_int_loose(text)
            if v is not None:
                snap.wheelbase_mm = v
        elif "前轮距" in label:
            v = _parse_int_loose(text)
            if v is not None:
                snap.front_track_mm = v
        elif "后轮距" in label:
            v = _parse_int_loose(text)
            if v is not None:
                snap.rear_track_mm = v
        elif "接近角" in label:
            d = _parse_decimal_loose(text)
            if d is not None:
                snap.approach_angle = d
        elif "离去角" in label:
            d = _parse_decimal_loose(text)
            if d is not None:
                snap.departure_angle = d
        elif "整备质量" in label or "装备质量" in label:
            v = _parse_int_loose(text)
            if v is not None:
                snap.curb_weight_kg = v
    _fill_body_group_by_mm_row_order(cfg, snap)
    _fill_curb_weight_from_basic_group(cfg, snap)
    return snap


def iter_spec_ids_from_html(html: str) -> List[int]:
    seen: set = set()
    out: List[int] = []
    for m in _RE_SPEC_ID.finditer(html or ""):
        sid = int(m.group(1))
        if sid not in seen:
            seen.add(sid)
            out.append(sid)
    return out


def iter_year_suffix_ids(html: str, series_id: int) -> List[int]:
    out: List[int] = []
    for a, b in _RE_SERIES_YEAR.findall(html or ""):
        if int(a) == series_id:
            yid = int(b)
            if yid not in out:
                out.append(yid)
    return out


async def _get_html(client: httpx.AsyncClient, url: str) -> Tuple[int, str]:
    try:
        r = await client.get(
            url,
            headers={
                "User-Agent": DEFAULT_USER_AGENT,
                "Referer": "https://www.autohome.com.cn/",
                "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
            },
            timeout=httpx.Timeout(45.0),
            follow_redirects=True,
        )
        return r.status_code, r.text or ""
    except Exception as e:
        logger.debug("GET %s: %s", url, e)
        return 0, ""


async def _try_specs_from_series_html(
    html: str,
) -> Optional[ParsedSeriesSpecs]:
    cfg = extract_config_dict_from_spec_html(html)
    if not cfg or not config_has_param_table(cfg):
        return None
    try:
        return specs_from_config_dict(cfg)
    except Exception as e:
        logger.debug("parse specs from series html: %s", e)
        return None


async def resolve_representative_spec_id(
    client: httpx.AsyncClient, series_id: int
) -> Tuple[Optional[int], str]:
    """
    返回 (spec_id, 最后使用的 host 前缀 www|car)，用于拼单车型参配 URL。
    优先 www，与前台参配对比页一致（如 /config/series/6643.html）。
    """
    for series_tpl, year_tpl in (
        (URL_CONFIG_SERIES_WWW, URL_CONFIG_SERIES_YEAR_WWW),
        (URL_CONFIG_SERIES_CAR, URL_CONFIG_SERIES_YEAR_CAR),
    ):
        url = series_tpl.format(series_id=series_id)
        st, html = await _get_html(client, url)
        if st != 200:
            continue
        host = HOST_WWW if "www.autohome" in url else HOST_CAR
        ids = iter_spec_ids_from_html(html)
        if ids:
            return ids[0], host
        for yid in iter_year_suffix_ids(html, series_id)[:8]:
            yurl = year_tpl.format(series_id=series_id, year_id=yid)
            st2, h2 = await _get_html(client, yurl)
            if st2 != 200:
                continue
            ids2 = iter_spec_ids_from_html(h2)
            if ids2:
                return ids2[0], host
    return None, HOST_WWW


async def fetch_series_specs_snapshot(
    client: httpx.AsyncClient, series_id: int
) -> Optional[ParsedSeriesSpecs]:
    # 1) 车系对比页本体常已内嵌 config（多列取首列），无需再请求 spec
    for series_tpl, year_tpl in (
        (URL_CONFIG_SERIES_WWW, URL_CONFIG_SERIES_YEAR_WWW),
        (URL_CONFIG_SERIES_CAR, URL_CONFIG_SERIES_YEAR_CAR),
    ):
        surl = series_tpl.format(series_id=series_id)
        st, html = await _get_html(client, surl)
        if st == 200:
            snap = await _try_specs_from_series_html(html)
            if snap:
                return snap
            for yid in iter_year_suffix_ids(html, series_id)[:8]:
                yurl = year_tpl.format(series_id=series_id, year_id=yid)
                st2, h2 = await _get_html(client, yurl)
                if st2 != 200:
                    continue
                snap2 = await _try_specs_from_series_html(h2)
                if snap2:
                    return snap2

    # 2) 兜底：从页面收集 spec 链接再打开单车型参配页
    spec_id, host = await resolve_representative_spec_id(client, series_id)
    if spec_id is None:
        return None
    spec_tpl = URL_CONFIG_SPEC_WWW if host == HOST_WWW else URL_CONFIG_SPEC_CAR
    alt_tpl = URL_CONFIG_SPEC_CAR if host == HOST_WWW else URL_CONFIG_SPEC_WWW
    for tpl in (spec_tpl, alt_tpl):
        url = tpl.format(spec_id=spec_id)
        st, html = await _get_html(client, url)
        if st != 200:
            continue
        cfg = extract_config_dict_from_spec_html(html)
        if not cfg:
            continue
        try:
            return specs_from_config_dict(cfg)
        except Exception as e:
            logger.debug("parse specs spec_id=%s: %s", spec_id, e)
    return None
