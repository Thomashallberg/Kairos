from datetime import date

from app.integrations.git_integration import GitIntegration
from app.services.daily_report_service import DailyReportService


class PromptBuilder:
    def __init__(
        self,
        daily_report_service: DailyReportService,
        git_integration: GitIntegration,
    ) -> None:
        self.daily_report_service = daily_report_service
        self.git_integration = git_integration

    def build_daily_summary_prompt(self) -> str:
        return self.build_summary_prompt(date.today())

    def build_summary_prompt(self, target_date: date) -> str:
        report_periods = self.daily_report_service.get_report_periods_for_date(
            target_date
        )

        branch = self.git_integration.get_current_branch()
        commits = self.git_integration.get_recent_commits()
        changed_files = self.git_integration.get_changed_files()

        commits_text = (
            "\n".join(f"- {commit}" for commit in commits)
            if commits
            else "- No recent commits found"
        )

        changed_files_text = (
            "\n".join(f"- {file}" for file in changed_files)
            if changed_files
            else "- No uncommitted files"
        )

        activity_sections: list[str] = []

        for period in report_periods:
            start_time = period.start_time.strftime("%H:%M")
            end_time = (
                period.end_time.strftime("%H:%M")
                if period.end_time is not None
                else "Ongoing"
            )

            period_sessions: list[str] = []

            for session in period.work_sessions:
                session_blocks: list[str] = []

                for block in session.work_blocks:
                    processes = ", ".join(block.processes) or "Unknown"
                    context = ", ".join(block.context) or "No additional context"

                    session_blocks.append(f"""Category: {block.category}
Processes: {processes}
Context: {context}""")

                blocks_text = "\n\n".join(session_blocks)

                period_sessions.append(f"""Session category: {session.primary_category}
Observed activities:
{blocks_text}""")

            sessions_text = "\n\n".join(period_sessions)

            activity_sections.append(f"""Report period:
{start_time}–{end_time}

Primary category:
{period.primary_category}

Included sessions:
{sessions_text}""")

        activity_text = "\n\n---\n\n".join(activity_sections)

        return f"""You are an AI assistant that prepares professional consultant time reports.

You MUST summarize the work ONLY from the supplied activity data and Git context.

Rules:
- Never invent meetings, customers, ticket numbers, projects, tasks, or outcomes.
- Never guess work that is not supported by the supplied data.
- Git commit messages are stronger evidence than window titles.
- Preserve every report period time range exactly as provided.
- Never merge different report period time ranges.
- Focus on actual work performed.
- Use professional English.
- Keep every description to one concise sentence.
- Do not mention VS Code, Chrome, Explorer, or application names unless they are essential for understanding the work.

STRICT OUTPUT REQUIREMENTS:
- Return ONLY the final time report.
- Do NOT explain your reasoning.
- Do NOT add introductions.
- Do NOT add conclusions.
- Do NOT add notes.
- Do NOT add rationale.
- Do NOT use Markdown.
- Do NOT use code blocks.
- Do NOT use bullet points.
- Every line MUST follow this exact format:

HH:MM–HH:MM: Professional work description

Observed Report Periods:

{activity_text}

Git Context:

Current branch:
{branch}

Recent commits:
{commits_text}

Uncommitted changed files:
{changed_files_text}

Final time report:
"""
