from datetime import timedelta

from app.models import WorkBlock


class WorkBlockNormalizer:
    @staticmethod
    def merge_short_interruptions(
        blocks: list[WorkBlock],
        maximum_interruption_seconds: int = 10,
    ) -> list[WorkBlock]:
        if len(blocks) < 3:
            return blocks.copy()

        normalized: list[WorkBlock] = []
        index = 0

        while index < len(blocks):
            if index + 2 >= len(blocks):
                normalized.extend(blocks[index:])
                break

            previous_block = blocks[index]
            interruption = blocks[index + 1]
            next_block = blocks[index + 2]

            can_merge = (
                previous_block.end_time is not None
                and interruption.end_time is not None
                and previous_block.category == next_block.category
                and interruption.start_time == previous_block.end_time
                and next_block.start_time == interruption.end_time
                and interruption.end_time - interruption.start_time
                <= timedelta(seconds=maximum_interruption_seconds)
            )

            if can_merge:
                normalized.append(
                    WorkBlock(
                        start_time=previous_block.start_time,
                        end_time=next_block.end_time,
                        category=previous_block.category,
                        processes=sorted(
                            set(previous_block.processes)
                            | set(next_block.processes)
                        ),
                        context=sorted(
                            set(previous_block.context)
                            | set(next_block.context)
                        ),
                    )
                )
                index += 3
            else:
                normalized.append(previous_block)
                index += 1

        return normalized