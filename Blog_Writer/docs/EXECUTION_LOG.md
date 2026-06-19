# 파이프라인 실행 로그

총 2회의 실행 기록이 있다. 실행 1은 Refine 루프가 실제로 작동한 2회 반복 케이스이고, 실행 2는 루브릭 수정 후 1회만에 수렴한 케이스다.

---

# 실행 1 — Refine 반복 발생 (2회 반복)

> **Run ID:** `20260524_202723_f52d016a`
> **실행일:** 2026-05-24
> **brief_hash:** `49985c3410c03e81`
> **최종 결과:** PASS (iteration 2 — Refine 후 수렴)

---

## 실행 요약

| Step | 역할 | 반복 | 결과 |
|------|------|------|------|
| Step 1 | Gen | 1회 | 초안 생성 |
| Step 2 | Critique | 1회 | 약점 3개 추출 (hook / evidence / actionability) |
| Step 3 | Eval | 1회 | weighted_total **2.4 → REJECT** |
| Step 4 | Refine | 1회 | 약점 반영 2차 초안 생성 |
| Step 2 | Critique (v2) | 2회 | 약점 3개 추출 (structure / evidence / hook) |
| Step 3 | Eval (v2) | 2회 | weighted_total **3.3 → PASS** |

> **수렴 지점:** Iteration 2, Step 3 Eval에서 weighted_total 3.3 ≥ 2.8 달성.

---

## Step 0. 입력

```json
{
  "topic": "내가 그릿에 온 이유",
  "materials": [
    "처음에는 포트폴리오를 쌓으려고 들어옴.",
    "혼자 공부하는 방법을 잘 몰라 능동적으로 공부하는 사람이 되고파 신청하게 됨.",
    "AI에 대해 생각보다 많이 물어봐서 당황했음.",
    "백엔드와 AI가 큰 영향이 있을까 의문이 들었음.",
    "프로그램을 진행하면서 그 생각은 잘못됐다고 느낌.",
    "AI를 똑똑하게 쓰고있는 방법을 배우고 있다고 생각함."
  ],
  "tone": "블로그 소개용. 너무 친화적이지 않았으면 좋겠지만 딱딱하지 않았으면 좋겠음."
}
```

---

## Iteration 1

### Step 1 — Gen

**모델:** `gemini-2.0-flash`

```
# GRIT, 그 시작은 포트폴리오 때문이었다

솔직히 말해, GRIT에 처음 발을 들인 이유는 포트폴리오를 채우고 싶었기 때문입니다.
개발자로서의 경험을 쌓고, 이를 증명할 수 있는 결과물을 만들고 싶었죠.
하지만 그뿐만이 아니었습니다. 혼자 공부하는 습관은 부족했고, 능동적으로 학습하는
방법을 체득하는 것이 시급했습니다.

## 예상치 못한 만남, AI에 대한 놀라움

GRIT에 참여하면서 가장 놀랐던 점 중 하나는 AI에 대한 질문이 예상보다 훨씬 많다는
것이었습니다. 처음에는 백엔드 개발과 AI가 어떤 직접적인 연관성이 있을지 의문이
들기도 했습니다. 과연 AI가 백엔드 개발에 큰 영향을 미칠 수 있을까 하는 생각이었죠.

## 편견을 깨다: AI와 백엔드의 시너지

하지만 GRIT 프로그램을 진행하면서 이러한 생각은 완전히 잘못되었음을 깨달았습니다.
AI는 단순히 흥미로운 기술이 아니라, 백엔드 개발의 효율성을 극대화하고 새로운 가능성을
열어주는 강력한 도구였습니다. 현재 저는 AI를 똑똑하게 활용하는 방법을 배우고 있으며,
이는 제 개발 역량을 한 단계 끌어올릴 것이라 확신합니다.
```

---

### Step 2 — Critique (iteration 1)

**모델:** `gemini-2.5-flash-lite` / 입력: content만

| # | Axis | 문제 요약 | 개선 제안 |
|---|------|-----------|-----------|
| 1 | **hook** | 첫 문단 동기는 명확하지만 독자 흥미 유발 요소 부족 | 개발자 고민 공감 요소 또는 구체적 에피소드 추가 |
| 2 | **evidence** | "AI가 개발 전반에 큰 영향"이라는 주장에 구체적 사례 없음 | AI 활용 사례(기능 구현 방식, 개발 시간 단축 경험) 1~2개 제시 |
| 3 | **actionability** | 마무리가 "성장해 나갈 것"에 그쳐 독자가 취할 행동 없음 | 다른 개발자도 적용 가능한 학습법·팁 1가지 이상 제시 |

