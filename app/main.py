from app.collectors.activity_tracker import track_activity
from app.repositories.activity_repository import ActivityRepository
from app.database.connection import SessionLocal, create_database
from app.models import Activity
from app.services.activity_service import ActivityService


def main() -> None:
    create_database()

    with SessionLocal() as session:
        repository = ActivityRepository(session)
        activity_service = ActivityService(repository)

        track_activity(activity_service)


if __name__ == "__main__":
    main()