from app.project.dal import ProjectRepo


class ProjectService:
    def __init__(self, project_repo: ProjectRepo):
        self.project_repo = project_repo
