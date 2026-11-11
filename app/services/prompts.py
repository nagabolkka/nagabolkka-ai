from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parents[2] / "prompts"
_cache: dict[str, str] = {}


def load(name: str) -> str:
    if name not in _cache:
        _cache[name] = (PROMPT_DIR / f"{name}.txt").read_text(encoding="utf-8")
    return _cache[name]