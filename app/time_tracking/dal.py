from sqlalchemy import and_, select, func

from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO
from app.time_tracking.models import TimeTrackingEntry
from app.time_tracking.tables import time_tracking_entry_table
from app.core.database import database


class TimeTrackingEntryCrud(CrudBase[int, DTO]):
    table = time_tracking_entry_table

    async def get_total_minutes_by_task_and_employee(self, task_id: int, employee_id: int) -> int:
        query = select(func.sum(self.table.c.duration_minutes)).where(
            and_(
                self.table.c.task_id == task_id,
                self.table.c.employee_id == employee_id
            )
        )
        result = await database.fetch_val(query)
        return result or 0


class TimeTrackingEntryRepo(RepoBase[int, TimeTrackingEntry]):
    crud: TimeTrackingEntryCrud

    def __init__(self, crud: TimeTrackingEntryCrud, serializer: Serializer[TimeTrackingEntry, DTO]):
        super().__init__(crud, serializer, TimeTrackingEntry)

    async def get_total_minutes_by_task_and_employee(self, task_id: int, employee_id: int) -> int:
        return await self.crud.get_total_minutes_by_task_and_employee(task_id, employee_id)


time_tracking_entry_repo = TimeTrackingEntryRepo(TimeTrackingEntryCrud(), DataclassSerializer(TimeTrackingEntry))
