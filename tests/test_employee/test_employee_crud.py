import pytest
from datetime import datetime

from app.employee.dal import EmployeeCrud
from app.core.types import PaginationParameters


@pytest.mark.asyncio
class TestEmployeeCrud:
    async def test_create_employee(self, db):
        crud = EmployeeCrud()
        employee_data = {
            "telegram_id": 123456789,
            "company_id": 1,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 25.0,
            "display_name": "John Doe"
        }

        employee_id = await crud.create(employee_data)
        assert employee_id is not None
        assert isinstance(employee_id, int)

    async def test_get_by_id(self, db):
        crud = EmployeeCrud()
        employee_data = {
            "telegram_id": 123456789,
            "company_id": 1,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 25.0,
            "display_name": "John Doe"
        }

        employee_id = await crud.create(employee_data)
        employee = await crud.get_by_id(employee_id)

        assert employee is not None
        assert employee["telegram_id"] == 123456789
        assert employee["display_name"] == "John Doe"
        assert employee["salary_per_hour"] == 25.0

    async def test_get_by_telegram_id_and_company_id(self, db):
        crud = EmployeeCrud()
        employee_data = {
            "telegram_id": 123456789,
            "company_id": 1,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 25.0,
            "display_name": "John Doe"
        }

        await crud.create(employee_data)
        employee = await crud.get_by_telegram_id_and_company_id(123456789, 1)

        assert employee is not None
        assert employee["telegram_id"] == 123456789
        assert employee["company_id"] == 1

    async def test_get_by_telegram_id_and_company_id_not_found(self, db):
        crud = EmployeeCrud()
        employee = await crud.get_by_telegram_id_and_company_id(999999999, 1)
        assert employee is None

    async def test_get_by_company_id(self, db):
        crud = EmployeeCrud()
        company_id = 1

        # Create multiple employees for the same company
        await crud.create({
            "telegram_id": 111111111,
            "company_id": company_id,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 25.0,
            "display_name": "Employee 1"
        })
        await crud.create({
            "telegram_id": 222222222,
            "company_id": company_id,
            "is_active": True,
            "is_admin": True,
            "created_at": datetime.now(),
            "salary_per_hour": 30.0,
            "display_name": "Employee 2"
        })
        await crud.create({
            "telegram_id": 333333333,
            "company_id": 2,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 20.0,
            "display_name": "Other Employee"
        })

        page_data = await crud.get_by_company_id(company_id)

        assert page_data.total == 2
        assert len(page_data.data) == 2
        assert all(e["company_id"] == company_id for e in page_data.data)

    async def test_get_by_company_id_with_pagination(self, db):
        crud = EmployeeCrud()
        company_id = 1

        # Create 5 employees
        for i in range(5):
            await crud.create({
                "telegram_id": 111111111 + i,
                "company_id": company_id,
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.now(),
                "salary_per_hour": 25.0,
                "display_name": f"Employee {i}"
            })

        pagination = PaginationParameters(page=1, page_size=2)
        page_data = await crud.get_by_company_id(company_id, pagination)

        assert page_data.total == 5
        assert len(page_data.data) == 2

    async def test_update_display_name(self, db):
        crud = EmployeeCrud()
        employee_data = {
            "telegram_id": 123456789,
            "company_id": 1,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 25.0,
            "display_name": "John Doe"
        }

        employee_id = await crud.create(employee_data)
        updated = await crud.update_display_name(employee_id, "Jane Smith")

        assert updated["display_name"] == "Jane Smith"
        assert updated["id"] == employee_id

    async def test_update_salary_per_hour(self, db):
        crud = EmployeeCrud()
        employee_data = {
            "telegram_id": 123456789,
            "company_id": 1,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 25.0,
            "display_name": "John Doe"
        }

        employee_id = await crud.create(employee_data)
        updated = await crud.update_salary_per_hour(employee_id, 30.0)

        assert updated["salary_per_hour"] == 30.0
        assert updated["id"] == employee_id

    async def test_update_is_active(self, db):
        crud = EmployeeCrud()
        employee_data = {
            "telegram_id": 123456789,
            "company_id": 1,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 25.0,
            "display_name": "John Doe"
        }

        employee_id = await crud.create(employee_data)
        updated = await crud.update_is_active(employee_id, False)

        assert updated["is_active"] is False
        assert updated["id"] == employee_id

    async def test_delete_employee(self, db):
        crud = EmployeeCrud()
        employee_data = {
            "telegram_id": 123456789,
            "company_id": 1,
            "is_active": True,
            "is_admin": False,
            "created_at": datetime.now(),
            "salary_per_hour": 25.0,
            "display_name": "John Doe"
        }

        employee_id = await crud.create(employee_data)
        await crud.delete(employee_id)

        employee = await crud.get_by_id(employee_id)
        assert employee is None
