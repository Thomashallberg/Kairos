from app.models import Activity
from app.services.activity_classifier import ActivityClassifier
from app.services.activity_grouper import ActivityGrouper


class ActivityFormatter:
    @staticmethod
    def format_activity_group(activities: list[Activity]) -> str:
        first_activity = activities[0]
        last_activity = activities[-1]

        start_time = first_activity.start_time.strftime("%H:%M")

        end_time = (
            last_activity.end_time.strftime("%H:%M")
            if last_activity.end_time is not None
            else "pågår"
        )

        category = ActivityClassifier.classify(first_activity)

        process_names = {
            activity.process_name
            for activity in activities
            if activity.process_name
        }

        process_text = ", ".join(sorted(process_names)) or "Okänt program"

        return (
            f"{start_time}–{end_time} | "
            f"{category} | "
            f"{process_text}"
        )

    @classmethod
    def format_activities(cls, activities: list[Activity]) -> str:
        if not activities:
            return "Inga aktiviteter hittades."

        groups = ActivityGrouper.group_consecutive(activities)

        return "\n".join(
            cls.format_activity_group(group)
            for group in groups
        )