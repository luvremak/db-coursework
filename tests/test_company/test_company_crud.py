import pytest

from app.company.dal import CompanyCrud
from app.core.types import PaginationParameters


@pytest.mark.asyncio
class TestCompanyCrud:
    async def test_create_company(self, db):
        crud = CompanyCrud()
        company_data = {
            "name": "Test Company",
            "code": "TST",
            "owner_tg_id": 123456789
        }

        company_id = await crud.create(company_data)
        assert company_id is not None
        assert isinstance(company_id, int)

    async def test_get_by_id(self, db):
        crud = CompanyCrud()
        company_data = {
            "name": "Test Company",
            "code": "TST",
            "owner_tg_id": 123456789
        }

        company_id = await crud.create(company_data)
        company = await crud.get_by_id(company_id)

        assert company is not None
        assert company["name"] == "Test Company"
        assert company["code"] == "TST"
        assert company["owner_tg_id"] == 123456789

    async def test_get_by_code(self, db):
        crud = CompanyCrud()
        company_data = {
            "name": "Test Company",
            "code": "TST",
            "owner_tg_id": 123456789
        }

        await crud.create(company_data)
        company = await crud.get_by_code("TST")

        assert company is not None
        assert company["name"] == "Test Company"
        assert company["code"] == "TST"

    async def test_get_by_code_not_found(self, db):
        crud = CompanyCrud()
        company = await crud.get_by_code("XXX")
        assert company is None

    async def test_get_by_owner_tg_id(self, db):
        crud = CompanyCrud()
        owner_tg_id = 123456789

        await crud.create({"name": "Company 1", "code": "AAA", "owner_tg_id": owner_tg_id})
        await crud.create({"name": "Company 2", "code": "BBB", "owner_tg_id": owner_tg_id})
        await crud.create({"name": "Other Company", "code": "OTH", "owner_tg_id": 987654321})

        page_data = await crud.get_by_owner_tg_id(owner_tg_id)

        assert page_data.total == 2
        assert len(page_data.data) == 2
        assert all(c["owner_tg_id"] == owner_tg_id for c in page_data.data)

    async def test_get_by_owner_tg_id_with_pagination(self, db):
        crud = CompanyCrud()
        owner_tg_id = 123456789

        codes = ["AAA", "BBB", "CCC", "DDD", "EEE"]
        for i, code in enumerate(codes):
            await crud.create({
                "name": f"Company {i}",
                "code": code,
                "owner_tg_id": owner_tg_id
            })

        pagination = PaginationParameters(page=1, page_size=2)
        page_data = await crud.get_by_owner_tg_id(owner_tg_id, pagination)

        assert page_data.total == 5
        assert len(page_data.data) == 2

    async def test_delete_company(self, db):
        crud = CompanyCrud()
        company_data = {
            "name": "Test Company",
            "code": "TST",
            "owner_tg_id": 123456789
        }

        company_id = await crud.create(company_data)
        await crud.delete(company_id)

        company = await crud.get_by_id(company_id)
        assert company is None

    async def test_update_company(self, db):
        crud = CompanyCrud()
        company_data = {
            "name": "Test Company",
            "code": "TST",
            "owner_tg_id": 123456789
        }

        company_id = await crud.create(company_data)

        updated_data = {
            "id": company_id,
            "name": "Updated Company",
            "code": "UPD",
            "owner_tg_id": 123456789
        }
        await crud.update(updated_data)

        company = await crud.get_by_id(company_id)
        assert company["name"] == "Updated Company"
        assert company["code"] == "UPD"

    async def test_get_all_companies(self, db):
        crud = CompanyCrud()

        await crud.create({"name": "Company 1", "code": "ABC", "owner_tg_id": 111})
        await crud.create({"name": "Company 2", "code": "DEF", "owner_tg_id": 222})
        await crud.create({"name": "Company 3", "code": "GHI", "owner_tg_id": 333})

        companies = await crud.get_all()
        assert len(companies) >= 3
