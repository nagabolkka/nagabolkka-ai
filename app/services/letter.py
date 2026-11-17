import json
import logging

from app.config import settings
from app.schemas import LetterRequest, LetterResponse
from app.services import openai_client, prompts
from app.services.openai_client import AiUnavailable

log = logging.getLogger(__name__)
MAX_LEN = 400
TOTAL_SLOTS = 25


def _closing(outing_count: int) -> str:
    if outing_count == 0:
        return "이번 주는 조용히 쉬어갔구나. 그것도 괜찮아."
    if outing_count <= 2:
        return "한 걸음 한 걸음이 다 소중했어."
    return "작은 걸음이 모여서 길이 되고 있어."


def template(req: LetterRequest) -> str:
    """OpenAI 실패 · 활동 없는 주. Spring LetterTemplate 과 같은 문장 (바꾸면 같이)"""
    return "\n\n".join([
        f"이번 주엔 {req.outingCount}번 바깥에 다녀왔어. {req.regionName}에 색이 {req.restoration}% 돌아왔고, "
        f"도감엔 조각이 {req.foundSlots}개 모였어.",
        "무리하지 않고 네 속도로 걸어온 게 느껴져.",
        _closing(req.outingCount),
    ])


def weekly(req: LetterRequest) -> LetterResponse:
    try:
        data = json.dumps(req.model_dump(), ensure_ascii=False)
        out = openai_client.chat_json(prompts.load("weekly_letter").format(), data, max_tokens=500,
                                      timeout=settings.letter_timeout)
        body = str(out["body"]).strip()
        if not body or len(body) > MAX_LEN:
            raise ValueError("본문 길이")
        return LetterResponse(body=body, fallback=False)
    except (AiUnavailable, KeyError, TypeError, ValueError) as e:
        log.info("주간 편지 템플릿 사용 (%s)", type(e).__name__)
        return LetterResponse(body=template(req)[:MAX_LEN], fallback=True)