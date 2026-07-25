"""审核时效：工作时段口径的 SLA 计算（纯逻辑，零 DB）

对应 04.运营审核与风控设计.md §2.1 与 §2.5：承诺 2 小时内处理（工作时段
8:30~20:30，非工作时段次日首个工作时段起算），队列里超过 1 小时未处理的标红。

## 为什么必须按工作时段算，不能用自然时长

凌晨 2 点提交的挂牌，早上 9 点审核员上班时自然时长已经 7 小时。用自然时长，
每天早上整个队列全是刺目的红色，红色也就失去了意义——审核员会开始忽略它，
而真正压线的那几条反倒被埋在里面。SLA 看板同理：把夜间等待算进平均审核时长，
指标只反映提交时间分布，不反映运营效率。

## 周末不排除

物流是七天运转的，周末的车照样在跑，货源的时效性不因为是周六就变弱。
排除周末等于告诉周五晚上发布的用户「等周一」，这条挂牌届时早已作废。
运营侧按排班覆盖周末，这里就不做例外。
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Optional

# 运营审核的工作时段
WORK_START = time(8, 30)
WORK_END = time(20, 30)

# 承诺处理时长（工作时段分钟数）
SLA_MINUTES = 120
# 队列标红阈值（工作时段分钟数），比承诺时长更早，是为了留出处理时间
WARN_MINUTES = 60

# 一次计算最多向前推的天数。正常队列里的挂牌不会等这么久，超出即视为异常数据，
# 与其死循环，不如给一个够大的结果让它排在队首被人看见
_MAX_SPAN_DAYS = 60


class AuditUrgency:
    """审核紧迫度，供队列排序与前端标色"""

    NORMAL = 0      # 正常
    WARNING = 1     # 等待超过 1 小时，标红催办
    OVERDUE = 2     # 已超出 2 小时承诺

    LABELS = {
        NORMAL: "正常",
        WARNING: "即将超时",
        OVERDUE: "已超时",
    }


def describe_urgency(level: int) -> str:
    return AuditUrgency.LABELS.get(int(level), "正常")


def work_minutes_between(start: datetime, end: datetime) -> int:
    """``start`` 到 ``end`` 之间落在工作时段内的分钟数

    ``end`` 早于 ``start`` 时返回 0，而不是负数：调用方通常在拼展示文案，
    负数分钟只会变成「已等待 -30 分钟」这种没人能理解的输出。
    """
    if end <= start:
        return 0

    total = 0
    day = start.date()
    last_day = min(end.date(), day + timedelta(days=_MAX_SPAN_DAYS))
    while day <= last_day:
        open_at = datetime.combine(day, WORK_START)
        close_at = datetime.combine(day, WORK_END)
        lo = max(start, open_at)
        hi = min(end, close_at)
        if hi > lo:
            total += int((hi - lo).total_seconds() // 60)
        day += timedelta(days=1)
    return total


def sla_deadline(submitted_at: datetime, minutes: int = SLA_MINUTES) -> datetime:
    """承诺处理时点（自然时间）

    非工作时段提交的从下一个工作时段起算，所以凌晨 2 点提交的挂牌，
    承诺时点是当天 10:30 而不是 4:00。这个值直接给运营看「几点前要处理完」。
    """
    cursor = _next_work_moment(submitted_at)
    remaining = max(0, int(minutes))
    for _ in range(_MAX_SPAN_DAYS + 1):
        close_at = datetime.combine(cursor.date(), WORK_END)
        available = int((close_at - cursor).total_seconds() // 60)
        if remaining <= available:
            return cursor + timedelta(minutes=remaining)
        remaining -= available
        cursor = datetime.combine(cursor.date() + timedelta(days=1), WORK_START)
    return cursor


def waited_minutes(submitted_at: datetime, now: Optional[datetime] = None) -> int:
    """已等待的工作时段分钟数"""
    return work_minutes_between(submitted_at, now or datetime.now())


def urgency(submitted_at: datetime, now: Optional[datetime] = None) -> int:
    """紧迫度等级"""
    waited = waited_minutes(submitted_at, now)
    if waited >= SLA_MINUTES:
        return AuditUrgency.OVERDUE
    if waited >= WARN_MINUTES:
        return AuditUrgency.WARNING
    return AuditUrgency.NORMAL


def is_overdue(submitted_at: datetime, now: Optional[datetime] = None) -> bool:
    return urgency(submitted_at, now) == AuditUrgency.OVERDUE


def overdue_before(now: datetime, minutes: int = SLA_MINUTES) -> datetime:
    """算出「提交时间早于这个时点就算超时」的自然时间界

    队列里逐条判断超时要在 Python 里跑，统计积压数却要在 SQL 里跑（几万条挂牌
    不可能全捞回来数）。这个函数把工作时段口径折算成一个可以直接写进
    ``WHERE created_at < ?`` 的时间点，让两处口径出自同一份规则。
    """
    remaining = max(0, int(minutes))
    cursor = _prev_work_moment(now)
    for _ in range(_MAX_SPAN_DAYS + 1):
        open_at = datetime.combine(cursor.date(), WORK_START)
        available = int((cursor - open_at).total_seconds() // 60)
        if remaining <= available:
            return cursor - timedelta(minutes=remaining)
        remaining -= available
        cursor = datetime.combine(cursor.date() - timedelta(days=1), WORK_END)
    return cursor


def _next_work_moment(moment: datetime) -> datetime:
    """把时间点前推到最近的工作时段内（已在时段内则原样返回）"""
    open_at = datetime.combine(moment.date(), WORK_START)
    close_at = datetime.combine(moment.date(), WORK_END)
    if moment < open_at:
        return open_at
    if moment >= close_at:
        return datetime.combine(moment.date() + timedelta(days=1), WORK_START)
    return moment


def _prev_work_moment(moment: datetime) -> datetime:
    """把时间点后退到最近的工作时段内（已在时段内则原样返回）"""
    open_at = datetime.combine(moment.date(), WORK_START)
    close_at = datetime.combine(moment.date(), WORK_END)
    if moment > close_at:
        return close_at
    if moment <= open_at:
        return datetime.combine(moment.date() - timedelta(days=1), WORK_END)
    return moment
