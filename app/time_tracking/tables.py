from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table

from app.core.database import metadata

time_tracking_entry_table = Table(
    'time_tracking_entry',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('task_id', Integer, ForeignKey('task.id'), nullable=False),
    Column('employee_id', Integer, ForeignKey('employee.id'), nullable=False),
    Column('duration_minutes', Integer, nullable=False),
    Column('created_at', DateTime, nullable=False),
)
