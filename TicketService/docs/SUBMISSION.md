# 제출물 — TicketService 리팩토링 kata (특성화 테스트 → Rich Domain + SOLID)

저장소: https://github.com/pigyechan/PROJECT
경로: `TicketService/`

---

## 1. 리팩토링 시작 전 특성화 테스트 GREEN 증빙

- **커밋**: [`e3b74ab`](https://github.com/pigyechan/PROJECT/commit/e3b74ab9932d48ff06580ce3015fbc19d7a6da9b)
  — "TicketService kata: 원본 코드 + 특성화 테스트 GREEN (리팩토링 전 안전망)"
- **내용**: Anemic `Ticket`(getter/setter만 존재) + SRP·DIP 위반 `TicketService.reserveTicket`
  (유저 조회 + 티켓 검증 + 결제 + 영속화가 한 메서드에 절차적으로 나열, `PaymentApi` 구체
  클래스 직접 의존)을 원본 상태로 재현하고, 구조를 건드리기 전에 8개 특성화 테스트로 그
  동작을 고정.
- **실행 로그**: [`test-logs/test-log-01-characterization.txt`](../test-logs/test-log-01-characterization.txt)
  — 8/8 PASSED, `BUILD SUCCESSFUL`.

## 2. 리팩토링 전/후 코드 + 단계별 커밋 히스토리

안전망(1번) 위에서 5단계로 리팩토링. 각 커밋은 기법 하나만 담았고, 매 단계 테스트 GREEN을
유지했다 (로그 파일로 증빙).

| # | 커밋 | Fowler 기법 | 변경 요지 | 테스트 로그 |
|---|------|------------|-----------|------------|
| 1 | [`56e6d1f`](https://github.com/pigyechan/PROJECT/commit/56e6d1f67fddbea5e19e8ebbfbc2e3ac5e25bd55) | **Move Method** | `TicketService`에 있던 "이미 예약됐는지 검증 + 예약 상태 전환"을 `Ticket.reserve(userId)`로 이동 | [test-log-02](../test-logs/test-log-02-move-method.txt) |
| 2 | [`5d437dc`](https://github.com/pigyechan/PROJECT/commit/5d437dccac6327262170797032013f1bb2a3a452) | **Extract Interface** | `PaymentApi`의 공개 계약만 뽑아 `PaymentGateway` 포트 추출. `TicketService`는 인터페이스에만 의존 (DIP) | [test-log-03](../test-logs/test-log-03-extract-interface.txt) |
| 3 | [`144cd6c`](https://github.com/pigyechan/PROJECT/commit/144cd6c5a7d3126f269c022c1f6ec907315b0a25) | **Rename Class** | `PaymentApi` → `TossPaymentAdapter` (Port/Adapter 역할을 이름으로 명확화) | [test-log-04](../test-logs/test-log-04-rename-class.txt) |
| 4 | [`e993a01`](https://github.com/pigyechan/PROJECT/commit/e993a018d85d940a9369c44ca71701d8be5ee01a) | **Extract Method** | `reserveTicket` 내부를 `findUserOrThrow` / `findAvailableTicketOrThrow` / `chargeOrThrow` 3단계로 분리 | [test-log-05](../test-logs/test-log-05-extract-method.txt) |
| 5 | [`30f7f52`](https://github.com/pigyechan/PROJECT/commit/30f7f52cf54d4885b36a71f99d8221170c24aef0) | **Remove Setting Method** | `Ticket.setReserved/setUserId` 제거 — `reserve()`만 공개해 Tell-Don't-Ask 강제 | [test-log-06](../test-logs/test-log-06-remove-setting-method.txt) |

**리팩토링 전/후 비교**

- 전: `Ticket`은 데이터 창고, `TicketService.reserveTicket` 한 메서드가 조회·검증·결제·저장을
  다 처리, 결제사 구체 클래스(`PaymentApi`)에 직접 의존.
- 후: `Ticket`이 스스로 예약 가능 여부를 검증하고 상태를 전환(`reserve()`만 공개, 우회 불가),
  `TicketService`는 `findUserOrThrow → findAvailableTicketOrThrow → chargeOrThrow → ticket.reserve → save` 순서만 조율하는 오케스트레이터, 결제는 `PaymentGateway` 인터페이스 뒤에
  숨겨진 `TossPaymentAdapter`(Port/Adapter 구조).
- 행위는 8개 특성화 테스트로 시종일관 동일하게 유지됨 — 구조만 바뀜.

## 3. '리팩토링이 필요한 경우 vs 불필요한 경우' 본인 기준

- **문서**: [`docs/refactoring-criteria.md`](refactoring-criteria.md)
  (커밋 [`11efcb2`](https://github.com/pigyechan/PROJECT/commit/11efcb233d15d31669855d22a7669cd734d9f56f))
- **요지**: 판단 도구는 Fowler 코드 스멜 카탈로그(이번 kata에서는 Feature Envy, Long Method /
  Divergent Change) + 비용/효용 저울. 스멜이 있어도 "다시 열 계획이 없거나 안전망이 없는데
  마감이 급하면" 리팩토링하지 않는 게 합리적이라는 기준을 세웠고, 멘토 프레임 '재즈 3단계'
  (모방 → 응용 → 자기화)로 이번 실습에서 어디까지 모방했고 어디서 응용/판단이 들어갔는지
  정리함.

## 4. 새 요구사항 검증 (예측 vs 실제)

- **문서**: [`docs/new-requirement-point-payment.md`](new-requirement-point-payment.md)
- **커밋**: [`a0a97a6`](https://github.com/pigyechan/PROJECT/commit/a0a97a673c28ea399bfe8ef9cfd06f7153c78fb3)
- **가정한 요구사항**: "카드 결제 말고 포인트로도 예약 결제를 할 수 있어야 한다."
- **변경 전 예측**: `PaymentGateway` 포트가 OCP를 만족한다면 새 어댑터 클래스 + 그 테스트만
  추가하면 되고, 기존 파일(`TicketService`, `Ticket`, `PaymentGateway`, `TossPaymentAdapter`,
  `TicketServiceTest`)은 전혀 안 바뀌어야 한다고 예측.
- **실제로 바뀐 파일** (모두 신규 파일, 기존 파일 수정 0건):
  - `src/main/java/ticket/PointPaymentAdapter.java`
  - `src/test/java/ticket/PointPaymentAdapterTest.java`
  - `src/test/java/ticket/TicketServiceWithPointPaymentTest.java`
- **예측 대비 결과**: 정확히 일치. 변경이 새 파일 3개에만 갇혔고, 기존 코드는 한 줄도 건드리지
  않았다. 전체 테스트 11개 GREEN
  ([test-log-07](../test-logs/test-log-07-point-payment-ocp.txt)).
- 어긋나거나 번진 부분: 없음. 다만 문서 말미에 "새는 지점이 있었다면 어디였을지"(결제수단별
  전환 규칙이 붙는 경우)와 그 경우의 절단 방법을 함께 적어둠.
