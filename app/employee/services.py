from datetime import datetime

from app.employee.dal import EmployeeCrud, EmployeeRepo
from app.employee.models import Employee
from app.employee.exceptions import EmployeeAccessDeniedError, EmployeeAlreadyExistsError
from app.company.services import company_service
from app.core.serializer import DataclassSerializer
from app.core.types import PageData, PaginationParameters


class EmployeeService:
    def __init__(self, employee_repo: EmployeeRepo):
        self.employee_repo = employee_repo

    async def verify_user_is_owner_or_admin(self, company_id: int, user_tg_id: int) -> bool:
        is_owner = await company_service.verify_user_is_owner(company_id, user_tg_id)
        if is_owner:
            return True

        employee = await self.employee_repo.get_by_telegram_id_and_company_id(user_tg_id, company_id)
        if employee and employee.is_admin and employee.is_active:
            return True

        return False

    async def create_employee(
        self,
        company_id: int,
        telegram_id: int,
        display_name: str,
        salary_per_hour: float,
        is_admin: bool,
        user_tg_id: int,
    ) -> Employee:
        is_authorized = await self.verify_user_is_owner_or_admin(company_id, user_tg_id)
        if not is_authorized:
            raise EmployeeAccessDeniedError("Only company owner or admin can create employees")

        existing = await self.employee_repo.get_by_telegram_id_and_company_id(telegram_id, company_id)
        if existing is not None:
            raise EmployeeAlreadyExistsError("Employee already exists in this company")

        employee = Employee(
            telegram_id=telegram_id,
            company_id=company_id,
            is_active=True,
            is_admin=is_admin,
            created_at=datetime.now(),
            salary_per_hour=salary_per_hour,
            display_name=display_name,
        )
        employee_id = await self.employee_repo.create(employee)
        return await self.employee_repo.get_by_id(employee_id)

    async def delete_employee(self, employee_id: int, user_tg_id: int) -> None:
        employee = await self.employee_repo.get_by_id(employee_id)

        is_authorized = await self.verify_user_is_owner_or_admin(employee.company_id, user_tg_id)
        if not is_authorized:
            raise EmployeeAccessDeniedError("Only company owner or admin can delete employees")

        await self.employee_repo.delete(employee_id)

    async def get_employees(
        self, company_id: int, pagination: PaginationParameters | None = None
    ) -> PageData[Employee]:
        return await self.employee_repo.get_by_company_id(company_id, pagination)

    async def get_employee_details(self, employee_id: int) -> Employee:
        return await self.employee_repo.get_by_id(employee_id)

    async def get_employee_by_telegram_id_and_company_id(
        self, telegram_id: int, company_id: int
    ) -> Employee | None:
        return await self.employee_repo.get_by_telegram_id_and_company_id(telegram_id, company_id)

    async def set_display_name(
        self, employee_id: int, display_name: str, user_tg_id: int
    ) -> Employee:
        employee = await self.employee_repo.get_by_id(employee_id)

        is_authorized = await self.verify_user_is_owner_or_admin(employee.company_id, user_tg_id)
        if not is_authorized:
            raise EmployeeAccessDeniedError("Only company owner or admin can set display name")

        return await self.employee_repo.update_display_name(employee_id, display_name)

    async def set_salary_per_hour(
        self, employee_id: int, salary_per_hour: float, user_tg_id: int
    ) -> Employee:
        employee = await self.employee_repo.get_by_id(employee_id)

        is_authorized = await self.verify_user_is_owner_or_admin(employee.company_id, user_tg_id)
        if not is_authorized:
            raise EmployeeAccessDeniedError("Only company owner or admin can set salary")

        return await self.employee_repo.update_salary_per_hour(employee_id, salary_per_hour)

    async def set_is_active(
        self, employee_id: int, is_active: bool, user_tg_id: int
    ) -> Employee:
        employee = await self.employee_repo.get_by_id(employee_id)

        is_authorized = await self.verify_user_is_owner_or_admin(employee.company_id, user_tg_id)
        if not is_authorized:
            raise EmployeeAccessDeniedError("Only company owner or admin can change employee status")

        return await self.employee_repo.update_is_active(employee_id, is_active)


employee_service = EmployeeService(EmployeeRepo(EmployeeCrud(), DataclassSerializer(Employee)))
