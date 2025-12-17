from app.core.crud_base import CrudBase
from app.core.repo_base import RepoBase
from app.core.serializer import Serializer, DataclassSerializer
from app.core.types import DTO
from app.time_tracking.models import TimeTrackingEntry
from app.time_tracking.tables import time_tracking_entry_table


class TimeTrackingEntryCrud(CrudBase[int, DTO]):
    table = time_tracking_entry_table


class TimeTrackingEntryRepo(RepoBase[int, TimeTrackingEntry]):
    crud: TimeTrackingEntryCrud

    def __init__(self, crud: TimeTrackingEntryCrud, serializer: Serializer[TimeTrackingEntry, DTO]):
        super().__init__(crud, serializer, TimeTrackingEntry)


time_tracking_entry_repo = TimeTrackingEntryRepo(TimeTrackingEntryCrud(), DataclassSerializer(TimeTrackingEntry))
