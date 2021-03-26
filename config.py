from pydantic import BaseSettings


class Settings(BaseSettings):
    SERVICE_CERT: str
    BIG_QUERY_CERT: str

    class Config:
        env_file = ".env"
