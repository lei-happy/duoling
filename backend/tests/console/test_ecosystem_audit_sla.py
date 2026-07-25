"""服务平台 · 审核时效（工作时段 SLA）测试

本模块守一条底线：**等待时长按工作时段算，不按自然时长算。**

凌晨 2 点提交的挂牌，早上 9 点审核员上班时自然时长已经 7 小时。用自然时长，
每天早上整个队列全是红的，红色也就失去了意义；SLA 看板上的「平均审核时长」
也只反映提交时间分布，不反映运营效率。

同时守一条一致性底线：Python 里逐条判超时（``urgency``）与 SQL 里统计积压数
（``overdue_before``）必须给出同一个答案，否则会出现「列表标红了但告警没报」。

对应需求：doc/02.需求文档/02.企业端/13.服务平台/04.运营审核与风控设计.md §2.1 §2.5
对应代码：backend/app/modules/console/services/ecosystem/audit_sla.py
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.modules.console.services.ecosystem import audit_sla
from app.modules.console.services.ecosystem.audit_sla import (
    SLA_MINUTES,
    WARN_MINUTES,
    AuditUrgency,
    describe_urgency,
    is_overdue,
    overdue_before,
    sla_deadline,
    urgency,
    waited_minutes,
    work_minutes_between,
)


def at(day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, day, hour, minute)


# ---------------------------------------------------------------------------
# 工作时段分钟数
# ---------------------------------------------------------------------------


class TestWorkMinutes:
    def test_fully_inside_work_hours(self):
        assert work_minutes_between(at(20, 9, 0), at(20, 11, 0)) == 120

    def test_end_before_start_is_zero_not_negative(self):
        """负数分钟会变成「已等待 -30 分钟」这种没人能读的文案"""
        assert work_minutes_between(at(20, 11, 0), at(20, 9, 0)) == 0

    def test_same_moment_is_zero(self):
        assert work_minutes_between(at(20, 9, 0), at(20, 9, 0)) == 0

    def test_before_work_start_does_not_count(self):
        """6:00 提交、9:00 现在：只有 8:30 之后的 30 分钟算等待"""
        assert work_minutes_between(at(20, 6, 0), at(20, 9, 0)) == 30

    def test_after_work_end_does_not_count(self):
        assert work_minutes_between(at(20, 19, 30), at(20, 23, 0)) == 60

    def test_whole_night_counts_nothing(self):
        """21:00 到次日 8:00 之间一分钟都不该算"""
        assert work_minutes_between(at(20, 21, 0), at(21, 8, 0)) == 0

    def test_across_days_sums_each_window(self):
        """前一天 19:00 到次日 9:00 = 90 + 30"""
        assert work_minutes_between(at(20, 19, 0), at(21, 9, 0)) == 120

    def test_full_day_span(self):
        """8:30~20:30 是 720 分钟"""
        assert work_minutes_between(at(20, 0, 0), at(20, 23, 59)) == 720

    def test_multiple_full_days(self):
        assert work_minutes_between(at(20, 0, 0), at(22, 23, 59)) == 720 * 3

    def test_span_beyond_cap_does_not_hang(self):
        """异常数据（等了两年）不能把计算卡死，给一个够大的值让它排队首"""
        result = work_minutes_between(at(20, 9, 0), at(20, 9, 0) + timedelta(days=800))
        assert result >= 720 * 60


# ---------------------------------------------------------------------------
# 承诺时点
# ---------------------------------------------------------------------------


class TestSlaDeadline:
    def test_within_work_hours(self):
        assert sla_deadline(at(20, 9, 0)) == at(20, 11, 0)

    def test_before_work_starts_counts_from_open(self):
        """凌晨 2 点提交，承诺时点是当天 10:30 而不是 4:00"""
        assert sla_deadline(at(20, 2, 0)) == at(20, 10, 30)

    def test_after_work_ends_counts_from_next_morning(self):
        assert sla_deadline(at(20, 22, 0)) == at(21, 10, 30)

    def test_exactly_at_work_end_rolls_to_next_day(self):
        assert sla_deadline(at(20, 20, 30)) == at(21, 10, 30)

    def test_late_submission_spills_into_next_day(self):
        """20:00 提交：当天只剩 30 分钟，余下 90 分钟顺延到次日"""
        assert sla_deadline(at(20, 20, 0)) == at(21, 10, 0)

    def test_deadline_is_reachable_by_waited_minutes(self):
        """承诺时点与等待时长必须自洽：到点时正好等了 SLA_MINUTES"""
        submitted = at(20, 20, 0)
        assert waited_minutes(submitted, sla_deadline(submitted)) == SLA_MINUTES

    def test_zero_minutes_returns_next_work_moment(self):
        assert sla_deadline(at(20, 2, 0), minutes=0) == at(20, 8, 30)


# ---------------------------------------------------------------------------
# 紧迫度
# ---------------------------------------------------------------------------


class TestUrgency:
    def test_fresh_submission_is_normal(self):
        assert urgency(at(20, 9, 0), at(20, 9, 30)) == AuditUrgency.NORMAL

    def test_one_hour_turns_warning(self):
        """§2.5：超过 1 小时未处理的标红"""
        assert urgency(at(20, 9, 0), at(20, 10, 0)) == AuditUrgency.WARNING

    def test_two_hours_turns_overdue(self):
        assert urgency(at(20, 9, 0), at(20, 11, 0)) == AuditUrgency.OVERDUE

    def test_overnight_wait_is_not_overdue_at_open(self):
        """核心用例：22:00 提交，次日 8:30 开工时不能已经是超时

        这一条挂了，每天早上队列会全红，审核员会开始无视红色。
        """
        assert urgency(at(20, 22, 0), at(21, 8, 30)) == AuditUrgency.NORMAL

    def test_overnight_wait_becomes_overdue_after_two_work_hours(self):
        assert urgency(at(20, 22, 0), at(21, 10, 30)) == AuditUrgency.OVERDUE

    def test_is_overdue_matches_urgency(self):
        assert is_overdue(at(20, 9, 0), at(20, 11, 0)) is True
        assert is_overdue(at(20, 9, 0), at(20, 10, 0)) is False

    def test_thresholds_are_ordered(self):
        assert WARN_MINUTES < SLA_MINUTES

    def test_labels_cover_all_levels(self):
        for level in (
            AuditUrgency.NORMAL,
            AuditUrgency.WARNING,
            AuditUrgency.OVERDUE,
        ):
            assert describe_urgency(level)

    def test_unknown_level_degrades_to_normal(self):
        """未知取值退化成能读的话，不抛错"""
        assert describe_urgency(99) == "正常"


# ---------------------------------------------------------------------------
# SQL 口径与 Python 口径必须一致
# ---------------------------------------------------------------------------


class TestOverdueBefore:
    def test_within_work_hours(self):
        """9:00 时，8:30 之前提交的还差 30 分钟够不上超时 → 界在前一天 19:00"""
        assert overdue_before(at(21, 9, 0)) == at(20, 19, 0)

    def test_midday_line_is_plain_subtraction(self):
        assert overdue_before(at(20, 15, 0)) == at(20, 13, 0)

    def test_after_work_hours_clamps_to_close(self):
        assert overdue_before(at(20, 23, 0)) == at(20, 18, 30)

    def test_before_work_hours_clamps_to_previous_close(self):
        assert overdue_before(at(21, 7, 0)) == at(20, 18, 30)

    @pytest.mark.parametrize(
        "now",
        [at(20, 9, 0), at(20, 15, 0), at(20, 23, 0), at(21, 7, 0), at(21, 8, 30)],
    )
    def test_line_agrees_with_urgency(self, now):
        """界上那一刻正好是超时，界之后一分钟不是——两套口径必须给同一个答案"""
        line = overdue_before(now)
        assert is_overdue(line, now) is True
        assert is_overdue(line + timedelta(minutes=2), now) is False

    def test_custom_minutes_supports_warning_line(self):
        """同一个函数也要能算标红界，否则前端标红与统计标红会分叉"""
        line = overdue_before(at(20, 15, 0), minutes=WARN_MINUTES)
        assert line == at(20, 14, 0)
        assert urgency(line, at(20, 15, 0)) >= AuditUrgency.WARNING


class TestWorkWindowConstants:
    def test_window_is_the_documented_one(self):
        assert (audit_sla.WORK_START.hour, audit_sla.WORK_START.minute) == (8, 30)
        assert (audit_sla.WORK_END.hour, audit_sla.WORK_END.minute) == (20, 30)

    def test_weekend_is_not_excluded(self):
        """周末不排除：物流七天运转，排除周末等于让周五晚上的货源等到周一

        2026-07-25 是周六。
        """
        saturday = datetime(2026, 7, 25, 9, 0)
        assert work_minutes_between(saturday, saturday + timedelta(hours=2)) == 120
