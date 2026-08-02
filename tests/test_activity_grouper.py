from datetime import datetime, timedelta

from app.models import Activity
from app.services.activity_grouper import ActivityGrouper


def make_activity(
    start: datetime,
    end: datetime,
    process_name: str,
    window_title: str,
) -> Activity:
    return Activity(
        start_time=start,
        end_time=end,
        process_name=process_name,
        window_title=window_title,
    )


def test_empty_activity_list_returns_no_groups():
    assert ActivityGrouper.group_consecutive([]) == []


def test_consecutive_activities_with_same_category_are_grouped():
    start = datetime(2026, 8, 2, 9, 0)

    first = make_activity(
        start,
        start + timedelta(minutes=10),
        "Code.exe",
        "main.py - Kairos - Visual Studio Code",
    )

    second = make_activity(
        start + timedelta(minutes=10),
        start + timedelta(minutes=20),
        "Code.exe",
        "activity_service.py - Kairos - Visual Studio Code",
    )

    groups = ActivityGrouper.group_consecutive([first, second])

    assert len(groups) == 1
    assert groups[0] == [first, second]


def test_category_change_creates_new_group():
    start = datetime(2026, 8, 2, 9, 0)

    development = make_activity(
        start,
        start + timedelta(minutes=10),
        "Code.exe",
        "main.py - Kairos - Visual Studio Code",
    )

    browser = make_activity(
        start + timedelta(minutes=10),
        start + timedelta(minutes=20),
        "chrome.exe",
        "SQLAlchemy documentation - Google Chrome",
    )

    groups = ActivityGrouper.group_consecutive(
        [development, browser]
    )

    assert len(groups) == 2
    assert groups[0] == [development]
    assert groups[1] == [browser]


def test_build_work_block_preserves_time_and_context():
    start = datetime(2026, 8, 2, 9, 0)

    first = make_activity(
        start,
        start + timedelta(minutes=10),
        "Code.exe",
        "main.py - Kairos - Visual Studio Code",
    )

    second = make_activity(
        start + timedelta(minutes=10),
        start + timedelta(minutes=20),
        "Code.exe",
        "activity_service.py - Kairos - Visual Studio Code",
    )

    blocks = ActivityGrouper.build_work_blocks([first, second])

    assert len(blocks) == 1

    block = blocks[0]

    assert block.start_time == first.start_time
    assert block.end_time == second.end_time
    assert block.category == "Development"
    assert block.processes == ["Code.exe"]
    assert block.context == [
        "activity_service.py - Kairos - Visual Studio Code",
        "main.py - Kairos - Visual Studio Code",
    ]