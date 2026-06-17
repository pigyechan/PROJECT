# Test_Writer Pipeline — 스펙

> Blog_Writer(Phase 0)를 테스트 케이스 생성 도메인으로 이식한 파이프라인.
> 자연어 요구사항을 입력하면 JUnit 5 단위 테스트 케이스와 Gherkin 시나리오 초안을 생성한다.

---

## 1. 전체 흐름

```
01_input.json
     │
     ▼
┌─────────┐
│  Step 1 │  Gen        자연어 → unit_tests[] + scenarios[]
└────┬────┘
     │ 02_output.json
     ▼
┌─────────┐
│  Step 2 │  Critique   content만 수신, 빈틈 3개 추출   ← Gen 히스토리 차단
└────┬────┘
     │ 02b_critique.json
     ▼
┌─────────┐
│  Step 3 │  Eval       content + rubric → weighted_total  ← Critique 결과 차단
└────┬────┘
     │
     ▼
┌─────────┐
│  Step 4 │  Validate   JSON 스키마 + Then 모호 패턴 + 품질 하한 (코드 게이트)
└────┬────┘
     │
  PASS? ──Yes──→ 04_next.json (종료)
     │
    No (REJECT)
     │
  iteration < MAX_ITERATIONS(3)?
     │ Yes
     ▼
┌─────────┐
│  Refine │  비평 + 점수 기반 개선 초안 생성 → 02_output_v{n}.json
└─────────┘
     │
     └──────────── Step 2로 돌아감

iteration == 3에서도 REJECT → 99_regen_request.json (종료)
```

**핵심 원칙 — Gen/Eval 격리**

- Critique는 `content` 필드만 받는다. Gen이 어떤 과정으로 초안을 만들었는지 모른다.
- Eval은 `content` + `brief_hash`만 받는다. Critique가 무엇을 지적했는지 모른다.
- 두 단계가 서로의 결과에 영향받지 않아야 평가의 독립성이 보장된다.

---

## 2. 입력 스펙 (`01_input.json`)

### 필드

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| `brief_hash` | string | ✅ | brief dict의 SHA-256 앞 16자리 |
| `brief.feature_name` | string | ✅ | 테스트 대상 클래스/기능 이름 |
| `brief.requirements` | string | ✅ | 자연어 요구사항 (메서드 시그니처, 예외 조건 등) |
| `brief.context` | string | - | 언어/프레임워크 환경 정보 |
| `created_at` | string | ✅ | ISO 8601 타임스탬프 |

### 예시

```json
{
  "brief_hash": "e199b3398e4a1fd9",
  "brief": {
    "feature_name": "DefectRateCalculator",
    "requirements": "calculateDefectRate(defective, total): ...",
    "context": "Java 클래스. JUnit 5 + Gherkin(Cucumber) 스타일."
  },
  "created_at": "2026-06-17T10:43:12.565349+00:00"
}
```

---

## 3. Step별 스펙

### Step 1 — Gen

| 항목 | 내용 |
|---|---|
| 파일 | `pipeline/steps/generator.py` |
| 모델 | `gemini-3.1-flash-lite` |
| 입력 | `01_input.json` → `brief` 필드 |
| 출력 | `02_output.json` |
| 역할 | 자연어 요구사항 → 단위 테스트 케이스 + Gherkin 시나리오 초안 생성 |
| 프롬프트 | `prompts/gen_system.md` |

**출력 artifact 구조 (`02_output.json`)**

```json
{
  "brief_hash": "e199b3398e4a1fd9",
  "unit_tests": [
    {
      "name": "test_calculate_defect_rate_success",
      "given": "defective=5, total=100",
      "when": "calculateDefectRate(5, 100)을 실행함",
      "then": "5.0이 반환됨"
    }
  ],
  "scenarios": [
    {
      "title": "경계값(주의 등급 시작) 테스트",
      "given": "불량률 1.0이 주어짐",
      "when": "evaluateGrade(1.0)을 실행함",
      "then": "'주의' 등급이 반환됨"
    }
  ],
  "content": "{ ... }",
  "generated_at": "2026-06-17T10:43:...",
  "generator_model": "gemini-3.1-flash-lite"
}
```

