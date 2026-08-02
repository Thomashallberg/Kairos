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