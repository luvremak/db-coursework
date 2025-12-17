from app.project.dal import ProjectRepo, project_repo


class ProjectService:
    def __init__(self, project_repo: ProjectRepo):
        self.project_repo = project_repo


project_service = ProjectService(project_repo)
