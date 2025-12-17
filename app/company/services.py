from app.company.dal import CompanyCrud, CompanyRepo
from app.company.exceptions import (
    CompanyAccessDeniedError,
    CompanyNotFoundError,
    InvalidCompanyCodeError,
)
from app.company.models import Company
from app.core.serializer import DataclassSerializer
from app.core.types import PageData, PaginationParameters


class CompanyService:
    def __init__(self, company_repo: CompanyRepo):
        self.company_repo = company_repo

    async def create_company(self, name: str, code: str, owner_tg_id: int) -> Company:
        code = code.upper()
        if len(code) != 3 or not code.isalpha():
            raise InvalidCompanyCodeError("Company code must be exactly 3 letters")

        company = Company(name=name, code=code, owner_tg_id=owner_tg_id)
        company_id = await self.company_repo.create(company)
        return await self.company_repo.get_by_id(company_id)

    async def delete_company(self, company_id: int, user_tg_id: int) -> None:
        company = await self.company_repo.get_by_id(company_id)

        if company.owner_tg_id != user_tg_id:
            raise CompanyAccessDeniedError("Only company owner can delete the company")

        await self.company_repo.delete(company_id)

    async def get_my_companies(
        self, user_tg_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Company]:
        return await self.company_repo.get_by_owner_tg_id(user_tg_id, pagination)

    async def get_company_details(self, company_id: int) -> Company:
        company = await self.company_repo.get_by_id(company_id)
        return company

    async def verify_user_is_owner(self, company_id: int, user_tg_id: int) -> bool:
        try:
            company = await self.company_repo.get_by_id(company_id)
            return company.owner_tg_id == user_tg_id
        except CompanyNotFoundError:
            return False


company_service = CompanyService(CompanyRepo(CompanyCrud(), DataclassSerializer(Company)))
