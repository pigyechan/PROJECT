# CodeQuality Reviewer — 설계서

> Test_Writer(1-1)의 Gen/Critique/Eval/Validate 하네스를 코드 품질(SOLID + Rich Domain) 도메인으로
> 확장한 기록. 어디를 재사용했고, 무엇을 새로 만들었으며, 왜 그렇게 결정했는지를 남긴다.

---

## 0. 요약 (300자)

1-1(Test_Writer)의 파이프라인 골격(`main.py` 루프), Gen/Eval 격리 원칙, `rubric.yaml` 형식,
`brief_hash` 추적 방식, `validate.py`의 "AI 판정을 코드가 재검증한다"는 계약 게이트 패턴을
그대로 가져왔다. 새로 만든 것은 세 가지다. 출력 스키마를 테스트 케이스(`unit_tests`/`scenarios`)
에서 코드 리뷰 결과(`violations`/`refactor_suggestions`)로 바꿨고, rubric 축을 SOLID 리뷰
품질 기준 4개로 교체했으며, Validate에 실제 `gradle test`를 실행해 대상 프로젝트가 GREEN인지
확인하는 `_check_tests_green`을 추가했다 — 이건 1-1에는 없던, 코드 품질 도메인에만 필요한
체크다.

---

## 1. 파이프라인 흐름 (1-1과 동일한 골격)

```
01_input.json  (feature_name + code + test_project_dir)
      ↓ brief 전달
┌─────────────────────────────────────────────────────┐
│ Step 1. Gen — gen_system.md                         │
│  · violations[] + refactor_suggestions[] 출력       │
│  · 검증 불가능한 긍정 표현 금지, Fowler 기법명 필수 │
└───────────────────────┬─────────────────────────────┘
                        ↓ content만 전달 ← Gen 내부 상태 완전 차단
┌─────────────────────────────────────────────────────┐
│ Step 2. Critique — critique_system.md               │
│  · "시니어 코드 리뷰어(과설계 경계경보)" 페르소나   │
│  · 빈틈 3개 추출 (axis + reason + fix_hint)          │
│  · 최소 1개는 minimal_change(과설계) 관점 필수 검토 │
└───────────────────────┬─────────────────────────────┘
                        ↓
02b_critique.json
                        ↓ content + brief_hash만 전달
┌─────────────────────────────────────────────────────┐
│ Step 3. Eval — eval_system.md + rubric.yaml         │
│  · 4축 루브릭 가중 평균 (1–5점)                     │
└───────────────────────┬─────────────────────────────┘
                        ↓
03_verdict.json
      ↓
┌─────────────────────────────────────────────────────┐
│ Step 4. Validate — validate.py (코드 기반 게이트)   │
│  · JSON 스키마 구조 검사                            │
│  · 검증 불가능한 rationale 패턴 감지                │
│  · rubric min_total 하한 검사                       │
│  · (신규) test_project_dir 에서 실제 gradle test    │
│    실행 → BUILD SUCCESSFUL 확인                     │
└──────────┬──────────────────────┬───────────────────┘
           ↓ PASS                 ↓ REJECT (iteration < 3)
    04_next.json           Refine → 02_output_v{n}.json → Step 2로 재진입
```

**격리 원칙(1-1과 동일)**: Critique는 `content`만, Eval은 `content + brief_hash`만 받는다.
Refine만 예외적으로 Critique·Eval 결과를 모두 받아 개선안을 만든다.

---

## 2. 1-1(Test_Writer)에서 재사용한 것

### 2-1. 파이프라인 골격 (`pipeline/main.py`)

`find_latest_run()`, `get_paths()`, `MAX_ITERATIONS = 3` 반복 루프, PASS/REJECT 분기,
`sys.exit(0/1)` 반환 코드까지 전부 동일하게 가져왔다. 유일하게 추가한 줄은 `01_input.json`에서
`brief.test_project_dir`을 읽어 `validate_contract()`에 넘기는 부분뿐이다.

### 2-2. Gen/Eval 격리 구현

`critique.py`가 `artifact["content"]`만 새 API 호출로 넘기는 방식, `evaluator.py`가
`content + brief_hash`만 받는 방식이 1-1과 완전히 동일하다 — 자기 검열(같은 세션에서
"만들어줘 → 채점해줘"를 하면 점수가 부풀어 오르는 문제)을 막는 구조를 그대로 물려받았다.

### 2-3. Gemini API 호출 패턴 + JSON 파싱 방어 코드

마크다운 코드블록(` ```json ... ``` `)과 JSON 객체를 정규식으로 추출하는 로직이 1-1의
모든 step 파일과 동일하다.

### 2-4. `brief_hash` 생성 방식

