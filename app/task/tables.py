from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table

from app.core.database import metadata

task_table = Table(
    'task',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('project_id', Integer, ForeignKey('project.id'), nullable=False),
    Column('name', String, nullable=False),
    Column('code', String, unique=True, nullable=False),
    Column('description', String, nullable=False),
    Column('deadline', DateTime, nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('assignee_user_id', Integer, nullable=False),
)
