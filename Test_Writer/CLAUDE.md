# Test Writer Pipeline

## 프로젝트 개요

Blog_Writer(Phase 0)의 Gen/Eval 분리 파이프라인 구조를 테스트 케이스 생성 도메인으로 이식한 프로젝트.

자연어 요구사항을 입력하면:
1. Generator가 단위 테스트 케이스 + Gherkin 시나리오 초안을 생성한다.
2. Critique가 빈틈(경계값 누락, 모호한 Then, 순서 의존 등) 3개를 지적한다.
3. Evaluator가 4축 rubric으로 품질을 채점한다.
4. Validator가 스키마·금지 패턴·품질 하한을 검증한다.
5. REJECT 시 Refine이 개선 초안을 생성하고 최대 3회 반복한다.

---

## 실행 방법

```bash
# Test_Writer/ 루트에서 실행

# 1. 입력 생성 (대화형)
python pipeline/create_input.py

# 2. DefectRateCalculator 샘플 입력 생성
python pipeline/sample_defect_rate.py

# 3. 파이프라인 실행
python pipeline/main.py                           # 최신 run 자동 선택
python pipeline/main.py runs/20260617_120000_abc  # 특정 run 지정
```

---

## Pipeline Rules (Blog_Writer에서 유지)

- generator.py는 초안 생성만 담당한다.
- evaluator.py는 결과 평가만 담당한다. Generator 내부 상태를 참조하지 않는다.
- validate.py는 코드 기반 계약 검증만 담당한다.
- Critique는 content만 전달받는다 (Gen 히스토리 차단).
- Eval은 content + brief_hash만 전달받는다 (Critique 결과 차단).

---

## Blog_Writer 대비 변경 사항

| 항목 | Blog_Writer (Phase 0) | Test_Writer (이번) |
|---|---|---|
| 입력 brief | topic, materials, tone | feature_name, requirements, context |
| Gen 출력 | content (str) | unit_tests[], scenarios[], content(직렬화) |
| rubric 축 | structure/evidence/tone/hook/uniqueness/actionability/length | coverage/unambiguity/independence/executability |
| validate 체크 | 글자 수, 금지어 | JSON 스키마, Then 절 모호 패턴, 품질 하한 |
| Critique 페르소나 | 시니어 편집자 | 시니어 QA 엔지니어 |
| 경로 방식 | 상대 경로 (CWD 의존) | Path(__file__) 절대 경로 (Career_Planner 패턴) |

---

## Output Rules

모든 출력은 스키마를 준수한다.

- schemas/input.schema.json
- schemas/output.schema.json
- schemas/verdict.schema.json

---

## Run Directory 파일 순서

```
runs/{timestamp_uuid}/
├── 01_input.json          (create_input.py 또는 sample_defect_rate.py)
├── 02_output.json         (Step 1: Gen)
├── 02b_critique.json      (Step 2: Critique)
├── 03_verdict.json        (Step 3: Eval + Step 4: Validate)
├── 04_next.json           (PASS 시)
├── 02_output_v2.json      (Refine → iteration 2)
└── 99_regen_request.json  (REJECT 시)
```

---

## Cross-file 연관 관계

| 변경 파일 | 확인해야 할 파일 |
|---|---|
| `config/rubric.yaml` | `prompts/eval_system.md` (축 일치), `pipeline/steps/validate.py` (QUALITY_MIN) |
| `schemas/output.schema.json` | `pipeline/steps/validate.py` (ARTIFACT_SCHEMA), `pipeline/steps/generator.py` (출력 필드) |
| `prompts/gen_system.md` | `pipeline/steps/generator.py` (출력 필드 파싱) |
| `prompts/critique_system.md` | `pipeline/steps/critique.py` (weaknesses 구조) |
| `prompts/eval_system.md` | `config/rubric.yaml` (축 이름 일치) |
| `prompts/refine_system.md` | `pipeline/steps/refine.py` (applied_fixes 구조) |
| `pipeline/main.py` | `docs/` (파이프라인 흐름) |

---

## AI 행동 규칙

- 코드 수정 전 이유 설명
- 커밋/푸시는 사용자가 명시적으로 요청할 때만
- 하드코딩 금지. 설정값은 rubric.yaml / schemas/ 분리
- 파일 수정 시 위 Cross-file 연관 관계 테이블을 확인한다
