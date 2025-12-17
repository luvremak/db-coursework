from sqlalchemy import select

from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO, PageData, PaginationParameters
from app.project.models import Project
from app.project.tables import project_table
from app.project.exceptions import ProjectAlreadyExistsError, ProjectNotFoundError
from app.core.database import database


class ProjectCrud(CrudBase[int, DTO]):
    table = project_table

    async def get_by_code(self, code: str) -> DTO | None:
        query = select(self.table).where(self.table.c.code == code)
        return await database.fetch_one(query)

    async def get_by_company_id(
        self, company_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[DTO]:
        filters = {"company_id": company_id}
        return await self.get_page(filters=filters, pagination=pagination)


class ProjectRepo(RepoBase[int, Project]):
    crud: ProjectCrud

    def __init__(self, crud: ProjectCrud, serializer: Serializer[Project, DTO]):
        super().__init__(crud, serializer, Project)
        self.not_found_exception_cls = ProjectNotFoundError
        self.unique_violation_exception_cls = ProjectAlreadyExistsError

    async def get_by_code(self, code: str) -> Project | None:
        dto = await self.crud.get_by_code(code)
        if dto is None:
            return None
        return self.serializer.deserialize(dto)

    async def get_by_company_id(
        self, company_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Project]:
        page_data = await self.crud.get_by_company_id(company_id, pagination)
        return PageData(
            data=list(self.serializer.flat.deserialize(page_data.data)),
            total=page_data.total,
        )


project_repo = ProjectRepo(ProjectCrud(), DataclassSerializer(Project))
