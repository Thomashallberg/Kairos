from datetime import date

from app.models import WorkBlock
from app.services.activity_formatter import ActivityFormatter
from app.services.activity_grouper import ActivityGrouper
from app.services.activity_service import ActivityService


class DailyReportService:
    def __init__(self, activity_service: ActivityService) -> None:
        self.activity_service = activity_service

    def get_work_blocks_for_date(
        self,
        target_date: date,
    ) -> list[WorkBlock]:
        activities = self.activity_service.get_activities_for_date(target_date)
        return ActivityGrouper.build_work_blocks(activities)

    def get_today_work_blocks(self) -> list[WorkBlock]:
        return self.get_work_blocks_for_date(date.today())

    def generate_report(
        self,
        target_date: date,
    ) -> str:
        activities = self.activity_service.get_activities_for_date(target_date)
        return ActivityFormatter.format_activities(activities)

    def generate_today_report(self) -> str:
        return self.generate_report(date.today())