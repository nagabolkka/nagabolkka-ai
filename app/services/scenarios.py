from pathlib import Path

import yaml
from fastapi import HTTPException

SCENARIO_DIR = Path(__file__).resolve().parents[2] / "scenarios"

SCENARIOS: dict[str, dict] = {
    p.stem: yaml.safe_load(p.read_text(encoding="utf-8"))
    for p in sorted(SCENARIO_DIR.glob("*.yaml"))
}


def get(code: str) -> dict:
    if code not in SCENARIOS:
        raise HTTPException(status_code=404, detail=f"unknown scenario {code}")
    return SCENARIOS[code]


def fallback_turn(sc: dict, turn: int, max_turns: int) -> dict:
    """턴별 고정 대사. 마지막 턴은 항상 마무리 대사"""
    lines = sc["fallback"]
    if turn >= max_turns:
        return lines[-1]
    return lines[min(turn, len(lines)) - 1]