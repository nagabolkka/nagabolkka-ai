from app.config import settings
from app.services import openai_client

URL = "/ai/live/session"
BODY = {"nickname": "윤지", "missionTitle": "집 앞 놀이터 벤치까지 10분 걷기", "placeName": "놀이터 벤치"}


def test_live_key_required(client):
    assert client.post(URL, json=BODY, headers={"X-Internal-Key": "wrong"}).status_code == 401


def test_live_no_openai_key_is_503(client):
    assert client.post(URL, json=BODY).status_code == 503


def test_live_ok(client, monkeypatch):
    seen = {}

    def fake(session):
        seen.update(session)
        return "ek_test", 1_800_000_000

    monkeypatch.setattr(openai_client, "realtime_client_secret", fake)
    r = client.post(URL, json=BODY)

    assert r.status_code == 200
    assert r.json() == {"clientSecret": "ek_test", "expiresAt": 1_800_000_000, "model": settings.realtime_model}
    assert seen["model"] == settings.realtime_model
    assert seen["audio"]["output"]["voice"] == settings.realtime_voice
    assert seen["audio"]["input"]["transcription"]["language"] == "ko"
    # 사용자 데이터가 프롬프트에 들어감
    assert "윤지" in seen["instructions"] and "놀이터 벤치" in seen["instructions"]
    # 잠깐 조용해도 끼어들지 않게 : 의미 기반 · 느긋한 턴 감지
    assert seen["audio"]["input"]["turn_detection"] == {
        "type": "semantic_vad", "eagerness": "low", "create_response": True, "interrupt_response": True}


def test_live_mission_description_in_prompt(client, monkeypatch):
    seen = {}
    monkeypatch.setattr(openai_client, "realtime_client_secret",
                        lambda s: (seen.update(s), ("ek", 1))[1])
    body = {"nickname": "윤지", "missionTitle": "북토크 뒷자리에서 듣기만 하기",
            "missionDescription": "말하지 않아도 돼요. 30분 듣고 와요.", "placeName": "아리랑 도서관"}
    assert client.post(URL, json=body).status_code == 200
    assert "북토크 뒷자리에서 듣기만 하기" in seen["instructions"]
    assert "30분 듣고 와요" in seen["instructions"]


def test_live_place_optional(client, monkeypatch):
    seen = {}
    monkeypatch.setattr(openai_client, "realtime_client_secret",
                        lambda s: (seen.update(s), ("ek", 1))[1])
    r = client.post(URL, json={"nickname": "윤지", "missionTitle": "창문 열기"})
    assert r.status_code == 200
    assert "정해진 곳 없음" in seen["instructions"]


def test_live_openai_fail_is_503(client, monkeypatch):
    def boom(session):
        raise openai_client.AiUnavailable("timeout")

    monkeypatch.setattr(openai_client, "realtime_client_secret", boom)
    assert client.post(URL, json=BODY).status_code == 503


def test_live_validation(client):
    assert client.post(URL, json={"nickname": "윤지"}).status_code == 422