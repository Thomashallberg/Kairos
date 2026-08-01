import requests

from app.config import OLLAMA_HOST, OLLAMA_MODEL


class OllamaClient:
    def __init__(
        self,
        host: str = OLLAMA_HOST,
        model: str = OLLAMA_MODEL,
    ) -> None:
        self.host = host
        self.model = model

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300,
        )

        response.raise_for_status()
        return response.json()["response"]