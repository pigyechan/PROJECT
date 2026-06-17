# Test Writer Pipeline — 설계서

> Blog_Writer(Phase 0) 구조를 테스트 케이스 생성 도메인으로 이식한 기록.
> 어디를 재사용했고, 무엇을 바꿨으며, 왜 그렇게 결정했는지를 남긴다.

---

## 0. 요약 (300자)

Blog_Writer의 파이프라인 흐름과 Gen/Eval 격리 원칙, rubric.yaml 구조, validate.py 계약 게이트는 그대로 가져왔다.

도메인에 맞게 바꾼 부분은 네 가지다. rubric 축을 블로그 기준 7개에서 테스트 품질 기준 4개로 교체했고, Gen이 텍스트 하나 대신 unit_tests와 scenarios 배열을 출력하도록 바꿨다. validate는 글자 수가 아닌 JSON 구조와 Then 절 모호 표현을 검사한다. Critique 페르소나도 편집자에서 QA 엔지니어로 전환했다.

---

## 1. 파이프라인 흐름

```
01_input.json  (feature_name + requirements)
      ↓ brief 전달
┌─────────────────────────────────────────────────────┐
│ Step 1. Gen — gen_system.md                         │
│  · unit_tests[] + scenarios[] 출력                  │
│  · Then 절 모호 표현 금지, 경계값·실패케이스 필수   │
└───────────────────────┬─────────────────────────────┘
                        ↓ content만 전달 ← Gen 내부 상태 완전 차단
┌─────────────────────────────────────────────────────┐
│ Step 2. Critique — critique_system.md               │
│  · "시니어 QA 엔지니어" 페르소나                    │
│  · 빈틈 3개 추출 (axis + reason + fix_hint)         │
└───────────────────────┬─────────────────────────────┘
                        ↓
02b_critique.json
                        ↓ content + brief_hash만 전달
┌─────────────────────────────────────────────────────┐
│ Step 3. Eval — eval_system.md + rubric.yaml         │
│  · 4축 루브릭 가중 평균 (1–5점)                     │
│  · 생성자 의도 추측 금지, 결과물만 판단             │
└───────────────────────┬─────────────────────────────┘
                        ↓
03_verdict.json
      ↓
┌─────────────────────────────────────────────────────┐
│ Step 4. Validate — validate.py (코드 기반 게이트)   │
│  · JSON 스키마 구조 검사                            │
│  · Then 절 모호 패턴 감지                           │
│  · rubric min_total 하한 검사                       │
└──────────┬──────────────────────┬───────────────────┘
           ↓ PASS                 ↓ REJECT (iteration < 3)
    04_next.json    ┌─────────────────────────────────────┐
                    │ Refine — refine_system.md           │
                    │  · content + weaknesses + scores    │
                    │  · applied_fixes[3]으로 수정 추적   │
                    │  · should_iterate 판정 포함         │
                    └──────────────┬──────────────────────┘
                                   ↓
                   02_output_v{n}.json → Step 2로 재진입
                   (최대 3회 반복, 최종 REJECT → 99_regen_request.json)
```

**격리 원칙:**

| 전달 방향 | 전달 내용 | 차단 내용 |
|---|---|---|
| Gen → Critique | content만 | Gen 히스토리, 내부 상태 |
| Gen → Eval | content + brief_hash만 | Gen 히스토리, Critique 결과 |
| Critique → Refine | weaknesses | — |
| Eval → Refine | rubric_scores | — |

---

## 2. Blog_Writer에서 재사용한 것

### 2-1. 파이프라인 골격 (`pipeline/main.py`)

Blog_Writer의 `main.py`를 거의 그대로 가져왔다.
아래 세 함수와 루프 구조가 동일하다.

```python
# Blog_Writer와 Test_Writer 모두 동일한 패턴
def find_latest_run() -> Path:
    """runs/ 디렉터리에서 01_input.json이 있는 가장 최신 폴더를 찾는다."""

def get_paths(run_dir: Path, iteration: int) -> tuple[Path, Path, Path]:
    """반복 횟수에 따라 output / critique / verdict 경로를 반환한다."""
    if iteration == 1:
        return (run_dir / "02_output.json",
                run_dir / "02b_critique.json",
                run_dir / "03_verdict.json")
    return (run_dir / f"02_output_v{iteration}.json", ...)

for iteration in range(1, MAX_ITERATIONS + 1):
    critique(output_path, critique_path)   # Step 2
    evaluate(output_path, verdict_path)    # Step 3
    validate_contract(output_path, ...)    # Step 4
    if result == "PASS": sys.exit(0)
    refine(...)                            # 다음 반복 준비
```

