# CodeQuality Reviewer Pipeline

## 프로젝트 개요

Test_Writer(1-1)의 Gen/Critique/Eval/Validate 파이프라인 구조를 코드 품질(SOLID + Rich
Domain) 진단 도메인으로 이식한 프로젝트. 소스 코드를 입력하면:

1. Generator가 SOLID 위반 후보와 Fowler 카탈로그 기반 리팩토링 제안을 생성한다.
2. Critique가 과설계·놓친 위반·행위 보존 위험 3개를 지적한다 ("과설계 경계경보" 페르소나).
3. Evaluator가 4축 rubric으로 품질을 채점한다.
4. Validator가 스키마·금지 패턴·품질 하한을 검증하고, **실제 대상 프로젝트에서 `gradle test`를
   실행해 GREEN인지 확인한다** (코드 기반 게이트, LLM 판단 아님).
5. REJECT 시 Refine이 개선 초안을 생성하고 최대 3회 반복한다.

---

## Pipeline Rules (1-1에서 유지)

- generator.py는 초안 생성만 담당한다.
- evaluator.py는 결과 평가만 담당한다. Generator 내부 상태를 참조하지 않는다.
- validate.py는 코드 기반 계약 검증만 담당한다.
- Critique는 content만 전달받는다 (Gen 히스토리 차단).
- Eval은 content + brief_hash만 전달받는다 (Critique 결과 차단).

---

## v0 범위 제한 (중요)

- 파이프라인이 제안한 `before_sketch`/`after_sketch`를 소스 파일에 **자동으로 patch
  적용하지 않는다**. Validate의 GREEN 확인은 `test_project_dir`의 기존 테스트 스위트를
  그대로 실행하는 것이지, 제안을 반영한 뒤의 결과가 아니다. 자동 패치 적용은 범위 밖 —
  다음 단계 과제로 남겨둔다.

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
| `pipeline/steps/validate.py` (`_check_tests_green`) | JAVA_HOME/GRADLE_USER_HOME 기본값 — 다른 환경이면 override 필요 |
| `pipeline/main.py` | `docs/` (파이프라인 흐름) |

---

## AI 행동 규칙

- 코드 수정 전 이유 설명
- 커밋/푸시는 사용자가 명시적으로 요청할 때만
- 하드코딩 금지. 설정값은 rubric.yaml / schemas/ 분리
- GEMINI_API_KEY는 절대 파일이나 커밋에 남기지 않는다 — 환경변수로만 전달
