"""挂牌状态机：合法流转的唯一判定点（纯逻辑，零 DB）

对应 01.架构与撮合内核设计.md §4.2 的状态图。把流转表集中在这里，是因为挂牌
状态会被四类角色改动——发布方、运营、成交流程、巡检 Worker——各自散写
``if post.status == ...`` 迟早会出现「某条路径漏判」的越权或脏状态。

## 表里包含、但状态图上没画的两条

| 流转 | 为什么必须允许 |
|------|--------------|
| 待审核 → 已下架 | 源单联动（`01` §5.3）会在挂牌还排在审核队列里时就判定信息失效，此时必须能下架；同时也是发布方「等不及了，先撤回」的出口 |
| 审核未通过 → 已下架 | 给发布方一个「这条不发了」的收口，否则驳回态会永久滞留在「我发布的」列表里 |

## 表里刻意不包含的两条

``已锁定 → 已下架`` 与 ``履约中 → 已下架``。这两个状态下都有成交单在跑，
从挂牌侧下架会留下一张指向「已下架挂牌」的孤儿成交单。运营遇到这类违规
应当走成交单终止流程，而不是把挂牌抽走。

## 职责边界

本模块只回答「这个流转本身合不合法」，**不回答「谁有资格触发」**。
后者由各 Service 方法自己判定（例如发布方不能主动下架已锁定的挂牌，
但那不是因为流转非法，而是因为角色不对）。
"""

from __future__ import annotations

from typing import Dict, FrozenSet, Optional

from app.common.exceptions import BizException
from app.modules.console.models.ecosystem.constants import PostStatus

# 状态中文名，用于拼用户文案。用户看到的必须是「已锁定」，不是 status=4
STATUS_LABELS: Dict[int, str] = {
    PostStatus.DRAFT: "草稿",
    PostStatus.AUDITING: "待审核",
    PostStatus.REJECTED: "审核未通过",
    PostStatus.LISTED: "展示中",
    PostStatus.LOCKED: "已锁定",
    PostStatus.FULFILLING: "履约中",
    PostStatus.FINISHED: "已完成",
    PostStatus.DELISTED: "已下架",
    PostStatus.CANCELLED: "已取消",
}

ALLOWED_TRANSITIONS: Dict[int, FrozenSet[int]] = {
    PostStatus.DRAFT: frozenset({PostStatus.AUDITING, PostStatus.DELISTED}),
    PostStatus.AUDITING: frozenset(
        {PostStatus.LISTED, PostStatus.REJECTED, PostStatus.DELISTED}
    ),
    PostStatus.REJECTED: frozenset({PostStatus.AUDITING, PostStatus.DELISTED}),
    # 展示中 → 待审核：编辑了核心信息，需完整重审（04 §2.4）
    PostStatus.LISTED: frozenset(
        {PostStatus.AUDITING, PostStatus.LOCKED, PostStatus.DELISTED}
    ),
    PostStatus.LOCKED: frozenset({PostStatus.LISTED, PostStatus.FULFILLING}),
    PostStatus.FULFILLING: frozenset({PostStatus.FINISHED, PostStatus.CANCELLED}),
    PostStatus.FINISHED: frozenset(),
    PostStatus.DELISTED: frozenset({PostStatus.AUDITING}),
    PostStatus.CANCELLED: frozenset(),
}


def describe(status: Optional[int]) -> str:
    """状态中文名，未知值退化为「未知状态」而不是抛错

    历史数据里出现表外取值时，用户看到一句能读懂的话比看到 500 好。
    """
    if status is None:
        return "未知状态"
    return STATUS_LABELS.get(int(status), "未知状态")


def can_transit(from_status: Optional[int], to_status: Optional[int]) -> bool:
    """流转是否合法。原地不动（from == to）视为合法，便于 FAST 编辑复用"""
    if from_status is None or to_status is None:
        return False
    if int(from_status) == int(to_status):
        return True
    return int(to_status) in ALLOWED_TRANSITIONS.get(int(from_status), frozenset())


def assert_transit(
    from_status: Optional[int],
    to_status: Optional[int],
    *,
    action: str,
    advice: Optional[str] = None,
) -> None:
    """流转非法时抛出可读的业务异常

    Args:
        action: 用户视角的动作名，如「停止展示」「重新上架」
        advice: 可选的下一步建议。没有建议时不硬凑，一句空话比没有更差
    """
    if can_transit(from_status, to_status):
        return
    tail = f"，{advice}" if advice else ""
    raise BizException(f"这条挂牌现在是「{describe(from_status)}」，不能{action}{tail}")


def is_terminal(status: Optional[int]) -> bool:
    return status is not None and int(status) in PostStatus.TERMINAL


def is_editable(status: Optional[int]) -> bool:
    return status is not None and int(status) in PostStatus.EDITABLE
