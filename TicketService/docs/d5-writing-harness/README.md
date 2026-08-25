# 글쓰기 하네스 v1

`Blog_Writer`(Phase 0/T8)의 Gen→Critique→Eval→Refine 하네스 v0를 에세이·전달 도메인으로 확장한 버전. 실제 자동화 스크립트 대신 Claude Code의 서브에이전트(Agent)를 각 단계의 "새 세션"으로 사용한다.

---

## 구조

```
Gen → Critique → Eval → (저자 판단) → Refine
```

- **Gen**: 저자의 재료(경험, 판단, 근거)를 4-Step 구조로 정리. 저자와의 대화로 진행하거나, `gen_system.md`를 시스템 프롬프트로 준 별도 에이전트로 진행할 수 있다.
- **Critique**: 이 글이 어떻게 쓰였는지 전혀 모르는 독립 서브에이전트(Claude Code `Agent` 도구)에게 완성된 텍스트만 주고 약점 3개를 뽑는다.
- **Eval**: Critique와 별도로, 역시 독립 서브에이전트가 `rubric.yaml` 4축을 채점한다. Critique 결과는 보여주지 않는다(Gen/Critique/Eval 상호 격리 — Test_Writer(1-1) "관대한 그린" 재발 방지).
- **저자 판단**: Critique의 weakness 각각을 저자가 채택/기각하고 이유를 남긴다. 이 판단은 AI가 대신할 수 없다.
- **Refine**: 채택된 항목만 반영해서 퇴고한다.

## 파일 구조

```
d5-writing-harness/
├── rubric.yaml           # 4축 루브릭 (message_clarity, four_step_fidelity, no_fluff, reader_alignment)
├── gen_system.md          # Gen 시스템 프롬프트
├── critique_system.md     # Critique 시스템 프롬프트
├── eval_system.md         # Eval 시스템 프롬프트
└── refine_system.md       # Refine 시스템 프롬프트
```

## v0(Blog_Writer) 대비 v0 → v1 변경점

| 구분 | v0 (Blog_Writer) | v1 (이 하네스) |
|---|---|---|
| 축 개수 | 7축 (structure, evidence, tone, hook, uniqueness, actionability, length_calibration) | 4축 (message_clarity, four_step_fidelity, no_fluff, reader_alignment) — D-5 과제가 명시한 축으로 축소 |
| 실행 방식 | Python 스크립트(`pipeline/*.py`)가 LLM API 직접 호출 | Claude Code `Agent` 도구로 서브에이전트를 직접 스폰 (별도 API 연동 불필요, 대화 중 즉시 실행 가능) |
| **저자 영역 침범 금지 규칙** | 없음 (v0는 마케팅/SEO 블로그 도메인이라 "저자 고유성"보다 "브랜드 톤 준수"가 우선순위) | **신규 추가.** Gen/Critique/Refine 프롬프트 전부에 "완성 문장 대필 금지, 방향만 제시" 규칙을 명시. 에세이는 개인 경험·판단이 핵심이라 AI가 메시지를 대신 만들면 안 됨 |
| 실행 로그 | `runs/{timestamp_uuid}/`에 JSON으로 영속 저장 | 각 에세이 문서(`d2-technical-essay.md` 등) 안에 표 형태로 직접 기록 |

**진짜 고도화 지점은 축 개수를 줄인 것이 아니라, "저자 영역 침범 금지" 규칙을 Gen·Critique·Refine 세 프롬프트 모두에 명시적으로 넣은 것이다.** v0는 이 문제를 다루지 않았다 — 블로그 마케팅 글은 애초에 AI가 메시지까지 만들어도 되는 도메인이었기 때문이다. 에세이 도메인으로 확장하면서 이 경계가 새로 필요해졌다.

## 실행 절차 (다음에 새 글이 생겼을 때)

1. **Gen**: 저자와 대화하며 재료를 모으고 4-Step 구조로 정리한다 (`gen_system.md` 원칙 준수).
2. **Critique 실행**: `Agent` 도구로 새 서브에이전트를 띄운다. 프롬프트 = `critique_system.md` 전문 + `rubric.yaml`의 axis 설명 + 완성된 초안 텍스트만. 초안이 어떻게 쓰였는지(AI 도움 여부 등) 절대 언급하지 않는다.
3. **Eval 실행**: 별도의 새 서브에이전트를 또 띄운다. 프롬프트 = `eval_system.md` 전문 + `rubric.yaml` + 초안 텍스트만. Critique 결과는 주지 않는다.
4. **저자 판단**: Critique의 weakness 각각에 대해 채택/기각 + 이유를 기록한다.
5. **Refine**: 채택된 것만 반영해서 퇴고한다 (`refine_system.md` 원칙 준수).
6. 판정 로그(Eval 점수, Critique 3건, 채택/기각 표)를 해당 글 문서에 남긴다.
