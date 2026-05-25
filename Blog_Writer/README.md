# Blog Writer Pipeline

AI 기반 블로그 초안 생성 파이프라인 (v0)

GitHub: https://github.com/pigyechan/Blog_Writer

---

## 파이프라인 구조

4단계 파이프라인으로 블로그 초안을 생성하고 평가합니다.

```
Gen → Critique → Eval → Refine
```

- **Gen**: 주제와 재료를 받아 초안 생성
- **Critique**: 새 세션에서 약점 3개 추출
- **Eval**: 루브릭 7축 기반 점수 산출
- **Refine**: 비평과 점수를 근거로 퇴고

---

## 파일 구조

```
Blog_Writer/
├── pipeline/
│   ├── main.py               # 파이프라인 오케스트레이터
│   ├── create_input.py       # 입력 파일 생성
│   └── steps/
│       ├── __init__.py
│       ├── generator.py      # Step 1: 초안 생성
│       ├── critique.py       # Step 2: 비평 추출
│       ├── evaluator.py      # Step 3: 루브릭 평가
│       ├── refine.py         # Step 4: 퇴고
│       └── validate.py       # Schema/길이/금지어 검증
├── config/
│   └── rubric.yaml           # 평가 루브릭 (7축 기준)
├── prompts/
│   ├── gen_system.md         # Generator 시스템 프롬프트
│   ├── eval_system.md        # Evaluator 시스템 프롬프트
│   ├── critique_system.md    # Critique 시스템 프롬프트
│   └── refine_system.md      # Refine 시스템 프롬프트
├── docs/
│   ├── DESIGN.md             # 하네스 설계서
│   └── PIPELINE_GUIDE.md     # 파이프라인 설계 가이드
├── schemas/
│   ├── input.schema.json
│   ├── output.schema.json
│   └── verdict.schema.json
└── runs/                     # 실행 로그 (gitignore)
    └── {timestamp_uuid}/
        ├── 01_input.json
        ├── 02_output.json
        ├── 02b_critique.json
        ├── 03_verdict.json
        ├── 04_next.json        # PASS 시 생성
        └── 99_regen_request.json  # REJECT 시 생성
```

---

## 실행

```bash
python pipeline/create_input.py   # 입력 생성
python pipeline/main.py           # 파이프라인 실행
```

---

## 문서

- [DESIGN.md](docs/DESIGN.md) — 하네스 설계서
- [PIPELINE_GUIDE.md](docs/PIPELINE_GUIDE.md) — 파이프라인 설계 가이드
- [EXECUTION_LOG.md](docs/EXECUTION_LOG.md) — 파이프라인 실행 로그

