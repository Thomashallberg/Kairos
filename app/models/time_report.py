from dataclasses import dataclass


@dataclass(slots=True)
class TimeReportEntry:
    start_time: str
    end_time: str
    description: str


@dataclass(slots=True)
class TimeReport:
    entries: list[TimeReportEntry]