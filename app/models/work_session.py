from dataclasses import dataclass
from datetime import datetime

from app.models import WorkBlock


@dataclass(slots=True)
class WorkSession:
    start_time: datetime
    end_time: datetime | None

    primary_category: str

    work_blocks: list[WorkBlock]
