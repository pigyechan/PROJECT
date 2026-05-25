# AI 파이프라인 설계 가이드

> 다음 파이프라인을 만들 때 처음부터 헤매지 않기 위한 참고서입니다.
> Blog Writer 파이프라인(v0)을 만들면서 배운 내용을 기록했습니다.

---

## Step 0. 시작 전에 답해야 할 질문

빈 폴더에서 파이프라인을 시작하기 전에 아래 세 질문에 답할 수 있어야 합니다.
답이 없으면 루브릭도, 코드도 쓸 수 없습니다.

```
Q1. 이 파이프라인이 무엇을 만들어내는가?
    예: 독자가 읽고 다음 행동을 취하게 만드는 블로그 초안

Q2. 산출물은 어떤 형태인가?
    예: 한국어 마크다운 텍스트, 300~4000자

Q3. 어디까지가 "성공"인가?
    예: 모든 주장에 근거가 있고, 첫 문장이 독자 상황을 직격한다
```

이 세 질문이 설계 순서를 결정합니다:

```
1. 목적 정의     ← Q1
2. 산출물 정의   ← Q2
3. 루브릭 작성   ← Q3 에서 나옴
4. 단계 설계
5. 프롬프트 작성
6. 코드 작성
```

---

## Step 1. 루브릭 설계

### 루브릭이란

루브릭은 표준이 아닙니다. **직접 설계하는 것**입니다.
Evaluator AI가 무엇을 기준으로 점수를 매길지, Validator 코드가 어떤 기준으로 합격 여부를 판정할지를 정의합니다.

### 설계 방법

**1. AI가 이 산출물을 자주 망치는 패턴을 나열한다**

실패 패턴 하나가 루브릭 축 하나가 됩니다.

```
첫 문단이 배경 설명만 한다       → hook 축
주장만 있고 근거가 없다           → evidence 축
읽고 나서 뭘 해야 할지 모른다    → actionability 축
너무 짧거나 너무 길다             → length_calibration 축
```

**2. 1점 / 3점 / 5점 기준을 검증 가능한 문장으로 쓴다**

| 나쁜 기준 | 좋은 기준 |
|---|---|
| 더 자연스럽게 | 전체 문서가 브랜드 보이스 가이드 준수 |
| 훅이 약하다 | 첫 문장부터 독자 상황 직격 |
| 근거가 부족하다 | 모든 주장에 직인용·수치·케이스 중 하나 이상 |

**3. 가중치는 "이게 틀리면 치명적인가"로 결정한다**

근거 없는 주장은 아무리 구조가 좋아도 퍼블리시할 수 없다 → evidence 20%

**4. 가중치 합이 반드시 1.0인지 확인한다**

### 산출물 유형별 자주 쓰는 축 참고

| 산출물 유형 | 자주 쓰는 축 |
|---|---|
| 블로그/에세이 | hook, structure, evidence(materials 충실도 포함), tone, uniqueness, actionability |
| 기술 문서 | accuracy, completeness, clarity, reproducibility |
| 코드 리뷰 | correctness, security, readability, test_coverage |
| 요약문 | fidelity, conciseness, key_point_coverage |
| 마케팅 카피 | emotional_resonance, cta_clarity, brand_voice, specificity |

> 루브릭을 먼저 완성한 뒤 코드를 짜세요.
> rubric.yaml만 바꾸면 evaluator.py는 다음 파이프라인에서 그대로 재사용할 수 있습니다.

---

## Step 2. 파이프라인 단계 설계

### 왜 4단계인가

한 번에 "써줘"를 시키면 안 되는 이유:
- AI는 자신이 쓴 글을 스스로 잘 평가하지 못합니다 (자기 채점 편향)
- 무엇이 왜 나쁜지 추적이 안 되면 개선도 안 됩니다

### Gen과 Eval을 반드시 분리해야 하는 이유

같은 세션에서 "써줘 → 점수 매겨봐"를 하면 거의 9점이 나옵니다.
AI가 자신의 결정을 정당화하는 방향으로 채점하기 때문입니다.

해결 방법은 새 API 호출 + content만 전달입니다:

```python
# evaluator.py
user_message = {
    "artifact": artifact["content"],      # content만
    "brief_hash": artifact["brief_hash"], # 참조용 해시만
    # Generator의 히스토리, 내부 상태, 의도 — 일절 전달 안 함
}
```

### 4단계 역할 요약

| 단계 | 역할 | 입력 | 출력 |
|---|---|---|---|
| Gen | 초안 생성 | brief (topic + materials) | content |
| Critique | 약점 비평 | content만 | weaknesses[3] |
| Eval | 루브릭 채점 | content + brief_hash만 | scores + PASS/REJECT |
| Refine | 퇴고 | content + weaknesses + scores | 개선된 content |

