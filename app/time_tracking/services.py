from datetime import datetime

from app.time_tracking.dal import TimeTrackingEntryCrud, TimeTrackingEntryRepo
from app.time_tracking.models import TimeTrackingEntry
from app.core.serializer import DataclassSerializer


class TimeTrackingEntryService:
    def __init__(self, time_tracking_entry_repo: TimeTrackingEntryRepo):
        self.time_tracking_entry_repo = time_tracking_entry_repo

    async def create_time_entry(
        self,
        task_id: int,
        employee_id: int,
        duration_minutes: int,
    ) -> TimeTrackingEntry:
        entry = TimeTrackingEntry(
            task_id=task_id,
            employee_id=employee_id,
            duration_minutes=duration_minutes,
            created_at=datetime.now(),
        )
        return await self.time_tracking_entry_repo.create(entry)


time_tracking_entry_service = TimeTrackingEntryService(
    TimeTrackingEntryRepo(TimeTrackingEntryCrud(), DataclassSerializer(TimeTrackingEntry))
)
