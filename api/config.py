import os
from functools import lru_cache


class Config:
    """Base application configuration."""

    ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = ENV == "development"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+psycopg://sidequest:sidequest@db:5432/sidequest"
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # MinIO Configuration
    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ACCESS_KEY", "sidequest")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_SECRET_KEY", "sidequest123")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET_NAME: str = os.getenv("MINIO_BUCKET_NAME", "sidequest-media")

    KEYN_AUTH_SERVER_URL: str = os.getenv("KEYN_AUTH_SERVER_URL", "https://auth.keyn.bynolo.ca")
    KEYN_JWKS_URL: str | None = os.getenv("KEYN_JWKS_URL")
    KEYN_CLIENT_ID: str | None = os.getenv("KEYN_CLIENT_ID")
    KEYN_CLIENT_SECRET: str | None = os.getenv("KEYN_CLIENT_SECRET")
    KEYN_REDIRECT_URI: str | None = os.getenv("KEYN_REDIRECT_URI")
    COOKIE_NAME: str = os.getenv("COOKIE_NAME", "sq_session")

    VAPID_PUBLIC_KEY: str | None = os.getenv("VAPID_PUBLIC_KEY")
    VAPID_PRIVATE_KEY: str | None = os.getenv("VAPID_PRIVATE_KEY")
    VAPID_SUBJECT: str | None = os.getenv("VAPID_SUBJECT")

    PREFERRED_URL_SCHEME: str = os.getenv("PREFERRED_URL_SCHEME", "https")


@lru_cache
def get_config() -> Config:
    return Config()
