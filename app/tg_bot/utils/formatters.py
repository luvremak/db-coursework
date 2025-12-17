from app.company.models import Company
from app.project.models import Project
from app.employee.models import Employee
from app.task.models import Task


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


def format_task_status(status: str) -> str:
    status_emoji = {
        "new": "🆕",
        "in_progress": "⚙️",
        "review": "👀",
        "done": "✅",
        "canceled": "❌"
    }
    status_labels = {
        "new": "New",
        "in_progress": "In Progress",
        "review": "Review",
        "done": "Done",
        "canceled": "Canceled"
    }
    emoji = status_emoji.get(status, "")
    label = status_labels.get(status, status)
    return f"{emoji} {label}"


def format_tracked_time(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} min"
    else:
        hours = minutes / 60
        return f"{hours:.1f} hours"


def format_task_details(task: Task, tracked_minutes: int = 0) -> str:
    tracked_time_line = ""
    if tracked_minutes > 0:
        tracked_time_line = f"<b>Time tracked:</b> {format_tracked_time(tracked_minutes)}\n"

    return (
        f"<b>Task #{task.code}</b>\n\n"
        f"<b>Name:</b> {task.name}\n"
        f"<b>Description:</b> {task.description}\n"
        f"<b>Status:</b> {format_task_status(task.status)}\n"
        f"<b>Deadline:</b> {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>Assignee ID:</b> {task.assignee_user_id}\n"
        f"{tracked_time_line}"
        f"<b>Created:</b> {task.created_at.strftime('%Y-%m-%d %H:%M')}\n"
        f"<b>ID:</b> {task.id}"
    )
