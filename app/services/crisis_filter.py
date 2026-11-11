"""1차 위기 감지: 정규식 규칙 (OpenAI 없이 동작)"""
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml

PATTERN_FILE = Path(__file__).resolve().parents[2] / "crisis" / "patterns.yaml"


class Level(str, Enum):
    CRISIS = "CRISIS"    # 위기 패턴 → 바로 위기
    CAUTION = "CAUTION"  # 주의 패턴 → Moderation 이 판단
    NONE = "NONE"        # 통과


@dataclass(frozen=True)
class RuleResult:
    level: Level
    rule_id: str | None = None


def _load(section: list[dict]) -> list[tuple[str, re.Pattern]]:
    return [(p["id"], re.compile(p["pattern"])) for p in section]


_raw = yaml.safe_load(PATTERN_FILE.read_text(encoding="utf-8"))
EXCEPTIONS = _load(_raw["exceptions"])
DOWNGRADES = _load(_raw["downgrades"])
HIGH = _load(_raw["high"])
CAUTION = _load(_raw["caution"])

_NOT_ALLOWED = re.compile(r"[^가-힣ㄱ-ㅎㅏ-ㅣa-z]")  # 한글 · 자음/모음 · 영문만 남김
_REPEAT = re.compile(r"(.)\1{2,}")                 # 같은 글자 3번 이상 → 1번


def normalize(text: str) -> str:
    text = text.lower()
    text = _NOT_ALLOWED.sub("", text)
    return _REPEAT.sub(r"\1", text)


def _first_match(text: str, patterns) -> str | None:
    for rule_id, pattern in patterns:
        if pattern.search(text):
            return rule_id
    return None


def check_rules(text: str) -> RuleResult:
    t = normalize(text)

    # ① 예외 표현 지우기
    for _, pattern in EXCEPTIONS:
        t = pattern.sub("", t)

    # ② 위기 → 주의로 낮출 표현은 지워 두고 기억
    downgraded = None
    for rule_id, pattern in DOWNGRADES:
        if pattern.search(t):
            downgraded = downgraded or rule_id
            t = pattern.sub("", t)

    # ③ 위기
    if rule_id := _first_match(t, HIGH):
        return RuleResult(Level.CRISIS, rule_id)

    # ④ 주의
    if downgraded:
        return RuleResult(Level.CAUTION, downgraded)
    if rule_id := _first_match(t, CAUTION):
        return RuleResult(Level.CAUTION, rule_id)

    return RuleResult(Level.NONE)