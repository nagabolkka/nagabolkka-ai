from fastapi import APIRouter

from app.schemas import CrisisCheckRequest, CrisisCheckResponse
from app.services import crisis_service

router = APIRouter(prefix="/ai/crisis", tags=["crisis"])


@router.post(
    "/check",
    response_model=CrisisCheckResponse,
    summary="위기 표현 검사",
    description="""
회고 · 연습 메시지에 위기 표현이 있는지 검사합니다.

**순서**: 정규화 → 예외 표현 제거 → 위기 패턴 → 주의 패턴 → OpenAI Moderation

| 결과 | 조건 |
|---|---|
| 위기 (`RULE`) | 위기 패턴 매치 · 또는 주의 패턴 + Moderation 실패 (안전 우선) |
| 위기 (`MODERATION`) | 주의 패턴 + 점수 ≥ 0.3 · 또는 패턴 없음 + intent/instructions ≥ 0.5, self-harm ≥ 0.7 |
| 통과 | 그 외 (주의 패턴만 걸리면 `ruleId` 는 채워서 돌려줌) |

원문은 로그에 남기지 않습니다. `crisis_events` 기록은 Spring 이 합니다.
""",
)
def check(req: CrisisCheckRequest):
    return crisis_service.check(req.text)