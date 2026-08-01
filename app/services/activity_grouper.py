from app.models import Activity
from app.services.activity_classifier import ActivityClassifier


class ActivityGrouper:
    @staticmethod
    def group_consecutive(activities: list[Activity]) -> list[list[Activity]]:
        if not activities:
            return []

        groups: list[list[Activity]] = []
        current_group = [activities[0]]
        current_category = ActivityClassifier.classify(activities[0])

        for activity in activities[1:]:
            category = ActivityClassifier.classify(activity)

            if category == current_category:
                current_group.append(activity)
            else:
                groups.append(current_group)
                current_group = [activity]
                current_category = category

        groups.append(current_group)

        return groups