> `content`는 `unit_tests` + `scenarios`를 JSON 직렬화한 문자열이다.
> Critique / Eval은 이 `content`만 전달받는다.

---

### Step 2 — Critique

| 항목 | 내용 |
|---|---|
| 파일 | `pipeline/steps/critique.py` |
| 모델 | `gemini-3.1-flash-lite` |
| 입력 | `artifact["content"]`만 — Gen 히스토리 없음 |
| 출력 | `02b_critique.json` |
| 역할 | 시니어 QA 페르소나로 빈틈 3개를 coverage / unambiguity / independence 기준으로 추출 |
| 제약 | `weaknesses` 배열이 정확히 3개가 아니면 `ValueError` 발생 |
| 프롬프트 | `prompts/critique_system.md` |

**출력 구조**

```json
{
  "brief_hash": "e199b3398e4a1fd9",
  "weaknesses": [
    {
      "axis": "coverage",
      "reason": "evaluateGrade 0과 100 경계값 검증 누락",
      "fix_hint": "등급 판정 경계값 케이스 추가"
    }
  ],
  "critique_model": "gemini-3.1-flash-lite",
  "critiqued_at": "..."
}
```

---

### Step 3 — Eval

| 항목 | 내용 |
|---|---|
| 파일 | `pipeline/steps/evaluator.py` |
| 모델 | `gemini-3.1-flash-lite` |
| 입력 | `artifact["content"]` + `rubric.yaml` (Critique 결과 없음) |
| 출력 | `03_verdict.json` (초안) |
| 역할 | rubric 4축으로 1~5점 채점, weighted_total 계산, PASS/REJECT 판정 |
| 보호 | `sum(weights) == 1.0` assert — 로딩 시 검증 |
| 프롬프트 | `prompts/eval_system.md` |

**rubric.yaml 축 요약**

| axis | weight | 5점 기준 |
|---|---|---|
| coverage | 0.30 | 경계값(min/max/zero/negative) + 실패 케이스 2개 이상 |
| unambiguity | 0.25 | 모든 Then이 구체적 반환값·예외 타입·상태를 명시 |
| independence | 0.25 | 모든 시나리오가 독립적으로 실행 가능 |
| executability | 0.20 | 모든 Given/When/Then이 구체적 파라미터로 Step 구현 가능 |
| **min_total** | | **2.5** (이하 시 REJECT) |

**weighted_total 계산**

```
weighted_total = coverage × 0.30
              + unambiguity × 0.25
              + independence × 0.25
              + executability × 0.20
```

---

### Step 4 — Validate

| 항목 | 내용 |
|---|---|
| 파일 | `pipeline/steps/validate.py` |
| 입력 | `02_output.json` + `03_verdict.json` |
| 출력 | `03_verdict.json` 덮어쓰기 (`contract_errors`, `verdict` 갱신) |
| 역할 | 코드 기반 이중 검문. AI 판정을 코드가 최종 확정한다. |
| LLM | 없음 — 순수 Python 코드로 실행 |

**검사 항목 3가지**

| 검사 | 실패 조건 | 에러 메시지 형식 |
|---|---|---|
| JSON 스키마 | `unit_tests[]` / `scenarios[]` 구조 불일치 | `schema: <jsonschema 메시지>` |
| Then 절 금지 패턴 | Then에 모호한 표현 포함 | `forbidden_then: '<name>' — '<pattern>'` |
| 품질 하한 | `weighted_total < 2.5` | `quality: <값> < 2.5` |

**금지 패턴 목록**

```python
FORBIDDEN_THEN_PATTERNS = [
    "should work", "works correctly",
    "정상 동작", "올바르게 동작", "정상적으로",
    "기대대로", "올바른 결과", "제대로 동작",
]
```

> `contract_errors`가 하나라도 있으면 `verdict`를 REJECT로 덮어쓴다.
> Eval이 PASS를 줬어도 Validate가 REJECT로 뒤집을 수 있다.

---

### Step 5 — Refine (REJECT 시만 실행)

