from sqlalchemy import Column, Integer, String, Table

from app.core.database import metadata

company_table = Table(
    'company',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
)
