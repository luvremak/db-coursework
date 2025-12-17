from app.company.models import Company
from app.project.models import Project


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
