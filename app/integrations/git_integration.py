import subprocess
from pathlib import Path


class GitIntegration:
    def __init__(self, repository_path: str | Path = ".") -> None:
        self.repository_path = Path(repository_path)

    def _run_git(self, *args: str) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.repository_path,
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return result.stdout.strip()

        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            OSError,
        ):
            return ""

    def get_current_branch(self) -> str:
        return self._run_git(
            "rev-parse",
            "--abbrev-ref",
            "HEAD",
        )

    def get_recent_commits(self, limit: int = 5) -> list[str]:
        output = self._run_git(
            "log",
            f"-{limit}",
            "--pretty=format:%s",
        )

        return output.splitlines() if output else []

    def get_changed_files(self) -> list[str]:
        output = self._run_git(
            "diff",
            "--name-only",
        )

        return output.splitlines() if output else []