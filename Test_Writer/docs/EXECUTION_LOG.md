# 실행 로그 — DefectRateCalculator 테스트 생성

> run ID: `20260617_194312_ba85dbb2`
> 실행 일시: 2026-06-17 10:43 ~ 10:54 UTC
> 모델: `gemini-3.1-flash-lite`
> 결과: **1회 반복 PASS**

---

## 전체 흐름 한눈에 보기

```
[10:43] 입력 생성 (sample_defect_rate.py)
   ↓  brief_hash: e199b3398e4a1fd9
[10:43] Step 1. Gen     → unit_tests 8개 + scenarios 3개
   ↓
[10:53] Step 2. Critique → 빈틈 3개 지적
   ↓
[10:53] Step 3. Eval    → weighted_total 5.0 → PASS
   ↓
[10:53] Step 4. Validate → contract_errors 없음 → PASS
   ↓
      ★ 수렴 (iteration 1 PASS) → 04_next.json
```

반복 없이 1회 만에 통과했다. Refine 단계는 실행되지 않았다.

---

## Step 0. 입력 (`01_input.json`)

```
feature_name : DefectRateCalculator
brief_hash   : e199b3398e4a1fd9
```

입력된 요구사항:

```
calculateDefectRate(defective, total)
  - 공식: (defective / total) * 100
  - total ≤ 0  → IllegalArgumentException('전체 수는 1 이상이어야 합니다.')
  - defective < 0 → IllegalArgumentException('불량 수는 0 이상이어야 합니다.')
  - defective > total → IllegalArgumentException('불량 수는 전체 수를 초과할 수 없습니다.')

evaluateGrade(defectRate)
  - defectRate < 0 또는 > 100 → IllegalArgumentException
  - defectRate < 1.0  → "양호"
  - 1.0 ≤ defectRate < 5.0 → "주의"
  - defectRate ≥ 5.0  → "불량"

context: Java 클래스. JUnit 5 + Gherkin(Cucumber) 스타일 테스트 케이스 생성 대상.
```

---

## Step 1. Gen (`02_output.json`)

**출력: 단위 테스트 8개 + Gherkin 시나리오 3개**

### 단위 테스트 8개

| # | 테스트 이름 | Given | Then |
|---|---|---|---|
| 1 | `test_calculate_defect_rate_success` | defective=5, total=100 | 5.0 반환 |
| 2 | `test_calculate_defect_rate_total_zero_or_negative` | defective=1, total=0 | IllegalArgumentException('전체 수는 1 이상이어야 합니다.') |
| 3 | `test_calculate_defect_rate_defective_negative` | defective=-1, total=10 | IllegalArgumentException('불량 수는 0 이상이어야 합니다.') |
| 4 | `test_calculate_defect_rate_defective_exceeds_total` | defective=11, total=10 | IllegalArgumentException('불량 수는 전체 수를 초과할 수 없습니다.') |
| 5 | `test_evaluate_grade_ranges` | defectRate=0.5 | "양호" 반환 |
| 6 | `test_evaluate_grade_warning_range` | defectRate=3.0 | "주의" 반환 |
| 7 | `test_evaluate_grade_defect_range` | defectRate=5.0 | "불량" 반환 |
| 8 | `test_evaluate_grade_invalid_input` | defectRate=100.1 | IllegalArgumentException |

### Gherkin 시나리오 3개

```gherkin
Scenario: 정상적인 불량률 계산 및 등급 판정
  Given 불량 수 2와 전체 수 100이 주어짐
  When  calculateDefectRate(2, 100)을 실행하고 결과를 evaluateGrade에 전달함
  Then  결과는 '양호' 등급이 반환됨

Scenario: 잘못된 입력값에 대한 예외 처리
  Given 불량 수 10과 전체 수 5가 주어짐
  When  calculateDefectRate(10, 5)를 실행함
  Then  '불량 수는 전체 수를 초과할 수 없습니다.' 메시지를 포함한
        IllegalArgumentException이 발생함

Scenario: 경계값(주의 등급 시작) 테스트
  Given 불량률 1.0이 주어짐
  When  evaluateGrade(1.0)을 실행함
  Then  '주의' 등급이 반환됨
```

---

## Step 2. Critique (`02b_critique.json`)

시니어 QA 페르소나가 지적한 빈틈 3개:

| # | axis | 지적 내용 | 개선 방향 |
|---|---|---|---|
| 1 | `coverage` | `evaluateGrade`에서 경계값 **0과 100** 누락 | 등급 판정 로직의 각 구간 경계값(0, 100)을 포함한 케이스 추가 |
| 2 | `unambiguity` | `invalid_input` 테스트에서 구체적인 **예외 메시지 검증 없음** | 예외 메시지가 정책에 부합하는지 명확히 검증하도록 구체화 |
| 3 | `independence` | 시나리오 1이 `calculateDefectRate` 결과를 `evaluateGrade`에 **의존적으로 전달** | 각 함수를 독립적으로 검증하는 단계로 분리 |

