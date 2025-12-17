from app.company.models import Company


def format_company_details(company: Company) -> str:
    return (
        f"<b>Company Details</b>\n\n"
        f"<b>Name:</b> {company.name}\n"
        f"<b>Code:</b> {company.code}\n"
        f"<b>ID:</b> {company.id}"
    )
