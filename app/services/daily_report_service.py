from app.services.activity_formatter import ActivityFormatter
from app.services.activity_service import ActivityService
from app.services.activity_grouper import ActivityGrouper


class DailyReportService:
    def __init__(self, activity_service: ActivityService) -> None:
        self.activity_service = activity_service

    def generate_today_report(self) -> str:
        activities = self.activity_service.get_today_activities()

        return ActivityFormatter.format_activities(activities)
    def get_work_blocks(self):
        activities = self.activity_service.get_today_activities()

        return ActivityGrouper.build_work_blocks(activities)