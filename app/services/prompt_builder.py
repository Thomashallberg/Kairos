from app.services.daily_report_service import DailyReportService


class PromptBuilder:
    def __init__(self, daily_report_service: DailyReportService) -> None:
        self.daily_report_service = daily_report_service

    def build_daily_summary_prompt(self) -> str:
        report = self.daily_report_service.generate_today_report()

        return f"""You are an experienced IT consultant.

Your task is to transform the following activity log into a professional consultant time report.

Guidelines:
- Group related work together.
- Use professional language.
- Do not invent activities.
- Be concise.
- Focus on business value.

Activity Log:

{report}

Professional Time Report:
"""