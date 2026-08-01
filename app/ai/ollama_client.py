from typing import Any

import requests

from app.config import OLLAMA_HOST, OLLAMA_MODEL


class OllamaClient:
    def __init__(
        self,
        host: str = OLLAMA_HOST,
        model: str = OLLAMA_MODEL,
    ) -> None:
        self.host = host.rstrip("/")
        self.model = model

    def generate(
        self,
        prompt: str,
        response_format: dict[str, Any] | str | None = None,
    ) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "temperature": 0.0,
                "seed": 42,
            },
        }

        if response_format is not None:
            payload["format"] = response_format

        response = requests.post(
            f"{self.host}/api/generate",
            json=payload,
            timeout=(10, 600),
        )

        response.raise_for_status()

        data = response.json()

        generated_text = (
        data.get("response")
        or data.get("thinking")
        or ""
        ).strip()

        if not generated_text:
            raise RuntimeError(
                f"Ollama returned an empty response. Full API response: {data}"
            )

        return generated_text