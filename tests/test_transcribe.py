from app.services import openai_client

URL = "/ai/practice/transcribe"


def _file(data=b"fake-audio", name="voice.webm", type_="audio/webm"):
    return {"audio": (name, data, type_)}


def test_transcribe_key_required(client):
    r = client.post(URL, files=_file(), headers={"X-Internal-Key": "wrong"})
    assert r.status_code == 401


def test_transcribe_no_openai_key_is_fallback(client):
    # conftest : openai_api_key = "" → AiUnavailable
    r = client.post(URL, files=_file())
    assert r.status_code == 200
    assert r.json() == {"text": None, "fallback": True}


def test_transcribe_ok(client, monkeypatch):
    got = {}

    def fake(data, filename, content_type):
        got.update(data=data, filename=filename, content_type=content_type)
        return "  네, 신청할게요.  "

    monkeypatch.setattr(openai_client, "transcribe", fake)
    r = client.post(URL, files=_file(name="voice.mp4", type_="audio/mp4"))
    assert r.json() == {"text": "네, 신청할게요.", "fallback": False}
    assert got == {"data": b"fake-audio", "filename": "voice.mp4", "content_type": "audio/mp4"}


def test_transcribe_empty_text_is_null(client, monkeypatch):
    monkeypatch.setattr(openai_client, "transcribe", lambda *a: "   ")
    assert client.post(URL, files=_file()).json() == {"text": None, "fallback": False}


def test_transcribe_empty_or_too_big(client, monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "stt_max_bytes", 5)
    assert client.post(URL, files=_file(data=b"")).status_code == 400
    assert client.post(URL, files=_file(data=b"123456")).status_code == 400


def test_transcribe_missing_file(client):
    assert client.post(URL).status_code == 422