import argparse
from datetime import date, timedelta

from app.ai.ollama_client import OllamaClient
from app.collectors.activity_tracker import track_activity
from app.database.connection import SessionLocal, create_database
from app.integrations.git_integration import GitIntegration
from app.repositories.activity_repository import ActivityRepository
from app.services.activity_service import ActivityService
from app.services.ai_summary_service import AISummaryService
from app.services.daily_report_service import DailyReportService
from app.services.prompt_builder import PromptBuilder


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="Kairos",
        description="Privacy-first AI time reporting assistant",
    )

    parser.add_argument(
        "command",
        choices=[
            "track",
            "report",
            "summarize",
        ],
        help="Command to execute",
    )

    parser.add_argument(
        "date",
        nargs="?",
        help="Date: today, yesterday, or YYYY-MM-DD (defaults to today)",
    )

    return parser.parse_args()


def parse_report_date(value: str | None) -> date:
    if value is None or value.lower() == "today":
        return date.today()

    if value.lower() == "yesterday":
        return date.today() - timedelta(days=1)

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(
            "Invalid date. Use 'today', 'yesterday', or YYYY-MM-DD."
        ) from exc


def main() -> None:
    args = parse_args()
    command = args.command
    report_date = parse_report_date(args.date)

    create_database()

    with SessionLocal() as session:
        repository = ActivityRepository(session)
        activity_service = ActivityService(repository)
        daily_report_service = DailyReportService(activity_service)

        if command == "track":
            track_activity(activity_service)

        elif command == "report":
            print(daily_report_service.generate_report(report_date))

        elif command == "summarize":
            git_integration = GitIntegration()
            prompt_builder = PromptBuilder(
                daily_report_service,
                git_integration,
            )
            ollama_client = OllamaClient()
            ai_summary_service = AISummaryService(
                prompt_builder,
                ollama_client,
            )

            time_report = ai_summary_service.summarize(report_date)

            for entry in time_report.entries:
                print(
                    f"{entry.start_time}–{entry.end_time}: "
                    f"{entry.description}"
                )


if __name__ == "__main__":
    main()