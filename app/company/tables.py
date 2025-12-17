from sqlalchemy import Column, Integer, String, Table

from app.core.database import metadata

company_table = Table(
    'company',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, nullable=False),
    Column('code', String(3), unique=True, nullable=False),
    Column('owner_tg_id', Integer, nullable=False),
)
