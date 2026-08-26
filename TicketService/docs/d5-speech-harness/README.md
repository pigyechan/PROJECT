# 스피치 리허설 에이전트

D-4 스피치 녹화의 전사(transcript)를 입력하면, 필러 워드 빈도·말 속도·구조(도입-핵심-예시-마무리)를 피드백하는 에이전트. `d5-writing-harness/`와 같은 방식 — Python 자동화 스크립트 대신 Claude Code의 `Agent` 도구를 실행 엔진으로 쓴다.

## 구성

```
d5-speech-harness/
├── README.md                      # 이 파일
└── rehearsal_agent_system.md      # 에이전트 시스템 프롬프트
```

## 입력 / 출력

- **입력**: ① 전사 텍스트(자동 받아쓰기 결과, 완벽하지 않을 수 있음) ② 녹화 길이(초)
- **출력**: JSON — `filler_words`(단어별 횟수), `filler_total`, `filler_per_minute`, `pace_chars_per_minute`, `pace_comment`, `structure`(4단계 각각 실제 문장 인용), `structure_issues`

## 저자 영역 침범 금지

발표 **내용**(메시지·논리)에는 의견을 내지 않는다. 오직 **전달 방식**(delivery — 필러 워드, 속도, 구조)만 다룬다. "이렇게 말하세요"라며 대사를 대신 써주지 않는다.

## 실행 절차 (다음에 새 녹화가 생겼을 때)

1. 녹화 파일의 전사를 만든다 (네이버 클로바노트 등 자동 받아쓰기 도구 사용 가능).
2. 녹화 파일의 길이(초)를 확인한다 — Windows 탐색기에서 파일 속성의 "길이" 항목으로 확인 가능.
3. Claude Code의 `Agent` 도구를 호출하면서, 프롬프트에 `rehearsal_agent_system.md` 전문 + 전사 텍스트 + 녹화 길이(초)를 그대로 붙여넣는다.
4. 돌아온 JSON 결과를 해당 스피치 문서(예: `d4-speech-delivery.md`)에 정리해 남긴다.

## 실행 이력

- 2026-08-27: 3~5분 헥사고날 스피치 녹화(3분 17초)에 실행. 결과는 [`../d4-speech-delivery.md`](../d4-speech-delivery.md) 참고. 처음엔 서브에이전트 없이 직접 분석했다가, "진짜 에이전트냐"는 지적을 받고 격리된 서브에이전트로 재실행 — 필러 워드 검출 정확도가 더 높아짐을 확인했다.
