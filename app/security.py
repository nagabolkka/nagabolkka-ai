import secrets

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

from app.config import settings

internal_key_header = APIKeyHeader(
    name="X-Internal-Key",
    auto_error=False,
    description="Spring 과 약속한 내부 키 (로컬: local-dev-key)",
)


def verify_internal_key(key: str | None = Security(internal_key_header)):
    """Spring 이 보내는 X-Internal-Key 헤더 확인 (외부 호출 차단)"""
    if not secrets.compare_digest(key or "", settings.ai_internal_key):
        raise HTTPException(status_code=401, detail="invalid internal key")