from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table

from app.core.database import metadata

project_table = Table(
    'project',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('company_id', Integer, ForeignKey('company.id'), nullable=False),
    Column('name', String, nullable=False),
    Column('code', String(3), unique=True, nullable=False),
    Column('created_at', DateTime, nullable=False),
)
