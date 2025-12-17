from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO
from app.employee.models import Employee
from app.employee.tables import employee_table


class EmployeeCrud(CrudBase[int, DTO]):
    table = employee_table


class EmployeeRepo(RepoBase[int, Employee]):
    crud: EmployeeCrud

    def __init__(self, crud: EmployeeCrud, serializer: Serializer[Employee, DTO]):
        super().__init__(crud, serializer, Employee)


employee_repo = EmployeeRepo(EmployeeCrud(), DataclassSerializer(Employee))
