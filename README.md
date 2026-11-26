# 🗺️ 나가볼까? - AI Server

> **나가볼까?** 의 AI 서버 레포지토리입니다. 
FastAPI 로 만든 내부 API 서버이며, 외부에 공개하지 않고 백엔드 ([nagabolkka-be](https://github.com/nagabolkka/nagabolkka-be)) 만 내부에서 호출합니다. DB 없이 요청을 받아 결과만 돌려주고, 세션 · 턴 수 · 기록 저장은 백엔드가 맡습니다.

```
프론트 ──▶ 백엔드 (api.nagabolkka.shop) ──▶ AI 서버 (내부 http://ai:8000) ──▶ OpenAI

루미 동행 통화만: 프론트 ──(임시 키 · WebRTC)──▶ OpenAI Realtime
                 (임시 키는 백엔드 → AI 서버를 거쳐 발급)
```

<br>

## 🧩 Implementation

| 구분 | 구현 방식 |
|---|---|
| **🆘 위기 감지** | 자체 규칙(위기 · 주의 · 예외 패턴) + OpenAI Moderation 2단계로 회고 · 연습 대화의 위기 표현을 감지합니다. |
| **💬 연습실 대화** | 첫 전화 · 첫 방문 · 모의 면접 시나리오별 상대역 롤플레이 응답과 선택지를 생성합니다. |
| **🎙️ 연습 음성 입력** | 연습실에서 녹음한 음성을 글자로 바꿉니다. (gpt-4o-mini-transcribe) |
| **📝 연습 피드백** | 대화를 바탕으로 잘한 점과 다음에 써 볼 문장을 생성합니다. |
| **🌟 루미 한마디** | 퀘스트 완료 후 회고 · 기분에 맞춘 응원 메시지를 생성합니다. |
| **💌 루미의 편지** | 한 주 기록을 바탕으로 주간 편지를 생성합니다. |
| **🎧 루미 동행 통화** | 오늘 퀘스트(제목 · 설명 · 장소)에 맞춘 루미 지시문으로 OpenAI Realtime 임시 키(60초)를 발급합니다. 실제 음성은 브라우저가 OpenAI 와 WebRTC 로 직접 주고받습니다. |
| **🛟 실패 대비** | OpenAI 실패 · 타임아웃 · 응답 형식 오류 시 시나리오별 고정 대사 · 고정 피드백 · 템플릿으로 대체합니다. |
| **🔒 내부 인증** | 모든 요청에 `X-Internal-Key` 헤더를 확인합니다. (헬스 체크 제외) |

### 🛡️ Safety

| 원칙 | 내용 |
|---|---|
| **위기 시 대화 중단** | 위기 표현이 감지되면 백엔드는 AI 대화를 호출하지 않고 도움 받기 화면으로 안내합니다. |
| **안전 우선 판정** | Moderation 호출이 실패하면 주의 표현이 있을 때 위기로 판단합니다. |
| **프롬프트 인젝션 대비** | 사용자 대화 · 회고 · 퀘스트 정보는 프롬프트에서 시스템 지시와 분리된 데이터로만 전달합니다. |
| **통화 안전 규칙** | 루미는 퀘스트에 없는 행동을 시키지 않고, 의료 조언 · 개인정보 요청을 하지 않으며, 위험 신호에는 109 · 도움 받기 화면을 안내합니다. |
| **OpenAI 키 비공개** | 브라우저에는 60초 뒤 만료되는 임시 키만 전달하고, OpenAI API 키는 AI 서버 밖으로 나가지 않습니다. |
| **원문 로그 금지** | 회고 · 대화 · 음성 원문은 로그에 남기지 않습니다. |

<br>

## 🛠️ Tech Stack

**Language · Framework**

![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=flat-square&logo=gunicorn&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)

**AI**

![OpenAI GPT-4.1 mini](https://img.shields.io/badge/GPT--4.1_mini-412991?style=flat-square&logo=openai&logoColor=white)
![OpenAI Moderation](https://img.shields.io/badge/Moderation-412991?style=flat-square&logo=openai&logoColor=white)
![OpenAI Transcribe](https://img.shields.io/badge/gpt--4o--mini--transcribe-412991?style=flat-square&logo=openai&logoColor=white)
![OpenAI Realtime](https://img.shields.io/badge/Realtime_API-412991?style=flat-square&logo=openai&logoColor=white)

**Config · Test**

![YAML](https://img.shields.io/badge/PyYAML-CB171E?style=flat-square&logo=yaml&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

**Infra**

![AWS EC2](https://img.shields.io/badge/AWS_EC2-FF9900?style=flat-square&logo=amazonec2&logoColor=white)
![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat-square&logo=githubactions&logoColor=white)

<br>

## 📁 Project Structure

```
nagabolkka-ai/
├── app/
│   ├── main.py              # 서버 시작점 · 라우터 등록
│   ├── config.py            # 환경 변수 설정
│   ├── security.py          # X-Internal-Key 확인
│   ├── schemas.py           # 요청 · 응답 모델
│   ├── routers/             # API 엔드포인트 (crisis, practice, lumi, letter, live)
│   └── services/            # 핵심 로직
│       ├── crisis_filter.py     # 1차 위기 감지 (정규식 규칙)
│       ├── crisis_service.py    # 규칙 + Moderation 판정
│       ├── openai_client.py     # OpenAI 호출 (타임아웃 · 재시도 없음)
│       ├── practice.py          # 연습 답변 · 피드백 · 음성 입력
│       ├── lumi.py              # 루미 한마디
│       ├── letter.py            # 루미의 편지
│       ├── live.py              # 루미 동행 통화 임시 키
│       ├── scenarios.py         # 시나리오 대본 읽기
│       └── prompts.py           # 프롬프트 파일 읽기
├── prompts/                 # 프롬프트 템플릿 (연습 · 루미 한마디 · 편지 · 동행 통화)
├── scenarios/               # 연습 시나리오 대본 (FIRST_CALL · FIRST_VISIT · INTERVIEW)
├── crisis/patterns.yaml     # 위기 · 주의 · 예외 표현 패턴
├── tests/                   # 테스트 코드
├── .github/workflows/       # 배포 워크플로
├── Dockerfile
├── docker-compose.yml       # 운영 배포용 (백엔드 Docker 네트워크에 연결)
├── requirements.txt         # 실행용 패키지
├── requirements-dev.txt     # 테스트용 패키지 포함
└── .env.example
```

<br>

## 🔗 API

| Method | URL | Description | 호출하는 백엔드 API |
|---|---|---|---|
| GET | `/ai/health` | 서버 상태 확인 | 배포 헬스 체크 |
| POST | `/ai/crisis/check` | 위기 표현 감지 | 퀘스트 완료 · 연습 대화 |
| GET | `/ai/practice/scenarios/{code}/opening` | 연습 첫 대사 · 선택지 | 연습 시작 |
| POST | `/ai/practice/reply` | 연습 대화 응답 · 선택지 생성 | 연습 대화 |
| POST | `/ai/practice/transcribe` | 연습 음성 → 글자 | 연습 음성 입력 |
| POST | `/ai/practice/feedback` | 연습 피드백 생성 | 연습 끝 |
| POST | `/ai/lumi/message` | 루미 한마디 생성 | 퀘스트 완료 |
| POST | `/ai/letter/weekly` | 루미의 편지 생성 | 주간 배치 |
| POST | `/ai/live/session` | 루미 동행 통화 임시 키 발급 | 동행 통화 시작 |

- `/ai/health` 를 제외한 모든 요청은 `X-Internal-Key` 헤더가 필요합니다.
- OpenAI 를 쓰는 응답에는 `fallback` 필드가 있습니다. `true` 면 고정 대사 · 템플릿으로 대체된 응답입니다.
- `/ai/live/session` 은 대체할 고정 응답이 없으므로, OpenAI 실패 시 `503` 을 돌려줍니다.
- 상세 명세는 로컬 실행 후 Swagger(`/docs`)에서 확인할 수 있습니다. 오른쪽 위 **Authorize** 에 내부 키를 넣으면 모든 요청에 적용됩니다. (운영 환경에서는 비활성화)

<br>

## 🚀 Getting Started

### ✅ Requirements

- Python 3.12 이상

### 📦 Install

```bash
git clone https://github.com/nagabolkka/nagabolkka-ai.git
cd nagabolkka-ai
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 🔑 Environment Variables

`.env.example` 을 복사해 프로젝트 루트에 `.env` 를 만들고 값을 채웁니다. (커밋하지 않음)

```bash
cp .env.example .env
```

```env
ENV=local
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
AI_INTERNAL_KEY=local-dev-key

OPENAI_TIMEOUT=4.0
MODERATION_TIMEOUT=3.0
LETTER_TIMEOUT=15.0
```

| Key | Description |
|---|---|
| `ENV` | 실행 환경 (`local` · `prod`) |
| `OPENAI_API_KEY` | OpenAI API 키 — 비워두면 모든 AI 응답이 고정 대사 · 템플릿으로 대체됨 (`fallback: true`), 동행 통화는 `503` |
| `OPENAI_MODEL` | 대화 · 피드백 · 한마디 · 편지에 쓰는 OpenAI 모델 |
| `AI_INTERNAL_KEY` | 백엔드가 `X-Internal-Key` 헤더로 보내는 내부 키 — 운영(`ENV=prod`)에서 기본값이면 서버가 시작되지 않음 |
| `OPENAI_TIMEOUT` | OpenAI 대기 시간(초) — 백엔드 `ai.timeout` (5초) 보다 짧게 |
| `MODERATION_TIMEOUT` | Moderation 대기 시간(초) |
| `LETTER_TIMEOUT` | 루미의 편지 생성 대기 시간(초) |

- 음성 입력 · 동행 통화 모델은 기본값(`gpt-4o-mini-transcribe` · `gpt-realtime-2.1-mini`, 목소리 `marin`)을 쓰며, 필요하면 `STT_MODEL` · `REALTIME_MODEL` · `REALTIME_VOICE` 로 바꿀 수 있습니다.

### ▶️ Run

```bash
uvicorn app.main:app --reload   # http://localhost:8000
```

- 헬스 체크 → `GET http://localhost:8000/ai/health` → `{"status":"ok"}`
- Swagger → http://localhost:8000/docs (Authorize → `local-dev-key`)
- 프롬프트 파일(`prompts/*.txt`)은 처음 읽을 때 캐시되므로, 수정한 뒤에는 서버를 다시 켜야 반영됩니다.

### 🧪 Test

```bash
pytest -q
```

위기 감지 테스트 문장 18개와 연습 대화 · 음성 입력 · 루미 한마디 · 편지 · 동행 통화 API 응답 및 실패 대비 테스트가 포함되어 있습니다.

<br>

## 🌐 Deployment

- 백엔드와 같은 EC2 서버에 Docker 컨테이너로 실행하며, 백엔드 Docker 네트워크(`nagabolkka-be_default`)에 `ai` 라는 이름으로 연결합니다.
- 포트를 외부에 열지 않으므로 인터넷에서는 접근할 수 없고, 백엔드만 `http://ai:8000` 으로 호출합니다.
- `main` 브랜치에 머지하면 GitHub Actions 가 테스트 후 서버에 배포합니다.

```bash
# 서버에서 수동 배포
cd ~/nagabolkka-ai && git pull origin main && docker compose up -d --build
```

<br>

## 🤝 Convention

### 🌿 Branch

| Branch | Usage |
|---|---|
| `main` | 배포 브랜치 (머지 시 운영 배포) |
| `develop` | 개발 브랜치 |
| `feat/#이슈번호/명칭` | 새로운 기능 개발 |
| `fix/#이슈번호/명칭` | 버그 수정 |
| `refactor/#이슈번호/명칭` | 리팩토링 작업 |
| `docs/#이슈번호/명칭` | 문서 작업 |
| `deploy/#이슈번호/명칭` | 배포 · CI/CD 설정 |

### 💬 Commit

`이모지 Type: 내용`

| Type | Usage |
|---|---|
| ✨ Feat | 새로운 기능 추가 |
| 🐛 Fix | 버그 수정 |
| ♻️ Refactor | 코드 리팩토링 |
| ✅ Test | 테스트 코드 추가 및 수정 |
| 🔧 Settings | 설정 파일 · 의존성 수정 |
| 🧹 Chore | 기능 변화 없는 정리 |
| 🚀 Deploy | 배포 · CI/CD 설정 |
| 📝 Docs | 문서 수정 |

### 🔀 Pull Request

`[타입/#이슈번호] 내용` — 예: `[FEAT/#10] 내 정보 조회 · 목표 변경 API 구현`
배포 PR (develop → main) 은 `[DEPLOY] 내용`