from datetime import datetime, date, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Activity


class ActivityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        start_time: datetime,
        process_name: str | None,
        window_title: str | None,
        end_time: datetime | None = None,
    ) -> Activity:
        activity = Activity(
            start_time=start_time,
            end_time=end_time,
            process_name=process_name,
            window_title=window_title,
        )

        self.session.add(activity)
        self.session.commit()
        self.session.refresh(activity)

        return activity

    def get_all(self) -> list[Activity]:
        statement = select(Activity).order_by(Activity.start_time)

        return list(
            self.session.scalars(statement).all()
        )
    def get_by_date(self, target_date: date) -> list[Activity]:
        day_start = datetime.combine(target_date, time.min)
        day_end = datetime.combine(target_date, time.max)

        statement = (
        select(Activity)
        .where(Activity.start_time >= day_start)
        .where(Activity.start_time <= day_end)
        .order_by(Activity.start_time)
        )

        return list(self.session.scalars(statement).all())