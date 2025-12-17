from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Table

from app.core.database import metadata

employee_table = Table(
    'employee',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('telegram_id', Integer, nullable=False),
    Column('company_id', Integer, ForeignKey('company.id'), nullable=False),
    Column('is_active', Boolean, nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('salary_per_hour', Float, nullable=False),
    Column('display_name', String, nullable=False),
)
