from sqlalchemy import select

from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO, PageData, PaginationParameters
from app.company.models import Company
from app.company.tables import company_table
from app.company.exceptions import CompanyAlreadyExistsError, CompanyNotFoundError
from app.core.database import database


class CompanyCrud(CrudBase[int, DTO]):
    table = company_table

    async def get_by_code(self, code: str) -> DTO | None:
        query = select(self.table).where(self.table.c.code == code)
        return await database.fetch_one(query)

    async def get_by_owner_tg_id(
        self, owner_tg_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[DTO]:
        filters = {"owner_tg_id": owner_tg_id}
        return await self.get_page(filters=filters, pagination=pagination)


class CompanyRepo(RepoBase[int, Company]):
    crud: CompanyCrud

    def __init__(self, crud: CompanyCrud, serializer: Serializer[Company, DTO]):
        super().__init__(crud, serializer, Company)
        self.not_found_exception_cls = CompanyNotFoundError
        self.unique_violation_exception_cls = CompanyAlreadyExistsError

    async def get_by_code(self, code: str) -> Company | None:
        dto = await self.crud.get_by_code(code)
        if dto is None:
            return None
        return self.serializer.deserialize(dto)

    async def get_by_owner_tg_id(
        self, owner_tg_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Company]:
        page_data = await self.crud.get_by_owner_tg_id(owner_tg_id, pagination)
        return PageData(
            data=list(self.serializer.flat.deserialize(page_data.data)),
            total=page_data.total,
        )


company_repo = CompanyRepo(CompanyCrud(), DataclassSerializer(Company))
