import pytest
import pytest_asyncio
from datetime import datetime

from app.employee.dal import EmployeeCrud, EmployeeRepo
from app.employee.services import EmployeeService
from app.employee.exceptions import (
    EmployeeAccessDeniedError,
    EmployeeNotFoundError,
    EmployeeAlreadyExistsError,
)
from app.company.dal import CompanyCrud
from app.company.services import company_service
from app.core.serializer import DataclassSerializer
from app.employee.models import Employee
from app.core.types import PaginationParameters


@pytest.fixture
def employee_service():
    repo = EmployeeRepo(EmployeeCrud(), DataclassSerializer(Employee))
    return EmployeeService(repo)


@pytest_asyncio.fixture
async def test_company(db):
    crud = CompanyCrud()
    company_id = await crud.create({
        "name": "Test Company",
        "code": "TST",
        "owner_tg_id": 111111111
    })
    return company_id


@pytest.mark.asyncio
class TestEmployeeService:
    async def test_create_employee_as_owner(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        employee = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        assert employee is not None
        assert employee.telegram_id == 222222222
        assert employee.display_name == "John Doe"
        assert employee.salary_per_hour == 25.0
        assert employee.is_active is True
        assert employee.is_admin is False

    async def test_create_employee_as_admin(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        admin_tg_id = 333333333

        # Create admin employee first
        await employee_service.create_employee(
            company_id=company_id,
            telegram_id=admin_tg_id,
            display_name="Admin User",
            salary_per_hour=30.0,
            is_admin=True,
            user_tg_id=owner_tg_id
        )

        # Admin creates another employee
        employee = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=444444444,
            display_name="Regular User",
            salary_per_hour=20.0,
            is_admin=False,
            user_tg_id=admin_tg_id
        )

        assert employee is not None
        assert employee.telegram_id == 444444444

    async def test_create_employee_unauthorized(self, db, employee_service, test_company):
        company_id = test_company
        unauthorized_user = 999999999

        with pytest.raises(EmployeeAccessDeniedError, match="Only company owner or admin"):
            await employee_service.create_employee(
                company_id=company_id,
                telegram_id=222222222,
                display_name="John Doe",
                salary_per_hour=25.0,
                is_admin=False,
                user_tg_id=unauthorized_user
            )

    async def test_create_employee_already_exists(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        telegram_id = 222222222

        # Create first employee
        await employee_service.create_employee(
            company_id=company_id,
            telegram_id=telegram_id,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        # Try to create same employee again
        with pytest.raises(EmployeeAlreadyExistsError):
            await employee_service.create_employee(
                company_id=company_id,
                telegram_id=telegram_id,
                display_name="Jane Smith",
                salary_per_hour=30.0,
                is_admin=False,
                user_tg_id=owner_tg_id
            )

    async def test_get_employees(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        # Create multiple employees
        await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="Employee 1",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )
        await employee_service.create_employee(
            company_id=company_id,
            telegram_id=333333333,
            display_name="Employee 2",
            salary_per_hour=30.0,
            is_admin=True,
            user_tg_id=owner_tg_id
        )

        page_data = await employee_service.get_employees(company_id)

        assert page_data.total == 2
        assert len(page_data.data) == 2

    async def test_get_employees_with_pagination(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        # Create 5 employees
        for i in range(5):
            await employee_service.create_employee(
                company_id=company_id,
                telegram_id=222222222 + i,
                display_name=f"Employee {i}",
                salary_per_hour=25.0,
                is_admin=False,
                user_tg_id=owner_tg_id
            )

        pagination = PaginationParameters(page=1, page_size=2)
        page_data = await employee_service.get_employees(company_id, pagination)

        assert page_data.total == 5
        assert len(page_data.data) == 2

    async def test_get_employee_details(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        details = await employee_service.get_employee_details(created.id)

        assert details.id == created.id
        assert details.display_name == "John Doe"

    async def test_get_employee_details_not_found(self, db, employee_service):
        with pytest.raises(EmployeeNotFoundError):
            await employee_service.get_employee_details(99999)

    async def test_get_employee_by_telegram_id_and_company_id(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        telegram_id = 222222222

        await employee_service.create_employee(
            company_id=company_id,
            telegram_id=telegram_id,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        employee = await employee_service.get_employee_by_telegram_id_and_company_id(
            telegram_id, company_id
        )

        assert employee is not None
        assert employee.telegram_id == telegram_id

    async def test_set_display_name_as_owner(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        updated = await employee_service.set_display_name(
            created.id, "Jane Smith", owner_tg_id
        )

        assert updated.display_name == "Jane Smith"

    async def test_set_display_name_unauthorized(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        unauthorized_user = 999999999

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        with pytest.raises(EmployeeAccessDeniedError, match="Only company owner or admin"):
            await employee_service.set_display_name(
                created.id, "Jane Smith", unauthorized_user
            )

    async def test_set_salary_per_hour_as_owner(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        updated = await employee_service.set_salary_per_hour(
            created.id, 30.0, owner_tg_id
        )

        assert updated.salary_per_hour == 30.0

    async def test_set_salary_per_hour_unauthorized(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        unauthorized_user = 999999999

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        with pytest.raises(EmployeeAccessDeniedError, match="Only company owner or admin"):
            await employee_service.set_salary_per_hour(
                created.id, 30.0, unauthorized_user
            )

    async def test_set_is_active_as_owner(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        updated = await employee_service.set_is_active(
            created.id, False, owner_tg_id
        )

        assert updated.is_active is False

    async def test_set_is_active_unauthorized(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        unauthorized_user = 999999999

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        with pytest.raises(EmployeeAccessDeniedError, match="Only company owner or admin"):
            await employee_service.set_is_active(
                created.id, False, unauthorized_user
            )

    async def test_delete_employee_as_owner(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        await employee_service.delete_employee(created.id, owner_tg_id)

        with pytest.raises(EmployeeNotFoundError):
            await employee_service.get_employee_details(created.id)

    async def test_delete_employee_unauthorized(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        unauthorized_user = 999999999

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=222222222,
            display_name="John Doe",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        with pytest.raises(EmployeeAccessDeniedError, match="Only company owner or admin"):
            await employee_service.delete_employee(created.id, unauthorized_user)

    async def test_verify_user_is_owner_or_admin_as_owner(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111

        is_authorized = await employee_service.verify_user_is_owner_or_admin(
            company_id, owner_tg_id
        )

        assert is_authorized is True

    async def test_verify_user_is_owner_or_admin_as_admin(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        admin_tg_id = 333333333

        await employee_service.create_employee(
            company_id=company_id,
            telegram_id=admin_tg_id,
            display_name="Admin User",
            salary_per_hour=30.0,
            is_admin=True,
            user_tg_id=owner_tg_id
        )

        is_authorized = await employee_service.verify_user_is_owner_or_admin(
            company_id, admin_tg_id
        )

        assert is_authorized is True

    async def test_verify_user_is_owner_or_admin_as_regular_employee(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        employee_tg_id = 222222222

        await employee_service.create_employee(
            company_id=company_id,
            telegram_id=employee_tg_id,
            display_name="Regular User",
            salary_per_hour=25.0,
            is_admin=False,
            user_tg_id=owner_tg_id
        )

        is_authorized = await employee_service.verify_user_is_owner_or_admin(
            company_id, employee_tg_id
        )

        assert is_authorized is False

    async def test_verify_user_is_owner_or_admin_inactive_admin(self, db, employee_service, test_company):
        company_id = test_company
        owner_tg_id = 111111111
        admin_tg_id = 333333333

        created = await employee_service.create_employee(
            company_id=company_id,
            telegram_id=admin_tg_id,
            display_name="Admin User",
            salary_per_hour=30.0,
            is_admin=True,
            user_tg_id=owner_tg_id
        )

        # Deactivate admin
        await employee_service.set_is_active(created.id, False, owner_tg_id)

        is_authorized = await employee_service.verify_user_is_owner_or_admin(
            company_id, admin_tg_id
        )

        assert is_authorized is False
