from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, BigInteger, CheckConstraint

from app.core.database import metadata
from app.task.models import TaskStatus

task_table = Table(
    'task',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('project.id', ondelete='CASCADE'), nullable=False),
    Column('name', String, nullable=False),
    Column('code', Integer, nullable=False),
    Column('description', String, nullable=False),
    Column('deadline', DateTime, nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('assignee_user_id', BigInteger, nullable=False),
    Column('status', String, nullable=False, server_default=TaskStatus.NEW.value),
    CheckConstraint(
        f"status IN ('{TaskStatus.NEW.value}', '{TaskStatus.IN_PROGRESS.value}', '{TaskStatus.REVIEW.value}', '{TaskStatus.DONE.value}', '{TaskStatus.CANCELED.value}')",
        name='task_status_check'
    ),
)