| 항목 | 내용 |
|---|---|
| 파일 | `pipeline/steps/refine.py` |
| 모델 | `gemini-3.1-flash-lite` |
| 입력 | `content` + `weaknesses` (Critique) + `rubric_scores` (Eval) |
| 출력 | `02_output_v{n}.json` |
| 역할 | 빈틈과 낮은 점수를 받은 축을 기준으로 개선 초안 생성 |
| 프롬프트 | `prompts/refine_system.md` |

**Refine만 Critique + Eval 결과를 모두 받는다.**
Gen/Eval 격리는 유지하면서, Refine은 개선을 위해 두 결과를 모두 참조한다.

**출력 추가 필드**

| 필드 | 설명 |
|---|---|
| `applied_fixes` | 이번 개선에서 적용한 수정 사항 목록 |
| `should_iterate` | 추가 반복이 필요한지 여부 |
| `iterate_reason` | 추가 반복이 필요한 이유 |

---

## 4. 반복 루프 규칙

```
MAX_ITERATIONS = 3
```

| 상황 | 동작 |
|---|---|
| Validate PASS | 즉시 종료 → `04_next.json` |
| Validate REJECT + iteration < 3 | Refine → 다음 iteration |
| Validate REJECT + iteration == 3 | 종료 → `99_regen_request.json` |

**iteration별 파일 명명 규칙**

| iteration | output | critique | verdict |
|---|---|---|---|
| 1 | `02_output.json` | `02b_critique.json` | `03_verdict.json` |
| 2 | `02_output_v2.json` | `02b_critique_v2.json` | `03_verdict_v2.json` |
| 3 | `02_output_v3.json` | `02b_critique_v3.json` | `03_verdict_v3.json` |

---

## 5. 실행 환경

| 항목 | 값 |
|---|---|
| 언어 | Python 3.12+ |
| AI API | Google Gemini (`google-generativeai`) |
| 모델 | `gemini-3.1-flash-lite` (전 단계 공통) |
| 환경 변수 | `GEMINI_API_KEY` |
| 의존 패키지 | `google-genai`, `pyyaml`, `jsonschema` |
| 실행 위치 | `Test_Writer/` 루트 |

**실행 명령**

```bash
# 1. 샘플 입력 생성 (DefectRateCalculator)
python pipeline/sample_defect_rate.py

# 2. 대화형 입력 생성
python pipeline/create_input.py

# 3. 파이프라인 실행 (최신 run 자동 선택)
python pipeline/main.py

# 4. 특정 run 지정
python pipeline/main.py runs/20260617_194312_ba85dbb2
```

---

## 6. run 디렉토리 구조

```
runs/{YYYYMMDD_HHMMSS_uuid8}/
├── 01_input.json           입력 brief
├── 02_output.json          iteration 1 Gen 결과
├── 02b_critique.json       iteration 1 Critique 결과
├── 03_verdict.json         iteration 1 Eval + Validate 최종 판정
├── 04_next.json            PASS 시 생성 (status, iterations 기록)
├── 02_output_v2.json       iteration 2 Refine 결과 (REJECT 시)
├── 02b_critique_v2.json    iteration 2 Critique
├── 03_verdict_v2.json      iteration 2 판정
└── 99_regen_request.json   3회 REJECT 시 생성
```

> `runs/`는 `.gitignore`에 등록되어 있다. 생성된 결과물은 버전 관리하지 않는다.

---

## 7. Blog_Writer 대비 변경 스펙

| 항목 | Blog_Writer | Test_Writer |
|---|---|---|
| Gen 출력 | `content: str` (블로그 글 전문) | `unit_tests[]` + `scenarios[]` + `content` (직렬화) |
| rubric 축 | 7축 (structure/evidence/tone/hook/uniqueness/actionability/length) | 4축 (coverage/unambiguity/independence/executability) |
| validate 체크 | 글자 수(300~4000), 금지어(마케팅 표현) | JSON 스키마, Then 절 모호 패턴, 품질 하한 |
| Critique 페르소나 | 시니어 편집자 | 시니어 QA 엔지니어 |
| min_total | 2.8 | 2.5 |
| 경로 방식 | 상대 경로 (CWD 의존) | `Path(__file__)` 절대 경로 |
