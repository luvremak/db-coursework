from app.time_tracking.dal import TimeTrackingEntryRepo


class TimeTrackingEntryService:
    def __init__(self, time_tracking_entry_repo: TimeTrackingEntryRepo):
        self.time_tracking_entry_repo = time_tracking_entry_repo
