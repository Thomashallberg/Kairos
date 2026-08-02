from datetime import datetime, timedelta

from app.models import WorkBlock
from app.services.work_block_normalizer import WorkBlockNormalizer


def test_short_interruption_between_same_category_is_merged():
    start = datetime(2026, 8, 2, 9, 0)

    development_before = WorkBlock(
        start_time=start,
        end_time=start + timedelta(minutes=30),
        category="Development",
        processes=["Code.exe"],
        context=["main.py"],
    )

    short_interruption = WorkBlock(
        start_time=start + timedelta(minutes=30),
        end_time=start + timedelta(minutes=30, seconds=3),
        category="File Management",
        processes=["explorer.exe"],
        context=[],
    )

    development_after = WorkBlock(
        start_time=start + timedelta(minutes=30, seconds=3),
        end_time=start + timedelta(minutes=60),
        category="Development",
        processes=["Code.exe"],
        context=["activity_service.py"],
    )

    normalized = WorkBlockNormalizer.merge_short_interruptions(
        [
            development_before,
            short_interruption,
            development_after,
        ]
    )

    assert len(normalized) == 1

    merged = normalized[0]

    assert merged.start_time == start
    assert merged.end_time == start + timedelta(minutes=60)
    assert merged.category == "Development"
    assert merged.processes == ["Code.exe"]
    assert merged.context == ["activity_service.py", "main.py"]


def test_long_interruption_is_not_merged():
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
        context=["Customer meeting"],
    )

    development_after = WorkBlock(
        start_time=start + timedelta(minutes=60),
        end_time=start + timedelta(minutes=90),
        category="Development",
        processes=["Code.exe"],
        context=["activity_service.py"],
    )

    normalized = WorkBlockNormalizer.merge_short_interruptions(
        [
            development_before,
            meeting,
            development_after,
        ]
    )

    assert normalized == [
        development_before,
        meeting,
        development_after,
    ]


def test_different_surrounding_categories_are_not_merged():
    start = datetime(2026, 8, 2, 9, 0)

    development = WorkBlock(
        start_time=start,
        end_time=start + timedelta(minutes=30),
        category="Development",
        processes=["Code.exe"],
        context=["main.py"],
    )

    short_interruption = WorkBlock(
        start_time=start + timedelta(minutes=30),
        end_time=start + timedelta(minutes=30, seconds=3),
        category="File Management",
        processes=["explorer.exe"],
        context=[],
    )

    email = WorkBlock(
        start_time=start + timedelta(minutes=30, seconds=3),
        end_time=start + timedelta(minutes=45),
        category="Email",
        processes=["OUTLOOK.EXE"],
        context=["Customer follow-up"],
    )

    normalized = WorkBlockNormalizer.merge_short_interruptions(
        [
            development,
            short_interruption,
            email,
        ]
    )

    assert normalized == [
        development,
        short_interruption,
        email,
    ]
