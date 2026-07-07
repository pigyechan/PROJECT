# CodeQuality Reviewer Pipeline

AI 기반 코드 품질(SOLID + Rich Domain) 진단 파이프라인. Test_Writer(1-1)의 Gen/Critique/Eval/Validate
하네스를 코드 품질 도메인으로 확장한 프로젝트 — 설계 배경은 [`docs/DESIGN.md`](docs/DESIGN.md) 참고.

GitHub: https://github.com/pigyechan/PROJECT/tree/master/CodeQuality_Reviewer

---

## 파이프라인 구조

```
Gen → Critique → Eval → Validate → (REJECT 시 Refine → 반복, 최대 3회)
```

- **Gen**: 소스 코드를 받아 SOLID 위반 후보 + Fowler 카탈로그 기반 리팩토링 제안 생성
- **Critique**: 새 세션에서 "시니어 코드 리뷰어(과설계 경계경보)" 페르소나로 빈틈 3개 추출
- **Eval**: rubric 4축(진단 정확도/변경 최소성/행위 보존 위험도/테스트 용이성 개선) 채점
- **Validate**: 스키마 + 금지 패턴(검증 불가능한 rationale) + 품질 하한 + **실제 `gradle test`
  실행으로 GREEN 확인** (코드 기반 게이트)

---

## 실행

```bash
# 환경변수 (필수)
export GEMINI_API_KEY="..."

# 1. B-2 TicketService 원본 코드 샘플 입력 생성
python pipeline/sample_ticket_service.py

# 2. 파이프라인 실행 (최신 run 자동 선택)
python pipeline/main.py
```

의존 패키지: `google-genai`, `pyyaml`, `jsonschema` (`pip install google-genai pyyaml jsonschema`)

---

## 문서

- [DESIGN.md](docs/DESIGN.md) — 1-1(Test_Writer)에서 재사용한 것 / 새로 만든 것
- [COMPARISON.md](docs/COMPARISON.md) — 파이프라인 제안 vs 본인 수작업 리팩토링(B-5) 비교
- [EXECUTION_LOG.md](docs/EXECUTION_LOG.md) — 실행 로그 + 과설계 제안 사례
- [sample-run/](docs/sample-run/) — 실제 실행 결과 원본 JSON (runs/는 gitignore 대상이라 별도 보존)
