import argparse

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

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    command = args.command

    create_database()

    with SessionLocal() as session:
        repository = ActivityRepository(session)
        activity_service = ActivityService(repository)
        daily_report_service = DailyReportService(activity_service)

        if command == "track":
            track_activity(activity_service)

        elif command == "report":
            print(daily_report_service.generate_today_report())

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

            print(ai_summary_service.summarize_today())


if __name__ == "__main__":
    main()