from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

INSECURE_SECRET = "change-this-secret-in-production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Azərbaycan HR & Payroll ERP"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg2://hr:hr_secret@localhost:5433/hr_erp"
    SECRET_KEY: str = INSECURE_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    AUTO_SEED: bool = True
    SEED_DEMO: bool = False
    INITIAL_ADMIN_EMAIL: str = "admin@hr.local"
    INITIAL_ADMIN_PASSWORD: str = ""
    INITIAL_ADMIN_NAME: str = "Sistem Administratoru"

    ENABLE_DOCS: bool = True
    CORS_ORIGINS: str = ""
    ALLOWED_HOSTS: str = ""
    MAX_REQUEST_BYTES: int = 2_000_000
    LOGIN_MAX_ATTEMPTS: int = 10
    LOGIN_WINDOW_MINUTES: int = 15

    DEFAULT_ANNUAL_LEAVE_DAYS: int = 21
    DEFAULT_NIGHT_BONUS_PCT: float = 0.20
    DEFAULT_OVERTIME_MULTIPLIER: float = 2.0
    DEFAULT_HOLIDAY_MULTIPLIER: float = 2.0
    DEFAULT_SEVERANCE_MONTHS: float = 1.0
    DEFAULT_LUNCH_BREAK_HOURS: float = 1.0

    TIMEZONE: str = "Asia/Baku"

    @property
    def cors_origins(self) -> list[str]:
        return [value.strip() for value in self.CORS_ORIGINS.split(",") if value.strip()]

    @property
    def allowed_hosts(self) -> list[str]:
        return [value.strip() for value in self.ALLOWED_HOSTS.split(",") if value.strip()]

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if self.ENVIRONMENT.lower() in {"production", "prod"}:
            if self.SECRET_KEY == INSECURE_SECRET or len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "Production üçün SECRET_KEY təyin olunmalı və ən azı 32 simvol olmalıdır"
                )
            if self.SEED_DEMO:
                raise ValueError("Production mühitində SEED_DEMO=false olmalıdır")
        return self


settings = Settings()
