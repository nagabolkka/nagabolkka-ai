import json
import logging

from app.schemas import Feedback, FeedbackResponse, ReplyRequest, ReplyResponse
from app.services import openai_client, prompts, scenarios
from app.services.openai_client import AiUnavailable

log = logging.getLogger(__name__)

REPLY_MAX = 120
CHOICE_MAX = 40
FEEDBACK_MAX = 60


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {x}" for x in items)


def _flow_text(sc: dict) -> str:
    lines = [f"0. 상대: {sc['opening']}"]
    for t in sc["flow"]:
        lines.append(f"{t['turn']}. 상대: {t['reply']}")
    return "\n".join(lines)


def _history_json(history, **extra) -> str:
    data = {"history": [h.model_dump() for h in history], **extra}
    return json.dumps(data, ensure_ascii=False)


def reply(req: ReplyRequest) -> ReplyResponse:
    sc = scenarios.get(req.scenarioCode)
    last = req.turn >= req.maxTurns

    turn_rule = (
        "- 이번이 마지막 턴이다. 대화를 자연스럽게 마무리하는 인사를 하고, choices 는 빈 배열 [] 로 둔다."
        if last
        else "- 대화를 이어갈 수 있게 답하고, choices 는 정확히 2개."
    )
    system = prompts.load("practice_reply").format(
        partner_role=sc["partner_role"],
        persona=sc["persona"],
        goal=sc["goal"],
        background=_bullets(sc["background"]),
        flow=_flow_text(sc),
        extra_rules=_bullets(sc["extra_rules"]) + "\n" if sc["extra_rules"] else "",
        max_turns=req.maxTurns,
        turn=req.turn,
        turn_rule=turn_rule,
    )
    user = _history_json(req.history, message=req.message)

    try:
        out = openai_client.chat_json(system, user, max_tokens=250)
        text = str(out["reply"]).strip()
        choices = [] if last else [str(c).strip() for c in out["choices"]][:2]
        if not text or len(text) > REPLY_MAX:
            raise ValueError("reply 길이")
        if not last and (len(choices) != 2 or any(not c or len(c) > CHOICE_MAX for c in choices)):
            raise ValueError("choices 형식")
        return ReplyResponse(reply=text, choices=choices, finished=last, fallback=False)
    except (AiUnavailable, KeyError, TypeError, ValueError) as e:
        log.info("연습 답변 고정 대사 사용 (%s)", type(e).__name__)
        fb = scenarios.fallback_turn(sc, req.turn, req.maxTurns)
        return ReplyResponse(
            reply=fb["reply"], choices=[] if last else fb["choices"], finished=last, fallback=True
        )


def feedback(scenario_code: str, history) -> FeedbackResponse:
    sc = scenarios.get(scenario_code)
    system = prompts.load("practice_feedback").format(
        title=sc["title"],
        partner_role=sc["partner_role"],
        goal=sc["goal"],
        examples=_bullets(sc["feedback_examples"]),
    )
    try:
        out = openai_client.chat_json(system, _history_json(history), max_tokens=250)
        good = [str(x).strip() for x in out["good"] if str(x).strip()][:2]
        nxt = [str(x).strip() for x in out["next"] if str(x).strip()][:1]
        if not good or not nxt or any(len(x) > FEEDBACK_MAX for x in good + nxt):
            raise ValueError("피드백 형식")
        return FeedbackResponse(feedback=Feedback(good=good, next=nxt), fallback=False)
    except (AiUnavailable, KeyError, TypeError, ValueError) as e:
        log.info("고정 피드백 사용 (%s)", type(e).__name__)
        return FeedbackResponse(feedback=Feedback(**sc["fallback_feedback"]), fallback=True)