import sys
import ctypes
import threading
import tkinter as tk
from datetime import date, timedelta
from pathlib import Path
from threading import Event
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from tkcalendar import Calendar

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


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

BG = "#0F1115"
CARD_BG = "#181B21"
REPORT_BG = "#111318"

TEXT = "#F4F6F8"
MUTED_TEXT = "#9299A6"

ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"

# Calendar colors
ACTIVITY_DAY = "#1E3A5F"
SELECTED_DAY = "#38A8FF"

SUCCESS = "#22C55E"
STOPPED = "#EF4444"

BORDER = "#292D36"


def resource_path(relative_path: str) -> Path:
    if getattr(sys, "frozen", False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve().parent.parent

    return base_path / relative_path


class KairosGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root

        # Keep the window hidden while the UI is being built.
        # This prevents the small startup window from flashing
        # before Kairos reaches its final size.
        self.root.withdraw()

        self.root.title("Kairos")
        self.root.iconbitmap(resource_path("assets/kairos.ico"))

        self.root.geometry("900x700")
        self.root.minsize(700, 560)
        self.root.configure(bg=BG)

        self.stop_event: Event | None = None
        self.tracking_thread: threading.Thread | None = None

        self.selected_date = date.today()

        create_database()

        self._build_ui()
        self.refresh_report()
        # Finish calculating the layout before showing Kairos.
        self.root.update_idletasks()
        self.root.deiconify()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main = tk.Frame(
            self.root,
            bg=BG,
        )
        main.pack(
            fill=tk.BOTH,
            expand=True,
            padx=36,
            pady=24,
        )

        # Header ---------------------------------------------------------

        header = tk.Frame(main, bg=BG)
        header.pack(fill=tk.X)

        header_left = tk.Frame(header, bg=BG)
        header_left.pack(side=tk.LEFT)

        tk.Label(
            header_left,
            text="KAIROS",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 26, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header_left,
            text="Private, local AI time reporting",
            bg=BG,
            fg=MUTED_TEXT,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        # Tracking card --------------------------------------------------

        tracking_card = tk.Frame(
            main,
            bg=CARD_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        tracking_card.pack(
            fill=tk.X,
            pady=(22, 18),
        )

        tracking_inner = tk.Frame(
            tracking_card,
            bg=CARD_BG,
        )
        tracking_inner.pack(
            fill=tk.X,
            padx=24,
            pady=16,
        )

        tk.Label(
            tracking_inner,
            text="TODAY",
            bg=CARD_BG,
            fg=MUTED_TEXT,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        self.status_label = tk.Label(
            tracking_inner,
            text="Tracking stopped",
            bg=CARD_BG,
            fg=STOPPED,
            font=("Segoe UI", 14, "bold"),
        )
        self.status_label.pack(
            anchor="w",
            pady=(7, 3),
        )

        self.status_description = tk.Label(
            tracking_inner,
            text="Kairos is ready to record your activity.",
            bg=CARD_BG,
            fg=MUTED_TEXT,
            font=("Segoe UI", 10),
        )
        self.status_description.pack(
            anchor="w",
            pady=(0, 12),
        )

        button_frame = tk.Frame(
            tracking_inner,
            bg=CARD_BG,
        )
        button_frame.pack(anchor="w")

        self.start_button = tk.Button(
            button_frame,
            text="▶  Start tracking",
            command=self.start_tracking,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            disabledforeground="#777C85",
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=22,
            pady=8,
        )
        self.start_button.pack(
            side=tk.LEFT,
            padx=(0, 10),
        )

        self.stop_button = tk.Button(
            button_frame,
            text="■  Stop tracking",
            command=self.stop_tracking,
            state=tk.DISABLED,
            bg="#272B33",
            fg=TEXT,
            activebackground="#343943",
            activeforeground=TEXT,
            disabledforeground="#626873",
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10),
            padx=22,
            pady=8,
        )
        self.stop_button.pack(side=tk.LEFT)

        # Activity header ------------------------------------------------

        activity_header = tk.Frame(main, bg=BG)
        activity_header.pack(
            fill=tk.X,
            pady=(0, 8),
        )

        tk.Label(
            activity_header,
            text="Activity",
            bg=BG,
            fg=TEXT,
            font=("Segoe UI", 14, "bold"),
        ).pack(side=tk.LEFT)

        # Date navigation ------------------------------------------------

        date_controls = tk.Frame(
            activity_header,
            bg=BG,
        )
        date_controls.pack(side=tk.RIGHT)

        self.previous_day_button = tk.Button(
            date_controls,
            text="‹",
            command=self.previous_day,
            bg="#20242B",
            fg=TEXT,
            activebackground="#30353E",
            activeforeground=TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 15),
            width=3,
        )
        self.previous_day_button.pack(
            side=tk.LEFT,
            padx=(0, 6),
        )

        self.date_button = tk.Button(
            date_controls,
            text="",
            command=self.open_calendar,
            bg="#20242B",
            fg=TEXT,
            activebackground="#30353E",
            activeforeground=TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=6,
        )
        self.date_button.pack(
            side=tk.LEFT,
            padx=(0, 6),
        )

        self.next_day_button = tk.Button(
            date_controls,
            text="›",
            command=self.next_day,
            bg="#20242B",
            fg=TEXT,
            activebackground="#30353E",
            activeforeground=TEXT,
            disabledforeground="#555B66",
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 15),
            width=3,
        )
        self.next_day_button.pack(
            side=tk.LEFT,
            padx=(0, 6),
        )

        self.today_button = tk.Button(
            date_controls,
            text="Today",
            command=self.go_to_today,
            bg="#20242B",
            fg=TEXT,
            activebackground="#30353E",
            activeforeground=TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=12,
            pady=6,
        )
        self.today_button.pack(side=tk.LEFT)

        # Bottom actions -------------------------------------------------

        action_frame = tk.Frame(
            main,
            bg=BG,
        )
        action_frame.pack(
            side=tk.BOTTOM,
            fill=tk.X,
            pady=(14, 0),
        )

        self.refresh_button = tk.Button(
            action_frame,
            text="↻  Refresh",
            command=self.refresh_report,
            bg="#20242B",
            fg=TEXT,
            activebackground="#30353E",
            activeforeground=TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10),
            padx=18,
            pady=8,
        )
        self.refresh_button.pack(side=tk.LEFT)

        self.summary_button = tk.Button(
            action_frame,
            text="✦  Generate AI report",
            command=self.generate_summary,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            disabledforeground="#A8A8A8",
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 10, "bold"),
            padx=20,
            pady=8,
        )
        self.summary_button.pack(side=tk.RIGHT)

        tk.Label(
            action_frame,
            text="AI runs locally on your device",
            bg=BG,
            fg=MUTED_TEXT,
            font=("Segoe UI", 9),
        ).pack(
            side=tk.RIGHT,
            padx=14,
        )

        # Report ---------------------------------------------------------

        report_frame = tk.Frame(
            main,
            bg=REPORT_BG,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        report_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.report_box = ScrolledText(
            report_frame,
            bg=REPORT_BG,
            fg="#D7DBE0",
            insertbackground=TEXT,
            selectbackground=ACCENT,
            selectforeground="white",
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            borderwidth=0,
            padx=16,
            pady=16,
        )
        self.report_box.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self._update_date_controls()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.on_close,
        )

    # ------------------------------------------------------------------
    # Date navigation
    # ------------------------------------------------------------------

    def _format_selected_date(self) -> str:
        return self.selected_date.strftime("%d %B %Y")

    def _update_date_controls(self) -> None:
        self.date_button.config(
            text=f"📅  {self._format_selected_date()}"
        )

        if self.selected_date >= date.today():
            self.next_day_button.config(state=tk.DISABLED)
        else:
            self.next_day_button.config(state=tk.NORMAL)

    def previous_day(self) -> None:
        self.selected_date -= timedelta(days=1)
        self._date_changed()

    def next_day(self) -> None:
        if self.selected_date >= date.today():
            return

        self.selected_date += timedelta(days=1)

        if self.selected_date > date.today():
            self.selected_date = date.today()

        self._date_changed()

    def go_to_today(self) -> None:
        self.selected_date = date.today()
        self._date_changed()

    def _date_changed(self) -> None:
        self._update_date_controls()
        self.refresh_report()

    # ------------------------------------------------------------------
    # Calendar
    # ------------------------------------------------------------------

    def _get_activity_dates(self) -> list[date]:
        session = None

        try:
            session, activity_service, _ = self._create_services()
            return activity_service.get_activity_dates()

        finally:
            if session is not None:
                session.close()

    def open_calendar(self) -> None:
        popup = tk.Toplevel(self.root)

        # Hide until fully positioned.
        popup.withdraw()

        popup.title("Select date")
        popup.iconbitmap(resource_path("assets/kairos.ico"))
        popup.configure(bg=CARD_BG)
        popup.resizable(False, False)
        popup.transient(self.root)

        calendar = Calendar(
            popup,
            selectmode="day",
            year=self.selected_date.year,
            month=self.selected_date.month,
            day=self.selected_date.day,
            maxdate=date.today(),
            date_pattern="yyyy-mm-dd",
            background=CARD_BG,
            foreground=TEXT,
            headersbackground="#20242B",
            headersforeground=TEXT,
            selectbackground=SELECTED_DAY,
            selectforeground="white",
            normalbackground=CARD_BG,
            normalforeground=TEXT,
            weekendbackground=CARD_BG,
            weekendforeground=TEXT,
            othermonthbackground="#12151A",
            othermonthforeground="#555B66",
            othermonthwebackground="#12151A",
            othermonthweforeground="#555B66",
            bordercolor=BORDER,
        )
        calendar.pack(
            padx=14,
            pady=(14, 8),
        )
        
        # Explicitly select the currently viewed date so the
        # selection styling is visible as soon as the calendar opens.
        calendar.selection_set(self.selected_date)

        # Highlight dates that contain recorded Kairos activity.
        try:
            activity_dates = self._get_activity_dates()

            calendar.tag_config(
                "activity",
                background=ACTIVITY_DAY,
                foreground=TEXT,
            )

            for activity_date in activity_dates:
                calendar.calevent_create(
                    activity_date,
                    "Activity recorded",
                    "activity",
                )

        except Exception as exc:
            print(
                f"Could not load calendar activity markers: {exc}"
            )

        button_frame = tk.Frame(
            popup,
            bg=CARD_BG,
        )
        button_frame.pack(
            fill=tk.X,
            padx=14,
            pady=(0, 14),
        )

        tk.Button(
            button_frame,
            text="Cancel",
            command=popup.destroy,
            bg="#272B33",
            fg=TEXT,
            activebackground="#343943",
            activeforeground=TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 9),
            padx=14,
            pady=6,
        ).pack(side=tk.LEFT)

        def select_date() -> None:
            selected = calendar.selection_get()

            if selected > date.today():
                return

            self.selected_date = selected

            popup.destroy()
            self._date_changed()

        tk.Button(
            button_frame,
            text="Select date",
            command=select_date,
            bg=ACCENT,
            fg="white",
            activebackground=ACCENT_HOVER,
            activeforeground="white",
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=6,
        ).pack(side=tk.RIGHT)

        # Calculate popup size and center it while hidden.
        popup.update_idletasks()

        x = (
            self.root.winfo_rootx()
            + (self.root.winfo_width() // 2)
            - (popup.winfo_width() // 2)
        )

        y = (
            self.root.winfo_rooty()
            + (self.root.winfo_height() // 2)
            - (popup.winfo_height() // 2)
        )

        popup.geometry(f"+{x}+{y}")

        # Show only after positioning.
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        
        
        
        calendar.selection_set(self.selected_date)
        calendar.focus_set()

    # ------------------------------------------------------------------
    # Services
    # ------------------------------------------------------------------

    def _create_services(self):
        session = SessionLocal()

        repository = ActivityRepository(session)
        activity_service = ActivityService(repository)
        daily_report_service = DailyReportService(activity_service)

        return session, activity_service, daily_report_service

    # ------------------------------------------------------------------
    # Tracking
    # ------------------------------------------------------------------

    def start_tracking(self) -> None:
        if self.tracking_thread and self.tracking_thread.is_alive():
            return

        self.stop_event = Event()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.status_label.config(
            text="Tracking active",
            fg=SUCCESS,
        )

        self.status_description.config(
            text="Kairos is recording your current activity."
        )

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

        self.status_label.config(
            text="Tracking stopped",
            fg=STOPPED,
        )

        self.status_description.config(
            text="Kairos is ready to record your activity."
        )

        self.refresh_report()

    def stop_tracking(self) -> None:
        if self.stop_event is not None:
            self.stop_event.set()

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def refresh_report(self) -> None:
        session = None

        try:
            session, _, daily_report_service = self._create_services()

            report = daily_report_service.generate_report(
                self.selected_date
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

    # ------------------------------------------------------------------
    # AI
    # ------------------------------------------------------------------

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
                self.selected_date
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
                self._summary_finished,
            )

    def _summary_finished(self) -> None:
        self.summary_button.config(
            state=tk.NORMAL,
            text="✦  Generate AI report",
        )

    def _show_summary(self, summary: str) -> None:
        self.report_box.delete("1.0", tk.END)
        self.report_box.insert(tk.END, summary)

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------

    def on_close(self) -> None:
        if self.stop_event is not None:
            self.stop_event.set()

        self.root.destroy()


def main() -> None:
    app_id = "ThomasHallberg.Kairos.0.1.0"

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            app_id
        )
    except (AttributeError, OSError):
        pass

    root = tk.Tk()
    KairosGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()