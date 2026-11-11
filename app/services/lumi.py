import json
import logging

from app.schemas import LumiRequest, LumiResponse
from app.services import openai_client, prompts
from app.services.openai_client import AiUnavailable

log = logging.getLogger(__name__)
MAX_LEN = 200 


def template(req: LumiRequest) -> str:
    if req.reflection:
        quote = req.reflection if len(req.reflection) <= 20 else req.reflection[:20] + "…"
        return f'"{quote}" ㅡ 그 말 기억할게. 네가 가져온 {req.pieceName} 덕분에 {req.restoreText}!'
    return f"오늘도 다녀와 줘서 고마워. 네가 가져온 {req.pieceName} 덕분에 {req.restoreText}!"


def message(req: LumiRequest) -> LumiResponse:
    try:
        data = json.dumps(req.model_dump(), ensure_ascii=False)
        out = openai_client.chat_json(prompts.load("lumi_message").format(), data, max_tokens=200)
        text = str(out["message"]).strip()
        if not text:
            raise ValueError("빈 메시지")
        return LumiResponse(message=text[:MAX_LEN], fallback=False)
    except (AiUnavailable, KeyError, TypeError, ValueError) as e:
        log.info("루미 한마디 템플릿 사용 (%s)", type(e).__name__)
        return LumiResponse(message=template(req)[:MAX_LEN], fallback=True)