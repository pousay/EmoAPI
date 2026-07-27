from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

env_file = Path(__file__).parent.parent.parent / ".env"
print("LOADING ENV FROM : ", env_file)


class Config(BaseSettings):
    PORT: int
    HOST: str
    DB_PATH: str

    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(env_file=env_file)


config = Config()

__all__ = ["config"]