`MAX_ITERATIONS = 3`, 파일 명명 규칙(`02_output_v{n}`), PASS/REJECT 분기 방식, `sys.exit(0/1)` 반환 코드까지 동일하다.

---

### 2-2. Gen/Eval 격리 구현

Critique와 Evaluator가 Gen의 대화 히스토리를 볼 수 없도록 `content`만 추출해 새 API 호출로 넘기는 방식이 Blog_Writer와 동일하다.

```python
# critique.py — Blog_Writer, Test_Writer 둘 다 동일
artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

# content만 전달 — Gen 내부 상태 차단
user_message = {"content": artifact["content"]}

response = client.models.generate_content(
    model=MODEL,
    contents=json.dumps(user_message, ensure_ascii=False),
    config=types.GenerateContentConfig(system_instruction=CRITIQUE_SYSTEM_PROMPT),
)
```

같은 세션에서 "써줘 → 채점해줘"를 하면 AI가 자신의 결과를 방어적으로 채점해 점수가 부풀어오른다. 새 API 호출 + content만 전달로 이 편향을 차단한다.

---

### 2-3. Gemini API 호출 패턴

AI 응답에서 마크다운 코드블록과 JSON을 추출하는 파싱 로직이 동일하다.

```python
# Blog_Writer, Test_Writer 모두 동일하게 적용
raw = response.text.strip()
code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", raw)
if code_block:
    raw = code_block.group(1).strip()
json_match = re.search(r"\{[\s\S]*\}", raw)
if json_match:
    raw = json_match.group(0)
```

Gemini는 JSON만 달라고 해도 ` ```json ... ``` ` 형태로 응답하는 경우가 많다. 모든 step 파일에 이 방어 코드가 들어간다.

---

### 2-4. `create_input.py` — brief_hash 생성 방식

입력 brief를 `sha256` 해시하여 16자 hex 문자열로 만들고, 이를 `brief_hash`로 모든 중간 파일에 기록하는 방식이 동일하다.

```python
# Blog_Writer, Test_Writer 둘 다 동일
def make_brief_hash(brief: dict) -> str:
    serialized = json.dumps(brief, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(serialized).hexdigest()[:16]
```

`brief_hash`를 쓰는 이유: 어떤 입력에서 나온 결과인지 파일만 봐도 추적 가능하고, 같은 입력을 두 번 실행했을 때 같은 해시가 나와 비교가 쉽다.

---

### 2-5. `validate.py` — 코드 기반 계약 게이트 구조

AI가 채점한 결과를 코드가 다시 검증하는 이중 검문 패턴이 동일하다.

```python
# Blog_Writer, Test_Writer 둘 다 동일한 구조
def validate_contract(artifact_path, verdict_path) -> dict:
    errors = []
    errors += check_A(artifact)   # Blog_Writer: check_schema
    errors += check_B(artifact)   # Blog_Writer: check_length
    errors += check_C(rubric)     # Blog_Writer: check_banned
    errors += check_quality(...)  # 동일

    verdict = {**verdict_existing, "contract_errors": errors,
               "verdict": "REJECT" if errors else "PASS"}
    Path(verdict_path).write_text(...)  # verdict 덮어쓰기
    return verdict
```

AI 평가자는 틀릴 수 있지만 코드는 틀리지 않는다. Eval이 PASS를 줬더라도 Validate에서 구조 오류가 발견되면 REJECT로 덮어쓴다.

---

### 2-6. `rubric.yaml` 형식

list 기반 axes 구조, `weight` 합 1.0 assert, `min_total` 필드 형식이 동일하다.

```yaml
# Blog_Writer, Test_Writer 둘 다 동일한 형식
axes:
  - name: coverage
    weight: 0.30
    scale:
      1: "..."
      3: "..."
      5: "..."
min_total: 2.5
```

```python
# evaluator.py에서 동일하게 파싱
assert abs(sum(a["weight"] for a in RUBRIC["axes"]) - 1.0) < 1e-6, \
    "rubric weight 합이 1.0이 아닙니다."
weights = {a["name"]: a["weight"] for a in RUBRIC["axes"]}
```

rubric.yaml 형식만 지키면 evaluator.py는 다음 파이프라인에서도 수정 없이 재사용 가능하다.

---

### 2-7. Refine 패턴

약점 + 루브릭 점수를 바탕으로 개선 초안을 만들고 `should_iterate`로 반복 여부를 판정하는 구조가 동일하다.

