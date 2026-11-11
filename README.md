# 🗺️ 나가볼까? — AI Server

AI 서버는 외부에 공개하지 않으며, 백엔드 ([nagabolkka-be](https://github.com/nagabolkka/nagabolkka-be)) 만 내부에서 호출합니다.
DB 없이 요청을 받아 결과만 돌려주고, 세션 · 턴 수 · 기록 저장은 백엔드가 맡습니다.

```
프론트 ──▶ 백엔드 (api.nagabolkka.shop) ──▶ AI 서버 (내부 http://ai:8000) ──▶ OpenAI
```

## 📨 주요 기능
| 기능 | 설명 |
| --- | --- |
| **🆘 위기 감지** | 자체 규칙(위기 · 주의 · 예외 패턴) + OpenAI Moderation 2단계로 회고 · 연습 대화의 위기 표현 감지 |
| **💬 연습실 대화** | 첫 전화 · 첫 방문 · 모의 면접 시나리오별 상대역 롤플레이 응답과 선택지 생성 |
| **📝 연습 피드백** | 대화를 바탕으로 잘한 점과 다음에 써 볼 문장 생성 |
| **🌟 루미 한마디** | 퀘스트 완료 후 회고 · 기분에 맞춘 응원 메시지 생성 |
| **🛟 실패 대비** | OpenAI 실패 · 타임아웃 · 응답 형식 오류 시 시나리오별 고정 대사 · 고정 피드백 · 템플릿으로 대체 |
| **🔒 내부 인증** | 모든 요청에 `X-Internal-Key` 헤더 확인 (헬스 체크 제외) |
| **💌 루미의 편지** | 한 주 기록을 바탕으로 주간 편지 생성 *(예정)* |

### 안전 원칙
- 위기 표현이 감지되면 백엔드는 AI 대화를 호출하지 않고 도움 받기 화면으로 안내합니다.
- Moderation 호출이 실패하면 **안전 우선** — 주의 표현이 있으면 위기로 판단합니다.
- 사용자 대화 · 회고는 프롬프트에서 시스템 지시와 분리된 데이터로만 전달합니다 (프롬프트 인젝션 대비).
- 회고 · 대화 원문은 로그에 남기지 않습니다.

## 🛠️ 기술 스택
| 구분 | 기술 스택 | 사용 목적 |
| --- | --- | --- |
| Language | Python 3.12 | 서버 개발 |
| Framework | FastAPI | 내부 REST API 서버 |
| Server | Uvicorn | ASGI 서버 |
| Validation | Pydantic, pydantic-settings | 요청 값 검증, 환경 변수 관리 |
| External API | OpenAI (Chat Completions, Moderation) | AI 대화 생성, 위기 표현 판정 |
| Config | PyYAML | 시나리오 · 위기 패턴 파일 관리 |
| Test | pytest | 위기 감지 · API 응답 테스트 |
| Infra | Docker, AWS EC2 | 백엔드와 같은 서버 · 같은 Docker 네트워크에 배포 |
| CI/CD | GitHub Actions | 테스트 · 배포 |
| Version Control | Git, GitHub | 버전 관리 |

## 📁 프로젝트 구조
```
nagabolkka-ai/
├── app/
│   ├── main.py              # 서버 시작점 · 라우터 등록
│   ├── config.py            # 환경 변수 설정
│   ├── security.py          # X-Internal-Key 확인
│   ├── schemas.py           # 요청 · 응답 모델
│   ├── routers/             # API 엔드포인트 (crisis, practice, lumi)
│   └── services/            # 핵심 로직
│       ├── crisis_filter.py     # 1차 위기 감지 (정규식 규칙)
│       ├── crisis_service.py    # 규칙 + Moderation 판정
│       ├── openai_client.py     # OpenAI 호출 (타임아웃 · 재시도 없음)
│       ├── practice.py          # 연습 답변 · 피드백
│       ├── lumi.py              # 루미 한마디
│       ├── scenarios.py         # 시나리오 대본 읽기
│       └── prompts.py           # 프롬프트 파일 읽기
├── prompts/                 # 프롬프트 템플릿
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

## 🔗 API 목록
| Method | URL | 설명 | 호출하는 백엔드 API |
| --- | --- | --- | --- |
| GET | `/ai/health` | 서버 상태 확인 | 배포 헬스 체크 |
| POST | `/ai/crisis/check` | 위기 표현 감지 | 퀘스트 완료 · 연습 대화 |
| GET | `/ai/practice/scenarios/{code}/opening` | 연습 첫 대사 · 선택지 | 연습 시작 |
| POST | `/ai/practice/reply` | 연습 대화 응답 · 선택지 생성 | 연습 대화 |
| POST | `/ai/practice/feedback` | 연습 피드백 생성 | 연습 끝 |
| POST | `/ai/lumi/message` | 루미 한마디 생성 | 퀘스트 완료 |
| POST | `/ai/letters/weekly` | 루미의 편지 생성 *(예정)* | 주간 배치 |

- `/ai/health` 를 제외한 모든 요청은 `X-Internal-Key` 헤더가 필요합니다.
- OpenAI 를 쓰는 응답에는 `fallback` 필드가 있습니다. `true` 면 고정 대사 · 템플릿으로 대체된 응답입니다.
- 상세 명세는 로컬 실행 후 Swagger(`/docs`)에서 확인할 수 있습니다. 오른쪽 위 **Authorize** 에 내부 키를 넣으면 모든 요청에 적용됩니다. (운영 환경에서는 비활성화)

## 🚀 실행 방법
### 1. 요구 사항
- Python 3.12 이상

### 2. 가상환경 및 패키지 설치
```bash
git clone https://github.com/nagabolkka/nagabolkka-ai.git
cd nagabolkka-ai
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 3. 환경 변수 설정
`.env.example` 을 복사해 프로젝트 루트에 `.env` 파일을 만들고 값을 채워주세요.
```bash
cp .env.example .env
```
```
ENV=local
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
AI_INTERNAL_KEY=local-dev-key
```
- `OPENAI_API_KEY` 를 비워두면 모든 AI 응답이 고정 대사 · 템플릿으로 대체됩니다 (`fallback: true`).
- 운영(`ENV=prod`)에서는 `AI_INTERNAL_KEY` 를 기본값으로 두면 서버가 시작되지 않습니다.

### 4. 실행
```bash
uvicorn app.main:app --reload
```

### 5. 확인
```
GET http://localhost:8000/ai/health
→ {"status":"ok"}
```
Swagger: http://localhost:8000/docs (Authorize → `local-dev-key`)

### 6. 테스트
```bash
pytest -q
```
위기 감지 테스트 문장 18개와 API 응답 · 실패 대비 테스트가 포함되어 있습니다.

## 📦 배포
- 백엔드와 같은 EC2 서버에 Docker 컨테이너로 실행하며, 백엔드 Docker 네트워크(`nagabolkka-be_default`)에 `ai` 라는 이름으로 연결합니다.
- 포트를 외부에 열지 않으므로 인터넷에서는 접근할 수 없고, 백엔드만 `http://ai:8000` 으로 호출합니다.
- `main` 브랜치에 머지하면 GitHub Actions 가 테스트 후 서버에 배포합니다.

```bash
# 서버에서 수동 배포
cd ~/nagabolkka-ai && git pull origin main && docker compose up -d --build
```

## 🎯 Git Convention
| Type | Description |
| --- | --- |
| 🎉 Start | 프로젝트 시작 |
| ✨ Feat | 새로운 기능 추가 |
| 🐛 Fix | 버그 수정 |
| ♻️ Refactor | 코드 리팩토링 |
| 🔧 Chore | 설정 파일 · 의존성 등 기타 수정 |
| ✅ Test | 테스트 코드 추가 및 수정 |
| ➕ Dependency/Plugin | 라이브러리 추가 |
| 📝 Docs | 문서 수정 |
| 🚀 Deploy | 배포 · CI/CD 설정 |
| 🚚 Rename | 파일 및 폴더 이름 수정 |
| 🔥 Remove | 파일 삭제 |

## 🌲 Branch Convention
| Branch | Description |
| --- | --- |
| main | 배포 브랜치 (머지 시 운영 배포) |
| develop | 개발 브랜치 |
| feat/#이슈번호/명칭 | 새로운 기능 개발 |
| fix/#이슈번호/명칭 | 버그 수정 |
| refactor/#이슈번호/명칭 | 리팩토링 작업 |
| docs/#이슈번호/명칭 | 문서 작업 |
| deploy/#이슈번호/명칭 | 배포 · CI/CD 설정 |
