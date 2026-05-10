"""
展示用脱敏（非加密）：用于协作动态等场景，避免企业/客户全程名直接曝光。
"""

from __future__ import annotations

from typing import Optional

# 自长到短，避免「公司」误匹配在「有限公司」之前截断
_ORG_NAME_SUFFIXES: tuple[str, ...] = (
    "股份有限公司",
    "有限责任公司",
    "有限公司",
    "集团公司",
    "集团",
    "公司",
)


def mask_organization_name(name: Optional[str]) -> str:
    """
    客户/企业名称脱敏，用于「最新动态」摘要文案。

    规则简述：
    - 识别常见组织名后缀（有限公司、公司等），后缀完整保留；
    - 主体部分保留前 1～2 字（地域或简称线索），中间固定「***」；
    - 极短名称退化处理，不出现全程原文。

    示例：
    - 「北京长江大桥物流有限公司」→「北京***有限公司」
    - 「京东」→「京*」
    """
    if name is None:
        return "**"
    s = str(name).strip()
    n = len(s)
    if n == 0:
        return "**"
    if n <= 2:
        return s[0] + "*"

    suffix = ""
    base = s
    for suf in _ORG_NAME_SUFFIXES:
        if n > len(suf) and s.endswith(suf):
            suffix = suf
            base = s[: n - len(suf)]
            break

    if not suffix and n >= 4:
        suffix = s[-2:]
        base = s[:-2]

    bn = len(base)
    if bn <= 0:
        return "***" + suffix
    if bn <= 3:
        head = base[0] + "*"
    else:
        head = base[:2]

    return head + "***" + suffix