`sha256(json.dumps(brief, sort_keys=True))[:16]` — 1-1과 동일. 어떤 입력에서 나온 결과인지
파일만 보고 추적 가능하다.

### 2-5. `validate.py` — 코드 기반 계약 게이트 구조

"AI가 PASS를 줘도 코드가 REJECT로 뒤집을 수 있다"는 이중 검문 구조를 그대로 가져왔다.
`_check_schema` / `_check_forbidden_*` / `_check_quality` 세 함수의 역할 분담도 동일하고,
`verdict` 딕셔너리를 덮어쓰는 방식도 동일하다.

### 2-6. `rubric.yaml` 형식

`axes` 리스트 + `weight` + `scale` 구조, `weight` 합 1.0 assert, `min_total` 필드까지
1-1과 형식이 완전히 같다. `evaluator.py`는 수정 없이 그대로 재사용했고, `rubric.yaml`
내용만 도메인에 맞게 교체했다.

### 2-7. Refine 패턴

`applied_fixes` + `should_iterate` + `iterate_reason` 구조를 그대로 재사용했다.

---

## 3. 새로 만든 것

### 3-1. 출력 스키마 — `unit_tests/scenarios` → `violations/refactor_suggestions`

| 1-1 (Test_Writer) | 이번 (CodeQuality_Reviewer) |
|---|---|
| `unit_tests[]` (name/given/when/then) | `violations[]` (principle/location/evidence/severity) |
| `scenarios[]` (title/given/when/then) | `refactor_suggestions[]` (technique/target/before_sketch/after_sketch/rationale) |

`violations`와 `refactor_suggestions`를 분리해 유지하는 이유는 1-1의 `unit_tests`/`scenarios`
분리와 같다 — Validate가 각각을 독립적으로 스키마 검사하고, `refactor_suggestions`의
`rationale`/`after_sketch`만 골라 금지 패턴을 스캔해야 하기 때문이다.

### 3-2. `config/rubric.yaml` — 4축을 코드 리뷰 기준으로 교체

| axis | weight | 5점 기준 |
|---|---:|---|
| diagnostic_accuracy | 30% | 모든 주요 SOLID/Anemic 위반을 정확히 짚고 구체적 근거 제시 |
| minimal_change | 25% | 지적한 위반 해소에 필요한 최소 범위로만 제안 (과설계 없음) |
| behavior_preservation | 25% | 동작 보존을 위해 지켜야 할 순서/제약을 명시 |
| testability_improvement | 20% | 적용 시 단위 테스트 가능해지는 지점을 구체적으로 설명 |

**축 설계 근거** (과제에서 지정한 4가지 Eval 기준을 그대로 축으로 사용):
- `diagnostic_accuracy`: 위반을 잘못 짚으면 리뷰 자체의 신뢰가 무너짐 → 최고 가중치
- `minimal_change`: 이 과제의 핵심 관심사 — "과설계 여부"를 정량적으로도 잡아낸다
- `behavior_preservation`: 리팩토링의 제1원칙(행위 보존)을 얼마나 의식했는지
- `testability_improvement`: 리팩토링의 실질적 목적(테스트 가능한 구조)을 달성했는지

### 3-3. `prompts/gen_system.md` — SOLID 위반 진단 + Fowler 기법 제안

1-1의 Then절 모호 표현 금지를 계승해, "더 좋아진다"류의 검증 불가능한 긍정 표현을
`rationale`/`after_sketch`에서 금지했다. 또한 `technique` 필드는 반드시 Fowler 카탈로그에
실존하는 기법명을 쓰도록 강제했다 — 이번 B-5 리팩토링에서 실제로 쓴 기법명(Move Method,
Extract Interface, Rename Class, Extract Method, Remove Setting Method)과 직접 비교하기
위해서다.

### 3-4. `prompts/critique_system.md` — 페르소나 교체 + 과설계 경계 임무 명시

| 항목 | 1-1 (Test_Writer) | 이번 |
|---|---|---|
| 페르소나 | 시니어 QA 엔지니어 | 시니어 코드 리뷰어 (과설계 경계경보) |
| 빈틈 axis | coverage/unambiguity/independence/executability | diagnostic_accuracy/minimal_change/behavior_preservation/testability_improvement |
| 특이 제약 | — | 3개 중 최소 1개는 반드시 `minimal_change`(과설계) 관점에서 검토 |

"과설계 여부"를 Critique의 필수 점검 항목으로 못 박은 이유: 이 과제의 목적 자체가
"파이프라인이 과설계를 제안한 사례가 있었는지"를 기록하는 것이기 때문이다. 우연히
걸리길 기다리지 않고, 매번 명시적으로 점검하게 만들었다.

