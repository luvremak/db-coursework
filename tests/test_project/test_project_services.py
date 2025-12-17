import pytest
import sqlite3

from app.project.dal import ProjectCrud, ProjectRepo
from app.project.services import ProjectService
from app.project.exceptions import (
    ProjectAccessDeniedError,
    ProjectNotFoundError,
    InvalidProjectCodeError,
    ProjectAlreadyExistsError,
)
from app.core.serializer import DataclassSerializer
from app.project.models import Project
from app.core.types import PaginationParameters
from app.company.services import company_service


@pytest.fixture
def project_service():
    repo = ProjectRepo(ProjectCrud(), DataclassSerializer(Project))
    return ProjectService(repo)


@pytest.mark.asyncio
class TestProjectService:
    async def test_create_project_success(self, db, project_service):
        # First create a company
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        # Create a project
        project = await project_service.create_project(
            company_id=company.id,
            name="Test Project",
            code="prj",
            user_tg_id=123456789
        )

        assert project is not None
        assert project.name == "Test Project"
        assert project.code == "PRJ"  # Should be uppercase
        assert project.company_id == company.id

    async def test_create_project_invalid_code_too_short(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        with pytest.raises(InvalidProjectCodeError, match="must be exactly 3 letters"):
            await project_service.create_project(
                company_id=company.id,
                name="Test Project",
                code="pr",
                user_tg_id=123456789
            )

    async def test_create_project_invalid_code_too_long(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        with pytest.raises(InvalidProjectCodeError, match="must be exactly 3 letters"):
            await project_service.create_project(
                company_id=company.id,
                name="Test Project",
                code="proj",
                user_tg_id=123456789
            )

    async def test_create_project_invalid_code_with_numbers(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        with pytest.raises(InvalidProjectCodeError, match="must be exactly 3 letters"):
            await project_service.create_project(
                company_id=company.id,
                name="Test Project",
                code="P12",
                user_tg_id=123456789
            )

    async def test_create_project_duplicate_code(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        await project_service.create_project(
            company_id=company.id,
            name="First Project",
            code="PRJ",
            user_tg_id=123456789
        )

        with pytest.raises(ProjectAlreadyExistsError):
            await project_service.create_project(
                company_id=company.id,
                name="Second Project",
                code="PRJ",
                user_tg_id=123456789
            )

    async def test_create_project_access_denied(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        # Try to create project with a different user
        with pytest.raises(ProjectAccessDeniedError, match="Only company owner can create projects"):
            await project_service.create_project(
                company_id=company.id,
                name="Test Project",
                code="PRJ",
                user_tg_id=987654321
            )

    async def test_get_projects_by_company(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        await project_service.create_project(company.id, "Project 1", "AAA", 123456789)
        await project_service.create_project(company.id, "Project 2", "BBB", 123456789)

        # Create another company with projects
        other_company = await company_service.create_company(
            name="Other Company",
            code="OTH",
            owner_tg_id=987654321
        )
        await project_service.create_project(other_company.id, "Other Project", "OTH", 987654321)

        page_data = await project_service.get_projects(company.id)

        assert page_data.total == 2
        assert len(page_data.data) == 2
        assert all(p.company_id == company.id for p in page_data.data)

    async def test_get_projects_with_pagination(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        codes = ["AAA", "BBB", "CCC", "DDD", "EEE"]
        for i, code in enumerate(codes):
            await project_service.create_project(
                company.id,
                f"Project {i}",
                code,
                123456789
            )

        pagination = PaginationParameters(page=1, page_size=2)
        page_data = await project_service.get_projects(company.id, pagination)

        assert page_data.total == 5
        assert len(page_data.data) == 2

    async def test_get_project_details(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        project = await project_service.create_project(
            company.id,
            "Test Project",
            "PRJ",
            123456789
        )

        details = await project_service.get_project_details(project.id)

        assert details.id == project.id
        assert details.name == "Test Project"
        assert details.code == "PRJ"
        assert details.company_id == company.id

    async def test_get_project_details_not_found(self, db, project_service):
        with pytest.raises(ProjectNotFoundError):
            await project_service.get_project_details(99999)

    async def test_delete_project_success(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        project = await project_service.create_project(
            company.id,
            "Test Project",
            "PRJ",
            123456789
        )

        await project_service.delete_project(project.id, 123456789)

        with pytest.raises(ProjectNotFoundError):
            await project_service.get_project_details(project.id)

    async def test_delete_project_access_denied(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        project = await project_service.create_project(
            company.id,
            "Test Project",
            "PRJ",
            123456789
        )

        # Try to delete with a different user
        with pytest.raises(ProjectAccessDeniedError, match="Only company owner can delete projects"):
            await project_service.delete_project(project.id, 987654321)

    async def test_delete_project_not_found(self, db, project_service):
        with pytest.raises(ProjectNotFoundError):
            await project_service.delete_project(99999, 123456789)

    async def test_code_case_insensitive(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        project1 = await project_service.create_project(company.id, "Project 1", "abc", 123456789)
        project2 = await project_service.create_project(company.id, "Project 2", "DEF", 123456789)
        project3 = await project_service.create_project(company.id, "Project 3", "xYz", 123456789)

        assert project1.code == "ABC"
        assert project2.code == "DEF"
        assert project3.code == "XYZ"

    async def test_multiple_companies_same_project_code(self, db, project_service):
        # Create two different companies
        company1 = await company_service.create_company(
            name="Company 1",
            code="CMP",
            owner_tg_id=111111111
        )

        company2 = await company_service.create_company(
            name="Company 2",
            code="COM",
            owner_tg_id=222222222
        )

        # Both companies should NOT be able to create projects with the same code
        # because project codes are globally unique (based on the current implementation)
        project1 = await project_service.create_project(company1.id, "Project", "PRJ", 111111111)

        with pytest.raises(ProjectAlreadyExistsError):
            await project_service.create_project(company2.id, "Project", "PRJ", 222222222)

    async def test_get_empty_projects_list(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        page_data = await project_service.get_projects(company.id)

        assert page_data.total == 0
        assert len(page_data.data) == 0

    async def test_project_created_at_timestamp(self, db, project_service):
        company = await company_service.create_company(
            name="Test Company",
            code="TST",
            owner_tg_id=123456789
        )

        project = await project_service.create_project(
            company.id,
            "Test Project",
            "PRJ",
            123456789
        )

        assert project.created_at is not None
        assert isinstance(project.created_at, type(project.created_at))
