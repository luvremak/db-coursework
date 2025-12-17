from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO
from app.company.models import Company
from app.company.tables import company_table


class CompanyCrud(CrudBase[int, DTO]):
    table = company_table


class CompanyRepo(RepoBase[int, Company]):
    crud: CompanyCrud

    def __init__(self, crud: CompanyCrud, serializer: Serializer[Company, DTO]):
        super().__init__(crud, serializer, Company)


company_repo = CompanyRepo(CompanyCrud(), DataclassSerializer(Company))
