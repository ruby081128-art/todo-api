# Todo API 과제

Python과 FastAPI를 사용해 Todo 관리용 REST API를 구현합니다. Todo의 생성, 조회, 수정, 삭제 기능은 필수이며, 데이터는 **SQLite**에 저장합니다.

## 필수 기술

* Python 3.12 이상
* FastAPI
* SQLite
* Git / GitHub

ORM, 패키지 관리 도구, 프로젝트 구조는 자유롭게 선택합니다.

## 구현 방향

Todo에는 제목과 완료 여부가 포함되어야 합니다. 설명, 마감일, 우선순위, 태그, 검색, 페이지네이션, 인증 등의 기능은 자유롭게 추가할 수 있습니다.

API 경로와 응답 형식은 직접 설계하며, 적절한 HTTP 메서드와 상태 코드를 사용합니다. 잘못된 입력과 존재하지 않는 데이터에 대한 처리도 구현합니다.

Claude Code를 포함한 AI 코딩 도구는 자유롭게 사용할 수 있습니다. 제출 시에는 코드의 구조와 동작을 설명할 수 있어야 합니다.

README에는 실행 방법, 사용 기술, API 목록, 구현한 기능을 작성하고, GitHub 저장소 형태로 제출합니다.

---

## 실행 방법

```bash
# 1. 가상환경 생성 및 활성화 (Windows PowerShell 예시)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 서버 실행
uvicorn app.main:app --reload
```

서버 실행 후 http://127.0.0.1:8000/docs 에서 Swagger UI로 API를 확인/테스트할 수 있습니다.
DB는 SQLite 파일(`todos.db`)로 프로젝트 루트에 자동 생성됩니다.

## 사용 기술

* Python 3.12+
* FastAPI
* SQLAlchemy (ORM)
* SQLite
* Pydantic v2 (요청/응답 검증)
* Uvicorn (ASGI 서버)

## API 목록

| Method | Path | 설명 |
|--------|------|------|
| POST | `/todos` | Todo 생성 |
| GET | `/todos` | Todo 목록 조회 (검색/필터/페이지네이션) |
| GET | `/todos/{todo_id}` | Todo 단건 조회 |
| PUT | `/todos/{todo_id}` | Todo 수정 (부분 수정 가능) |
| DELETE | `/todos/{todo_id}` | Todo 삭제 |

### `GET /todos` 쿼리 파라미터

* `skip` (기본 0), `limit` (기본 20, 최대 100) — 페이지네이션
* `completed` — true/false로 완료 여부 필터링
* `q` — 제목/설명에 대한 부분 문자열 검색

## 구현한 기능

* Todo CRUD (생성/조회/수정/삭제) 전체 구현
* Todo 필드: 제목(필수), 완료 여부, 설명, 마감일, 우선순위(low/medium/high), 태그(목록)
* 목록 조회 시 검색(`q`), 완료 여부 필터, 페이지네이션(`skip`/`limit`) 지원
* 존재하지 않는 Todo 조회/수정/삭제 시 404 응답
* 잘못된 입력(빈 제목, 잘못된 타입 등)에 대해 Pydantic 검증을 통한 422 응답
* 생성/수정 시각(`created_at`/`updated_at`) 자동 기록
