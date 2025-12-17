from datetime import datetime
from collections import defaultdict

from app.time_tracking.dal import TimeTrackingEntryCrud, TimeTrackingEntryRepo
from app.time_tracking.models import TimeTrackingEntry
from app.core.serializer import DataclassSerializer


class TimeTrackingEntryService:
    def __init__(self, time_tracking_entry_repo: TimeTrackingEntryRepo):
        self.time_tracking_entry_repo = time_tracking_entry_repo

    async def create_time_entry(
        self,
        task_id: int,
        employee_id: int,
        duration_minutes: int,
    ) -> TimeTrackingEntry:
        entry = TimeTrackingEntry(
            task_id=task_id,
            employee_id=employee_id,
            duration_minutes=duration_minutes,
            created_at=datetime.now(),
        )
        return await self.time_tracking_entry_repo.create(entry)

    async def get_total_minutes_by_task_and_employee(
        self,
        task_id: int,
        employee_id: int,
    ) -> int:
        return await self.time_tracking_entry_repo.get_total_minutes_by_task_and_employee(task_id, employee_id)

    async def get_project_stats_for_company(self, company_id: int) -> list[dict]:
        from app.company.services import company_service
        from app.project.services import project_service
        from app.task.services import task_service
        from app.employee.services import employee_service

        company = await company_service.get_company_details(company_id)
        entries = await self.time_tracking_entry_repo.get_all_entries_for_company(company_id)

        projects_page = await project_service.get_projects(company_id, pagination=None)
        projects = {p.id: p for p in projects_page.data}

        task_to_project = {}
        for project in projects.values():
            tasks_page = await task_service.get_tasks(project.id, pagination=None)
            for task in tasks_page.data:
                task_to_project[task.id] = project

        employees = {}
        from app.employee.dal import employee_repo
        all_employees_page = await employee_repo.get_by_company_id(company_id, pagination=None)
        for emp in all_employees_page.data:
            employees[emp.id] = emp

        project_stats = defaultdict(lambda: {"total_minutes": 0, "total_cost": 0.0})

        for entry in entries:
            if entry.task_id in task_to_project:
                project = task_to_project[entry.task_id]
                employee = employees.get(entry.employee_id)

                if employee:
                    hours = entry.duration_minutes / 60.0
                    cost = hours * employee.salary_per_hour

                    project_stats[project.id]["total_minutes"] += entry.duration_minutes
                    project_stats[project.id]["total_cost"] += cost

        rows = []
        for project_id, stats in project_stats.items():
            project = projects[project_id]
            rows.append({
                "company_code": company.code,
                "project_code": project.code,
                "total_hours_spent": round(stats["total_minutes"] / 60.0, 2),
                "total_money_spent": round(stats["total_cost"], 2)
            })

        return rows

    async def get_employee_stats_for_company(self, company_id: int) -> list[dict]:
        from app.company.services import company_service
        from app.project.services import project_service
        from app.task.services import task_service
        from app.employee.services import employee_service

        company = await company_service.get_company_details(company_id)
        entries = await self.time_tracking_entry_repo.get_all_entries_for_company(company_id)

        projects_page = await project_service.get_projects(company_id, pagination=None)
        projects = {p.id: p for p in projects_page.data}

        tasks = {}
        task_to_project = {}
        for project in projects.values():
            tasks_page = await task_service.get_tasks(project.id, pagination=None)
            for task in tasks_page.data:
                tasks[task.id] = task
                task_to_project[task.id] = project

        employees = {}
        from app.employee.dal import employee_repo
        all_employees_page = await employee_repo.get_by_company_id(company_id, pagination=None)
        for emp in all_employees_page.data:
            employees[emp.id] = emp

        rows = []
        for entry in entries:
            task = tasks.get(entry.task_id)
            employee = employees.get(entry.employee_id)

            if task and employee:
                project = task_to_project[task.id]
                hours = entry.duration_minutes / 60.0
                salary = hours * employee.salary_per_hour

                rows.append({
                    "company_code": company.code,
                    "project_code": project.code,
                    "task_code": task.code,
                    "task_name": task.name,
                    "employee_display_name": employee.display_name,
                    "created_at": entry.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_minutes": entry.duration_minutes,
                    "salary": round(salary, 2)
                })

        return rows


time_tracking_entry_service = TimeTrackingEntryService(
    TimeTrackingEntryRepo(TimeTrackingEntryCrud(), DataclassSerializer(TimeTrackingEntry))
)
