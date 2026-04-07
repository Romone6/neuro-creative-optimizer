from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str | None = None
    anthropic_base_url: str | None = None

    openai_api_key: str | None = None
    openai_base_url: str | None = None

    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    local_model_base_url: str = "http://localhost:11434/v1"
    local_model_api_key: str = "local-dev"

    default_analysis_provider: str = "openrouter"
    default_analysis_model: str = "openrouter/auto"
    default_heavy_provider: str = "openai"
    default_heavy_model: str = "gpt-5"
    default_local_provider: str = "local"
    default_local_model: str = "llama3.1"