---

### Step 3 — Eval (iteration 1)

**모델:** `gemini-2.0-flash` / 입력: content + brief_hash만

| Axis | Weight | Score |
|------|-------:|------:|
| evidence | 20% | **1.0** |
| structure | 15% | 3.0 |
| tone | 15% | **5.0** |
| hook | 15% | 3.0 |
| uniqueness | 15% | **1.0** |
| actionability | 10% | **1.0** |
| length_calibration | 10% | 3.0 |
| **weighted_total** | | **2.4** |

**판정:** `REJECT` — 임계값 2.8 미달 / contract_errors: `quality: 2.40 < 2.5`

---

### Step 4 — Refine (iteration 1)

**입력:** content + weaknesses[3] + rubric_scores

Critique의 약점 3개를 반영해 2차 초안 생성. applied_fixes 요약:

| Axis | 수정 내용 |
|------|-----------|
| hook | 제목을 "GRIT, 포트폴리오를 넘어 AI와 백엔드의 시너지를 발견하다"로 교체. 첫 문단에 개발자 공감 동기 추가 |
| evidence | 데이터 전처리 자동화, 사용자 로그 분석, AI 기반 코드 추천·오류 감지 사례 추가 |
| actionability | "작은 규모로 시작하여 점진적으로 확장" 팁을 마지막 문단에 명시 |

**should_iterate:** `false` (Refine 스스로 추가 반복 불필요 판단)

> ⚠️ **v0 한계 확인:** evidence 개선을 위해 Refine이 materials에 없는 내용("사용자 로그 데이터 분석", "AI 기반 코드 추천")을 창작했다. 이후 rubric.yaml evidence 척도를 수정하여 재실행(실행 2)에서 이 문제를 억제했다.

---

## Iteration 2

### Step 2 — Critique (iteration 2)

| # | Axis | 문제 요약 | 개선 제안 |
|---|------|-----------|-----------|
| 1 | **structure** | 제목에서 'AI와 백엔드 시너지'를 암시하지만 본문은 AI 사례 나열에 그침 | 시너지가 구체적으로 어떻게 발생하는지에 초점을 맞춰 재구성 |
| 2 | **evidence** | 로그 분석·코드 추천 사례가 언급되지만 어떤 데이터·모델·결과인지 불분명 | 도구·데이터 종류·결과 수치 구체화 |
| 3 | **hook** | "포트폴리오 채우기" 동기가 여전히 일반적 | AI·백엔드 시너지라는 주제가 왜 중요한지 독창적 통찰 추가 |

---

### Step 3 — Eval (iteration 2)

| Axis | Weight | Score |
|------|-------:|------:|
| evidence | 20% | 3.0 |
| structure | 15% | 3.0 |
| tone | 15% | **5.0** |
| hook | 15% | 3.0 |
| uniqueness | 15% | 3.0 |
| actionability | 10% | 3.0 |
| length_calibration | 10% | 3.0 |
| **weighted_total** | | **3.3** |

**판정:** `PASS` — contract_errors 없음

---

## 점수 변화 요약 (실행 1)

| Axis | Iteration 1 | Iteration 2 | 변화 |
|------|------------:|------------:|------|
| evidence | 1.0 | 3.0 | ▲ +2.0 |
| uniqueness | 1.0 | 3.0 | ▲ +2.0 |
| actionability | 1.0 | 3.0 | ▲ +2.0 |
| tone | 5.0 | 5.0 | — |
| 나머지 | 3.0 | 3.0 | — |
| **weighted_total** | **2.4** | **3.3** | **▲ +0.9** |

---

---

# 실행 2 — 루브릭 수정 후 1회 수렴

> **Run ID:** `20260524_212453_553380ff`
> **실행일:** 2026-05-24
> **brief_hash:** `49985c3410c03e81`
> **최종 결과:** PASS (iteration 1 — 1회만에 수렴)
> **변경점:** evidence 루브릭 척도 수정 후 재실행 (materials 외부 내용 창작 억제)

---

## 실행 요약

