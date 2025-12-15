import os.path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f'{os.path.dirname(__file__)}/../../.env')

    DB_URI: str = "sqlite+aiosqlite:///./database.sqlite"


settings = Settings()  # noqa
