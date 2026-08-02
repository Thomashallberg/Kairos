from datetime import timedelta

from app.models import ReportPeriod, WorkSession


class ReportPeriodBuilder:
    @staticmethod
    def build(
        work_sessions: list[WorkSession],
        maximum_support_minutes: int = 5,
    ) -> list[ReportPeriod]:
        periods: list[ReportPeriod] = []
        index = 0

        while index < len(work_sessions):
            if index + 2 < len(work_sessions):
                first = work_sessions[index]
                support = work_sessions[index + 1]
                last = work_sessions[index + 2]

                support_duration = (
                    support.end_time - support.start_time
                    if support.end_time is not None
                    else None
                )

                can_merge = (
                    first.end_time is not None
                    and support.end_time is not None
                    and last.end_time is not None
                    and first.primary_category == last.primary_category
                    and first.end_time == support.start_time
                    and support.end_time == last.start_time
                    and support_duration <= timedelta(minutes=maximum_support_minutes)
                )

                if can_merge:
                    periods.append(
                        ReportPeriod(
                            start_time=first.start_time,
                            end_time=last.end_time,
                            primary_category=first.primary_category,
                            work_sessions=[first, support, last],
                        )
                    )
                    index += 3
                    continue

            session = work_sessions[index]

            periods.append(
                ReportPeriod(
                    start_time=session.start_time,
                    end_time=session.end_time,
                    primary_category=session.primary_category,
                    work_sessions=[session],
                )
            )

            index += 1

        return periods
