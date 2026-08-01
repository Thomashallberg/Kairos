from dataclasses import dataclass


@dataclass(slots=True)
class WorkBlock:
    start_time: str
    end_time: str
    category: str
    processes: list[str]
    context: list[str]