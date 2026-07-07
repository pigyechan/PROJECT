# 파이프라인 제안 vs 본인 수작업 리팩토링(B-5) 비교

대상: `TicketService`/`Ticket`/`PaymentApi` 원본(커밋
[`e3b74ab`](https://github.com/pigyechan/PROJECT/commit/e3b74ab9932d48ff06580ce3015fbc19d7a6da9b)).
파이프라인 실행 결과 원본: [`docs/sample-run/`](sample-run/).

---

## 1. 위반 진단(violations) — 완전히 일치

| # | 파이프라인(Gen)이 짚은 위반 | 본인이 B-3/B-4에서 짚은 위반 |
|---|---|---|
| 1 | Anemic Domain — `Ticket`에 예약 검증/상태 변경 로직이 없고 `TicketService`가 대신 제어 | 동일 (Feature Envy로 표현) |
| 2 | SRP — `reserveTicket`이 유저 조회·검증·결제·영속화를 한 메서드에서 처리 | 동일 (Long Method / Divergent Change로 표현) |
| 3 | DIP — `TicketService`가 `PaymentApi` 구체 클래스에 직접 의존 | 동일 |

**진단 단계는 사람과 파이프라인이 완전히 같은 3개 위반에 도달했다.** 파이프라인은 이걸
약 3초 만에 생성했다. 다만 공정한 비교는 아니다 — 이번 경우 사람(본인)이 B-3/B-4에서
이미 같은 코드를 분석한 뒤였고, 파이프라인은 그 분석 없이 코드만 보고 독립적으로
같은 결론에 도달했다는 점이 오히려 의미 있다.

---

## 2. 리팩토링 제안(refactor_suggestions) vs 실제 적용(B-5 5단계) — 여기서 갈린다

| 파이프라인 제안 | 본인 수작업(B-5) | 일치 여부 |
|---|---|---|
| Move Method — `Ticket.reserve(userId)` | Move Method — `Ticket.reserve(userId)` ([`56e6d1f`](https://github.com/pigyechan/PROJECT/commit/56e6d1f67fddbea5e19e8ebbfbc2e3ac5e25bd55)) | ✅ 일치 |
| Extract Interface — `PaymentService` (파이프라인 명명) | Extract Interface — `PaymentGateway` ([`5d437dc`](https://github.com/pigyechan/PROJECT/commit/5d437dccac6327262170797032013f1bb2a3a452)) | ✅ 개념 일치 (이름만 다름) |
| Extract Method — `validateUser/processPayment/updateTicketStatus` | Extract Method — `findUserOrThrow/findAvailableTicketOrThrow/chargeOrThrow` ([`e993a01`](https://github.com/pigyechan/PROJECT/commit/e993a018d85d940a9369c44ca71701d8be5ee01a)) | ✅ 개념 일치 (메서드 이름만 다름) |
| — (제안 없음) | Rename Class — `PaymentApi` → `TossPaymentAdapter` ([`144cd6c`](https://github.com/pigyechan/PROJECT/commit/144cd6c5a7d3126f269c022c1f6ec907315b0a25)) | ❌ 파이프라인이 놓침 |
| — (제안 없음) | **Remove Setting Method** — `setReserved/setUserId` 제거 ([`30f7f52`](https://github.com/pigyechan/PROJECT/commit/30f7f52cf54d4885b36a71f99d8221170c24aef0)) | ❌ 파이프라인이 놓침 |

### 어느 쪽이 더 나았고, 왜

**진단(무엇이 문제인가)은 동등했다.** 3개 위반 모두 정확히 일치했고, 나머지 3개
제안(Move Method / Extract Interface / Extract Method)도 개념적으로 동일했다 — 이름과
스케치 수준의 디테일 차이뿐이었다.

**완성도(어디까지 밀어붙였는가)는 사람 쪽이 더 나았다.** 이유는 하나로 요약된다:
파이프라인은 "권장되는 길을 만드는 것"까지만 갔고, "잘못된 길을 막는 것"까지는 가지
못했다.

- Move Method로 `Ticket.reserve()`를 추가하자는 제안은 있었지만, 기존
  `setReserved/setUserId`를 **제거하자는 제안은 없었다**. 즉 파이프라인의 제안을 그대로
  적용해도 `ticket.setReserved(true)`로 검증을 우회할 수 있는 뒷문은 여전히 열려 있다.
  Tell, Don't Ask를 절반만 완성한 셈이다. 본인은 여기서 한 걸음 더 나가 setter를 완전히
  삭제해(`30f7f52`) 컴파일러 수준에서 우회 자체를 불가능하게 만들었다.
- `PaymentApi` → `TossPaymentAdapter` 같은 Rename Class는 동작에 영향을 주지 않는
  "사소한" 리팩토링이라 파이프라인이 우선순위에서 밀어냈을 가능성이 크다. 하지만 이
  이름이 Port/Adapter 구조를 코드 밖에서도 즉시 읽히게 만든다는 점에서, 장기적으로
  협업 비용을 줄이는 조각이다.
- Critique 자체가 `behavior_preservation` 축에서 낮은 점수(2.0/5)를 준 이유("결제 API
  호출과 티켓 상태 갱신 사이의 트랜잭션/부작용 보존 방안이 언급되지 않음")는, 정확히
  본인이 수작업에서 신경 쓴 지점과 겹친다. 본인은 Move Method 커밋 메시지에
  "결제 전 중복예약 차단 순서(원본 동작)를 그대로 유지하기 위해 `isReserved()` 가드를
  결제 호출 앞에 남겨뒀다"고 명시적으로 기록했다 — 파이프라인 제안에는 이 순서 보존에
  대한 언급이 전혀 없었다.

**결론**: 이 규모의 kata에서는 **진단은 파이프라인이 사람만큼 빠르고 정확했지만, "안전하게
끝까지 마무리하는" 감각(우회로 차단, 순서 보존 근거 명시, 사소해 보이지만 의도를 전달하는
개명)은 사람 쪽이 더 나았다.** 파이프라인은 "무엇을 고쳐야 하는가"는 잘 찾지만 "이걸로
충분한가"는 스스로 판단하지 못했다 — 정확히는, Critique가 그 부족함(`behavior_preservation`
저점)을 스스로 지적하긴 했지만, 그 지적이 다음 iteration에서 실제로 반영됐는지는 이번
실행이 1회 iteration 만에 PASS로 끝나 확인되지 않았다(아래 3번 참고).

---

## 3. 왜 1회 만에 PASS했는가 — Refine 루프가 작동하지 않은 이유

`weighted_total = 3.8`로 `min_total(2.5)`을 넉넉히 넘겨 1회 iteration 만에 PASS했다.
Critique가 `behavior_preservation`의 약점을 정확히 짚었음에도, Eval의 가중 평균이
`min_total`을 이미 넘겼기 때문에 Refine이 호출되지 않았다. 즉 이번 실행에서는
"Critique가 지적했지만 점수 문턱을 넘어서 개선 없이 통과"하는 상황이 실제로 발생했다.

이건 1-1(Test_Writer)의 `docs/DESIGN.md`에 이미 기록된 "평가자 관대함 주의"와 같은 종류의
문제다 — `min_total`을 3.0 이상으로 올리거나, Eval 프롬프트에 "Critique가 지적한 축은
반드시 4점 미만으로 채점하라"는 제약을 추가하는 게 다음 개선 방향이다.

---

## 4. 종합

| 관점 | 우위 |
|---|---|
| 위반 진단 정확도 | 동일 |
| 진단 속도 | 파이프라인 (수 초) |
| 리팩토링 완성도(우회 차단까지) | 사람 (Remove Setting Method) |
| 사소하지만 의도 전달에 기여하는 조각 | 사람 (Rename Class) |
| 자기 제안의 약점을 스스로 인지 | 파이프라인 Critique (그러나 실제 반영은 안 됨) |
