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

    def is_available(self) -> bool:
        """Check whether the Ollama server is reachable."""
        try:
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=2,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def is_model_available(self) -> bool:
        """Check whether the configured model exists locally."""
        try:
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=5,
            )
            response.raise_for_status()

            models = response.json().get("models", [])

            return any(
                model.get("name") == self.model
                or model.get("model") == self.model
                for model in models
            )

        except requests.RequestException:
            return False

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
                f"Ollama returned an empty response. "
                f"Full API response: {data}"
            )

        return generated_text