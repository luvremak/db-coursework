from datetime import datetime

from app.task.dal import TaskCrud, TaskRepo
from app.task.models import Task
from app.task.exceptions import (
    TaskAccessDeniedError,
    TaskNotFoundError,
)
from app.project.services import project_service
from app.employee.services import employee_service
from app.company.services import company_service
from app.core.serializer import DataclassSerializer
from app.core.types import PageData, PaginationParameters


class TaskService:
    def __init__(self, task_repo: TaskRepo):
        self.task_repo = task_repo

    @staticmethod
    async def verify_user_has_access_to_project(project_id: int, user_tg_id: int) -> bool:
        project = await project_service.get_project_details(project_id)
        return await employee_service.verify_user_is_owner_or_admin(project.company_id, user_tg_id)

    async def create_task(
        self,
        project_id: int,
        name: str,
        description: str,
        deadline: datetime,
        assignee_user_id: int,
        user_tg_id: int,
    ) -> Task:
        has_access = await self.verify_user_has_access_to_project(project_id, user_tg_id)
        if not has_access:
            raise TaskAccessDeniedError("Only company owner or admin can create tasks")

        code = await self.task_repo.get_next_code_for_project(project_id)

        task = Task(
            project_id=project_id,
            name=name,
            code=code,
            description=description,
            deadline=deadline,
            created_at=datetime.now(),
            assignee_user_id=assignee_user_id,
        )
        task_id = await self.task_repo.create(task)
        return await self.task_repo.get_by_id(task_id)

    async def delete_task(self, task_id: int, user_tg_id: int) -> None:
        task = await self.task_repo.get_by_id(task_id)

        has_access = await self.verify_user_has_access_to_project(task.project_id, user_tg_id)
        if not has_access:
            raise TaskAccessDeniedError("Only company owner or admin can delete tasks")

        await self.task_repo.delete(task_id)

    async def get_my_tasks(
        self, user_tg_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Task]:
        return await self.task_repo.get_by_assignee_user_id(user_tg_id, pagination)

    async def get_tasks(
        self, project_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Task]:
        return await self.task_repo.get_by_project_id(project_id, pagination)

    async def get_task_details(self, task_id: int) -> Task:
        return await self.task_repo.get_by_id(task_id)

    async def edit_name(self, task_id: int, name: str, user_tg_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        has_access = await self.verify_user_has_access_to_project(task.project_id, user_tg_id)
        if not has_access:
            raise TaskAccessDeniedError("Only company owner or admin can edit task name")

        return await self.task_repo.update_name(task_id, name)

    async def edit_description(self, task_id: int, description: str, user_tg_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        has_access = await self.verify_user_has_access_to_project(task.project_id, user_tg_id)
        if not has_access:
            raise TaskAccessDeniedError("Only company owner or admin can edit task description")

        return await self.task_repo.update_description(task_id, description)

    async def set_deadline(self, task_id: int, deadline: datetime, user_tg_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        has_access = await self.verify_user_has_access_to_project(task.project_id, user_tg_id)
        if not has_access:
            raise TaskAccessDeniedError("Only company owner or admin can set task deadline")

        return await self.task_repo.update_deadline(task_id, deadline)

    async def assign_to_user(
        self, task_id: int, assignee_user_id: int, user_tg_id: int
    ) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        has_access = await self.verify_user_has_access_to_project(task.project_id, user_tg_id)
        if not has_access:
            raise TaskAccessDeniedError("Only company owner or admin can assign tasks")

        return await self.task_repo.update_assignee(task_id, assignee_user_id)

    async def update_status(self, task_id: int, status: str, user_tg_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        has_access = await self.verify_user_has_access_to_project(task.project_id, user_tg_id)
        if not has_access:
            raise TaskAccessDeniedError("Only company owner or admin can change task status")

        return await self.task_repo.update_status(task_id, status)

    async def get_soon_deadlines(self, days: int = 7) -> list[Task]:
        return await self.task_repo.get_soon_deadlines(days)

    async def get_task_by_full_code(self, company_code: str, project_code: str, task_code: int) -> Task:
        company = await company_service.company_repo.get_by_code(company_code.upper())
        if not company:
            raise TaskNotFoundError(f"Company with code '{company_code}' not found")

        project = await project_service.project_repo.get_by_code(project_code.upper())
        if not project:
            raise TaskNotFoundError(f"Project with code '{project_code}' not found")

        if project.company_id != company.id:
            raise TaskNotFoundError(f"Project '{project_code}' does not belong to company '{company_code}'")

        task = await self.task_repo.get_by_code_and_project_id(task_code, project.id)
        if not task:
            raise TaskNotFoundError(f"Task with code '{task_code}' not found in project '{project_code}'")

        return task


task_service = TaskService(TaskRepo(TaskCrud(), DataclassSerializer(Task)))
