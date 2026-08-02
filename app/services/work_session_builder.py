from datetime import timedelta

from app.models import WorkBlock, WorkSession


class WorkSessionBuilder:
    @staticmethod
    def build(
        work_blocks: list[WorkBlock],
        maximum_support_block_minutes: int = 5,
    ) -> list[WorkSession]:
        sessions: list[WorkSession] = []
        index = 0

        while index < len(work_blocks):
            if index + 2 < len(work_blocks):
                first = work_blocks[index]
                support = work_blocks[index + 1]
                last = work_blocks[index + 2]

                support_duration = (
                    support.end_time - support.start_time
                    if support.end_time is not None
                    else None
                )

                can_merge = (
                    first.end_time is not None
                    and support.end_time is not None
                    and last.end_time is not None
                    and first.category == last.category
                    and first.end_time == support.start_time
                    and support.end_time == last.start_time
                    and support_duration
                    <= timedelta(minutes=maximum_support_block_minutes)
                )

                if can_merge:
                    sessions.append(
                        WorkSession(
                            start_time=first.start_time,
                            end_time=last.end_time,
                            primary_category=first.category,
                            work_blocks=[first, support, last],
                        )
                    )
                    index += 3
                    continue

            block = work_blocks[index]

            sessions.append(
                WorkSession(
                    start_time=block.start_time,
                    end_time=block.end_time,
                    primary_category=block.category,
                    work_blocks=[block],
                )
            )

            index += 1

        return sessions