```python
# Blog_Writer refine.py와 동일한 입력 구조
user_message = {
    "brief_hash": artifact["brief_hash"],
    "content": artifact["content"],
    "weaknesses": critique_data["weaknesses"],    # Critique 결과
    "rubric_scores": verdict_data["rubric_scores"]["scores"],  # Eval 점수
}
```

---

## 3. 새로 만든 것

### 3-1. `config/rubric.yaml` — 4축으로 교체

Blog_Writer의 7축(`structure / evidence / tone / hook / uniqueness / actionability / length`)을 테스트 케이스 품질 기준인 4축으로 전면 교체했다.

| Axis | Weight | 1점 | 3점 | 5점 |
|---|---:|---|---|---|
| coverage | **30%** | 정상 케이스만 있음. 경계값·실패 케이스 전혀 없음 | 일부 경계값 포함, 실패 케이스 1개 이하 | 경계값(min/max/zero/negative) + 실패 케이스 2개 이상 |
| unambiguity | 25% | "정상 동작", "should work" 등 모호한 Then만 있음 | 일부 Then은 구체적, 일부는 모호 | 모든 Then이 구체적 반환값·예외 타입·상태를 명시 |
| independence | 25% | 시나리오 간 공유 상태·실행 순서 의존 다수 | 대부분 독립적이나 1-2개 순서 의존 있음 | 모든 시나리오가 독립적으로 실행 가능 |
| executability | 20% | 추상적 설명만 있어 Step 정의 구현 불가 | 일부 Step은 구현 가능하나 나머지는 모호 | 모든 Given/When/Then이 구체적 파라미터와 함께 Step으로 구현 가능 |

**축 설계 근거:**
- `coverage`: 경계값·실패 케이스를 빠뜨리는 것이 테스트에서 가장 흔한 실패 패턴 → 가중치 최고(30%)
- `unambiguity`: "정상 동작한다"는 Then은 검증 불가능 → 테스트의 존재 이유를 흔드는 문제
- `independence`: 시나리오가 실행 순서에 의존하면 CI 환경에서 간헐적 실패 발생
- `executability`: Cucumber Step 정의로 구현 불가능한 케이스는 실제로 쓸 수 없음

---

### 3-2. `prompts/gen_system.md` — 출력 형식 변경

Blog_Writer Gen은 단일 `content(str)`를 출력했지만, Test_Writer Gen은 구조화된 배열 두 개를 출력한다.

**Blog_Writer Gen 출력:**
```json
{ "content": "블로그 본문 텍스트..." }
```

**Test_Writer Gen 출력:**
```json
{
  "unit_tests": [
    {
      "name": "test_calculate_defect_rate_exception_total_zero",
      "given": "defective = 5, total = 0",
      "when": "calculateDefectRate(5, 0) 호출",
      "then": "IllegalArgumentException('전체 수는 1 이상이어야 합니다.') 발생"
    }
  ],
  "scenarios": [
    {
      "title": "전체 수가 0인 경우의 불량률 계산 예외 처리",
      "given": "불량 수는 5, 전체 수는 0",
      "when": "calculateDefectRate(5, 0)를 호출할 때",
      "then": "IllegalArgumentException이 발생하며, 메시지는 '전체 수는 1 이상이어야 합니다.'이다."
    }
  ]
}
```

Then 절 금지 패턴도 명시적으로 추가했다:
`"should work"`, `"works correctly"`, `"정상 동작"`, `"올바르게 동작"`, `"정상적으로"`, `"기대대로"`, `"올바른 결과"`

---

### 3-3. `prompts/critique_system.md` — 페르소나 교체

| 항목 | Blog_Writer | Test_Writer |
|---|---|---|
| 페르소나 | 출판 경력 10년 시니어 편집자 | 테스트 설계 경험 10년 시니어 QA 엔지니어 |
| 약점 axis | structure / evidence / tone / hook / uniqueness / actionability / length | coverage / unambiguity / independence / executability |
| 지적 대상 | 구조, 근거 부족, 톤 이탈 | 경계값 누락, 모호한 Then, 순서 의존, 구현 불가 단계 |

Critique가 지적할 수 있는 axis를 rubric.yaml의 4개로 제한한 이유: 루브릭에 없는 기준으로 비평하면 Refine이 그 방향으로 수정해도 Eval 점수가 오르지 않아 루프가 비효율적으로 돈다.

---

### 3-4. `pipeline/steps/validate.py` — 체크 항목 교체

Blog_Writer validate.py의 체크 항목:
- `check_schema`: artifact JSON 구조
- `check_length`: 본문 300~4,000자
- `check_banned`: "무조건", "완벽", "절대", "반드시" 포함 금지

