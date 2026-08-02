from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class WorkBlock:
    start_time: datetime
    end_time: datetime | None
    category: str
    processes: list[str]
    context: list[str]
