"""루미 동행 통화 : 프롬프트 · 음성 설정을 담은 Realtime 임시 키 발급 (대화 내용은 서버를 거치지 않음)"""
from app.config import settings
from app.schemas import LiveSessionRequest, LiveSessionResponse
from app.services import openai_client, prompts


def _session(req: LiveSessionRequest) -> dict:
    instructions = prompts.load("live_companion").format(
        nickname=req.nickname,
        mission_title=req.missionTitle,
        mission_description=req.missionDescription or "설명 없음",
        place_name=req.placeName or "정해진 곳 없음",
    )
    return {
        "type": "realtime",
        "model": settings.realtime_model,
        "instructions": instructions,
        "max_output_tokens": "inf",
        "audio": {
            "input": {
                # 실시간 자막 · 위기 감지용 (사용자 말 → 글자). 음성 · 자막 모두 서버 저장 없음
                "transcription": {"model": settings.stt_model, "language": "ko"},
                "noise_reduction": {"type": "near_field"},  # 이어폰 마이크 기준
                # 말 끝을 「의미」로 판단 + 느긋하게 → 잠깐 조용하거나 주변 소리에 루미가 끼어들지 않게
                "turn_detection": {
                    "type": "semantic_vad",
                    "eagerness": "low",
                    "create_response": True,
                    "interrupt_response": True,
                },
            },
            "output": {"voice": settings.realtime_voice},
        },
    }


def session(req: LiveSessionRequest) -> LiveSessionResponse:
    """실패하면 AiUnavailable (라우터가 503 으로 → Spring 은 「지금은 통화할 수 없어요」)"""
    secret, expires_at = openai_client.realtime_client_secret(_session(req))
    return LiveSessionResponse(clientSecret=secret, expiresAt=expires_at, model=settings.realtime_model)