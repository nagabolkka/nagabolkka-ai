from fastapi import APIRouter

from app.schemas import LetterRequest, LetterResponse
from app.services import letter

router = APIRouter(prefix="/ai/letter", tags=["letter"])


@router.post(
    "/weekly",
    response_model=LetterResponse,
    summary="주간 편지 본문",
    description="""
매주 월요일 Spring 배치가 사용자마다 1번 부릅니다. 지난주 통계로 루미의 편지 본문을 만듭니다.

- 숫자 통계 · 지역 · 기분 평균만 받습니다 (회고 · 미션 원문 없음).
- 인사(○○에게) · 서명(루미가)은 앱이 붙이므로 본문에 넣지 않습니다.
- OpenAI 실패 · 형식 오류 · 400자 초과 → 템플릿 (`fallback: true`).
""",
)
def weekly(req: LetterRequest):
    return letter.weekly(req)