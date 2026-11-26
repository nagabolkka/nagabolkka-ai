from fastapi import APIRouter, HTTPException

from app.schemas import LiveSessionRequest, LiveSessionResponse
from app.services import live
from app.services.openai_client import AiUnavailable

router = APIRouter(prefix="/ai/live", tags=["live"])


@router.post(
    "/session",
    response_model=LiveSessionResponse,
    summary="루미 동행 통화 임시 키",
    description="""
외출 중 루미와 이어폰으로 통화할 수 있도록 OpenAI Realtime **임시 키**를 발급합니다.

- 브라우저가 이 키로 OpenAI 에 WebRTC 로 **직접** 연결 → 음성 · 대화는 우리 서버를 거치지 않음
- 루미 동행 프롬프트 · 목소리 · 실시간 자막(사용자 말) 설정이 키에 담겨 있음
- 키는 60초 안에 연결을 시작할 때만 유효 (통화 시간 제한은 앱에서)
- OpenAI 실패 · 키 없음 → **503** (대체값 없음)
""",
    responses={503: {"description": "OpenAI 실패 · 키 없음"}},
)
def create_session(req: LiveSessionRequest):
    try:
        return live.session(req)
    except AiUnavailable:
        raise HTTPException(status_code=503, detail="live session unavailable")