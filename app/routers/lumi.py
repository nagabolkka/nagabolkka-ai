from fastapi import APIRouter

from app.schemas import LumiRequest, LumiResponse
from app.services import lumi

router = APIRouter(prefix="/ai/lumi", tags=["lumi"])


@router.post(
    "/message",
    response_model=LumiResponse,
    summary="루미 한마디",
    description="""
퀘스트 완료 후 루미가 건네는 한마디를 만듭니다. 최대 200자 (`quest_records.lumi_message`).

- `reflection` 은 **위기 검사를 통과한 회고만** 보냅니다 (위기면 `null`).
- 회고가 있으면 짧게 인용해 공감, 없으면 미션 · 기분으로.
- OpenAI 실패 → 템플릿 문장 (`fallback: true`).
""",
)
def message(req: LumiRequest):
    return lumi.message(req)