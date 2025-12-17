from app.employee.dal import EmployeeRepo


class EmployeeService:
    def __init__(self, employee_repo: EmployeeRepo):
        self.employee_repo = employee_repo