### 3-5. `pipeline/steps/validate.py` — `_check_tests_green` 신규 추가

1-1의 `validate.py`에는 없던, 코드 품질 도메인에만 필요한 체크다.

```python
def _check_tests_green(test_project_dir: str | None) -> tuple[list[str], bool | None]:
    ...
    result = subprocess.run([gradle_exe, "test", "--console=plain"], cwd=..., env=..., ...)
    success = "BUILD SUCCESSFUL" in (result.stdout + result.stderr)
    ...
```

**설계 결정 — 자동 패치 적용은 v0 범위 밖**: 과제 설명은 "적용 후 1-1 테스트가 전부
GREEN인지 자동 확인"이라고 되어 있다. 이걸 문자 그대로 하려면 파이프라인이 제안한
`before_sketch`/`after_sketch`를 실제 소스 파일에 자동으로 patch 적용해야 하는데, 이건
LLM이 생성한 코드 스니펫을 무인으로 실행 가능한 코드에 자동 반영하는 것이라 리스크가 크고
scope가 크다. 그래서 v0은 범위를 좁혔다: `test_project_dir`(이번 실행에서는
`TicketService/`, 이미 B-5에서 사람이 수작업으로 리팩토링을 적용해 GREEN인 상태)의
테스트 스위트를 실제로 실행해서 "지금 이 저장소가 GREEN인가"를 코드로 확인한다. 이는
1-1의 "AI 판정을 코드가 재검증한다"는 원칙을 코드 품질 도메인에 맞게 적용한 것이다 —
Gen/Critique/Eval의 판단은 텍스트 수준이지만, Validate의 마지막 관문은 항상 실행 가능한
사실(테스트 결과)이어야 한다는 원칙은 그대로 지켰다.

자동 패치 적용은 B-7 이후 과제로 남겨두는 것을 제안한다.

### 3-6. `pipeline/sample_ticket_service.py` — B-2 원본 코드 샘플 입력 생성기

1-1의 `sample_defect_rate.py`와 동일한 역할. B-2/B-5에서 만든 실제 kata의 원본(커밋
`e3b74ab` 시점, 리팩토링 시작 전 "죽은 코드")을 그대로 brief에 담고,
`test_project_dir`을 실제 `TicketService/` 경로로 지정해 Validate가 진짜 프로젝트를
대상으로 동작하게 했다.

---

## 4. 변경한 것 (같은 역할, 다른 내용)

### 4-1. `generator.py` / `refine.py` — 출력 필드만 교체

1-1의 `unit_tests`/`scenarios` 파싱 로직 구조를 그대로 두고 필드명만
`violations`/`refactor_suggestions`로 바꿨다. 함수 시그니처, 에러 처리, `content` 직렬화
방식 모두 동일하다.

### 4-2. `validate.py` — 체크 3개는 그대로, 1개(`_check_tests_green`) 추가

`_check_schema`, `_check_forbidden_claims`(1-1의 `_check_forbidden_then`과 동일 구조,
스캔 대상 필드만 `then` → `rationale`/`after_sketch`로 교체), `_check_quality`는 그대로다.

---

## 5. 파일 구조

```
CodeQuality_Reviewer/
├── CLAUDE.md
├── README.md
├── config/
│   └── rubric.yaml                 — 4축 루브릭 (diagnostic_accuracy/minimal_change/behavior_preservation/testability_improvement)
├── docs/
│   ├── DESIGN.md                   — 이 문서
│   ├── COMPARISON.md               — 파이프라인 제안 vs B-5 수작업 리팩토링 비교
│   ├── EXECUTION_LOG.md            — 실행 로그 + 과설계 제안 사례 메모
│   └── sample-run/                 — 실제 실행 결과 원본 JSON (runs/는 gitignore 대상이라 별도 보존)
├── pipeline/
│   ├── main.py
│   ├── create_input.py
│   ├── sample_ticket_service.py    — B-2 원본 코드 샘플 입력 생성
│   └── steps/
│       ├── generator.py            — Step 1: Gen
│       ├── critique.py             — Step 2: Critique
│       ├── evaluator.py            — Step 3: Eval
│       ├── validate.py             — Step 4: Validate (+ gradle test GREEN 확인)
│       └── refine.py               — Refine (REJECT 시)
├── prompts/
│   ├── gen_system.md
│   ├── critique_system.md
│   ├── eval_system.md
│   └── refine_system.md
├── schemas/
│   ├── input.schema.json           — feature_name + code + test_project_dir(선택)
│   ├── output.schema.json          — violations[] + refactor_suggestions[]
│   └── verdict.schema.json         — rubric_scores + tests_green + verdict
└── runs/                           — 실행 결과 (gitignore)
```
