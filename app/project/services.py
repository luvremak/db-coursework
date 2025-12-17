from app.project.dal import ProjectCrud, ProjectRepo
from app.project.models import Project
from app.core.serializer import DataclassSerializer


class ProjectService:
    def __init__(self, project_repo: ProjectRepo):
        self.project_repo = project_repo


project_service = ProjectService(ProjectRepo(ProjectCrud(), DataclassSerializer(Project)))