| Step | 역할 | 입력 | 출력 | 반복 |
|------|------|------|------|------|
| Step 1 | Gen (초안 생성) | 01_input.json | 02_output.json | 1회 |
| Step 2 | Critique (비평) | 02_output.json | 02b_critique.json | 1회 |
| Step 3 | Eval (품질 평가) | 02_output.json | 03_verdict.json | 1회 |
| Step 3-V | Validate (코드 검증) | 02_output.json + 03_verdict.json | — | 1회 |
| Step 4 | Refine (퇴고) | — | — | **실행 없음 (PASS)** |

> **수렴 지점:** Step 3 Eval에서 weighted_total 3.1 ≥ 2.8 (PASS 임계값) 달성 → Step 4 Refine 진입 없이 종료.

---

## Step 0. 입력 (01_input.json)

사용자가 `create_input.py`를 통해 작성한 브리프.

```json
{
  "brief_hash": "49985c3410c03e81",
  "brief": {
    "topic": "내가 그릿에 온 이유",
    "materials": [
      "처음에는 포트폴리오를 쌓으려고 들어옴.",
      "혼자 공부하는 방법을 잘 몰라 능동적으로 공부하는 사람이 되고파 신청하게 됨.",
      "AI에 대해 생각보다 많이 물어봐서 당황했음.",
      "백엔드와 AI가 큰 영향이 있을까 의문이 들었음.",
      "프로그램을 진행하면서 그 생각은 잘못됐다고 느낌.",
      "AI를 똑똑하게 쓰고있는 방법을 배우고 있다고 생각함."
    ],
    "tone": "블로그 소개용. 너무 친화적이지 않았으면 좋겠지만 딱딱하지 않았으면 좋겠음."
  },
  "created_at": "2026-05-24T12:24:53.016835+00:00"
}
```

---

## Step 1. Gen — 초안 생성 (02_output.json)

**모델:** `gemini-2.0-flash`
**입력:** topic + materials + tone (brief 전체)
**출력:** title / content / summary / keywords

**생성된 초안:**

```
제목: GRIT에 오게 된 계기: 포트폴리오 구축에서 능동적 학습으로

## GRIT에 오게 된 계기: 포트폴리오 구축에서 능동적 학습으로

GRIT에 처음 발을 들였던 이유는 순전히 포트폴리오를 쌓기 위해서였습니다.
하지만 혼자 공부하는 방법을 제대로 알지 못했고, 좀 더 능동적으로 학습하는
사람이 되고 싶다는 갈증이 있었습니다. 이러한 고민 끝에 GRIT 프로그램에
참여하게 되었습니다.

## 예상치 못한 질문과 나의 편견

프로그램에 참여하면서 예상치 못한 경험들을 했습니다. 특히 AI에 대한 질문이
생각보다 훨씬 많이 나와서 처음에는 당황스러웠습니다. 솔직히 백엔드 개발과
AI가 서로 큰 영향을 주고받을 것이라고는 생각하지 못했습니다.

## 편견을 깨고 AI의 가능성을 발견하다

하지만 GRIT 프로그램을 진행하면서 이러한 생각은 명백히 잘못되었음을 깨달았습니다.
백엔드 기술과 AI는 서로 깊은 연관성을 가지고 있으며, AI를 효과적으로 활용하는
것이 개발 전반에 얼마나 큰 영향을 미칠 수 있는지 배우고 있습니다. 현재 저는
AI를 똑똑하게 사용하는 방법을 배우며 기술적인 지평을 넓혀가고 있습니다.
```

---

## Step 2. Critique — 비평 (02b_critique.json)

**모델:** `gemini-2.5-flash-lite`
**입력:** content 텍스트만 (Gen 히스토리 차단)
**출력:** weaknesses 3개 (axis / reason / fix_hint)

| # | Axis | 문제 요약 | 개선 제안 |
|---|------|-----------|-----------|
| 1 | **hook** | 제목이 GRIT가 무엇인지, 독자가 왜 읽어야 하는지를 설명하지 못해 흥미 유발 부족 | 제목에 프로그램 특징이나 구체적 이점 포함 (예: "백엔드 개발자가 AI를 만나 능동적 학습자로 거듭난 GRIT 경험기") |
| 2 | **evidence** | "AI가 개발 전반에 큰 영향"이라 주장하지만 어떤 AI 기술인지, 어떻게 영향을 미쳤는지 구체적 사례 없음 | 머신러닝 활용 성능 예측, 코드 자동 생성 등 실제 경험 상세 추가 |
| 3 | **uniqueness** | "몰랐다가 깨달았다"는 서사가 일반적이어서 다른 경험담과 차별화 안 됨 | 특별한 어려움, 창의적 극복 과정, 개인적 에피소드 추가 |

