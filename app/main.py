import sys

from app.collectors.activity_tracker import track_activity
from app.database.connection import SessionLocal, create_database
from app.repositories.activity_repository import ActivityRepository
from app.services.activity_service import ActivityService
from app.services.daily_report_service import DailyReportService


def print_usage() -> None:
    print("Usage:")
    print("  python -m app.main track")
    print("  python -m app.main report")


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    create_database()

    with SessionLocal() as session:
        repository = ActivityRepository(session)
        activity_service = ActivityService(repository)

        if command == "track":
            track_activity(activity_service)

        elif command == "report":
            report_service = DailyReportService(activity_service)
            print(report_service.generate_today_report())

        else:
            print(f"Unknown command: {command}")
            print_usage()


if __name__ == "__main__":
    main()