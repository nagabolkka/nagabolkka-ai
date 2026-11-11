from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "local"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_timeout: float = 2.5       # Spring AiClient 타임아웃(3초)보다 짧게
    moderation_timeout: float = 2.0
    ai_internal_key: str = "local-dev-key"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()