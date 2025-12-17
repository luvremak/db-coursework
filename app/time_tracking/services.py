from app.time_tracking.dal import TimeTrackingEntryRepo, time_tracking_entry_repo


class TimeTrackingEntryService:
    def __init__(self, time_tracking_entry_repo: TimeTrackingEntryRepo):
        self.time_tracking_entry_repo = time_tracking_entry_repo


time_tracking_entry_service = TimeTrackingEntryService(time_tracking_entry_repo)
