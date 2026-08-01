from app.models import Activity
from app.services.activity_classifier import ActivityClassifier


class ActivityFormatter:
    @staticmethod
    def format_activity(activity: Activity) -> str:
        start_time = activity.start_time.strftime("%H:%M")

        end_time = (
            activity.end_time.strftime("%H:%M")
            if activity.end_time is not None
            else "pågår"
        )

        process_name = activity.process_name or "Okänt program"
        window_title = activity.window_title or "Ingen fönstertitel"
        category = ActivityClassifier.classify(activity)

        return (
            f"{start_time}–{end_time} | "
            f"{category} | "
            f"{process_name} | "
            f"{window_title}"
        )

    @classmethod
    def format_activities(cls, activities: list[Activity]) -> str:
        if not activities:
            return "Inga aktiviteter hittades."

        return "\n".join(
            cls.format_activity(activity)
            for activity in activities
        )