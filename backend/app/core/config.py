from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

RAIZ_PROYECTO = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=RAIZ_PROYECTO / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Plataforma DDRR-Catastro"
    environment: str = "development"

    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    redis_url: str = "redis://localhost:6379/0"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    secret_key: str
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    inactivity_minutes: int = 10
    preauth_minutes: int = 5
    reto_minutes: int = 5

    webauthn_rp_id: str = "localhost"
    webauthn_rp_name: str = "Plataforma DDRR-Catastro"

    login_max_intentos_usuario: int = 5
    login_max_intentos_ip: int = 20
    login_ventana_minutos: int = 15

    max_upload_mb: int = 20
    storage_dir: Path = RAIZ_PROYECTO / "storage"
    frontend_origin: str = "http://localhost:5173"

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def cookie_secure(self) -> bool:
        # En desarrollo (http://localhost) la cookie no puede ser Secure;
        # en cualquier otro entorno sí (R-SEG-3).
        return self.environment != "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
