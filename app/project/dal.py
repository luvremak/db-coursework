from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO
from app.project.models import Project
from app.project.tables import project_table


class ProjectCrud(CrudBase[int, DTO]):
    table = project_table


class ProjectRepo(RepoBase[int, Project]):
    crud: ProjectCrud

    def __init__(self, crud: ProjectCrud, serializer: Serializer[Project, DTO]):
        super().__init__(crud, serializer, Project)


project_repo = ProjectRepo(ProjectCrud(), DataclassSerializer(Project))
