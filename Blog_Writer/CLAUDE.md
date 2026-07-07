# Blog Writer Pipeline

## Project Overview

이 프로젝트는 AI 기반 블로그 초안 생성 파이프라인이다.

입력된 주제와 재료를 기반으로:
1. Generator가 초안을 생성한다.
2. Evaluator가 품질을 평가한다.
3. Validator가 schema를 검증한다.
4. PASS 시 다음 단계로 진행한다.

---

## Pipeline Rules

- generator.py는 초안 생성만 담당한다.
- evaluator.py는 결과 평가만 담당한다.
- validate.py는 schema 검증만 담당한다.
- Evaluator는 Generator의 내부 상태를 참조하지 않는다.
- 평가 시 output.json만 기준으로 판단한다.

---

## Output Rules

모든 출력은 schema를 반드시 준수한다.

- input.schema.json
- output.schema.json
- verdict.schema.json

schema 검증 실패 시 저장 금지.

---

## AI Assistant Rules

- 코드 수정 전 이유 설명
- 위험한 작업 전 사용자 확인
- edge case 고려
- 하드코딩 금지
- 설정값은 yaml/json 분리

---

## Git Rules

- main 직접 push 금지
- feature branch 사용
- commit 전 사용자 확인
- PR 생성 후 merge
- **커밋 전 GitHub 동기화 상태 반드시 확인** (`git status`로 origin 대비 ahead/behind 파악 후 사용자에게 안내)

---

## Run Directory Rules

runs/{timestamp_uuid}/

생성 순서:
1. 01_input.json
2. 02_output.json
3. 03_verdict.json
4. 04_next.json (PASS 시)
5. 99_regen_request.json (REJECT 시)

---

## Cross-file Consistency Rules

하나의 파일이 변경되면 연관된 다른 파일도 업데이트가 필요한지 반드시 확인한다.

| 변경된 파일 | 확인해야 할 파일 |
|---|---|
| `config/rubric.yaml` | `pipeline/steps/evaluator.py` (rubric 읽기 경로·파싱), `prompts/eval_system.md` (축 일치), `docs/DESIGN.md` (루브릭 표) |
| `schemas/*.json` | `pipeline/steps/validate.py` (schema 검증 로직), schema를 출력하는 각 step 파일 |
| `prompts/eval_system.md` | `config/rubric.yaml` (축 일치 여부) |
| `prompts/` 아래 파일 | 해당 프롬프트를 읽는 `pipeline/steps/*.py`, `docs/DESIGN.md` (프롬프트 전략 섹션) |
| `pipeline/steps/*.py` | `../PIPELINE_GUIDE.md` (저장소 루트, Python 파일 목록·공통 패턴), `docs/DESIGN.md` |
| `pipeline/main.py` | `docs/DESIGN.md` (파이프라인 흐름도), `../PIPELINE_GUIDE.md` |
| 파일 추가·이동·삭제 | `README.md` (파일 구조), `../PIPELINE_GUIDE.md` (Python 파일 목록), import 경로를 참조하는 모든 `.py` |
| 실행 결과 변경 | `docs/EXECUTION_LOG.md` |
| `CLAUDE.md` | `docs/EXECUTION_LOG.md` (변경 이력) |

규칙:
- 변경 작업 후 위 표를 기준으로 연관 파일을 순서대로 확인한다.
- 확인 후 수정이 필요 없으면 넘어가도 되지만, 확인 자체는 생략하지 않는다.
- 연관 파일 수정까지 완료된 뒤 커밋한다.

---

## Execution Log Rules

프로젝트 전체에 수정사항이 발생하면 `docs/EXECUTION_LOG.md`의 **변경 이력** 섹션에 자동으로 기록한다.

기록 대상:
- 코드 변경 (pipeline/, steps/ 아래 .py 파일)
- 설정 변경 (config/rubric.yaml, schemas/)
- 프롬프트 변경 (prompts/)
- 문서 변경 (docs/, README.md, CLAUDE.md)
- 파이프라인 실행 결과 (새 run 디렉터리 생성 시)

기록 형식:
```
### YYYY-MM-DD — <변경 대상 파일 또는 기능>
- 변경 내용 한 줄 요약
- 변경 이유 (선택)
```

규칙:
- 변경 작업 완료 직후 즉시 기록한다.
- 사용자가 별도로 요청하지 않아도 자동 반영한다.
- 기존 실행 결과(Step 1~4 로그)는 덮어쓰지 않는다. 섹션을 분리한다.

---

## Writing Goal

목표는 "완성된 글"이 아니라
"수정 가능한 품질 높은 초안" 생성이다.