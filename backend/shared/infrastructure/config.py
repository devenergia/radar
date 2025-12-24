"""Configuracoes da aplicacao usando Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracoes da aplicacao carregadas de variaveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="PRD_RADAR_",
        case_sensitive=False,
        extra="ignore",
    )

    # Ambiente
    environment: Literal["development", "staging", "production"] = "development"
    app_name: str = "radar-api"
    app_version: str = "1.0.0"

    # Servidor
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    debug: bool = False

    # Banco de Dados Oracle
    oracle_user: str = Field(..., description="Usuario do banco de dados Oracle")
    oracle_password: str = Field(default="", description="Senha do banco de dados Oracle")
    oracle_dsn: str = Field(..., description="DSN de conexao Oracle (//host:port/service)")
    oracle_schema: str = Field(default="RADAR", description="Schema Oracle")

    # Pool de conexoes
    pool_min: int = Field(default=2, ge=1)
    pool_max: int = Field(default=10, ge=1)
    pool_increment: int = Field(default=1, ge=1)
    pool_timeout: int = Field(default=60, ge=1)

    # Autenticacao
    api_key: str = Field(..., description="Chave de API para autenticacao")
    allowed_ips: str = Field(
        default="*", description="IPs permitidos (separados por virgula)"
    )

    # IP Whitelist - redes adicionais para dev/test (CIDRs separados por virgula)
    ip_whitelist_extra: str | None = Field(
        default=None,
        description="CIDRs adicionais para whitelist (ex: 10.0.0.0/8,192.168.0.0/16)",
    )

    # Cache
    cache_ttl_seconds: int = Field(default=300, ge=1)
    cache_stale_ttl_seconds: int = Field(default=3600, ge=1)
    cache_max_items: int = Field(default=1000, ge=1)

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "console"] = "json"

    # Metricas
    metrics_enabled: bool = True

    # CORS
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        description="Origens CORS permitidas (separadas por virgula)",
    )

    # Email
    email_indisponibilidade: str = "radar@roraimaenergia.com.br"

    @property
    def is_development(self) -> bool:
        """Verifica se esta em ambiente de desenvolvimento."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Verifica se esta em ambiente de producao."""
        return self.environment == "production"

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de origens CORS."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def allowed_ips_list(self) -> list[str]:
        """Retorna lista de IPs permitidos."""
        if self.allowed_ips == "*":
            return ["*"]
        return [ip.strip() for ip in self.allowed_ips.split(",")]


@lru_cache
def get_settings() -> Settings:
    """
    Retorna instancia singleton das configuracoes.

    Usa cache para evitar recarregar do .env a cada chamada.
    """
    return Settings()
