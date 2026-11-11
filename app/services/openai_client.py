"""OpenAI 호출 모음. 실패하면 예외를 던지고, 대체값은 호출한 쪽에서 정한다."""
import json
import logging
from functools import lru_cache

from openai import OpenAI

from app.config import settings

log = logging.getLogger(__name__)


class AiUnavailable(Exception):
    """키 없음 · 타임아웃 · 429 · 응답 형식 오류 등 → 대체값 사용"""


@lru_cache
def _client() -> OpenAI:
    if not settings.openai_api_key:
        raise AiUnavailable("OPENAI_API_KEY 없음")
    # 재시도 없음: Spring 이 3초 안에 답을 받아야 하므로
    return OpenAI(api_key=settings.openai_api_key, max_retries=0)


def moderation_scores(text: str) -> dict[str, float]:
    """self-harm 3개 카테고리 점수"""
    try:
        res = _client().with_options(timeout=settings.moderation_timeout).moderations.create(
            model="omni-moderation-latest", input=text
        )
        s = res.results[0].category_scores
        return {
            "self-harm": s.self_harm,
            "self-harm/intent": s.self_harm_intent,
            "self-harm/instructions": s.self_harm_instructions,
        }
    except AiUnavailable:
        raise
    except Exception as e:  # 타임아웃 · 429 · 네트워크
        log.warning("moderation 실패: %s", type(e).__name__)
        raise AiUnavailable(str(e)) from e


def chat_json(system: str, user: str, max_tokens: int = 300) -> dict:
    """system 지시 + user 데이터 → JSON 객체"""
    try:
        res = _client().with_options(timeout=settings.openai_timeout).chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=max_tokens,
        )
        return json.loads(res.choices[0].message.content or "")
    except AiUnavailable:
        raise
    except Exception as e:
        log.warning("chat 실패: %s", type(e).__name__)
        raise AiUnavailable(str(e)) from e