from app.company.dal import CompanyRepo, company_repo


class CompanyService:
    def __init__(self, company_repo: CompanyRepo):
        self.company_repo = company_repo


company_service = CompanyService(company_repo)
