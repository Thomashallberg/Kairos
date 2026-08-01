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

    def summarize_today(self) -> str:
        prompt = self.prompt_builder.build_daily_summary_prompt()

        return self.ollama_client.generate(prompt)