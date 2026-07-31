from datetime import datetime

from app.repositories.activity_repository import ActivityRepository
from app.models import Activity


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