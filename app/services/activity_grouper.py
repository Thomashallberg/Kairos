from app.models import Activity, WorkBlock
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
    @staticmethod
    def build_work_blocks(
        activities: list[Activity],
    ) -> list[WorkBlock]:
        groups = ActivityGrouper.group_consecutive(activities)

        work_blocks: list[WorkBlock] = []

        for group in groups:
            first = group[0]
            last = group[-1]

            work_blocks.append(
                WorkBlock(
                    start_time=first.start_time,
                    end_time=last.end_time,
                    category=ActivityClassifier.classify(first),
                    processes=sorted(
                        {
                            activity.process_name
                            for activity in group
                            if activity.process_name
                        }
                    ),
                    context=sorted(
                        {
                            activity.window_title
                            for activity in group
                            if activity.window_title
                        }
                    ),
                )
            )

        return work_blocks