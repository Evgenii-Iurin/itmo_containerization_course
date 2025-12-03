from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator, Field
from typing import Literal
from abc import ABC

class BaseModelConfig(BaseSettings, ABC):
    """Base model configuration with common fields."""
    
    model: str
    temperature: float = 0.5
    max_tokens: int | None = None
    
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )


class OpenAIConfig(BaseModelConfig):
    """OpenAI model configuration."""
    
    openai_api_key: str
    temperature: float
    model: str

    model_config = SettingsConfigDict(
        env_file=".env.openai_model",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class GigachatConfig(BaseModelConfig):
    """GigaChat model configuration."""
    
    gigachat_api_key: str
    gigachat_credentials: str  # Path to credentials file or credentials string
    model: str = "GigaChat-Pro"

    model_config = SettingsConfigDict(
        env_file=".env.gigachat_model",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class Settings(BaseSettings):
    """Application settings."""

    service_name: str = "router"
    log_level: str = "INFO"

    llm_model_timeout: int = 120  # Longer timeout for generation
    
    model_provider: Literal["openai", "gigachat"] = "openai"

    llm_model: BaseModelConfig | None = Field(default=None, validation_alias=None)
    
    postgres_user: str = "booking_user"
    postgres_password: str = "booking_password"
    postgres_db: str = "beauty_booking"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    @property
    def database_url(self) -> str:
        """Construct PostgreSQL connection URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    @model_validator(mode="after")
    def load_model_config(self):
        """Load the appropriate model config based on model_provider."""
        if self.llm_model is None:
            if self.model_provider == "openai":
                self.llm_model = OpenAIConfig()
            elif self.model_provider == "gigachat":
                self.llm_model = GigachatConfig()
            else:
                raise ValueError(f"Unknown model provider: {self.model_provider}")
        return self



settings = Settings()
