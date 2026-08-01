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
        work_blocks = self.daily_report_service.get_today_work_blocks()
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
        work_blocks = self.daily_report_service.get_today_work_blocks()
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

        return f"""You are an AI assistant that prepares professional consultant time reports.

You MUST summarize the work ONLY from the supplied activity data and Git context.

Rules:
- Never invent meetings, customers, ticket numbers, projects, tasks or outcomes.
- Never guess work that is not supported by the supplied data.
- Git commit messages are stronger evidence than window titles.
- Preserve every time range exactly as provided.
- Never merge different time ranges.
- Ignore very short system events (less than 2 minutes) that clearly represent application switching or startup noise.
- Focus on actual work performed.
- Use professional English.
- Keep every description to one concise sentence.
- Do not mention VS Code, Chrome, Explorer or application names unless they are essential for understanding the work.

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

Example:

09:00–09:30: Participated in the daily scrum meeting.
09:30–10:20: Implemented the activity service for Kairos.
10:20–10:45: Improved activity reporting for Jira task KAI-123.

Observed Work Blocks:

{activity_text}

Git Context

Current branch:
{branch}

Recent commits:
{commits_text}

Uncommitted changed files:
{changed_files_text}

Final time report:
"""