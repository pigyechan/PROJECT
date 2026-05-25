# SESSION_CONTEXT.md

> 이 파일은 Claude Code 대화창이 닫혔다가 다시 열릴 때 맥락을 복원하기 위한 파일입니다.
> 새 대화를 시작할 때 "SESSION_CONTEXT.md를 읽어줘"라고 말하면 됩니다.
> Claude가 작업 완료 후 자동으로 업데이트합니다.

---

## 프로젝트 구조

```
C:\PROJECT\
├── SESSION_CONTEXT.md          ← 이 파일 (대화 맥락 복원용)
├── PIPELINE_GUIDE.md           ← 파이프라인 설계 가이드 (Blog_Writer 경험으로 작성)
├── Blog_Writer\                ← v0 파이프라인 (완성)
│   ├── pipeline\main.py        ← 4단계 루프 진입점
│   ├── pipeline\steps\         ← generator / critique / evaluator / refine / validate
│   ├── prompts\                ← gen_system.md / critique_system.md / eval_system.md / refine_system.md
│   ├── config\rubric.yaml      ← 7축 루브릭 (가중치 합 1.0)
│   ├── schemas\                ← input / output / verdict JSON schema
│   ├── runs\                   ← 실행 결과 (타임스탬프_uuid 폴더)
│   └── docs\                   ← DESIGN.md / PIPELINE_GUIDE.md / EXECUTION_LOG.md
├── Career_Planner\             ← 채용공고 분석 + 포지셔닝 초안 파이프라인 (완성)
│   ├── pipeline\main.py        ← 6단계 파이프라인 진입점
│   ├── pipeline\steps\         ← analyzer / reporter / drafter / critic / evaluator / validate / refiner
│   ├── prompts\                ← 단계별 시스템 프롬프트
│   ├── config\rubric.yaml      ← 6축 루브릭 + user_background.json
│   └── schemas\                ← input / analysis / draft / verdict JSON schema
└── Grit_Project\               ← Git 워크플로우 학습 프로젝트
    └── CLAUDE.md               ← 브랜치 전략, 커밋 규칙
```

---

## 사용자 정보

- 삼성전자 협력사(오픈에스지) 프리랜서. 품질팀 응용프로그램 유지보수 담당.
- 현재 업무: C# / .NET Framework 기반 Windows 앱, Oracle DB, Java AP.
- 목표: 웹 백엔드(특히 DB 중심) 개발자로 성장.
- 그릿 프로그램 참여 중.

---

## 완료된 작업

### Blog_Writer 파이프라인 (v0) — 2026-05-23 ~ 2026-05-24 완료
- **무엇**: 주제 + 재료(materials) → 블로그 초안 자동 생성
- **구조**: Gen → Critique → Eval → Refine 4단계 루프 (최대 3회 반복)
- **모델**: 전체 단계 `gemini-2.5-flash-lite` (Gemini API)
- **상태**: 완성. 2회 실행 기록 있음 (EXECUTION_LOG.md 참고)
- **주요 교훈**: PIPELINE_GUIDE.md에 정리됨

### Grit_Project Git 워크플로우 — 2026-05-16 ~ 2026-05-24 완료
- PR #1~#4 머지 완료
- CLAUDE.md에 브랜치 네이밍, 커밋 규칙, 워크플로우 순서 정의됨

---

## 진행 중인 작업

### Career_Planner 파이프라인 — 2026-05-25 구현 완료
- **위치**: `C:\PROJECT\Career_Planner\`
- **목적**: 채용공고 20~30개 텍스트 → 시장 패턴 분석 + StoryBrand 7요소 포지셔닝 초안
- **모델**: 전체 단계 `gemini-2.5-flash-lite` (Gemini API) / 환경변수: `GEMINI_API_KEY`
- **핵심 설계**: Analyze 단계가 표면 스킬이 아닌 "숨은 기대치" 해석 (예: "Kafka/Redis" → "대용량 트래픽 경험")
- **제출 산출물**: 분류 로그 / 시장 패턴 리포트 / 포지셔닝 초안 / 소화 메모 템플릿
- **상태**: 코드 완성 및 유지보수 완료. GEMINI_API_KEY 환경변수 설정 후 실행 가능.

---

## AI 행동 규칙 (CLAUDE.md 요약)

- 감성 서사 금지 (칭찬, 격려 문구 불필요)
- 선택지와 trade-off 항상 함께 제시
- 커밋/푸시는 사용자가 명시적으로 요청할 때만
- 브랜치 생성 전 이름 확인 필수
- 질문 의도가 학습이면 답 전에 먼저 방향 유도

---

## 다음 할 일

- [ ] `GEMINI_API_KEY` 환경변수 설정 후 Career_Planner 파이프라인 실행
- [ ] `cd C:\PROJECT\Career_Planner\pipeline && python create_input.py` 로 채용공고 입력
- [ ] 실행 결과 확인 후 필요 시 프롬프트/루브릭 조정
- [ ] 제출용 파일 완성 (03_draft.md, 02b_report.md, memo_template.md 직접 작성)

---

*마지막 업데이트: 2026-05-26*
