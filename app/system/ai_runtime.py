import subprocess
import time

from app.ai.ollama_client import OllamaClient


class AIRuntime:
    def __init__(self, client: OllamaClient | None = None) -> None:
        self.client = client or OllamaClient()

    def ensure_ready(self) -> None:
        if not self.client.is_available():
            print("Starting local AI...")
            self._start_ollama()

        if not self._wait_for_ollama():
            raise RuntimeError(
                "Kairos could not start the local AI service."
            )

        if not self.client.is_model_available():
            print(f"Preparing AI model '{self.client.model}'...")
            self._pull_model()

        if not self.client.is_model_available():
            raise RuntimeError(
                f"AI model '{self.client.model}' could not be prepared."
            )

    def _start_ollama(self) -> None:
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Local AI runtime is not installed."
            ) from exc

    def _wait_for_ollama(
        self,
        timeout_seconds: int = 15,
    ) -> bool:
        deadline = time.monotonic() + timeout_seconds

        while time.monotonic() < deadline:
            if self.client.is_available():
                return True

            time.sleep(0.5)

        return False

    def _pull_model(self) -> None:
        try:
            subprocess.run(
                ["ollama", "pull", self.client.model],
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "Local AI runtime is not installed."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(
                f"Could not prepare AI model '{self.client.model}'."
            ) from exc