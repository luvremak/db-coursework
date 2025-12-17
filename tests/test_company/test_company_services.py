import pytest
import sqlite3

from app.company.dal import CompanyCrud, CompanyRepo
from app.company.services import CompanyService
from app.company.exceptions import (
    CompanyAccessDeniedError,
    CompanyNotFoundError,
    InvalidCompanyCodeError,
    CompanyAlreadyExistsError,
)
from app.core.serializer import DataclassSerializer
from app.company.models import Company
from app.core.types import PaginationParameters


@pytest.fixture
def company_service():
    repo = CompanyRepo(CompanyCrud(), DataclassSerializer(Company))
    return CompanyService(repo)


@pytest.mark.asyncio
class TestCompanyService:
    async def test_create_company_success(self, db, company_service):
        company = await company_service.create_company(
            name="Test Company",
            code="tst",
            owner_tg_id=123456789
        )

        assert company is not None
        assert company.name == "Test Company"
        assert company.code == "TST"  # Should be uppercase
        assert company.owner_tg_id == 123456789

    async def test_create_company_invalid_code_too_short(self, db, company_service):
        with pytest.raises(InvalidCompanyCodeError, match="must be exactly 3 letters"):
            await company_service.create_company(
                name="Test Company",
                code="ts",
                owner_tg_id=123456789
            )

    async def test_create_company_invalid_code_too_long(self, db, company_service):
        with pytest.raises(InvalidCompanyCodeError, match="must be exactly 3 letters"):
            await company_service.create_company(
                name="Test Company",
                code="test",
                owner_tg_id=123456789
            )

    async def test_create_company_invalid_code_with_numbers(self, db, company_service):
        with pytest.raises(InvalidCompanyCodeError, match="must be exactly 3 letters"):
            await company_service.create_company(
                name="Test Company",
                code="T12",
                owner_tg_id=123456789
            )

    async def test_create_company_duplicate_code(self, db, company_service):
        await company_service.create_company(
            name="First Company",
            code="TST",
            owner_tg_id=123456789
        )

        # SQLite raises IntegrityError instead of asyncpg.UniqueViolationError
        with pytest.raises(sqlite3.IntegrityError):
            await company_service.create_company(
                name="Second Company",
                code="TST",
                owner_tg_id=987654321
            )

    async def test_get_my_companies(self, db, company_service):
        owner_tg_id = 123456789

        await company_service.create_company("Company 1", "AAA", owner_tg_id)
        await company_service.create_company("Company 2", "BBB", owner_tg_id)

        await company_service.create_company("Other Company", "OTH", 987654321)

        page_data = await company_service.get_my_companies(owner_tg_id)

        assert page_data.total == 2
        assert len(page_data.data) == 2
        assert all(c.owner_tg_id == owner_tg_id for c in page_data.data)

    async def test_get_my_companies_with_pagination(self, db, company_service):
        owner_tg_id = 123456789

        codes = ["AAA", "BBB", "CCC", "DDD", "EEE"]
        for i, code in enumerate(codes):
            await company_service.create_company(
                f"Company {i}",
                code,
                owner_tg_id
            )

        pagination = PaginationParameters(page=1, page_size=2)
        page_data = await company_service.get_my_companies(owner_tg_id, pagination)

        assert page_data.total == 5
        assert len(page_data.data) == 2

    async def test_get_company_details(self, db, company_service):
        company = await company_service.create_company(
            "Test Company",
            "TST",
            123456789
        )

        details = await company_service.get_company_details(company.id)

        assert details.id == company.id
        assert details.name == "Test Company"
        assert details.code == "TST"

    async def test_get_company_details_not_found(self, db, company_service):
        with pytest.raises(CompanyNotFoundError):
            await company_service.get_company_details(99999)

    async def test_verify_user_is_owner_true(self, db, company_service):
        owner_tg_id = 123456789
        company = await company_service.create_company(
            "Test Company",
            "TST",
            owner_tg_id
        )

        is_owner = await company_service.verify_user_is_owner(company.id, owner_tg_id)
        assert is_owner is True

    async def test_verify_user_is_owner_false(self, db, company_service):
        owner_tg_id = 123456789
        other_user_tg_id = 987654321
        company = await company_service.create_company(
            "Test Company",
            "TST",
            owner_tg_id
        )

        is_owner = await company_service.verify_user_is_owner(company.id, other_user_tg_id)
        assert is_owner is False

    async def test_verify_user_is_owner_company_not_found(self, db, company_service):
        is_owner = await company_service.verify_user_is_owner(99999, 123456789)
        assert is_owner is False

    async def test_delete_company_success(self, db, company_service):
        owner_tg_id = 123456789
        company = await company_service.create_company(
            "Test Company",
            "TST",
            owner_tg_id
        )

        await company_service.delete_company(company.id, owner_tg_id)

        with pytest.raises(CompanyNotFoundError):
            await company_service.get_company_details(company.id)

    async def test_delete_company_access_denied(self, db, company_service):
        owner_tg_id = 123456789
        other_user_tg_id = 987654321
        company = await company_service.create_company(
            "Test Company",
            "TST",
            owner_tg_id
        )

        with pytest.raises(CompanyAccessDeniedError, match="Only company owner can delete"):
            await company_service.delete_company(company.id, other_user_tg_id)

    async def test_delete_company_not_found(self, db, company_service):
        with pytest.raises(CompanyNotFoundError):
            await company_service.delete_company(99999, 123456789)

    async def test_code_case_insensitive(self, db, company_service):
        company1 = await company_service.create_company("Company 1", "abc", 111)
        company2 = await company_service.create_company("Company 2", "DEF", 222)
        company3 = await company_service.create_company("Company 3", "xYz", 333)

        assert company1.code == "ABC"
        assert company2.code == "DEF"
        assert company3.code == "XYZ"
