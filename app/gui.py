import sys
import ctypes
import threading
import tkinter as tk
from datetime import date
from pathlib import Path
from threading import Event
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from app.ai.ollama_client import OllamaClient
from app.collectors.activity_tracker import track_activity
from app.database.connection import SessionLocal, create_database
from app.integrations.git_integration import GitIntegration
from app.repositories.activity_repository import ActivityRepository
from app.services.activity_service import ActivityService
from app.services.ai_summary_service import AISummaryService
from app.services.daily_report_service import DailyReportService
from app.services.prompt_builder import PromptBuilder
from app.system.ai_runtime import AIRuntime


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path


class KairosGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Kairos")
        self.root.iconbitmap(
            resource_path("assets/kairos.ico")
        )
        self.root.geometry("760x600")
        self.root.minsize(650, 500)

        self.stop_event: Event | None = None
        self.tracking_thread: threading.Thread | None = None

        create_database()

        self._build_ui()
        self.refresh_report()

    def _build_ui(self) -> None:
        title = tk.Label(
            self.root,
            text="KAIROS",
            font=("Segoe UI", 24, "bold"),
        )
        title.pack(pady=(20, 0))

        subtitle = tk.Label(
            self.root,
            text="Local AI Time Reporting",
            font=("Segoe UI", 11),
        )
        subtitle.pack(pady=(0, 20))

        self.status_label = tk.Label(
            self.root,
            text="● Tracking stopped",
            font=("Segoe UI", 11),
        )
        self.status_label.pack(pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="Start tracking",
            width=18,
            command=self.start_tracking,
        )
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(
            button_frame,
            text="Stop tracking",
            width=18,
            command=self.stop_tracking,
            state=tk.DISABLED,
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        report_title = tk.Label(
            self.root,
            text="Today's report",
            font=("Segoe UI", 14, "bold"),
        )
        report_title.pack(pady=(20, 5))

        self.report_box = ScrolledText(
            self.root,
            height=14,
            font=("Consolas", 10),
            wrap=tk.WORD,
        )
        self.report_box.pack(
            fill=tk.BOTH,
            expand=True,
            padx=25,
            pady=5,
        )

        action_frame = tk.Frame(self.root)
        action_frame.pack(pady=15)

        tk.Button(
            action_frame,
            text="Refresh report",
            width=18,
            command=self.refresh_report,
        ).pack(side=tk.LEFT, padx=5)

        self.summary_button = tk.Button(
            action_frame,
            text="Generate AI summary",
            width=20,
            command=self.generate_summary,
        )
        self.summary_button.pack(side=tk.LEFT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _create_services(self):
        session = SessionLocal()

        repository = ActivityRepository(session)
        activity_service = ActivityService(repository)
        daily_report_service = DailyReportService(activity_service)

        return session, activity_service, daily_report_service

    def start_tracking(self) -> None:
        if self.tracking_thread and self.tracking_thread.is_alive():
            return

        self.stop_event = Event()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="● Tracking active")

        self.tracking_thread = threading.Thread(
            target=self._tracking_worker,
            daemon=True,
        )
        self.tracking_thread.start()

    def _tracking_worker(self) -> None:
        session = None

        try:
            session, activity_service, _ = self._create_services()

            track_activity(
                activity_service,
                stop_event=self.stop_event,
            )

        except Exception as exc:
            error_message = str(exc)

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Kairos",
                    f"Tracking failed:\n{error_message}",
                ),
            )

        finally:
            if session is not None:
                session.close()

            self.root.after(
                0,
                self._tracking_finished,
            )

    def _tracking_finished(self) -> None:
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="● Tracking stopped")

        self.refresh_report()

    def stop_tracking(self) -> None:
        if self.stop_event is not None:
            self.stop_event.set()

    def refresh_report(self) -> None:
        session = None

        try:
            session, _, daily_report_service = self._create_services()

            report = daily_report_service.generate_report(
                date.today()
            )

            self.report_box.delete("1.0", tk.END)
            self.report_box.insert(tk.END, report)

        except Exception as exc:
            messagebox.showerror(
                "Kairos",
                f"Could not load report:\n{exc}",
            )

        finally:
            if session is not None:
                session.close()

    def generate_summary(self) -> None:
        self.summary_button.config(
            state=tk.DISABLED,
            text="Generating...",
        )

        threading.Thread(
            target=self._summary_worker,
            daemon=True,
        ).start()

    def _summary_worker(self) -> None:
        session = None

        try:
            ai_runtime = AIRuntime()
            ai_runtime.ensure_ready()

            session, _, daily_report_service = self._create_services()

            git_integration = GitIntegration()

            prompt_builder = PromptBuilder(
                daily_report_service,
                git_integration,
            )

            ollama_client = OllamaClient()

            ai_summary_service = AISummaryService(
                prompt_builder,
                ollama_client,
            )

            time_report = ai_summary_service.summarize(
                date.today()
            )

            summary = "\n".join(
                f"{entry.start_time}–{entry.end_time}: "
                f"{entry.description}"
                for entry in time_report.entries
            )

            self.root.after(
                0,
                lambda: self._show_summary(summary),
            )

        except Exception as exc:
            error_message = str(exc)

            self.root.after(
                0,
                lambda: messagebox.showerror(
                    "Kairos",
                    f"AI summary failed:\n{error_message}",
                ),
            )

        finally:
            if session is not None:
                session.close()

            self.root.after(
                0,
                lambda: self.summary_button.config(
                    state=tk.NORMAL,
                    text="Generate AI summary",
                ),
            )

    def _show_summary(self, summary: str) -> None:
        self.report_box.delete("1.0", tk.END)
        self.report_box.insert(tk.END, summary)

    def on_close(self) -> None:
        if self.stop_event is not None:
            self.stop_event.set()

        self.root.destroy()


def main() -> None:
    app_id = "ThomasHallberg.Kairos.0.1.0"

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except (AttributeError, OSError):
        pass

    root = tk.Tk()
    KairosGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()