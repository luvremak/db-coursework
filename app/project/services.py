from datetime import datetime

from app.project.dal import ProjectCrud, ProjectRepo
from app.project.models import Project
from app.project.exceptions import (
    InvalidProjectCodeError,
    ProjectAccessDeniedError,
    ProjectAlreadyExistsError,
)
from app.company.services import company_service
from app.core.serializer import DataclassSerializer
from app.core.types import PageData, PaginationParameters


class ProjectService:
    def __init__(self, project_repo: ProjectRepo):
        self.project_repo = project_repo

    async def create_project(
        self, company_id: int, name: str, code: str, user_tg_id: int
    ) -> Project:
        is_owner = await company_service.verify_user_is_owner(company_id, user_tg_id)
        if not is_owner:
            raise ProjectAccessDeniedError("Only company owner can create projects")

        code = code.upper()
        if len(code) != 3 or not code.isalpha():
            raise InvalidProjectCodeError("Project code must be exactly 3 letters")

        existing = await self.project_repo.get_by_code(code)
        if existing is not None:
            raise ProjectAlreadyExistsError(f"Project with code '{code}' already exists")

        project = Project(
            company_id=company_id,
            name=name,
            code=code,
            created_at=datetime.now(),
        )
        project_id = await self.project_repo.create(project)
        return await self.project_repo.get_by_id(project_id)

    async def delete_project(self, project_id: int, user_tg_id: int) -> None:
        project = await self.project_repo.get_by_id(project_id)

        is_owner = await company_service.verify_user_is_owner(project.company_id, user_tg_id)
        if not is_owner:
            raise ProjectAccessDeniedError("Only company owner can delete projects")

        await self.project_repo.delete(project_id)

    async def get_projects(
        self, company_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Project]:
        return await self.project_repo.get_by_company_id(company_id, pagination)

    async def get_project_details(self, project_id: int) -> Project:
        return await self.project_repo.get_by_id(project_id)


project_service = ProjectService(ProjectRepo(ProjectCrud(), DataclassSerializer(Project)))
