from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "local"
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_timeout: float = 4.0     
    letter_timeout: float = 15.0 
    moderation_timeout: float = 3.0
    stt_model: str = "gpt-4o-mini-transcribe" 
    stt_timeout: float = 8.0                 
    stt_max_bytes: int = 2 * 1024 * 1024      
    # 루미 동행 통화 (Realtime · 브라우저가 WebRTC 로 OpenAI 에 직접 연결 · 우리는 임시 키만 발급)
    realtime_model: str = "gpt-realtime-2.1-mini"
    realtime_voice: str = "marin"
    realtime_key_seconds: int = 60      # 임시 키는 연결을 시작할 때만 쓰임 (통화 길이와 무관)
    realtime_timeout: float = 5.0
    ai_internal_key: str = "local-dev-key"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()