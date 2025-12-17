from databases import Database
from sqlalchemy import MetaData

from app.core.settings import settings

metadata = MetaData()

database = Database(settings.DB_URI)
