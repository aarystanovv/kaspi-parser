from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: int = Field(5432, alias="DB_PORT")
    db_name: str = Field("kaspi", alias="DB_NAME")
    db_user: str = Field("postgres", alias="DB_USER")
    db_password: str = Field("postgres", alias="DB_PASSWORD")

    app_env: str = Field("development", alias="APP_ENV")
    log_level: str = Field("info", alias="LOG_LEVEL")
    scheduler_enabled: bool = Field(False, alias="SCHEDULER_ENABLED")
    export_dir: str = Field("export", alias="EXPORT_DIR")
    log_dir: str = Field("logs", alias="LOG_DIR")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()
