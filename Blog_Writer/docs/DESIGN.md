# Blog Writer Pipeline — 하네스 설계서

> 최종 업데이트: 2026-05-24 · 모델: gemini-2.5-flash-lite · 루브릭 버전: v1

---

## 1. Gen/Eval 분리 구조

Gen과 Eval은 반드시 다른 API 호출로 분리한다.
같은 세션에서 "생성 → 평가"를 시키면 AI가 자신의 결과물을 방어적으로 채점해 점수가 부풀어오른다.

```
01_input.json
      ↓ brief 전달
┌─────────────────────────────────────────────────────┐
│ Step 1. Gen — gen_system.md                         │
│  · content 만 출력 (자기평가·자기해설 금지)           │
└───────────────────────┬─────────────────────────────┘
                        ↓
02_output.json
                        ↓ content 만 전달 ← Gen 내부 상태 완전 차단
┌─────────────────────────────────────────────────────┐
│ Step 2. Critique — critique_system.md               │
│  · "시니어 편집자" 페르소나, Gen 히스토리 전달 금지   │
│  · 약점 3개 추출 (axis + reason + fix_hint)          │
└───────────────────────┬─────────────────────────────┘
                        ↓
02b_critique.json
                        ↓ content + brief_hash 만 전달
┌─────────────────────────────────────────────────────┐
│ Step 3. Eval — eval_system.md + rubric.yaml         │
│  · 7축 루브릭 가중 평균 (1–5점)                      │
│  · Generator 의도 추측 금지, 결과물만 판단            │
└───────────────────────┬─────────────────────────────┘
                        ↓
03_verdict.json
      ↓
[Validator] schema + 글자 수 + 금지어 + 품질 하한
      ↓ PASS                      ↓ REJECT (iteration < 3)
04_next.json          ┌──────────────────────────────────┐
                      │ Step 4. Refine — refine_system.md │
                      │  · content + weaknesses + scores  │
                      │  · 약점 3개 각각 수정 반영         │
                      │  · should_iterate 판정 포함        │
                      └─────────────────┬────────────────┘
                                        ↓
                      02_output_v{n}.json → Step 2 로 재진입
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

## 2. 4단계 프롬프트 전략

### Step 1 — Gen (초안 생성)

**목표:** topic + materials → 수정 가능한 품질 높은 초안

| 항목 | 내용 |
|------|------|
| 역할 | "전문 블로그 초안 작성 AI" — 편집자·평가자 역할 금지 |
| 출력 형식 | JSON 고정 `{"title", "summary", "content", "keywords"}` |
| 핵심 제약 | 추측성 정보·근거 없는 통계·허위 정보 생성 금지 |
| 정보 부족 시 | `{"error": "insufficient_information"}` 반환, 추측 금지 |
| 자기평가 금지 | 초안 품질에 대한 자체 해설·메모 출력 금지 |

---

### Step 2 — Critique (비평)

**목표:** 초안의 핵심 약점 3개를 독립적 시각으로 추출

| 항목 | 내용 |
|------|------|
| 역할 | "시니어 편집자" — 출판 10년 경력, 독자 대변 |
| 입력 | `content` 텍스트만. Gen 히스토리 전달 금지 |
| 출력 구조 | `weaknesses[3]` — 각 항목: `axis` / `reason` / `fix_hint` |
| axis 제약 | rubric.yaml의 7개 축 중 하나만 사용 |
| 건설적 비평 | 칭찬 금지. 개선 가능한 약점만 서술 |
| 개수 고정 | 반드시 3개. 미만·초과 모두 ValueError 처리 |

출력 예시:
```json
{
  "weaknesses": [
    {
      "axis": "evidence",
      "reason": "2문단의 '효과가 크다'는 주장에 수치·케이스 없음",
      "fix_hint": "구체적 사례 1개 또는 인용 통계 추가"
    }
  ]
}
```

---

### Step 3 — Eval (품질 평가)

**목표:** rubric 7축 기반 가중 평균 산출 + PASS/REJECT 판정

| 항목 | 내용 |
|------|------|
| 역할 | "블로그 품질 평가 AI" — rubric 외 기준 추가 금지 |
| 입력 | `content` + `brief_hash` + `rubric.yaml` 전체 |
| 독립성 | Generator 의도 추측 금지, 결과물만 판단 |
| 점수 보정 | "5점은 드뭅니다. 평균 기준 3.0" 명시 |
| 애매한 경우 | 보수적으로 평가 (낮은 점수 선택) |
| 출력 형식 | `{"scores": {...}, "reasons": {...}}` |

---

### Step 4 — Refine (퇴고)

**목표:** 비평 + 평가 근거로 개선 초안 생성 + 반복 여부 판정

| 항목 | 내용 |
|------|------|
| 역할 | "전문 에디터 겸 재작성 AI" |
| 입력 | `content` + `weaknesses[3]` + `rubric_scores` |
| 수정 우선순위 | 가중치 높은 축(evidence 20%, structure 15%)부터 처리 |
| 약점 반영 | 각 `fix_hint` 명시적 반영, `applied_fixes`로 추적 |
| 창작 제약 | 원본 materials 범위 벗어난 내용 추가 금지 |
| 반복 판정 | `should_iterate: bool` + `iterate_reason` 출력 |
| 출력 형식 | `{"content", "applied_fixes[3]", "should_iterate", "iterate_reason"}` |

---

## 3. 루브릭 점수 기준

점수 범위: **1–5점** · 합산 방식: **가중 평균** · 출처: `rubric.yaml`

| Axis | Weight | 1점 | 3점 | 5점 |
|------|-------:|-----|-----|-----|
| evidence | **20%** | 모든 주장에 근거 없음, 또는 materials에 없는 내용을 사실처럼 서술 | 일부 주장에만 근거, 근거가 materials 범위 안인지 불분명 | 모든 주장에 근거가 있으며 해당 근거가 materials 안에 있는 내용임 |
| structure | 15% | 주장·근거·예시 한 덩어리 | 구분 있으나 불균형 | 3요소 균형 + 결론 명시 분리 |
| tone | 15% | 브랜드 톤 이탈·외국어 혼재 | 대부분 유지, 1–2문장 이탈 | 전체 브랜드 보이스 준수 |
| hook | 15% | 배경 설명으로 시작, 핵심 지연 | 두 번째 문단에서 핵심 등장 | 첫 문장부터 독자 상황 직격 |
| uniqueness | 15% | 일반론 나열, 고유 관점 없음 | 저자 관점 한 군데 등장 | 여러 문단에 고유 비유·조어 |
| actionability | 10% | 다음 행동 모호 | 다음 행동 암시, 비구체적 | 다음 행동 명시 + 소요 시간 |
| length_calibration | 10% | 의도 길이 50% 미만 또는 200% 초과 | 범위 내, 문단 밀도 불균일 | 범위 내 + 문단별 밀도 균일 |

### PASS 조건 (이중 검문)

| 검문 주체 | 기준 | 임계값 |
|-----------|------|--------|
| Evaluator (AI) | rubric 가중합 | ≥ **2.8** |
| Validator (코드) | 가중합 재확인 | ≥ **2.5** |
| Validator (코드) | 본문 글자 수 | 300 – 4,000자 |
| Validator (코드) | 금지어 포함 여부 | 무조건·완벽보장·절대안전·반드시성공 |

REJECT 시 → `99_regen_request.json`에 점수·사유 기록.

### evidence 점수 설계 시 주의사항

evidence 5.0 기준("모든 주장에 근거가 있으며 해당 근거가 materials 안에 있는 내용")은 **입력된 materials의 품질에 달려 있다.**

- materials에 구체적인 수치, 사례, 인용이 있으면 → 5.0 도달 가능
- materials가 추상적인 경험 서술("AI를 잘 쓰게 됐다")뿐이면 → 3.0이 상한

루브릭이 아무리 엄격해도 입력 재료가 빈약하면 점수 상한이 낮아진다. materials 입력 단계에서 사용자에게 구체적인 재료를 요청하는 것이 품질 향상의 선행 조건이다.
