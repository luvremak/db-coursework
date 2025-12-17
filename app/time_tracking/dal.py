from sqlalchemy import and_, select, func, join

from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO
from app.employee.tables import employee_table
from app.project.tables import project_table
from app.task.tables import task_table
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
        self.log_query(query)
        result = await database.fetch_val(query)
        return result or 0

    async def get_all_entries_for_company(self, company_id: int) -> list[DTO]:
        query = (
            select(self.table)
            .select_from(
                self.table
                .join(task_table, self.table.c.task_id == task_table.c.id)
                .join(project_table, task_table.c.project_id == project_table.c.id)
            )
            .where(project_table.c.company_id == company_id)
            .order_by(self.table.c.created_at.desc())
        )
        self.log_query(query)
        return await database.fetch_all(query)

    async def get_project_stats_for_company(self, company_id: int) -> list[dict]:
        time_sum = func.sum(self.table.c.duration_minutes).label("total_minutes")
        cost_sum = func.sum(
            (self.table.c.duration_minutes / 60.0) * employee_table.c.salary_per_hour
        ).label("total_cost")

        query = (
            select(
                project_table.c.code.label("project_code"),
                time_sum,
                cost_sum
            )
            .select_from(
                self.table
                .join(employee_table, self.table.c.employee_id == employee_table.c.id)
                .join(task_table, self.table.c.task_id == task_table.c.id)
                .join(project_table, task_table.c.project_id == project_table.c.id)
            )
            .where(project_table.c.company_id == company_id)
            .group_by(project_table.c.code)
            .order_by(cost_sum.desc())
        )
        self.log_query(query)
        return await database.fetch_all(query)

class TimeTrackingEntryRepo(RepoBase[int, TimeTrackingEntry]):
    crud: TimeTrackingEntryCrud

    def __init__(self, crud: TimeTrackingEntryCrud, serializer: Serializer[TimeTrackingEntry, DTO]):
        super().__init__(crud, serializer, TimeTrackingEntry)

    async def get_total_minutes_by_task_and_employee(self, task_id: int, employee_id: int) -> int:
        return await self.crud.get_total_minutes_by_task_and_employee(task_id, employee_id)

    async def get_all_entries_for_company(self, company_id: int) -> list[TimeTrackingEntry]:
        dtos = await self.crud.get_all_entries_for_company(company_id)
        return list(self.serializer.flat.deserialize(dtos))

    async def get_project_stats_for_company(self, company_id: int) -> list[dict]:
        return await self.crud.get_project_stats_for_company(company_id)

time_tracking_entry_repo = TimeTrackingEntryRepo(TimeTrackingEntryCrud(), DataclassSerializer(TimeTrackingEntry))
