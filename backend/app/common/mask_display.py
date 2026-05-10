"""
展示用脱敏（非加密）：用于协作动态等场景，避免企业/客户全称直接曝光。
"""

from __future__ import annotations

from typing import Optional


def mask_organization_name(name: Optional[str]) -> str:
    """
    客户/企业名称脱敏，用于「最新动态」摘要文案。

    规则（产品约定）：
    - 名称长度 **≥4**：保留 **第 1 字** + 固定 `***` + **最后 2 字**（如「小***公司」）。
    - 名称长度 **<4**：只保留第 1 字，其余位全部用 `*` 填充（1 字名仅显示该字）。

    示例：
    - 「小米通讯有限公司」→「小***公司」
    - 「京东」→「京*」
    - 「阿里」→「阿*」（2 字）
    """
    if name is None:
        return "**"
    s = str(name).strip()
    n = len(s)
    if n == 0:
        return "**"
    if n < 4:
        if n == 1:
            return s[0]
        return s[0] + "*" * (n - 1)

    return s[0] + "***" + s[-2:]
