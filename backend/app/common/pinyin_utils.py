"""拼音搜索辅助工具（与项目《拼音搜索集成指南》一致）"""

from pypinyin import Style, lazy_pinyin


def match_pinyin(text: str, keyword: str) -> bool:
    """
    判断 text 是否匹配 keyword（支持中文子串、全拼、首字母）。

    匹配规则（均忽略大小写）：
      1. 中文包含：text 包含 keyword
      2. 全拼：keyword 为全拼子串
      3. 首字母：keyword 为首字母子串
    """
    if not keyword:
        return True
    if not text:
        return False

    kw = keyword.lower().strip()
    txt = text.lower()

    if kw in txt:
        return True

    full_pinyin = "".join(lazy_pinyin(text)).lower()
    if kw in full_pinyin:
        return True

    initials = "".join(lazy_pinyin(text, style=Style.FIRST_LETTER)).lower()
    if kw in initials:
        return True

    return False
