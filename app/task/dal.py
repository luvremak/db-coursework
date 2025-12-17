from datetime import datetime, timedelta
from sqlalchemy import and_, select, func

from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO, PageData, PaginationParameters
from app.task.models import Task
from app.task.tables import task_table
from app.task.exceptions import TaskAlreadyExistsError, TaskNotFoundError
from app.core.database import database


class TaskCrud(CrudBase[int, DTO]):
    table = task_table

    async def get_next_code_for_project(self, project_id: int) -> int:
        query = select(func.max(self.table.c.code)).where(self.table.c.project_id == project_id)
        max_code = await database.fetch_val(query)
        return (max_code or 0) + 1

    async def get_by_code(self, code: int) -> DTO | None:
        query = select(self.table).where(self.table.c.code == code)
        return await database.fetch_one(query)

    async def get_by_assignee_user_id(
        self, assignee_user_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[DTO]:
        filters = {"assignee_user_id": assignee_user_id}
        return await self.get_page(filters=filters, pagination=pagination)

    async def get_by_project_id(
        self, project_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[DTO]:
        filters = {"project_id": project_id}
        return await self.get_page(filters=filters, pagination=pagination)

    async def get_soon_deadlines(self, days: int = 7) -> list[DTO]:
        now = datetime.now()
        deadline_limit = now + timedelta(days=days)
        query = select(self.table).where(
            and_(
                self.table.c.deadline >= now,
                self.table.c.deadline <= deadline_limit
            )
        ).order_by(self.table.c.deadline.asc())
        return await database.fetch_all(query)

    async def update_name(self, task_id: int, name: str) -> DTO:
        query = (
            self.table.update()
            .where(self.table.c.id == task_id)
            .values(name=name)
            .returning(self.table)
        )
        return await database.fetch_one(query)

    async def update_description(self, task_id: int, description: str) -> DTO:
        query = (
            self.table.update()
            .where(self.table.c.id == task_id)
            .values(description=description)
            .returning(self.table)
        )
        return await database.fetch_one(query)

    async def update_deadline(self, task_id: int, deadline: datetime) -> DTO:
        query = (
            self.table.update()
            .where(self.table.c.id == task_id)
            .values(deadline=deadline)
            .returning(self.table)
        )
        return await database.fetch_one(query)

    async def update_assignee(self, task_id: int, assignee_user_id: int) -> DTO:
        query = (
            self.table.update()
            .where(self.table.c.id == task_id)
            .values(assignee_user_id=assignee_user_id)
            .returning(self.table)
        )
        return await database.fetch_one(query)


class TaskRepo(RepoBase[int, Task]):
    crud: TaskCrud

    def __init__(self, crud: TaskCrud, serializer: Serializer[Task, DTO]):
        super().__init__(crud, serializer, Task)
        self.not_found_exception_cls = TaskNotFoundError
        self.unique_violation_exception_cls = TaskAlreadyExistsError

    async def get_next_code_for_project(self, project_id: int) -> int:
        return await self.crud.get_next_code_for_project(project_id)

    async def get_by_code(self, code: int) -> Task | None:
        dto = await self.crud.get_by_code(code)
        if dto is None:
            return None
        return self.serializer.deserialize(dto)

    async def get_by_assignee_user_id(
        self, assignee_user_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Task]:
        page_data = await self.crud.get_by_assignee_user_id(assignee_user_id, pagination)
        return PageData(
            data=list(self.serializer.flat.deserialize(page_data.data)),
            total=page_data.total,
        )

    async def get_by_project_id(
        self, project_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Task]:
        page_data = await self.crud.get_by_project_id(project_id, pagination)
        return PageData(
            data=list(self.serializer.flat.deserialize(page_data.data)),
            total=page_data.total,
        )

    async def get_soon_deadlines(self, days: int = 7) -> list[Task]:
        dtos = await self.crud.get_soon_deadlines(days)
        return list(self.serializer.flat.deserialize(dtos))

    async def update_name(self, task_id: int, name: str) -> Task:
        dto = await self.crud.update_name(task_id, name)
        return self.serializer.deserialize(dto)

    async def update_description(self, task_id: int, description: str) -> Task:
        dto = await self.crud.update_description(task_id, description)
        return self.serializer.deserialize(dto)

    async def update_deadline(self, task_id: int, deadline: datetime) -> Task:
        dto = await self.crud.update_deadline(task_id, deadline)
        return self.serializer.deserialize(dto)

    async def update_assignee(self, task_id: int, assignee_user_id: int) -> Task:
        dto = await self.crud.update_assignee(task_id, assignee_user_id)
        return self.serializer.deserialize(dto)


task_repo = TaskRepo(TaskCrud(), DataclassSerializer(Task))
