from datetime import datetime, timedelta

from app.models import WorkBlock, ReportPeriod, WorkSession
from app.services.report_period_builder import ReportPeriodBuilder


def make_session(
    start_time: datetime,
    duration_minutes: int,
    category: str,
    context: str,
) -> WorkSession:
    end_time = start_time + timedelta(minutes=duration_minutes)

    block = WorkBlock(
        start_time=start_time,
        end_time=end_time,
        category=category,
        processes=[],
        context=[context],
    )

    return WorkSession(
        start_time=start_time,
        end_time=end_time,
        primary_category=category,
        work_blocks=[block],
    )


def test_related_short_sessions_are_combined_into_larger_report_period():
    start = datetime(2026, 8, 2, 12, 24)

    development_before = make_session(
        start_time=start,
        duration_minutes=4,
        category="Development",
        context="activity_rules.py - Kairos",
    )

    supporting_research = make_session(
        start_time=start + timedelta(minutes=4),
        duration_minutes=4,
        category="Browser",
        context="AI agent course and documentation",
    )

    development_after = make_session(
        start_time=start + timedelta(minutes=8),
        duration_minutes=5,
        category="Development",
        context="work_block.py - Kairos",
    )

    periods = ReportPeriodBuilder.build(
        [
            development_before,
            supporting_research,
            development_after,
        ]
    )

    assert len(periods) == 1

    period = periods[0]

    assert period.start_time == start
    assert period.end_time == start + timedelta(minutes=13)
    assert period.primary_category == "Development"
    assert period.work_sessions == [
        development_before,
        supporting_research,
        development_after,
    ]
def test_long_supporting_session_is_not_combined():
    start = datetime(2026, 8, 2, 12, 24)

    development_before = make_session(
        start_time=start,
        duration_minutes=4,
        category="Development",
        context="activity_rules.py - Kairos",
    )

    long_course_session = make_session(
        start_time=start + timedelta(minutes=4),
        duration_minutes=25,
        category="Browser",
        context="AI agent builder course on Udemy",
    )

    development_after = make_session(
        start_time=start + timedelta(minutes=29),
        duration_minutes=5,
        category="Development",
        context="work_block.py - Kairos",
    )

    periods = ReportPeriodBuilder.build(
        [
            development_before,
            long_course_session,
            development_after,
        ]
    )

    assert len(periods) == 3
    assert periods[0].work_sessions == [development_before]
    assert periods[1].work_sessions == [long_course_session]
    assert periods[2].work_sessions == [development_after]