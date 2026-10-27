# ✨ 나가볼까? — AI Server

> 잃어버린 세상의 조각들 — 방 밖으로 한 걸음씩, 루미와 함께하는 모험

**나가볼까?** 는 고립·은둔 청년이 작은 일상 퀘스트를 하나씩 해내며 바깥세상과 다시 연결되도록 돕는 RPG형 모바일 웹 서비스입니다.

AI 서버는 외부에 공개하지 않으며, 백엔드(nagabolkka-be)만 내부에서 호출합니다.
DB 없이 요청을 받아 결과만 돌려주고, 세션 · 턴 수 · 기록 저장은 백엔드가 맡습니다.

## ✨ 주요 기능
| 기능 | 설명 |
| --- | --- |
| 🆘 위기 감지 | 자체 키워드 규칙 + OpenAI Moderation 2단계로 회고 · 연습 대화의 위기 표현 감지 |
| 💬 연습실 대화 | 첫 전화 · 첫 방문 · 모의 면접 시나리오별 NPC 롤플레이 응답과 선택지 생성 |
| 📝 연습 피드백 | 대화를 바탕으로 잘한 점과 다음에 써 볼 문장 생성 |
| 🌟 루미 한마디 | 퀘스트 완료 후 회고에 맞춘 응원 메시지 생성 |
| 💌 루미의 편지 | 한 주 기록을 바탕으로 주간 편지 생성 |
| 🛟 실패 대비 | OpenAI 호출 실패 시 시나리오별 고정 대사 · 피드백 · 템플릿으로 대체 |

## 🛠️ 기술 스택
| 구분 | 기술 스택 | 사용 목적 |
| --- | --- | --- |
| Language | Python 3.12 | 서버 개발 |
| Framework | FastAPI | 내부 REST API 서버 |
| Server | Uvicorn | ASGI 서버 |
| Validation | Pydantic, pydantic-settings | 요청 값 검증, 환경 변수 관리 |
| External API | OpenAI (Chat, Moderation) | AI 대화 생성, 위기 표현 판정 |
| Config | PyYAML | 시나리오 · 위기 패턴 파일 관리 |
| Test | pytest | 위기 감지 · 응답 형식 테스트 |
| Version Control | Git, GitHub | 버전 관리 |

## 📁 프로젝트 구조
```
nagabolkka-ai/
├── app/
│   ├── main.py            # 서버 시작점
│   ├── config.py          # 환경 변수 설정
│   ├── routers/           # API 엔드포인트 (crisis, practice, lumi, letters)
│   ├── services/          # 핵심 로직 (위기 감지, OpenAI 호출, 프롬프트 조립, 실패 대비)
│   └── schemas.py         # 요청 · 응답 모델
├── prompts/               # 프롬프트 템플릿
├── scenarios/             # 연습 시나리오 대본 (첫 대사 · 선택지 · 고정 대사)
├── crisis/                # 위기 · 주의 · 예외 표현 패턴
├── tests/                 # 테스트 코드
├── scripts/               # 비용 계산 등 보조 스크립트
├── .env.example
└── requirements.txt
```
​
## 🔗 API 목록
| Method | URL | 설명 | 호출하는 백엔드 API |
| --- | --- | --- | --- |
| GET | `/ai/health` | 서버 상태 확인 | - |
| POST | `/ai/crisis/check` | 위기 표현 감지 | 퀘스트 완료 · 연습 대화 |
| POST | `/ai/practice/reply` |  연습 대화 응답 · 선택지 생성 | 연습 대화 |
| POST | `/ai/practice/feedback` |  연습 피드백 생성 | 연습 끝 |
| POST | `/ai/lumi/message` |  루미 한마디 생성 | 퀘스트 완료 |
| POST | `/ai/letters/weekly` | 루미의 편지 생성 | 주간 배치 |

`/ai/health` 를 제외한 모든 요청은 X-Internal-Key 헤더가 필요합니다.
상세 명세는 로컬 실행 후 Swagger(/docs)에서 확인할 수 있습니다. (운영 환경에서는 비활성화)

## 🚀 실행 방법
### 1. 요구 사항
- Python 3.12 이상
### 2. 가상환경 및 패키지 설치
```
git clone <https://github.com/nagabolkka/nagabolkka-ai.git>
cd nagabolkka-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
### 3. 환경 변수 설정
`.env.example` 을 복사해 프로젝트 루트에 `.env` 파일을 만들고 값을 채워주세요.
```
ENV=local
OPENAI_API_KEY=
AI_INTERNAL_KEY=
```
### 4. 실행
```
fastapi dev app/main.py
```
### 5. 확인
```
GET <http://localhost:8000/ai/health>
→ {"status":"ok"}
```
Swagger: http://localhost:8000/docs
### 6. 테스트
```
pytest
```
​
## 🎯 Git Convention
| Type | Description |
| --- | --- |
| 🎉 Start | 프로젝트 시작 |
| ✨ Feat | 새로운 기능 추가 |
| 🐛 Fix | 버그 수정 |
| ♻️ Refactor | 코드 리팩토링 |
| 🔧 Settings | 설정 파일 수정 |
| ✅ Test | 테스트 코드 추가 및 수정 |
| ➕ Dependency/Plugin | 라이브러리 추가 |
| 📝 Docs | 문서 수정 |
| 🚚 Rename | 파일 및 폴더 이름 수정 |
| 🔥 Remove | 파일 삭제 |

## 🌲 Branch Convention
| Branch | Description |
| --- | --- |
| main | 배포 가능한 브랜치 |
| develop | 개발 브랜치 |
| feat/#이슈번호/명칭 | 새로운 기능 개발 |
| fix/#이슈번호/명칭 | 버그 수정 |
| refactor/#이슈번호/명칭 | 리팩토링 작업 |

