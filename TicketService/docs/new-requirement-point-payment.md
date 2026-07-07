# 새 요구사항: 포인트 결제 수단 추가

## 가정한 요구사항

"카드 결제 말고, 사용자가 보유한 포인트로도 예약 결제를 할 수 있어야 한다."

## 변경 전 예측

리팩토링으로 만든 `PaymentGateway` 포트가 진짜로 OCP(개방-폐쇄)를 만족한다면, 이 요구사항은
**새 어댑터 클래스 하나를 추가하는 것**으로 끝나야 하고 기존 클래스는 한 줄도 안 바뀌어야 한다.

예측:

- **새로 추가**: `PointPaymentAdapter.java` (PaymentGateway 구현체), 그 단위 테스트
  `PointPaymentAdapterTest.java`, 그리고 `TicketService`가 이 어댑터로도 수정 없이 동작함을
  보이는 통합 테스트 `TicketServiceWithPointPaymentTest.java`
- **수정 없음**: `TicketService.java`, `Ticket.java`, `PaymentGateway.java`,
  `TossPaymentAdapter.java`, 기존 `TicketServiceTest.java`

## 실제 변경 파일

```
신규: TicketService/src/main/java/ticket/PointPaymentAdapter.java
신규: TicketService/src/test/java/ticket/PointPaymentAdapterTest.java
신규: TicketService/src/test/java/ticket/TicketServiceWithPointPaymentTest.java
```

기존 파일 수정: **없음**.

## 결과

예측과 실제가 정확히 일치했다 — 변경이 새 어댑터 클래스 + 그 테스트 두 곳에만 갇혔다.
`TicketService`는 생성자에서 `PaymentGateway` 인터페이스만 알고 있고 어떤 구현체가 오는지
모르기 때문에, 새 결제 수단은 그 인터페이스를 구현하는 새 클래스를 추가하는 것만으로
끼워 넣을 수 있었다.

만약 리팩토링 전 원본 코드(`TicketService`가 `PaymentApi` 구체 클래스에 직접 의존)였다면
어떻게 됐을지 대조해보면: `TicketService` 생성자 시그니처와 필드 타입을 바꾸거나, 결제
수단 분기(`if (method == CARD) ... else if (method == POINT) ...`)를 `TicketService` 안에
추가해야 했을 것이다 — 즉 변경이 `TicketService`까지 번졌을 것이다. DIP/OCP를 적용해둔
지점(`PaymentGateway`)이 정확히 그 번짐을 막는 절단면 역할을 한 것이 이번 검증으로 확인됐다.

## 새는 곳이 있었다면

이번엔 새지 않았지만, 만약 새는 지점이 있었다면 가장 유력한 후보는 "결제 수단별로 사전 조건이
다른 경우"였을 것이다. 예를 들어 포인트 결제는 "잔액 부족 시 카드로 자동 전환" 같은 규칙이
붙는 순간, 그 조율 로직을 어디에 둘지(`PaymentGateway` 구현체 내부 vs `TicketService`)를
다시 결정해야 하고, 후자를 택하면 결합이 `TicketService`로 다시 새게 된다. 그 경우 끊는 법은
"전환 규칙" 자체를 별도 정책 객체(`PaymentFallbackPolicy` 같은)로 뽑아 `TicketService`는
여전히 단일 `PaymentGateway` 하나만 호출하도록 유지하는 것이다.
