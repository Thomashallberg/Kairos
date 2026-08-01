from app.models import Activity


class ActivityClassifier:
    @staticmethod
    def classify(activity: Activity) -> str:
        process_name = (activity.process_name or "").lower()
        window_title = (activity.window_title or "").lower()

        if "teams" in process_name or "teams" in window_title:
            return "Meeting"

        if "outlook" in process_name:
            return "Email"

        if process_name in {"code.exe", "pycharm64.exe"}:
            return "Development"

        if "jira" in window_title:
            return "Issue Tracking"

        if process_name in {"chrome.exe", "msedge.exe", "firefox.exe"}:
            return "Browser"

        if process_name == "explorer.exe":
            return "File Management"

        return "Other"