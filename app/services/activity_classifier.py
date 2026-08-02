from app.activity_rules import (
    BROWSER_PROCESSES,
    PROCESS_CATEGORY_RULES,
    PROCESS_CONTAINS_RULES,
    WINDOW_TITLE_RULES,
)
from app.models import Activity


class ActivityClassifier:
    @staticmethod
    def classify(activity: Activity) -> str:
        process_name = (activity.process_name or "").lower()
        window_title = (activity.window_title or "").lower()

        for keyword, category in WINDOW_TITLE_RULES.items():
            if keyword in window_title:
                return category

        if process_name in PROCESS_CATEGORY_RULES:
            return PROCESS_CATEGORY_RULES[process_name]

        for keyword, category in PROCESS_CONTAINS_RULES.items():
            if keyword in process_name or keyword in window_title:
                return category

        if process_name in BROWSER_PROCESSES:
            return "Browser"

        return "Other"
