from app.employee.dal import EmployeeCrud, EmployeeRepo
from app.employee.models import Employee
from app.core.serializer import DataclassSerializer


class EmployeeService:
    def __init__(self, employee_repo: EmployeeRepo):
        self.employee_repo = employee_repo


employee_service = EmployeeService(EmployeeRepo(EmployeeCrud(), DataclassSerializer(Employee)))
