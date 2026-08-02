import time
from datetime import datetime

from app.collectors.active_window import get_active_window
from app.config import TRACKING_INTERVAL_SECONDS
from app.services.activity_service import ActivityService


def track_activity(
    activity_service: ActivityService,
    interval_seconds: int = TRACKING_INTERVAL_SECONDS,
) -> None:
    previous_window: dict[str, str | int | None] | None = None
    activity_start_time: datetime | None = None

    print("Kairos is tracking activity. Press Ctrl+C to stop.")

    try:
        while True:
            current_window = get_active_window()
            now = datetime.now()

            if current_window != previous_window:
                if previous_window is not None and activity_start_time is not None:
                    activity_service.record_activity(
                        process_name=previous_window["process_name"],
                        window_title=previous_window["title"],
                        start_time=activity_start_time,
                        end_time=now,
                    )

                    print(
                        f"Saved: {previous_window['process_name']} | "
                        f"{previous_window['title']}"
                    )

                previous_window = current_window
                activity_start_time = now

            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        if previous_window is not None and activity_start_time is not None:
            activity_service.record_activity(
                process_name=previous_window["process_name"],
                window_title=previous_window["title"],
                start_time=activity_start_time,
                end_time=datetime.now(),
            )

        print("\nKairos stopped tracking.")
