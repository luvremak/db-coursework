from app.employee.dal import EmployeeRepo, employee_repo


class EmployeeService:
    def __init__(self, employee_repo: EmployeeRepo):
        self.employee_repo = employee_repo


employee_service = EmployeeService(employee_repo)