---

## Step 3. 파일 구조 설계

### 실행 결과 파일 (runs/ 안에 생성)

```
runs/{timestamp_uuid}/
  01_input.json          — 입력 (topic + materials + tone + brief_hash)
  02_output.json         — Gen 초안
  02b_critique.json      — Critique 약점 3개
  03_verdict.json        — Eval 점수 + PASS/REJECT
  02_output_v2.json      — Refine 후 2차 초안 (반복 시)
  02b_critique_v2.json   — 2차 비평
  03_verdict_v2.json     — 2차 평가
  04_next.json           — 최종 PASS
  99_regen_request.json  — 최종 REJECT + 사유
```

파일로 남기는 이유: 에러 발생 위치 추적, 초안 간 변화 비교, 프로그램 재시작 후 재개 가능.

`brief_hash`를 모든 파일에 넣는 이유: 어떤 input에서 나온 결과인지 파일만 봐도 확인 가능.

### 설정 파일

```
config/rubric.yaml          — 루브릭 정의 (축 + 가중치 + PASS 임계값)
schemas/input.schema.json   — 01_input.json 형식 강제
schemas/output.schema.json  — 02_output.json 형식 강제
schemas/verdict.schema.json — 03_verdict.json 형식 강제
prompts/gen_system.md       — Gen 역할 지시
prompts/critique_system.md  — Critique 역할 지시
prompts/eval_system.md      — Eval 역할 지시
prompts/refine_system.md    — Refine 역할 지시
```

프롬프트를 .py 안에 하드코딩하지 않는 이유: 프롬프트만 수정할 때 코드 파일을 건드리지 않기 위해.

schema 파일이 필요한 이유: AI가 잘못된 키 이름을 쓰거나 필수 필드를 빠뜨려도 파일은 만들어집니다. schema는 "약속한 모양인지" 코드로 강제하는 틀입니다.

### Python 파일

```
pipeline/main.py               — 파이프라인 전체 실행 (지휘자)
pipeline/create_input.py       — 01_input.json 생성
pipeline/steps/generator.py    — Step 1: Gen
pipeline/steps/critique.py     — Step 2: Critique
pipeline/steps/evaluator.py    — Step 3: Eval
pipeline/steps/validate.py     — Step 3-V: 코드 기반 이중 검증
pipeline/steps/refine.py       — Step 4: Refine
```

각 파일이 하나의 역할만 하는 이유: 단일 책임 원칙(SRP). Gen을 Claude로 바꾸고 싶으면 `pipeline/steps/generator.py`만 건드리면 됩니다.

모든 단계 파일의 공통 패턴:
```python
def generate(input_path: Path, output_path: Path) -> None:
    data = json.loads(input_path.read_text(encoding="utf-8"))  # 읽기
    response = client.models.generate_content(...)              # AI 호출
    output_path.write_text(json.dumps(result, ...), ...)        # 저장
```

validate.py만 AI를 호출하지 않습니다. AI 판단은 틀릴 수 있지만 글자 수는 틀리지 않습니다.

---

## Step 4. 프롬프트 작성 원칙

- 역할을 구체적으로 지정한다 ("편집자"가 아니라 "출판 경력 10년 시니어 편집자")
- "하지 말 것"을 명시한다 (금지 규칙이 허용 규칙보다 중요)
- 출력 형식을 JSON으로 고정하고 예시를 준다
- 애매한 경우 어떻게 처리할지 적는다 ("보수적으로 낮은 점수 선택")
- AI 응답에서 마크다운 코드블록(```json ... ```)을 제거하는 파싱 로직을 반드시 추가한다

---

## 체크리스트

### 설계 단계

- [ ] 목적을 한 문장으로 쓸 수 있는가
- [ ] 산출물 형태와 성공 기준이 정의되었는가
- [ ] 루브릭 축이 실패 패턴에서 나왔는가
- [ ] 1점/3점/5점 기준이 검증 가능한 문장인가
- [ ] 가중치 합이 1.0인가

### 구현 단계

- [ ] Gen과 Eval이 다른 API 호출로 분리되어 있는가
- [ ] Evaluator가 content와 brief_hash 외에 다른 것을 받지 않는가
- [ ] 모든 AI 응답 파싱에 코드블록 제거 로직이 있는가
- [ ] 각 단계 출력이 JSON schema를 준수하는가
- [ ] 반복 횟수 상한이 설정되어 있는가
- [ ] REJECT 시 사유가 파일로 저장되는가

### 검증 단계

- [ ] 루브릭 축과 eval_system.md 내용이 일치하는가
- [ ] 2차 초안이 1차 대비 어떤 부분이 바뀌었는지 추적 가능한가

