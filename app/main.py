import sys

from app.ai.ollama_client import OllamaClient
from app.collectors.activity_tracker import track_activity
from app.database.connection import SessionLocal, create_database
from app.repositories.activity_repository import ActivityRepository
from app.services.activity_service import ActivityService
from app.services.ai_summary_service import AISummaryService
from app.services.daily_report_service import DailyReportService
from app.services.prompt_builder import PromptBuilder


def print_usage() -> None:
    print("Usage:")
    print("  python -m app.main track")
    print("  python -m app.main report")
    print("  python -m app.main summarize")


def main() -> None:
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1].lower()

    create_database()

    with SessionLocal() as session:
        repository = ActivityRepository(session)
        activity_service = ActivityService(repository)
        daily_report_service = DailyReportService(activity_service)
        prompt_builder = PromptBuilder(daily_report_service)
        ollama_client = OllamaClient()
        ai_summary_service = AISummaryService(
            prompt_builder,
            ollama_client,
        )

        if command == "track":
            track_activity(activity_service)

        elif command == "report":
            print(daily_report_service.generate_today_report())

        elif command == "summarize":
            print(ai_summary_service.summarize_today())

        else:
            print(f"Unknown command: {command}")
            print_usage()


if __name__ == "__main__":
    main()