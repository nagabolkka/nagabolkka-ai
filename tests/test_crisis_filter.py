import pytest

from app.services.crisis_filter import Level, check_rules, normalize

CASES = [
    ("오늘 그냥 죽고 싶었어", Level.CRISIS, "H01"),
    ("죽 고 싶 다", Level.CRISIS, "H01"),
    ("ㅈㄱㅅㄷ", Level.CRISIS, "H01"),
    ("살기 싫어", Level.CRISIS, "H04"),
    ("유서 써놨어", Level.CRISIS, "H08"),
    ("극단적 선택 하고 싶다", Level.CRISIS, "H09"),
    ("사라지고 싶다", Level.CAUTION, "C01"),
    ("내가 없어도 다들 잘 살 거야", Level.CAUTION, "C05"),
    ("창피해서 죽고 싶었음", Level.CAUTION, "D01"),
    ("뉴스에서 자살 얘기 봤어", Level.CAUTION, "C07"),
    ("배고파 죽겠다", Level.NONE, None),
    ("웃겨 죽는 줄", Level.NONE, None),
    ("축구 보다가 자살골 나옴", Level.NONE, None),
    ("번개탄 구이 먹었다", Level.NONE, None),
    ("옥상에서 바람 쐬었다", Level.NONE, None),
    ("한강 걷고 왔다", Level.NONE, None),
    ("목매달고 싶다", Level.CRISIS, "H07"),
    ("취업에 목매고 있어", Level.CAUTION, "C10"),
]


@pytest.mark.parametrize("text,level,rule_id", CASES)
def test_rules(text, level, rule_id):
    result = check_rules(text)
    assert result.level == level
    assert result.rule_id == rule_id


def test_normalize():
    assert normalize("죽.고.싶.어") == "죽고싶어"
    assert normalize("자1살") == "자살"
    assert normalize("싶어어어") == "싶어"


def test_downgrade_does_not_hide_real_crisis():
    # 창피해서 죽고 싶다 + 자살 의도 → 위기 패턴이 우선
    assert check_rules("창피해서 죽고 싶었어 자살하고 싶다").level == Level.CRISIS