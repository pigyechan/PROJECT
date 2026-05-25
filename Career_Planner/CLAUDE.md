# Career Planner Pipeline

## 프로젝트 개요

채용공고 20~30개 텍스트 → 역량 패턴 분석 + StoryBrand 7요소 포지셔닝 초안 자동 생성.

### 제출 산출물 매핑

| 제출 항목 | 파이프라인 출력 파일 |
|---|---|
| 채용공고 수집·분류 로그 | `runs/{id}/01_input.json` + `02_analysis.json` |
| 시장 패턴 리포트 1페이지 | `runs/{id}/02b_report.md` |
| 포지셔닝 초안 1페이지 | `runs/{id}/03_draft.md` |
| 무기가 되는 스토리 소화 메모 | `runs/{id}/memo_template.md` (사용자가 직접 작성) |

---

## 실행 방법

```
# 1. 채용공고 입력
cd pipeline
python create_input.py

# 2. 파이프라인 실행
python main.py ../inputs/input_{hash}.json
```

## API

- **모델**: Gemini API (Google)
  - Analyze / Draft / Eval / Refine / Report: `gemini-2.0-flash`
  - Critique: `gemini-2.5-flash-lite`
- **환경변수**: `GEMINI_API_KEY` 필요

---

## 파이프라인 단계

```
Step 1. Analyze  — 채용공고 분류 + 표면 스킬 + 숨은 기대치 추출
Step 2. Report   — 시장 패턴 리포트 생성 (마크다운 1페이지)
Step 3. Draft    — StoryBrand 7요소 포지셔닝 초안
Step 4. Critique — 약점 3개 추출 (독립 호출 / full_text만 전달)
Step 5. Eval     — 루브릭 6축 채점 + PASS/REJECT
Step 6. Refine   — REJECT 시 약점 반영 재작성 (최대 3회)
```

### 핵심 설계 원칙: 행간 읽기

Analyze는 기술 스택 나열이 아니라 숨은 기대치를 해석합니다.
- "Kafka/Redis 경험" → "대용량 트래픽 처리 경험"
- "MSA 설계 경험" → "분산 시스템 운영과 장애 대응"

### 격리 원칙

- Critique는 `full_text`만 전달 (Draft 히스토리 차단)
- Eval은 `content` + `brief_hash`만 전달 (Critique 결과 차단)

---

## 파일 구조

```
Career_Planner/
├── pipeline/
│   ├── main.py              — 파이프라인 진입점
│   ├── create_input.py      — 01_input.json 생성
│   └── steps/
│       ├── analyzer.py      — Step 1
│       ├── reporter.py      — Step 2
│       ├── drafter.py       — Step 3
│       ├── critic.py        — Step 4
│       ├── evaluator.py     — Step 5
│       ├── validate.py      — Step 5-V (코드 기반 이중 검증)
│       └── refiner.py       — Step 6
├── prompts/                 — 단계별 시스템 프롬프트
├── config/rubric.yaml       — 6축 루브릭 (가중치 합 1.0)
├── schemas/                 — JSON 스키마
├── inputs/                  — create_input.py 출력 저장소
└── runs/{timestamp_hash}/   — 실행 결과
```

---

## AI 행동 규칙

- 코드 수정 전 이유 설명
- 커밋/푸시는 사용자가 명시적으로 요청할 때만
- 파일 하나 변경 시 연관 파일 확인 (rubric.yaml ↔ eval_system.md ↔ DESIGN.md)
- 하드코딩 금지. 설정값은 yaml/json 분리.

## Cross-file 연관 관계

| 변경 파일 | 확인할 파일 |
|---|---|
| `config/rubric.yaml` | `prompts/eval_system.md` (축 일치), `pipeline/steps/validate.py` (파싱) |
| `schemas/*.json` | `pipeline/steps/validate.py`, 해당 schema를 출력하는 step |
| `prompts/*.md` | 해당 프롬프트를 읽는 `steps/*.py` |
| `pipeline/main.py` | `docs/DESIGN.md` 흐름도 |
