from datetime import date, datetime

from app.models import WorkBlock, WorkSession
from app.models.report_period import ReportPeriod
from app.services.prompt_builder import PromptBuilder


class FakeDailyReportService:
    def get_report_periods_for_date(
        self,
        target_date: date,
    ) -> list[ReportPeriod]:
        block = WorkBlock(
            start_time=datetime(2026, 8, 2, 9, 0),
            end_time=datetime(2026, 8, 2, 10, 0),
            category="Development",
            processes=["Code.exe"],
            context=["activity_service.py - Kairos"],
        )

        session = WorkSession(
            start_time=block.start_time,
            end_time=block.end_time,
            primary_category="Development",
            work_blocks=[block],
        )

        return [
            ReportPeriod(
                start_time=session.start_time,
                end_time=session.end_time,
                primary_category="Development",
                work_sessions=[session],
            )
        ]


class FakeGitIntegration:
    def get_current_branch(self) -> str:
        return "main"

    def get_recent_commits(self) -> list[str]:
        return [
            "feat: add structured time reports",
            "test: cover WorkSessionBuilder behavior",
        ]

    def get_changed_files(self) -> list[str]:
        return ["app/services/prompt_builder.py"]


def build_prompt() -> str:
    prompt_builder = PromptBuilder(
        FakeDailyReportService(),  # type: ignore[arg-type]
        FakeGitIntegration(),  # type: ignore[arg-type]
    )

    return prompt_builder.build_summary_prompt(date(2026, 8, 2))


def test_prompt_contains_work_session_context():
    prompt = build_prompt()

    assert "Observed Report Periods:" in prompt
    assert "09:00–10:00" in prompt
    assert "Primary category:\nDevelopment" in prompt
    assert "activity_service.py - Kairos" in prompt


def test_prompt_contains_git_context():
    prompt = build_prompt()

    assert "Current branch:\nmain" in prompt
    assert "- feat: add structured time reports" in prompt
    assert "- test: cover WorkSessionBuilder behavior" in prompt
    assert "- app/services/prompt_builder.py" in prompt


def test_prompt_contains_strict_output_requirements():
    prompt = build_prompt()

    assert "Return ONLY the final time report." in prompt
    assert "Do NOT explain your reasoning." in prompt
    assert "HH:MM–HH:MM: Professional work description" in prompt
