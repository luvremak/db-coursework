import pytest
from datetime import datetime

from app.project.dal import ProjectCrud
from app.core.types import PaginationParameters


@pytest.mark.asyncio
class TestProjectCrud:
    async def test_create_project(self, db):
        crud = ProjectCrud()
        project_data = {
            "company_id": 1,
            "name": "Test Project",
            "code": "TST",
            "created_at": datetime.now()
        }

        project_id = await crud.create(project_data)
        assert project_id is not None
        assert isinstance(project_id, int)

    async def test_get_by_id(self, db):
        crud = ProjectCrud()
        project_data = {
            "company_id": 1,
            "name": "Test Project",
            "code": "TST",
            "created_at": datetime.now()
        }

        project_id = await crud.create(project_data)
        project = await crud.get_by_id(project_id)

        assert project is not None
        assert project["name"] == "Test Project"
        assert project["code"] == "TST"
        assert project["company_id"] == 1

    async def test_get_by_code(self, db):
        crud = ProjectCrud()
        project_data = {
            "company_id": 1,
            "name": "Test Project",
            "code": "TST",
            "created_at": datetime.now()
        }

        await crud.create(project_data)
        project = await crud.get_by_code("TST")

        assert project is not None
        assert project["name"] == "Test Project"
        assert project["code"] == "TST"

    async def test_get_by_code_not_found(self, db):
        crud = ProjectCrud()
        project = await crud.get_by_code("XXX")
        assert project is None

    async def test_get_by_company_id(self, db):
        crud = ProjectCrud()
        company_id = 1

        await crud.create({
            "company_id": company_id,
            "name": "Project 1",
            "code": "AAA",
            "created_at": datetime.now()
        })
        await crud.create({
            "company_id": company_id,
            "name": "Project 2",
            "code": "BBB",
            "created_at": datetime.now()
        })
        await crud.create({
            "company_id": 2,
            "name": "Other Project",
            "code": "OTH",
            "created_at": datetime.now()
        })

        page_data = await crud.get_by_company_id(company_id)

        assert page_data.total == 2
        assert len(page_data.data) == 2
        assert all(p["company_id"] == company_id for p in page_data.data)

    async def test_get_by_company_id_with_pagination(self, db):
        crud = ProjectCrud()
        company_id = 1

        codes = ["AAA", "BBB", "CCC", "DDD", "EEE"]
        for i, code in enumerate(codes):
            await crud.create({
                "company_id": company_id,
                "name": f"Project {i}",
                "code": code,
                "created_at": datetime.now()
            })

        pagination = PaginationParameters(page=1, page_size=2)
        page_data = await crud.get_by_company_id(company_id, pagination)

        assert page_data.total == 5
        assert len(page_data.data) == 2

    async def test_delete_project(self, db):
        crud = ProjectCrud()
        project_data = {
            "company_id": 1,
            "name": "Test Project",
            "code": "TST",
            "created_at": datetime.now()
        }

        project_id = await crud.create(project_data)
        await crud.delete(project_id)

        project = await crud.get_by_id(project_id)
        assert project is None

    async def test_update_project(self, db):
        crud = ProjectCrud()
        project_data = {
            "company_id": 1,
            "name": "Test Project",
            "code": "TST",
            "created_at": datetime.now()
        }

        project_id = await crud.create(project_data)

        updated_data = {
            "id": project_id,
            "company_id": 1,
            "name": "Updated Project",
            "code": "UPD",
            "created_at": datetime.now()
        }
        await crud.update(updated_data)

        project = await crud.get_by_id(project_id)
        assert project["name"] == "Updated Project"
        assert project["code"] == "UPD"

    async def test_get_all_projects(self, db):
        crud = ProjectCrud()

        await crud.create({
            "company_id": 1,
            "name": "Project 1",
            "code": "ABC",
            "created_at": datetime.now()
        })
        await crud.create({
            "company_id": 1,
            "name": "Project 2",
            "code": "DEF",
            "created_at": datetime.now()
        })
        await crud.create({
            "company_id": 2,
            "name": "Project 3",
            "code": "GHI",
            "created_at": datetime.now()
        })

        projects = await crud.get_all()
        assert len(projects) >= 3

    async def test_get_page_with_filters(self, db):
        crud = ProjectCrud()

        # Create projects for different companies
        for i in range(5):
            await crud.create({
                "company_id": 1,
                "name": f"Company 1 Project {i}",
                "code": f"C1{i}",
                "created_at": datetime.now()
            })

        for i in range(3):
            await crud.create({
                "company_id": 2,
                "name": f"Company 2 Project {i}",
                "code": f"C2{i}",
                "created_at": datetime.now()
            })

        # Test filtering by company_id
        page_data = await crud.get_page(filters={"company_id": 1})
        assert page_data.total == 5
        assert all(p["company_id"] == 1 for p in page_data.data)

        page_data = await crud.get_page(filters={"company_id": 2})
        assert page_data.total == 3
        assert all(p["company_id"] == 2 for p in page_data.data)
