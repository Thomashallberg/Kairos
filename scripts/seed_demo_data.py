from datetime import date, datetime, time

from app.database.connection import SessionLocal, create_database
from app.repositories.activity_repository import ActivityRepository


def at(hour: int, minute: int) -> datetime:
    return datetime.combine(
        date.today(),
        time(hour=hour, minute=minute),
    )


def main() -> None:
    create_database()

    demo_activities = [
        {
            "start_time": at(9, 0),
            "end_time": at(9, 30),
            "process_name": "ms-teams.exe",
            "window_title": "Daily Scrum | Microsoft Teams",
        },
        {
            "start_time": at(9, 30),
            "end_time": at(10, 20),
            "process_name": "Code.exe",
            "window_title": "activity_service.py - Kairos - Visual Studio Code",
        },
        {
            "start_time": at(10, 20),
            "end_time": at(10, 45),
            "process_name": "chrome.exe",
            "window_title": "KAI-123 Improve activity reporting - Jira",
        },
        {
            "start_time": at(10, 45),
            "end_time": at(12, 0),
            "process_name": "Code.exe",
            "window_title": "prompt_builder.py - Kairos - Visual Studio Code",
        },
        {
            "start_time": at(13, 0),
            "end_time": at(13, 25),
            "process_name": "OUTLOOK.EXE",
            "window_title": "Customer follow-up - Outlook",
        },
        {
            "start_time": at(13, 25),
            "end_time": at(14, 40),
            "process_name": "Code.exe",
            "window_title": "git_integration.py - Kairos - Visual Studio Code",
        },
        {
            "start_time": at(14, 40),
            "end_time": at(15, 10),
            "process_name": "ms-teams.exe",
            "window_title": "Customer sync | Microsoft Teams",
        },
        {
            "start_time": at(15, 10),
            "end_time": at(16, 0),
            "process_name": "Code.exe",
            "window_title": "ollama_client.py - Kairos - Visual Studio Code",
        },
    ]

    with SessionLocal() as session:
        repository = ActivityRepository(session)

        for activity in demo_activities:
            repository.create(**activity)

    print(f"Inserted {len(demo_activities)} demo activities.")


if __name__ == "__main__":
    main()