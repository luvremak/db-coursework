from datetime import datetime

from app.core.serializer import DataclassSerializer
from app.time_tracking.dal import TimeTrackingEntryCrud, TimeTrackingEntryRepo
from app.time_tracking.models import TimeTrackingEntry


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
        return await self.time_tracking_entry_repo.create_and_get(entry)

    async def get_total_minutes_by_task_and_employee(
        self,
        task_id: int,
        employee_id: int,
    ) -> int:
        return await self.time_tracking_entry_repo.get_total_minutes_by_task_and_employee(task_id, employee_id)

    async def get_project_stats_for_company(self, company_id: int) -> list[dict]:
        stats = await self.time_tracking_entry_repo.get_project_stats_for_company(company_id)

        from app.company.services import company_service
        company = await company_service.get_company_details(company_id)

        rows = []
        for stat in stats:
            rows.append(
                {
                    "company_code": company.code,
                    "project_code": stat["project_code"],
                    "total_hours_spent": round(stat["total_minutes"] / 60.0, 2),
                    "total_money_spent": round(stat["total_cost"], 2)
                }
            )
        return rows

    async def get_employee_stats_for_company(self, company_id: int) -> list[dict]:
        stats = await self.time_tracking_entry_repo.get_employee_stats_for_company(company_id)

        from app.company.services import company_service
        company = await company_service.get_company_details(company_id)

        rows = []
        for stat in stats:
            rows.append(
                {
                    "company_code": company.code,
                    "project_code": stat["project_code"],
                    "task_code": stat["task_code"],
                    "task_name": stat["task_name"],
                    "employee_display_name": stat["employee_display_name"],
                    "created_at": stat["created_at"].strftime("%Y-%m-%d %H:%M:%S") if stat["created_at"] else None,
                    "duration_minutes": stat["duration_minutes"],
                    "salary": round(stat["salary_cost"], 2),
                    "employee_total_minutes": stat["employee_total_minutes"]
                }
            )
        return rows


time_tracking_entry_service = TimeTrackingEntryService(
    TimeTrackingEntryRepo(TimeTrackingEntryCrud(), DataclassSerializer(TimeTrackingEntry))
)