---

## Step 3. Eval — 품질 평가 (03_verdict.json)

**모델:** `gemini-2.0-flash`
**입력:** content + brief_hash만 (Gen 히스토리·Critique 결과 차단)
**기준:** rubric.yaml 7축 가중 평균

| Axis | Weight | Score | 가중 점수 |
|------|-------:|------:|----------:|
| evidence | 20% | 3.0 | 0.60 |
| structure | 15% | 3.0 | 0.45 |
| tone | 15% | **5.0** | 0.75 |
| hook | 15% | 3.0 | 0.45 |
| uniqueness | 15% | 3.0 | 0.45 |
| actionability | 10% | 1.0 | 0.10 |
| length_calibration | 10% | 3.0 | 0.30 |
| **weighted_total** | | | **3.10** |

**판정:** `PASS` (임계값 2.8 이상)
**contract_errors:** 없음

---

## Step 3-V. Validate — 코드 검증

AI 없이 코드 기반으로 이중 검증 실행.

| 항목 | 기준 | 결과 |
|------|------|------|
| 가중합 재확인 | ≥ 2.5 | 3.1 → **통과** |
| 본문 글자 수 | 300~4,000자 | **통과** |
| 금지어 | 무조건·완벽보장·절대안전·반드시성공 | **없음** |

---

## Step 4. Refine — 퇴고

**실행되지 않음.**

Step 3 Eval에서 weighted_total **3.1 ≥ 2.8** 로 PASS 판정 → 루프 종료.
`04_next.json`에 PASS 기록 후 파이프라인 정상 종료.

---

## 루프 수렴 요약

```
Iteration 1:
  Gen     → 초안 생성 완료
  Critique → 약점 3개 추출 (hook / evidence / uniqueness)
  Eval    → weighted_total 3.1 → PASS ← 여기서 수렴
  Refine  → 실행 안 함

총 반복: 1회 / 최대 허용: 3회
최종 파일: 04_next.json (status: PASS, iterations: 1)
```

---

## v0 한계 (다음 버전 개선 과제)

| 약점 | 현재 점수 | 원인 | 개선 방향 |
|------|----------:|------|-----------|
| actionability | 1.0 | "다음에 무엇을 하면 되는가"가 글에 없음 | Gen 프롬프트에 CTA 문장 명시 요구 추가 |
| evidence | 3.0 | materials가 추상적 경험 서술 위주 → 구체 수치·사례 없음 | create_input.py에 "구체적 수치나 사례 입력 권장" 안내 추가 |
| uniqueness | 3.0 | 일반적인 "깨달음" 서사 | 고유 에피소드 유도 프롬프트 강화 |

---

## 변경 이력

> 이 섹션은 프로젝트 전체에 수정사항이 발생할 때마다 자동으로 기록된다. (CLAUDE.md Execution Log Rules 참고)

### 2026-05-23 — v0 초기 구현
- Gen → Eval 2단계 파이프라인 기본 구조 작성
- Gemini API(gemini-2.0-flash) 연동
- rubric.yaml 기반 7축 평가 시스템 설계
- input/output/verdict JSON schema 정의

### 2026-05-23 — Gen/Eval 세션 분리
- evaluator.py: content + brief_hash만 전달하도록 수정 (자기 채점 편향 방지)

### 2026-05-23 — generator.py 마크다운 파싱 버그 수정
- AI 응답에서 ```json ... ``` 코드 블록 제거하는 정규식 추가

### 2026-05-23 — Critique / Refine 단계 신규 추가
- pipeline/steps/critique.py 생성 (시니어 편집자 페르소나, 약점 3개 추출)
- pipeline/steps/refine.py 생성 (비평 + 점수 기반 퇴고)
- prompts/critique_system.md, prompts/refine_system.md 추가
- main.py: Gen → Critique → Eval → Refine 4단계 루프로 확장

### 2026-05-23 — config/rubric.yaml evidence 축 강화
- 기존: "근거 있음" 여부만 판단
- 변경: "materials 안의 내용인지" 여부까지 평가하도록 scale 수정
- 이유: Refine이 materials 외부 내용을 창작하는 문제 억제