---

## Step 3. Eval (`03_verdict.json`)

### 루브릭 점수

| axis | 점수 | 가중치 | 기여 | 평가 이유 |
|---|---|---|---|---|
| coverage | 5.0 | 30% | 1.50 | 다양한 경계값(0, 음수, 초과)과 실패 케이스 다수 포함 |
| unambiguity | 5.0 | 25% | 1.25 | 반환값과 예외 메시지를 명확히 규정하여 모호함 없음 |
| independence | 5.0 | 25% | 1.25 | 각 케이스가 독립적 입력과 기대를 가짐 |
| executability | 5.0 | 20% | 1.00 | 구체적 파라미터와 기대 결과 명시, 즉시 구현 가능 |
| **합계** | | **100%** | **5.00** | |

```
weighted_total = 5.0 × 0.30
              + 5.0 × 0.25
              + 5.0 × 0.25
              + 5.0 × 0.20
              = 5.0000

min_total = 2.5
5.0000 ≥ 2.5 → AI 판정: PASS
```

---

## Step 4. Validate (`03_verdict.json` 덮어쓰기)

코드가 직접 수행한 3가지 검사:

| 검사 항목 | 기준 | 결과 |
|---|---|---|
| JSON 스키마 | unit_tests / scenarios 배열, 각 항목에 name/given/when/then 필수 | ✅ 통과 |
| Then 절 금지 패턴 | "should work", "정상 동작", "올바르게 동작" 등 모호 표현 | ✅ 없음 |
| 품질 하한 | weighted_total ≥ 2.5 | ✅ 5.0 ≥ 2.5 |

```
contract_errors: []
최종 verdict: PASS
```

---

## 수렴 지점

### 반복 횟수 추적

파이프라인 설정: `MAX_ITERATIONS = 3`

| iteration | Gen | Critique | Eval (weighted_total) | Validate | 결과 |
|---|---|---|---|---|---|
| **1** | 8 unit_tests, 3 scenarios | 빈틈 3개 | **5.0** | contract_errors 없음 | **✅ PASS — 수렴** |
| 2 | — | — | — | — | 실행 안 됨 |
| 3 | — | — | — | — | 실행 안 됨 |

```
MAX_ITERATIONS = 3
실제 실행 횟수 = 1
수렴 iteration = 1  (최선 시나리오)
```

Refine이 한 번도 실행되지 않았다. iteration 1 Validate에서 PASS가 나오자마자 루프가 종료됐다.

만약 REJECT가 반복됐다면:

```
iteration 1 → REJECT → Refine → 02_output_v2.json
iteration 2 → REJECT → Refine → 02_output_v3.json
iteration 3 → REJECT → Refine 없이 종료 → 99_regen_request.json
```

**iteration 1 에서 즉시 수렴한 이유:**

Eval이 weighted_total 5.0을 줬기 때문이다. 그런데 Critique는 3개의 실제 빈틈을 정확히 잡았다.
이 두 결과가 모순처럼 보인다.

이유는 **Gen/Eval 격리** 때문이다.
Eval은 Critique 결과를 받지 않는다. Critique가 independence 문제를 지적했어도
Eval은 그 정보 없이 결과물만 보고 독립적으로 채점한다.
결과물 자체는 구체적인 값이 있고 구조도 맞기 때문에 높은 점수를 받았다.

즉, **"빈틈이 있어도 PASS"** 가 나올 수 있는 구조다.

---

## 관찰: Eval 관대함 문제

이번 run에서 Eval이 5.0 만점을 준 것은 지나치게 관대하다.
Critique가 지적한 3개의 빈틈은 실제로 존재한다:

- `evaluateGrade(0)`, `evaluateGrade(100)` 케이스 없음 → coverage 5.0은 과함
- 시나리오 1이 두 함수를 연결 → independence 5.0은 과함

**개선 방향:**

| 옵션 | 방법 | 효과 |
|---|---|---|
| `min_total` 상향 | 2.5 → 3.5 | 더 엄격한 통과 기준 |
| Eval 프롬프트 강화 | "5점은 드뭅니다. 평균 3.0 기준" 재강조 | 채점 보수화 |
| Critique → Validate 연동 | 지적된 axis가 낮은 점수인지 코드로 확인 | 구조적 보완 |

현재 `min_total = 2.5`는 Blog_Writer에서 가져온 기본값이다.
테스트 도메인에서는 3.0 이상으로 올리는 것이 적절하다.

---

## 생성 파일 목록

```
runs/20260617_194312_ba85dbb2/
├── 01_input.json       brief_hash: e199b3398e4a1fd9
├── 02_output.json      unit_tests 8개, scenarios 3개
├── 02b_critique.json   빈틈 3개 (coverage / unambiguity / independence)
├── 03_verdict.json     weighted_total=5.0, verdict=PASS
└── 04_next.json        status=PASS, iterations=1
```
