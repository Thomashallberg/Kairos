import json
from datetime import date
from typing import Any

from app.ai.ollama_client import OllamaClient
from app.models import TimeReport, TimeReportEntry
from app.services.prompt_builder import PromptBuilder

TIME_REPORT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "entries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "start_time": {"type": "string"},
                    "end_time": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": [
                    "start_time",
                    "end_time",
                    "description",
                ],
            },
        },
    },
    "required": ["entries"],
}


class AISummaryService:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        ollama_client: OllamaClient,
    ) -> None:
        self.prompt_builder = prompt_builder
        self.ollama_client = ollama_client

    def summarize(self, target_date: date) -> TimeReport:
        prompt = self.prompt_builder.build_summary_prompt(target_date)

        response = self.ollama_client.generate(
            prompt,
            response_format=TIME_REPORT_SCHEMA,
        )

        data = json.loads(response)

        entries = [
            TimeReportEntry(
                start_time=entry["start_time"],
                end_time=entry["end_time"],
                description=entry["description"],
            )
            for entry in data["entries"]
        ]

        return TimeReport(entries=entries)

    def summarize_today(self) -> TimeReport:
        return self.summarize(date.today())
