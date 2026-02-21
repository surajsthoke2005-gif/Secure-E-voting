from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Secure E-Voting"
    secret_key: str = "replace-with-long-random-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/secure_voting"
    fernet_key: str = "replace-with-generated-fernet-key"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_sender: str = "noreply@secure-vote.local"
    election_start: str = "2026-01-01T08:00:00"
    election_end: str = "2026-01-01T20:00:00"
    csrf_secret: str = "replace-with-csrf-secret"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
