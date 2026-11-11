"""위기 감지 전체 흐름: 규칙 → Moderation (「위기 표현 목록」 1 · 6장)"""
from app.schemas import CrisisCheckResponse
from app.services import openai_client
from app.services.crisis_filter import Level, check_rules

CATEGORIES = ("self-harm/intent", "self-harm/instructions", "self-harm")
# 패턴이 없을 때 기준 (초기값, 테스트 문장으로 조정)
STRICT = {"self-harm/intent": 0.5, "self-harm/instructions": 0.5, "self-harm": 0.7}
# 주의 패턴이 있을 때 기준
LOOSE = 0.3


def check(text: str) -> CrisisCheckResponse:
    rule = check_rules(text)

    # ③ 위기 패턴 → Moderation 호출 없이 바로 위기
    if rule.level == Level.CRISIS:
        return CrisisCheckResponse(crisis=True, method="RULE", ruleId=rule.rule_id)

    caution = rule.level == Level.CAUTION
    try:
        scores = openai_client.moderation_scores(text)
    except openai_client.AiUnavailable:
        # Moderation 실패 → 안전 우선: 주의 패턴이 있으면 위기
        if caution:
            return CrisisCheckResponse(crisis=True, method="RULE", ruleId=rule.rule_id)
        return CrisisCheckResponse(crisis=False, ruleId=None)

    for cat in CATEGORIES:
        limit = LOOSE if caution else STRICT[cat]
        if scores.get(cat, 0.0) >= limit:
            return CrisisCheckResponse(
                crisis=True, method="MODERATION", ruleId=rule.rule_id, category=cat
            )

    # 통과 (주의 패턴만 걸린 경우 ruleId 를 돌려줘서 Spring 이 ID 만 로그로 남길 수 있게)
    return CrisisCheckResponse(crisis=False, ruleId=rule.rule_id)