Test_Writer validate.py의 체크 항목 (같은 구조, 다른 내용):
- `_check_schema`: `unit_tests[]`와 `scenarios[]` 배열 구조 (각 항목에 name/given/when/then 필수)
- `_check_forbidden_then`: **unit_tests와 scenarios의 then 필드만** 스캔하여 모호 패턴 감지
- `_check_quality`: rubric weighted_total ≥ min_total (동일)

```python
# Test_Writer에 추가된 then 필드 특정 스캔
def _check_forbidden_then(artifact: dict) -> list[str]:
    errors = []
    for test in artifact.get("unit_tests", []):
        then_text = test.get("then", "")
        for pattern in FORBIDDEN_THEN_PATTERNS:
            if pattern in then_text:
                errors.append(
                    f"forbidden_then: unit_test '{test.get('name', '?')}' — '{pattern}'"
                )
    # scenarios도 동일하게 스캔
    ...
```

블로그에서는 "본문 전체"에서 금지어를 찾았지만, 테스트에서는 "then 필드만" 검사한다. `given`이나 `when`에 "정상 동작"이 들어가도 문제없지만 `then`에 들어가면 검증 불가능한 테스트가 된다.

---

### 3-5. `pipeline/sample_defect_rate.py` — Blog_Writer에 없는 파일

DefectRateCalculator의 요구사항을 코드로 하드코딩한 샘플 입력 생성기다.
Blog_Writer의 `create_input.py`는 대화형 입력만 지원하지만, 이 파일은 실행하면 즉시 DefectRateCalculator 전용 `01_input.json`을 생성한다.

샘플에 포함된 요구사항:
- `calculateDefectRate(defective, total)`: 불량률 계산 공식 및 세 가지 예외 조건
- `evaluateGrade(defectRate)`: 세 등급 판정 (양호/주의/불량) 및 범위 초과 예외

---

## 4. 변경한 것 (같은 역할, 다른 내용)

### 4-1. `generator.py` — 출력 구조 확장

Blog_Writer generator.py는 AI 응답에서 `content(str)` 하나만 추출했다.
Test_Writer generator.py는 `unit_tests[]`, `scenarios[]` 두 배열을 파싱한 뒤, Critique/Eval에 전달할 텍스트 표현을 `content`로 직렬화한다.

```python
# Test_Writer generator.py
parsed = json.loads(raw)
unit_tests = parsed.get("unit_tests", [])
scenarios  = parsed.get("scenarios", [])

# content: Critique / Eval 에 전달할 텍스트 표현
content = json.dumps({"unit_tests": unit_tests, "scenarios": scenarios},
                     ensure_ascii=False, indent=2)

artifact = {
    "brief_hash": ...,
    "unit_tests": unit_tests,   # 추가: Validate가 구조 검사에 사용
    "scenarios": scenarios,     # 추가: Validate가 구조 검사에 사용
    "content": content,         # 기존: Critique/Eval에 전달
    ...
}
```

`unit_tests`와 `scenarios`를 별도 필드로 유지하는 이유: Validate가 `then` 필드를 직접 꺼내 모호 패턴을 검사하려면 문자열이 아니라 파싱된 배열이 필요하기 때문이다.

---

### 4-2. `refine.py` — `applied_fixes` 추적 추가

Blog_Writer refine.py는 개선된 `content`와 `should_iterate` 판정만 출력했다.
Test_Writer refine.py는 여기에 `applied_fixes[3]`를 추가해 어떤 axis의 빈틈을 어떻게 고쳤는지 추적한다.

```python
# Test_Writer refine.py 출력 구조
artifact_refined = {
    "unit_tests": unit_tests,
    "scenarios": scenarios,
    "content": content,
    "applied_fixes": parsed.get("applied_fixes", []),  # 추가
    # 예시:
    # [{"axis": "coverage", "fix": "evaluateGrade 경계값 0, 100 케이스 추가"},
    #  {"axis": "unambiguity", "fix": "예외 메시지 문자열 구체적으로 명시"},
    #  {"axis": "independence", "fix": "calculateDefectRate와 evaluateGrade를 별도 시나리오로 분리"}]
    "should_iterate": ...,
    "iterate_reason": ...,
}
```

`applied_fixes`가 있으면 2차 초안과 1차 초안을 비교할 때 "어떤 빈틈이 어떻게 수정됐는지" 파일만 봐도 알 수 있다.

---

### 4-3. 경로 방식 — 상대 경로 → 절대 경로

Blog_Writer의 step 파일들은 상대 경로를 사용해 프로젝트 루트에서만 실행 가능했다.

