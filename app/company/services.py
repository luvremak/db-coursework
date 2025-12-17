from app.company.dal import CompanyCrud, CompanyRepo
from app.company.models import Company
from app.core.serializer import DataclassSerializer


class CompanyService:
    def __init__(self, company_repo: CompanyRepo):
        self.company_repo = company_repo


company_service = CompanyService(CompanyRepo(CompanyCrud(), DataclassSerializer(Company)))
