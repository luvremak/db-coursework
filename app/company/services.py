from app.company.dal import CompanyRepo


class CompanyService:
    def __init__(self, company_repo: CompanyRepo):
        self.company_repo = company_repo
