from sqlalchemy import and_, select

from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO, PageData, PaginationParameters
from app.employee.models import Employee
from app.employee.tables import employee_table
from app.employee.exceptions import EmployeeAlreadyExistsError, EmployeeNotFoundError
from app.core.database import database


class EmployeeCrud(CrudBase[int, DTO]):
    table = employee_table

    async def get_by_telegram_id_and_company_id(self, telegram_id: int, company_id: int) -> DTO | None:
        query = select(self.table).where(
            and_(
                self.table.c.telegram_id == telegram_id,
                self.table.c.company_id == company_id
            )
        )
        self.log_query(query)
        return await database.fetch_one(query)

    async def get_by_company_id(
        self, company_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[DTO]:
        filters = {"company_id": company_id}
        return await self.get_page(filters=filters, pagination=pagination)

    async def update_display_name(self, employee_id: int, display_name: str) -> DTO:
        query = (
            self.table.update()
            .where(self.table.c.id == employee_id)
            .values(display_name=display_name)
            .returning(self.table)
        )
        self.log_query(query)
        return await database.fetch_one(query)

    async def update_salary_per_hour(self, employee_id: int, salary_per_hour: float) -> DTO:
        query = (
            self.table.update()
            .where(self.table.c.id == employee_id)
            .values(salary_per_hour=salary_per_hour)
            .returning(self.table)
        )
        self.log_query(query)
        return await database.fetch_one(query)

    async def update_is_active(self, employee_id: int, is_active: bool) -> DTO:
        query = (
            self.table.update()
            .where(self.table.c.id == employee_id)
            .values(is_active=is_active)
            .returning(self.table)
        )
        self.log_query(query)
        return await database.fetch_one(query)


class EmployeeRepo(RepoBase[int, Employee]):
    crud: EmployeeCrud

    def __init__(self, crud: EmployeeCrud, serializer: Serializer[Employee, DTO]):
        super().__init__(crud, serializer, Employee)
        self.not_found_exception_cls = EmployeeNotFoundError
        self.unique_violation_exception_cls = EmployeeAlreadyExistsError

    async def get_by_telegram_id_and_company_id(
        self, telegram_id: int, company_id: int
    ) -> Employee | None:
        dto = await self.crud.get_by_telegram_id_and_company_id(telegram_id, company_id)
        if dto is None:
            return None
        return self.serializer.deserialize(dto)

    async def get_by_company_id(
        self, company_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Employee]:
        page_data = await self.crud.get_by_company_id(company_id, pagination)
        return PageData(
            data=list(self.serializer.flat.deserialize(page_data.data)),
            total=page_data.total,
        )

    async def update_display_name(self, employee_id: int, display_name: str) -> Employee:
        dto = await self.crud.update_display_name(employee_id, display_name)
        return self.serializer.deserialize(dto)

    async def update_salary_per_hour(self, employee_id: int, salary_per_hour: float) -> Employee:
        dto = await self.crud.update_salary_per_hour(employee_id, salary_per_hour)
        return self.serializer.deserialize(dto)

    async def update_is_active(self, employee_id: int, is_active: bool) -> Employee:
        dto = await self.crud.update_is_active(employee_id, is_active)
        return self.serializer.deserialize(dto)


employee_repo = EmployeeRepo(EmployeeCrud(), DataclassSerializer(Employee))
