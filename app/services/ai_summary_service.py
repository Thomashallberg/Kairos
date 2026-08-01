from datetime import date

from app.ai.ollama_client import OllamaClient
from app.services.prompt_builder import PromptBuilder


class AISummaryService:
    def __init__(
        self,
        prompt_builder: PromptBuilder,
        ollama_client: OllamaClient,
    ) -> None:
        self.prompt_builder = prompt_builder
        self.ollama_client = ollama_client

    def summarize(self, target_date: date) -> str:
        prompt = self.prompt_builder.build_summary_prompt(target_date)
        return self.ollama_client.generate(prompt)

    def summarize_today(self) -> str:
        return self.summarize(date.today())