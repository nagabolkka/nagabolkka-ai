from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------- 위기 감지 ----------
class CrisisCheckRequest(BaseModel):
    text: str = Field(max_length=300, description="검사할 문장 (회고 최대 100자 · 연습 메시지 최대 200자)")

    model_config = ConfigDict(json_schema_extra={"examples": [{"text": "오늘 그냥 죽고 싶었어"}]})


class CrisisCheckResponse(BaseModel):
    crisis: bool = Field(description="true 면 Spring 이 도움 받기 화면 + crisis_events 기록")
    method: Literal["RULE", "MODERATION"] | None = Field(
        default=None, description="위기일 때 감지 방식 (통과면 null)")
    ruleId: str | None = Field(default=None, description="걸린 패턴 ID (H01 · C07 · D01 …)")
    category: str | None = Field(default=None, description="Moderation 으로 감지했을 때 카테고리")


# ---------- 연습실 ----------
class Line(BaseModel):
    role: Literal["user", "partner"] = Field(description="user = 사용자, partner = 상대역")
    text: str = Field(max_length=300)


class OpeningResponse(BaseModel):
    opening: str = Field(description="상대역 첫 대사")
    choices: list[str] = Field(description="사용자 선택지 2개")


class ReplyRequest(BaseModel):
    scenarioCode: str = Field(description="FIRST_CALL · FIRST_VISIT · INTERVIEW")
    turn: int = Field(ge=1, le=5, description="이번에 만들 턴 번호 (Spring 의 turn_count + 1)")
    maxTurns: int = Field(default=3, ge=1, le=5, description="시나리오 최대 턴 수")
    message: str = Field(min_length=1, max_length=200, description="사용자가 방금 한 말 (위기 검사 통과)")
    history: list[Line] = Field(default_factory=list, max_length=7, description="지금까지의 대화 (최대 7개)")

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "scenarioCode": "FIRST_CALL",
        "turn": 1,
        "maxTurns": 3,
        "message": "북토크 문의하려고 전화했어요.",
        "history": [{"role": "partner", "text": "네, OO도서관입니다. 무엇을 도와드릴까요?"}],
    }]})


class ReplyResponse(BaseModel):
    reply: str = Field(description="상대역 대사")
    choices: list[str] = Field(description="다음 선택지 2개 (마지막 턴이면 [])")
    finished: bool = Field(description="마지막 턴이면 true → Spring 은 17번 피드백으로")
    fallback: bool = Field(description="true = OpenAI 실패로 고정 대사 사용")


class FeedbackRequest(BaseModel):
    scenarioCode: str = Field(description="FIRST_CALL · FIRST_VISIT · INTERVIEW")
    history: list[Line] = Field(min_length=1, max_length=7, description="연습 대화 전체")

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "scenarioCode": "FIRST_CALL",
        "history": [
            {"role": "partner", "text": "네, OO도서관입니다. 무엇을 도와드릴까요?"},
            {"role": "user", "text": "북토크 문의하려고 전화했어요."},
            {"role": "partner", "text": "아, 토요 북토크요! 이번 주 토요일 오후 2시에 3층에서 해요."},
        ],
    }]})


class Feedback(BaseModel):
    good: list[str] = Field(description="좋았던 점 1~2개")
    next: list[str] = Field(description="다음에 써 볼 문장 1개")


class FeedbackResponse(BaseModel):
    feedback: Feedback
    fallback: bool = Field(description="true = OpenAI 실패로 고정 피드백 사용")


# ---------- 루미 한마디 ----------
class LumiRequest(BaseModel):
    nickname: str = Field(default="탐험가", max_length=30, description="표시 이름")
    missionTitle: str = Field(max_length=100, description="완료한 미션 제목")
    mood: int = Field(ge=1, le=5, description="기분 1(매우 나쁨) ~ 5(매우 좋음)")
    reflection: str | None = Field(default=None, max_length=100, description="한 줄 회고 (위기 검사 통과한 것만, 없으면 null)")
    pieceName: str = Field(max_length=30, description="받은 조각 이름")
    restoreText: str = Field(max_length=60, description="조각 복원 문구")

    model_config = ConfigDict(json_schema_extra={"examples": [{
        "nickname": "윤지",
        "missionTitle": "창문 열고 바깥 공기 3분 마시기",
        "mood": 4,
        "reflection": "오랜만에 나갔는데 바람이 시원했다",
        "pieceName": "햇살 조각",
        "restoreText": "하늘에 색이 돌아왔어",
    }]})


class LumiResponse(BaseModel):
    message: str = Field(description="루미 한마디 (최대 200자)")
    fallback: bool = Field(description="true = OpenAI 실패로 템플릿 사용")