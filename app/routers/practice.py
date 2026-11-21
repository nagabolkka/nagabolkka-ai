from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings

from app.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    OpeningResponse,
    ReplyRequest,
    ReplyResponse,
    TranscribeResponse,
)
from app.services import openai_client, practice, scenarios
from app.services.openai_client import AiUnavailable

router = APIRouter(prefix="/ai/practice", tags=["practice"])


@router.get(
    "/scenarios/{code}/opening",
    response_model=OpeningResponse,
    summary="첫 대사 · 선택지",
    description="""
연습 시작에 쓰는 상대역 첫 대사와 선택지 2개를 돌려줍니다.
`scenarios/{code}.yaml` 고정값이라 OpenAI 를 호출하지 않습니다.

`code`: `FIRST_CALL` · `FIRST_VISIT` · `INTERVIEW` (없는 코드 → 404)
""",
)
def opening(code: str):
    sc = scenarios.get(code)
    return OpeningResponse(opening=sc["opening"], choices=sc["choices"])


@router.post(
    "/reply",
    response_model=ReplyResponse,
    summary="상대역 답변",
    description="""
연습 대화에서 사용자 말에 대한 상대역 답변과 다음 선택지를 만듭니다.

- **위기 검사는 Spring 이 `/ai/crisis/check` 로 먼저** 하고, 통과했을 때만 이 API 를 부릅니다.
- `turn` 은 Spring 이 센 이번 턴 번호 (`turn_count + 1`). `turn >= maxTurns` 면 마무리 대사 + `choices: []` + `finished: true`.
- `history` 는 프롬프트에서 지시와 분리된 "대화 내용"으로만 들어갑니다 (프롬프트 인젝션 대비).
- OpenAI 실패 · 응답 형식 오류 → 시나리오별 턴 고정 대사 (`fallback: true`).
""",
)
def reply(req: ReplyRequest):
    return practice.reply(req)


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    summary="연습 피드백",
    description="""
연습 끝에서 대화 전체를 보고 피드백을 만듭니다.

- `good` 1~2개: 사용자가 실제로 한 말을 근거로 "~했어요" 체
- `next` 1개: 다음에 써 볼 문장 그대로
- 지적 · 점수 · 부정 표현 없음
- OpenAI 실패 → 시나리오별 고정 피드백 (`fallback: true`)
""",
)
def feedback(req: FeedbackRequest):
    return practice.feedback(req.scenarioCode, req.history)


# 연습 음성 → 글자
# OpenAI 를 기다리는 동안 다른 요청 (헬스 체크 등) 이 막히지 않게 스레드에서 실행
@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="연습 음성 → 글자",
    description="""
연습 대화에서 사용자가 녹음한 음성을 글자로 바꿉니다. (`multipart/form-data` · 필드 이름 `audio`)

- 2MB 초과 · 빈 파일 → 400
- 파일 · 글자는 저장하지 않고 로그에도 남기지 않습니다.
- OpenAI 실패 → `{"text": null, "fallback": true}` (Spring 은 그대로 null 을 돌려주고, 프론트는 다시 말하기 · 직접 입력 안내)
""",
)
def transcribe(audio: UploadFile = File(...)):
    data = audio.file.read(settings.stt_max_bytes + 1)
    if not data or len(data) > settings.stt_max_bytes:
        raise HTTPException(status_code=400, detail="audio size")
    try:
        text = openai_client.transcribe(data, audio.filename or "voice.webm", audio.content_type or "audio/webm")
        return TranscribeResponse(text=text.strip() or None, fallback=False)
    except AiUnavailable:
        return TranscribeResponse(text=None, fallback=True)