# 실행 로그

## Run: `20260707_235030_5d130fc5`

- 입력: [`docs/sample-run/01_input.json`](sample-run/01_input.json) — B-2 원본 TicketService
  코드(커밋 `e3b74ab`), `test_project_dir` = 실제 `TicketService/` 경로
- brief_hash: `44ea91a312b76c9a`
- 콘솔 출력 전문: [`docs/sample-run/pipeline_stdout.log`](sample-run/pipeline_stdout.log)

### 실행 결과 요약

| Step | 결과 |
|---|---|
| Gen | violations 3개, refactor_suggestions 3개 |
| Critique | weaknesses 3개 (minimal_change, diagnostic_accuracy, behavior_preservation) |
| Eval | weighted_total = 3.8000 (min_total 2.5 통과) |
| Validate | contract_errors 없음, **tests_green = true** (실제 `gradle test` 실행 결과) |
| 최종 판정 | **PASS** (iteration 1) |

전체 원본:
[`02_output.json`](sample-run/02_output.json) ·
[`02b_critique.json`](sample-run/02b_critique.json) ·
[`03_verdict.json`](sample-run/03_verdict.json) ·
[`04_next.json`](sample-run/04_next.json)

### `tests_green` 검증이 실제로 무엇을 했는가

`pipeline/steps/validate.py`의 `_check_tests_green()`이 `TicketService/` 디렉터리에서
실제로 `gradle test --console=plain`을 서브프로세스로 실행했다. 이번 세션에서 설치한
JDK 21(Temurin) + Gradle 8.10.2, 그리고 `GRADLE_USER_HOME`을 한글 경로 밖으로 돌리는
환경설정([[env_gradle_korean_path]] 메모리 참고)을 그대로 재사용했다. 출력에서
`BUILD SUCCESSFUL` 문자열을 확인해 `tests_green: true`를 기록했다 — LLM의 판단이 아니라
실제 빌드 도구 실행 결과다.

---

## 과설계(over-engineering) 제안 사례

**있었다.** Critique가 Gen의 세 번째 제안 중 하나를 명시적으로 과설계로 지적했다.

> **axis**: `minimal_change`
> **reason**: "PaymentService 인터페이스 추출 제안은 결제 모듈이 1개뿐인 현 시점에서
> 불필요한 추상화 레이어를 추가하는 과설계입니다."
> **fix_hint**: "현재 결제 수단이 단일하다면 인터페이스 도입 대신 의존성 주입을 통한
> 결합도 완화만으로 충분합니다."

### 이 지적을 어떻게 봐야 하는가 — 사후 검증 결과와의 긴장

이 지적은 Gen이 제안한 시점(결제 구현체가 `PaymentApi` 하나뿐인 상태)만 놓고 보면 합리적인
YAGNI 판단이다. 실제로 본인도 B-3/B-4에서 정리한 "리팩토링이 필요한 경우 vs 불필요한 경우"
기준의 핵심이 "그 객체에 지켜야 할 불변식이나 확장 계획이 있는가"였다 — 확장 계획이 안
보이는데 인터페이스부터 만드는 건 이 기준으로도 과설계로 분류될 수 있다.

하지만 본인은 실제로 B-5에서 이 Extract Interface를 적용했고, B-8에서 "포인트 결제
수단 추가"라는 새 요구사항을 가정해 검증한 결과 — `PaymentGateway` 인터페이스 덕분에
새 어댑터 클래스 하나만 추가하고 기존 `TicketService`/`Ticket`/`TicketServiceTest`는
한 줄도 안 바꿔도 됐다(`docs/new-requirement-point-payment.md` in `TicketService/`,
커밋 [`a0a97a6`](https://github.com/pigyechan/PROJECT/commit/a0a97a673c28ea399bfe8ef9cfd06f7153c78fb3)).

즉 **Critique의 과설계 지적은 "이 시점의 정보만으로는" 합리적이었지만, 결과적으로는
틀렸다** — 두 번째 결제 수단이라는 요구사항이 실제로 왔고, 그때 이 추상화가 정확히
비용을 아껴줬다. 이건 파이프라인의 결함이 아니라 **YAGNI의 근본적인 한계**를 보여준다:
"미래에 확장이 올지 안 올지"는 지금 코드만 봐서는 확정할 수 없다. Critique는 확장 계획을
알 방법이 없으므로 보수적으로 과설계라고 지적한 것이고, 이는 정보가 제한된 상태에서는
올바른 기본값(default)이다.

### 이 사례에서 얻은 교훈 (B-4 재즈 3단계 프레임과 연결)

- **자기화 관점에서**: "지금 정보로 과설계처럼 보인다"와 "실제로 과설계다"는 다른
  명제다. Critique 페르소나는 전자만 판단할 수 있고, 후자는 도메인 로드맵을 아는
  사람(또는 실제 요구사항이 도착한 뒤)만 판단할 수 있다.
- **파이프라인 개선 방향**: `context` 필드에 "이 결제 모듈은 곧 결제수단이 추가될
  예정이다" 같은 로드맵 정보를 명시적으로 넣을 수 있게 하면, Critique가 근거 있는
  과설계 판단을 내릴 수 있다. 지금 구조에서는 Gen/Critique 둘 다 코드만 보고 판단하므로
  이런 종류의 오탐(false positive over-engineering flag)이 구조적으로 발생할 수 있다 —
  이 사실 자체를 파이프라인의 알려진 한계로 기록해둔다.