### 2026-05-23 — prompts/eval_system.md rubric 정렬
- 기존 축(readability, clarity 등)을 rubric.yaml 7축 기준으로 전면 재작성

### 2026-05-23 — 문서 최초 작성
- docs/DESIGN.md: Gen/Eval 분리 구조, 4단계 프롬프트 전략, 루브릭 기준
- docs/PIPELINE_GUIDE.md: Step 0~4 실행 가이드, 체크리스트, v0 교훈

### 2026-05-23 — GitHub 연동
- 저장소 pigyechan/Blog_Writer 생성 및 초기 커밋 push

### 2026-05-24 — 파일 구조 재편
- docs/: DESIGN.md, PIPELINE_GUIDE.md 이동
- config/: rubric.yaml 이동
- pipeline/steps/: generator.py, critique.py, evaluator.py, refine.py, validate.py 이동
- pipeline/steps/__init__.py 추가 (Python 패키지 인식)
- main.py import 경로 수정: `from steps.generator import generate` 방식으로 통일
- evaluator.py rubric.yaml 경로를 `config/rubric.yaml`로 업데이트

### 2026-05-24 — README.md 파일 구조 및 History 섹션 추가
- 재편된 디렉터리 트리 반영
- 날짜별 개발 이력 History 섹션 작성

### 2026-05-24 — docs/PIPELINE_GUIDE.md 경로 수정
- 설정 파일: `rubric.yaml` → `config/rubric.yaml`
- Python 파일 목록: `pipeline/` 및 `pipeline/steps/` 기준으로 업데이트

### 2026-05-24 — docs/EXECUTION_LOG.md 최초 작성
- Step 1~4 입출력, 루브릭 점수, 수렴 지점, v0 한계 포함한 실행 로그 작성

### 2026-05-24 — CLAUDE.md Execution Log Rules 섹션 추가
- 프로젝트 변경 시 EXECUTION_LOG.md 변경 이력 자동 기록 규칙 정의

### 2026-05-24 — EXECUTION_LOG.md 실행 기록 2건으로 재구성
- 실행 1 추가: Refine 루프 2회 반복 케이스 (REJECT 2.4 → PASS 3.3)
- 실행 2: 기존 1회 수렴 케이스 유지

### 2026-05-24 — CLAUDE.md Cross-file Consistency Rules 섹션 추가
- 파일 변경 시 연관 파일(실행 파일 포함) 동기화 확인 규칙 및 파일별 연관 관계 표 정의
- 설정→실행 파일, 설정→문서, 실행 결과→로그 세 방향 커버
- docs/PIPELINE_GUIDE.md 체크리스트에 연관 파일 동기화 확인 단계 추가

### 2026-06-20 — prompts/gen_system.md, refine_system.md 금지어 지시 추가
- "다음 단어 사용 금지: 무조건, 완벽, 절대, 반드시" 항목 추가
- 이유: 이전 실행에서 generator가 '완벽' 사용 → banned 오류로 REJECT

### 2026-06-20 — runs/20260620_013135_a67ea4f5 실행 완료 (엔지니어링 문제 해결 사고 주제)
- 주제: 엔지니어링 문제 해결 능력 진단 (티켓 예매 시스템 시나리오)
- 결과: **PASS** (weighted_total=3.95, iteration=1)
- Critique + Eval 병렬 실행 첫 적용

### 2026-06-20 — Gemini → Claude API 전체 마이그레이션 + 병렬 구조 적용 (롤백)
- pipeline/steps/generator.py, critique.py, evaluator.py, refine.py: `google.genai` → `anthropic` SDK로 전환
- 모델 `gemini-3.1-flash-lite` → `claude-opus-4-8` (모든 스텝 공통)
- 환경변수 `GEMINI_API_KEY` → `ANTHROPIC_API_KEY` (anthropic.Anthropic()가 자동 읽음)
- pipeline/main.py: Critique + Eval 병렬 실행 적용 (ThreadPoolExecutor, max_workers=2)
  - 이유: 두 스텝 모두 output.json만 읽으므로 독립적 — Anthropic 블로그 Parallelization 패턴 적용
- Gemini JSONDecodeError 버그 해소 (Claude는 마크다운 코드블록 감싸기가 일관적)
