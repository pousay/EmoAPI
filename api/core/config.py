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

    REFRESH_TOKEN_EXPIRE_DAYS: int
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    RATE_LIMITER_ENABLED: bool
    RATE_LIMITER_PER_MINUTE: int
    model_config = SettingsConfigDict(env_file=env_file)


config = Config()

__all__ = ["config"]
