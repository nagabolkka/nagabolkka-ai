from fastapi import Depends, FastAPI

from app.config import settings
from app.routers import crisis, lumi, practice
from app.security import verify_internal_key

if settings.env == "prod" and settings.ai_internal_key in ("", "local-dev-key"):
    raise RuntimeError("운영에서는 AI_INTERNAL_KEY 를 꼭 바꿔야 해요 (32자 이상 권장)")

TAGS = [
    {"name": "crisis", "description": "위기 표현 감지 (회고 · 연습 메시지)"},
    {"name": "practice", "description": "연습실 상대역 대화 · 피드백"},
    {"name": "lumi", "description": "퀘스트 완료 후 루미 한마디"},
    {"name": "health", "description": "서버 상태 확인 (키 없이 호출 가능)"},
]

app = FastAPI(
    title="나가볼까 AI 서버",
    description="Spring (nagabolkka-be) 전용 내부 API. `/ai/health` 를 뺀 모든 요청에 **X-Internal-Key** 헤더가 필요합니다.",
    openapi_tags=TAGS,
    docs_url=None if settings.env == "prod" else "/docs",
    redoc_url=None,
    openapi_url=None if settings.env == "prod" else "/openapi.json",
)

# 헬스 체크만 키 없이, 나머지는 모두 X-Internal-Key 필요
protected = [Depends(verify_internal_key)]
app.include_router(crisis.router, dependencies=protected)
app.include_router(practice.router, dependencies=protected)
app.include_router(lumi.router, dependencies=protected)


@app.get("/ai/health", tags=["health"], summary="서버 상태 확인")
def health():
    return {"status": "ok"}