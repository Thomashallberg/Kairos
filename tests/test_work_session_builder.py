from datetime import datetime, timedelta

from app.models import WorkBlock
from app.services.work_session_builder import WorkSessionBuilder


def test_single_work_block_creates_single_session():
    block = WorkBlock(
        start_time=datetime(2026, 8, 2, 9, 0),
        end_time=datetime(2026, 8, 2, 10, 0),
        category="Development",
        processes=["Code.exe"],
        context=["main.py"],
    )

    sessions = WorkSessionBuilder.build([block])

    assert len(sessions) == 1

    session = sessions[0]

    assert session.primary_category == "Development"
    assert session.start_time == block.start_time
    assert session.end_time == block.end_time
    assert session.work_blocks == [block]
    
def test_supporting_browser_activity_belongs_to_same_work_session():
    start = datetime(2026, 8, 2, 9, 30)

    development_before = WorkBlock(
        start_time=start,
        end_time=start + timedelta(minutes=15),
        category="Development",
        processes=["Code.exe"],
        context=["activity_service.py - Kairos"],
    )

    browser_research = WorkBlock(
        start_time=start + timedelta(minutes=15),
        end_time=start + timedelta(minutes=16),
        category="Browser",
        processes=["chrome.exe"],
        context=["SQLAlchemy documentation"],
    )

    development_after = WorkBlock(
        start_time=start + timedelta(minutes=16),
        end_time=start + timedelta(minutes=30),
        category="Development",
        processes=["Code.exe"],
        context=["activity_service.py - Kairos"],
    )

    sessions = WorkSessionBuilder.build(
        [
            development_before,
            browser_research,
            development_after,
        ]
    )

    assert len(sessions) == 1

    session = sessions[0]

    assert session.start_time == start
    assert session.end_time == start + timedelta(minutes=30)
    assert session.primary_category == "Development"
    assert session.work_blocks == [
        development_before,
        browser_research,
        development_after,
    ]
    
def test_meeting_breaks_work_session():
    start = datetime(2026, 8, 2, 9, 0)

    development_before = WorkBlock(
        start_time=start,
        end_time=start + timedelta(minutes=30),
        category="Development",
        processes=["Code.exe"],
        context=["main.py"],
    )

    meeting = WorkBlock(
        start_time=start + timedelta(minutes=30),
        end_time=start + timedelta(minutes=60),
        category="Meeting",
        processes=["ms-teams.exe"],
        context=["Daily Scrum"],
    )

    development_after = WorkBlock(
        start_time=start + timedelta(minutes=60),
        end_time=start + timedelta(minutes=90),
        category="Development",
        processes=["Code.exe"],
        context=["activity_service.py"],
    )

    sessions = WorkSessionBuilder.build(
        [
            development_before,
            meeting,
            development_after,
        ]
    )

    assert len(sessions) == 3
    
    
def test_empty_input_returns_empty_list():
    sessions = WorkSessionBuilder.build([])

    assert sessions == []