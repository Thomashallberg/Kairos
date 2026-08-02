from app.models import WorkBlock, WorkSession


class WorkSessionBuilder:
    @staticmethod
    def build(
        work_blocks: list[WorkBlock],
    ) -> list[WorkSession]:
        return [
            WorkSession(
                start_time=block.start_time,
                end_time=block.end_time,
                primary_category=block.category,
                work_blocks=[block],
            )
            for block in work_blocks
        ]