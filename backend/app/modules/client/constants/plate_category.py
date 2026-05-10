"""自有运力：车牌类型（与前端约定一致，存库为字符串）"""

from __future__ import annotations

import re
from typing import Optional

PLATE_CATEGORY_BLUE = "BLUE"
PLATE_CATEGORY_YELLOW = "YELLOW"
PLATE_CATEGORY_NEW_ENERGY = "NEW_ENERGY"

ALLOWED_PLATE_CATEGORIES = frozenset(
    {PLATE_CATEGORY_BLUE, PLATE_CATEGORY_YELLOW, PLATE_CATEGORY_NEW_ENERGY}
)

# 蓝/黄：7 个字符；新能源：8 个
PLATE_LEN_CLASSIC = 7
PLATE_LEN_NEW_ENERGY = 8


def normalize_plate_input(raw: str) -> str:
    """去空白、去常见分隔符，用于存库与长度校验。"""
    if not raw:
        return ""
    s = "".join(raw.split())
    for ch in ("·", "・", "-", "－"):
        s = s.replace(ch, "")
    return s


def validate_plate_category_value(category: Optional[str]) -> None:
    from app.common.exceptions import BizException

    if not category or category not in ALLOWED_PLATE_CATEGORIES:
        raise BizException("车牌类型无效，请选择蓝牌、黄牌或新能源")


def validate_plate_for_category(category: str, plate: str) -> None:
    from app.common.exceptions import BizException

    validate_plate_category_value(category)
    n = normalize_plate_input(plate)
    if not n:
        raise BizException("车牌号不能为空")
    if len(n) > 20:
        raise BizException("车牌号过长")

    if not ("\u4e00" <= n[0] <= "\u9fff"):
        raise BizException("车牌号应以省份简称开头")

    if category == PLATE_CATEGORY_NEW_ENERGY:
        if len(n) != PLATE_LEN_NEW_ENERGY:
            raise BizException("新能源车牌号须为 8 位（省称+字母+6 位序号）")
        rest = n[1:]
        if not re.match(r"^[A-HJ-NP-Z][0-9A-HJ-NP-Z]{6}$", rest):
            raise BizException("新能源车牌号格式不正确")
    else:
        if len(n) != PLATE_LEN_CLASSIC:
            raise BizException("车牌号须为 7 位（省称+字母+5 位序号）")
        rest = n[1:]
        if not re.match(r"^[A-HJ-NP-Z][0-9A-HJ-NP-Z]{5}$", rest):
            raise BizException("车牌号格式不正确")


def validate_trailer_plate_for_category(category: str, plate: str) -> None:
    """挂车号牌：黄牌常见为 省+字母+4 数字+「挂」，如 京A1234挂；新能源可按小型新能源规则。"""
    from app.common.exceptions import BizException

    validate_plate_category_value(category)
    n = normalize_plate_input(plate)
    if not n:
        raise BizException("挂车号牌不能为空")
    if len(n) > 20:
        raise BizException("挂车号牌过长")

    if category == PLATE_CATEGORY_NEW_ENERGY:
        validate_plate_for_category(PLATE_CATEGORY_NEW_ENERGY, plate)
        return

    # 黄牌挂车常见：省 + 字母 + 4 位数字 + 「挂」，共 7 个 Unicode 字符（如 京A1234挂）
    if len(n) != 7 or not n.endswith("挂"):
        raise BizException("挂车号牌格式应为 省称+字母+4位数字+挂（如 京A1234挂）")
    core = n[:-1]
    if not ("\u4e00" <= core[0] <= "\u9fff"):
        raise BizException("挂车号牌应以省份简称开头")
    rest = core[1:]
    if not re.match(r"^[A-HJ-NP-Z][0-9]{4}$", rest):
        raise BizException("挂车号牌格式不正确")
