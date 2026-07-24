# C-6: Walking Skeleton + AI 파이프라인

## 1. Walking Skeleton — 이미 완성된 한 줄기

C-4/C-5에서 만든 코드가 그대로 이번 walking skeleton이다.

```
HTTP 요청
  → TicketController                (Inbound Adapter)
  → TicketReservationUseCase        (Inbound Port)
  → TicketService                   (Core)
  → UserRepository / TicketRepository (Outbound Port)
  → JpaUserRepositoryAdapter / JpaTicketRepositoryAdapter (Outbound Adapter)
  → Postgres (docker-compose: 실행 시 / Testcontainers: 인수테스트 시)
```

- **1-command 기동**: `docker compose up --build` (C-4에서 검증)
- **인수테스트 초록불**: `reserve_ticket.feature`의 4개 시나리오가 Testcontainers의 실제 Postgres로 통과 (C-5, GitHub Actions에서 확인)

## 2. AI 파이프라인 — 이번엔 대화형으로 운영

`Test_Writer`(1-1)/`CodeQuality_Reviewer`처럼 별도 Python Gen/Critique/Eval 스크립트를 새로 만드는 대신, **Claude Code와의 대화 자체를 파이프라인으로 썼다.** 컨텍스트는 새로 만든 [`TicketService/CLAUDE.md`](../CLAUDE.md)에 헥사고날 컨벤션(패키지=레이어, 의존성 방향, 리뷰 체크리스트 3개 항목)으로 고정해두었고, 매 레이어를 만들 때마다 이 컨벤션을 기준으로 즉시 검수했다.

## 3. Layer 단위 검수 로그

기존에 생성된 코드를 `TicketService/CLAUDE.md`의 체크리스트 기준으로 레이어별로 재감사했다.

| 레이어 | 파일 | 점검 내용 | 결과 |
|---|---|---|---|
| Core | `TicketService`, `Ticket`, `User`, Port 인터페이스 전부 | import 문이 하나라도 있는가? | **import 0개 — 통과.** 사용자 본인이 `TicketService.java`를 직접 열어 `import` 문이 없음을 육안으로 재확인함 (AI의 자체 보고를 그대로 수용하지 않고 독립적으로 검증). |
| Inbound Adapter | `TicketController` | `TicketService` 구체 클래스가 아니라 `TicketReservationUseCase` 인터페이스만 받는가? | **수용.** 생성자가 인터페이스 타입만 받음. |
| Outbound Adapter | `JpaUserRepositoryAdapter`, `JpaTicketRepositoryAdapter` | 도메인 객체(`User`, `Ticket`)를 그대로 저장하는가, 별도 Entity로 매핑하는가? | **수용.** `UserEntity`/`TicketEntity`로 분리 매핑, 도메인 객체엔 JPA 애노테이션 없음. |
| Composition Root | `BeanConfiguration` | Core와 Adapter를 동시에 아는 유일한 지점인가? | **수용.** 이 파일에서만 `new TicketService(...)` 조립이 일어남. |
| (부가 발견) | `TossPaymentAdapter`, `PointPaymentAdapter` | 다른 어댑터처럼 `ticket.adapter.out`에 있는가? | **기각(구조 일관성 문제로 기록).** 의존 방향은 올바르지만 패키지 위치가 예전 그대로 남아있음 — 다음 리팩토링 대상. |

## 4. 헥사고날 경계 위반 사례 (또는 위반 없음 + 근거)

이번 감사에서는 헥사고날 경계 위반을 발견하지 못했다. 검수 시 적용한 점검은 세 가지였다. 첫째, Core 패키지(`ticket` 루트)의 모든 파일에서 import 문을 확인했는데, `TicketService`·`Ticket`·`User`·Port 인터페이스 전부 import가 하나도 없어 프레임워크 의존이 전혀 없었다. 둘째, Outbound Adapter(`JpaUserRepositoryAdapter`, `JpaTicketRepositoryAdapter`)가 Core의 도메인 객체(`User`, `Ticket`)를 그대로 저장하지 않고, JPA 전용 Entity(`UserEntity`, `TicketEntity`)로 별도 매핑하는지 확인했다. 실제로 도메인 객체에는 `@Entity` 같은 JPA 애노테이션이 전혀 없었다. 셋째, Inbound Adapter(`TicketController`)가 `TicketService` 구체 클래스가 아니라 `TicketReservationUseCase` 인터페이스만 생성자로 받는지 확인했다.

AI 출력이 경계를 지킨 이유는, 처음부터 패키지 구조 자체를 `ticket`(Core) / `ticket.adapter.in` / `ticket.adapter.out` / `ticket.config`로 미리 분리해두고 코드를 생성했기 때문이라고 판단된다.

다만 완벽하지는 않았는데, `TossPaymentAdapter`와 `PointPaymentAdapter`는 다른 어댑터들과 달리 `ticket.adapter.out`으로 옮겨지지 않고 예전 위치(`ticket` 루트)에 그대로 남아 있었다. 의존 방향 자체는 여전히 올바르므로 경계 위반은 아니지만, 패키지 구조의 일관성이 깨진 사례로 기록해 다음 리팩토링 대상으로 남긴다.

**중요한 메타 포인트**: 이 "위반 없음" 결론도 AI(본 세션의 Claude)가 스스로 감사한 자체 보고다. `Test_Writer`(1-1)의 "관대한 그린" 사건이 정확히 이 지점을 경고한다 — Eval이 스스로 5점을 줬다고 그걸 그대로 믿으면 안 된다는 것. 그래서 문서화 전에 사용자가 `TicketService.java`를 직접 열어 import 부재를 육안으로 재확인하는 절차를 거쳤다.
