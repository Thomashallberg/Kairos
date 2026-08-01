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
        work_blocks = self.daily_report_service.get_work_blocks()
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

        for block in work_blocks:
            processes = ", ".join(block.processes) or "Unknown"
            context = ", ".join(block.context) or "No additional context"

            activity_sections.append(
                f"""Time:
        {block.start_time}–{block.end_time}

        Category:
        {block.category}

        Processes:
        {processes}

        Context:
        {context}
        """
            )

        activity_text = "\n\n".join(activity_sections)

        return f"""You are assisting an IT consultant with preparing a daily time report.

The activity data below was collected automatically and may be incomplete.

Your task is to summarize the work performed based ONLY on the observed activity and Git context.

Rules:
- Never invent meetings, customers, ticket numbers, projects, tasks, or outcomes.
- Never guess work that is not supported by the supplied data.
- Preserve every provided time range exactly.
- Every output item must begin with its corresponding time range.
- Do not omit time ranges.
- Do not merge blocks with different time ranges.
- If the data is ambiguous, describe it conservatively.
- Use Git commits as stronger evidence than window titles.
- Do not claim that older commits were completed today unless supported by today's activity.
- Focus on completed or observed work rather than applications used.
- Do not add names, dates, total time, headings, placeholders, or business value claims.
- Write in professional English.
Output exactly one entry per observed work block using this format:

HH:MM–HH:MM
Professional description
Example output:

09:00–10:30
Implemented activity tracking improvements for Kairos.

10:30–11:15
Updated leave request handling in the AI HR assistant.

Observed Work Activity:

{activity_text}

Git Context:

Current branch:
{branch}

Recent commits:
{commits_text}

Uncommitted changed files:
{changed_files_text}

Summary:
"""