### 연관 파일 동기화 확인 단계

파일 하나가 바뀌면 연관된 파일도 함께 확인한다. (CLAUDE.md Cross-file Consistency Rules 참고)

**설정 → 실행 파일**
- [ ] rubric.yaml을 수정했다면 → evaluator.py의 rubric 읽기 경로·파싱 로직도 확인했는가
- [ ] schemas/를 수정했다면 → validate.py 및 해당 schema를 출력하는 step 파일도 확인했는가
- [ ] 프롬프트 파일을 수정했다면 → 해당 프롬프트를 읽는 step 파일 경로가 일치하는가

**설정·실행 파일 → 문서**
- [ ] rubric.yaml을 수정했다면 → eval_system.md, DESIGN.md 루브릭 표도 업데이트했는가
- [ ] 프롬프트 파일을 수정했다면 → DESIGN.md 프롬프트 전략 섹션과 일치하는가
- [ ] main.py 흐름이 바뀌었다면 → DESIGN.md 파이프라인 흐름도도 수정했는가
- [ ] 파일을 추가·이동·삭제했다면 → README.md 파일 구조, PIPELINE_GUIDE.md Python 파일 목록, import 경로를 갱신했는가

**실행 결과 → 로그**
- [ ] 실행 결과가 바뀌었다면 → EXECUTION_LOG.md 변경 이력에 기록했는가
- [ ] 위 작업이 모두 끝난 뒤 커밋했는가

---

## v0에서 발견하고 수정한 문제들

다음 파이프라인에서 같은 실수를 반복하지 않기 위해 기록합니다.

**1. eval_system.md와 rubric.yaml이 불일치**
- 문제: eval_system.md가 rubric과 다른 축을 정의. 우연히 동작했지만 system prompt가 사실상 무시되고 있던 상태.
- 교훈: 프롬프트 파일과 설정 파일이 같은 기준을 쓰는지 항상 대조할 것.

**2. Critique와 Refine 단계가 미구현**
- 문제: 설계 문서에는 있었지만 코드와 프롬프트가 없었음. main.py가 2단계만 실행.
- 교훈: 설계 문서의 구현 현황을 항상 실제 파일과 함께 관리할 것.

**3. AI 응답 마크다운 파싱 누락**
- 문제: Gemini가 ```json ... ``` 형태로 응답할 때 파싱 실패. evaluator.py에는 처리 코드가 있었지만 generator.py에는 없었음.
- 교훈: AI 응답 파싱 로직은 모든 호출 파일에 일관되게 적용할 것.

**4. Refine이 materials에 없는 내용을 만들어냈다** — 루브릭 수정으로 개선됨
- 문제: refine_system.md에 "원본 materials 범위 벗어난 내용 추가 금지"를 명시했음에도, Refine이 evidence 약점을 고치는 과정에서 materials에 없는 사례("사용자 로그 데이터 분석", "AI 기반 코드 추천")를 창작했음. evidence 점수는 올랐지만 내용의 신뢰성은 오히려 낮아진 상태.
- 수정: rubric.yaml의 evidence 척도에 "materials에 없는 내용을 사실처럼 서술하면 1점" 기준 추가.
- 결과: 루브릭 수정 후 재실행 시 Gen이 materials 범위 안에서만 작성 → evidence 3.0, 1회만에 PASS(weighted_total 3.1). 이전 run 대비 비교:

  | | 수정 전 | 수정 후 |
  |---|---|---|
  | evidence (1차 초안) | 1.0 | 3.0 |
  | weighted_total | 2.4 → REJECT | 3.1 → PASS |
  | 반복 횟수 | 2회 | 1회 |

- 교훈: 프롬프트 금지 규칙만으로는 AI의 창작 충동을 막기 어렵다. **루브릭 척도에 직접 반영하는 것이 더 효과적이다.**

**5. evidence 5.0은 materials 품질에 달려 있다** — 구조적 한계
- 발견: 수정 후 실행에서 evidence가 3.0에 머물렀음. 5점 기준("모든 주장에 근거가 있으며 해당 근거가 materials 안에 있는 내용임")을 충족하려면 materials 자체에 구체적인 수치, 사례, 인용이 있어야 한다. "AI를 똑똑하게 쓰고 있다"처럼 추상적인 재료만 들어오면 AI가 아무리 잘 써도 evidence 5.0은 불가능하다.
- 교훈: **루브릭 점수의 상한은 입력 품질이 결정한다.** 사용자에게 materials를 입력받을 때 "구체적인 수치나 사례가 있으면 품질이 올라간다"는 안내가 필요하다. v1에서는 create_input.py에 이 안내를 추가하는 것을 고려할 것.
