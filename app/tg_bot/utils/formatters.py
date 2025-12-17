from app.company.models import Company
from app.project.models import Project
from app.employee.models import Employee


def format_company_details(company: Company) -> str:
    return (
        f"<b>Company Details</b>\n\n"
        f"<b>Name:</b> {company.name}\n"
        f"<b>Code:</b> {company.code}\n"
        f"<b>ID:</b> {company.id}"
    )


def format_project_details(project: Project) -> str:
    return (
        f"<b>Project Details</b>\n\n"
        f"<b>Name:</b> {project.name}\n"
        f"<b>Code:</b> {project.code}\n"
        f"<b>Created:</b> {project.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>ID:</b> {project.id}"
    )


def format_employee_details(employee: Employee) -> str:
    status = "✅ Active" if employee.is_active else "❌ Inactive"
    role = "👑 Admin" if employee.is_admin else "👤 Employee"

    return (
        f"<b>Employee Details</b>\n\n"
        f"<b>Display Name:</b> {employee.display_name}\n"
        f"<b>Telegram ID:</b> {employee.telegram_id}\n"
        f"<b>Salary/Hour:</b> ${employee.salary_per_hour:.2f}\n"
        f"<b>Role:</b> {role}\n"
        f"<b>Status:</b> {status}\n"
        f"<b>Created:</b> {employee.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>ID:</b> {employee.id}"
    )
