from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "local"
    openai_api_key: str = ""
    ai_internal_key: str = "local-dev-key"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