```python
# Blog_Writer (상대 경로 — 실행 위치에 의존)
GEN_SYSTEM_PROMPT = Path("prompts/gen_system.md").read_text(encoding="utf-8")
RUBRIC = yaml.safe_load(Path("config/rubric.yaml").read_text(encoding="utf-8"))
```

Test_Writer는 Career_Planner 패턴을 차용해 `Path(__file__)`로 절대 경로를 계산한다.

```python
# Test_Writer (절대 경로 — 어디서 실행해도 동작)
_ROOT = Path(__file__).parent.parent.parent   # Test_Writer/ 루트
EVAL_SYSTEM_PROMPT = (_ROOT / "prompts" / "eval_system.md").read_text(encoding="utf-8")
RUBRIC = yaml.safe_load((_ROOT / "config" / "rubric.yaml").read_text(encoding="utf-8"))
```

---

## 5. 실행 결과 (DefectRateCalculator)

### 입력

```json
{
  "feature_name": "DefectRateCalculator",
  "requirements": "calculateDefectRate(defective, total): 불량률(%) 계산...\nevaluateGrade(defectRate): 품질 등급 반환 (양호/주의/불량)..."
}
```

### Step 1 Gen 출력 요약

단위 테스트 8개 / Gherkin 시나리오 3개 생성.
경계값(defective=0, total=0, defective=total), 예외 케이스(음수 입력, total 초과) 모두 포함됨.

### Step 2 Critique 지적 내용

| # | axis | 지적 내용 |
|---|---|---|
| 1 | coverage | `evaluateGrade` 에서 경계값 0, 100 누락 |
| 2 | unambiguity | `invalid_input` 테스트에서 예외 메시지 문자열 없이 "발생"만 명시 |
| 3 | independence | `calculateDefectRate` 결과를 `evaluateGrade`에 직접 전달하는 조합 시나리오 → 독립성 위반 |

### Step 3 Eval 점수

| axis | 점수 | 이유 |
|---|---|---|
| coverage | 5.0 | 경계값(0, 음수, 초과)과 실패 케이스 다수 포함 |
| unambiguity | 5.0 | 반환값과 예외 메시지 명확히 규정 |
| independence | 5.0 | 각 케이스가 독립적 입력과 기대를 가짐 |
| executability | 5.0 | 구체적 파라미터와 기대 결과 명시 |
| **weighted_total** | **5.0** | |

### Step 4 Validate 결과

schema 구조 이상 없음 / then 절 모호 패턴 없음 / 품질 하한(2.5) 충족 → **PASS**

**→ 1회 반복 만에 PASS** `04_next.json` 생성.

> **평가자 관대함 주의**: Eval이 5.0을 줬지만 Critique는 실제 빈틈을 정확히 지적했다.  
> Gen이 잘 만들어진 경우에도 Eval은 너그러운 경향이 있다.  
> 실제 운영에서는 `min_total`을 3.0 이상으로 조정하거나 Eval 프롬프트에 "5점은 드뭅니다" 기준을 더 강하게 명시할 필요가 있다.

---

## 6. 파일 구조

```
Test_Writer/
├── CLAUDE.md                       — 프로젝트 규칙 + 연관 파일 동기화 규칙
├── config/
│   └── rubric.yaml                 — 4축 루브릭 (coverage/unambiguity/independence/executability)
├── docs/
│   └── DESIGN.md                   — 이 문서
├── pipeline/
│   ├── main.py                     — 파이프라인 전체 실행 (지휘자)
│   ├── create_input.py             — 대화형 입력 생성
│   ├── sample_defect_rate.py       — DefectRateCalculator 샘플 입력 생성
│   └── steps/
│       ├── generator.py            — Step 1: Gen
│       ├── critique.py             — Step 2: Critique
│       ├── evaluator.py            — Step 3: Eval
│       ├── validate.py             — Step 4: Validate (코드 기반)
│       └── refine.py               — Refine (REJECT 시)
├── prompts/
│   ├── gen_system.md               — Gen 역할 지시 + 출력 형식
│   ├── critique_system.md          — 시니어 QA 페르소나 + 빈틈 유형
│   ├── eval_system.md              — 루브릭 기반 채점 지시
│   └── refine_system.md            — 개선 지시 + applied_fixes 출력
├── schemas/
│   ├── input.schema.json           — feature_name + requirements 구조
│   ├── output.schema.json          — unit_tests[] + scenarios[] 구조
│   └── verdict.schema.json         — rubric_scores + verdict 구조
└── runs/
    └── {timestamp_uuid}/
        ├── 01_input.json
        ├── 02_output.json
        ├── 02b_critique.json
        ├── 03_verdict.json
        └── 04_next.json  또는  99_regen_request.json
```
