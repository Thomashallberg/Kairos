from datetime import date, datetime

from app.models import Activity
from app.repositories.activity_repository import ActivityRepository


class ActivityService:
    def __init__(self, repository: ActivityRepository) -> None:
        self.repository = repository

    def record_activity(
        self,
        process_name: str | None,
        window_title: str | None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> Activity:
        return self.repository.create(
            start_time=start_time or datetime.now(),
            end_time=end_time,
            process_name=process_name,
            window_title=window_title,
        )

    def get_all_activities(self) -> list[Activity]:
        return self.repository.get_all()

    def get_activities_for_date(
        self,
        target_date: date,
    ) -> list[Activity]:
        return self.repository.get_by_date(target_date)

    def get_today_activities(self) -> list[Activity]:
        return self.get_activities_for_date(date.today())
