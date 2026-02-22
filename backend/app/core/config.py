from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "GreenOS"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://greenos:greenos_dev@db:5432/greenos"
    DATABASE_URL_SYNC: str = "postgresql://greenos:greenos_dev@db:5432/greenos"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # MQTT
    MQTT_HOST: str = "mqtt"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str | None = None
    MQTT_PASSWORD: str | None = None

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"


settings = Settings()
