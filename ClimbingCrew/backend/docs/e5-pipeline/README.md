# E-5: API Contract 검증 파이프라인

Phase 1 하네스(Blog_Writer, CodeQuality_Reviewer 등)를 API 계약 도메인으로 이식했다. 무엇을 재사용했고 무엇을 새로 만들었는지는 아래와 같다.

## 재사용한 것

- **Gen/Critique/Eval 격리 원칙** (PIPELINE_GUIDE.md): Gen은 Critique/Eval의 존재를 모르고, Critique/Eval은 서로의 판단을 못 보고 원본 산출물만 본다는 원칙을 그대로 가져왔다. 구체적으로 Gen 서브에이전트에게는 테스트 파일을 절대 보여주지 않았고("테스트 파일은 찾지도, 참고하지도 말라"고 명시), Critique 서브에이전트에게도 `src/test/`를 보지 말라고 명시했다.
- **격리 구현 방식**: TicketService의 `d5-writing-harness`가 이미 증명한 대로, Python/API 호출 대신 **Claude Code 서브에이전트를 새로 띄우는 것**으로 격리를 구현했다. Gen 1개, Critique 1개, 총 2개의 독립 서브에이전트를 사용했다.
- **rubric.yaml 구조**: CodeQuality_Reviewer의 `config/rubric.yaml` 형식(axes + weight + 1/3/5 scale + min_total)을 그대로 재사용하고, 축 이름과 설명만 API 계약 도메인에 맞게 새로 썼다.
- **validate = 결정적 게이트라는 원칙**: CodeQuality_Reviewer의 `validate.py`가 `gradle test`를 실제로 돌려서 그 결과를 판정에 merge하는 패턴을 그대로 따랐다. 다만 실행 방식은 아래 "새로 만든 것"에 적었다.

## 새로 만든 것

- **명세 먼저, 구현은 나중 순서**: 기존 파이프라인들은 모두 "Gen이 먼저 초안을 만들고 그 다음 Critique/Eval이 검증"하는 순서였다. 이번엔 반대로 **사람이 먼저 계약 테스트(`RecordContractTest.java`)를 쓰고, 그 다음에야 Gen(AI 구현)을 실행**했다. Gen 서브에이전트는 자기가 어떤 테스트로 판정받을지 전혀 모르는 상태로 구현했다.
- **validate 실행 메커니즘**: 이 환경에서 Gradle의 표준 `test` 태스크가 워커 프로세스 부트스트랩 단계에서 `ClassNotFoundException: worker.org.gradle.process.internal.worker.GradleWorkerMain`을 내며 실행 자체가 안 되는 환경 버그를 만났다(원인 불명 — 매우 긴 클래스패스 + 한글 사용자 경로 조합에서만 재현). 우회책으로 `JavaExec` 태스크(`runDirectTests`, `build.gradle`에 등록)로 JUnit Platform Launcher를 직접 호출하는 방식을 새로 만들었다. 이 환경에 한정된 우회책이며, 다른 환경에서는 표준 `./gradlew test`가 정상 동작할 가능성이 높다.
- **Spring Boot 백엔드 스캐폴딩**: ClimbingCrew는 이번 스테이션 전까지 백엔드 코드가 전혀 없었다. `backend/` 아래에 Gradle+Spring Boot+H2 프로젝트를 처음부터 새로 만들었다(TicketService의 build.gradle을 참고하되 Testcontainers+Postgres 대신 H2로 가볍게 감).
- **Critique의 채점 범위 규칙**: "구현 지시에서 명시적으로 범위 밖으로 뺀 항목(인증/권한)은 감점하지 않는다"는 규칙을 rubric에 추가했다. 기존 rubric들에는 없던 규칙인데, Gen 프롬프트 자체가 "인증 시스템을 과도하게 만들지 말라"고 지시했기 때문에, 그 지시를 따른 것까지 감점하면 프롬프트와 평가 기준이 서로 모순되기 때문이다.

## 최종 판정 흐름

1. `RecordContractTest.java` 작성 (사람) → RED 확인 (구현 없음)
2. Gen 서브에이전트가 계약만 보고 구현 → 자체 self-assessment 보고
3. `runDirectTests`로 계약 테스트 실행 → 2/2 GREEN (validate, 결정적)
4. Critique 서브에이전트가 코드+계약만 보고 위반사항 지적 (테스트 결과 모름) → 3개 위반 발견
5. Eval: rubric.yaml 기준 채점 → weighted_total 3.90, PASS (min_total 3.0)
6. 종합 판단: `judgment.md` 참고
