import time
from datetime import datetime

from app.collectors.active_window import get_active_window


def track_activity(interval_seconds: int = 2) -> None:
    previous_window: dict[str, str | int | None] | None = None

    print("Kairos is tracking activity. Press Ctrl+C to stop.")

    try:
        while True:
            current_window = get_active_window()

            if current_window != previous_window:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                print(
                    f"[{timestamp}] "
                    f"{current_window['process_name']} | "
                    f"{current_window['title']}"
                )

                previous_window = current_window

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\nKairos stopped tracking.")