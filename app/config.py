from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "local"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_timeout: float = 4.0      
    moderation_timeout: float = 3.0
    ai_internal_key: str = "local-dev-key"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()