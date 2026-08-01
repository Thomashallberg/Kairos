from app.models import Activity, WorkBlock
from app.services.activity_grouper import ActivityGrouper


class ActivityFormatter:
    @staticmethod
    def format_work_block(work_block: WorkBlock) -> str:
        processes = ", ".join(work_block.processes) or "Okänt program"
        context = ", ".join(work_block.context) or "Ingen ytterligare kontext"

        return (
            f"{work_block.start_time}–{work_block.end_time} | "
            f"{work_block.category} | "
            f"{processes} | "
            f"{context}"
        )

    @classmethod
    def format_activities(cls, activities: list[Activity]) -> str:
        if not activities:
            return "Inga aktiviteter hittades."

        work_blocks = ActivityGrouper.build_work_blocks(activities)

        return "\n".join(
            cls.format_work_block(work_block)
            for work_block in work_blocks
        )