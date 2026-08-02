from dataclasses import dataclass
from datetime import datetime

from app.models.work_session import WorkSession


@dataclass(slots=True)
class ReportPeriod:
    start_time: datetime
    end_time: datetime | None
    primary_category: str
    work_sessions: list[WorkSession]