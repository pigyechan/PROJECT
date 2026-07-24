# TicketService — 헥사고날 컨벤션 (AI 컨텍스트)

이 프로젝트에서 코드를 생성/수정할 때는 아래 규약을 반드시 지킨다. 위반한 제안은 그 이유를 들어 기각한다.

## 패키지 = 레이어

| 패키지 | 역할 | 무엇을 알아도 되는가 |
|---|---|---|
| `ticket` (루트) | Core: 도메인 모델(`Ticket`, `User`), 유스케이스(`TicketService`), Port 인터페이스(`TicketReservationUseCase`, `UserRepository`, `TicketRepository`, `PaymentGateway`) | **아무 프레임워크도 모른다.** Spring, JPA, HTTP, Testcontainers 등 그 어떤 것도 import 하지 않는다. 순수 Java만 쓴다. |
| `ticket.adapter.in.*` | Inbound Adapter (드라이빙): REST 컨트롤러 등 | Inbound Port(`TicketReservationUseCase`)만 의존한다. Core의 구체 클래스(`TicketService`)나 Outbound Adapter를 직접 알면 안 된다. |
| `ticket.adapter.out.*` | Outbound Adapter (드리븐): JPA 리포지토리 구현체 등 | Outbound Port(`UserRepository` 등)를 구현한다. Spring/JPA를 자유롭게 써도 된다. |
| `ticket.config` | 조립(Composition Root) | 유일하게 Core와 모든 Adapter를 동시에 알아도 되는 곳. 여기서만 `new TicketService(...)` 같은 생성자 조립이 일어난다. |

## 의존성 방향 규칙 (가장 중요)

**항상 바깥(Adapter) → 안쪽(Port) → Core 방향으로만 의존한다. Core는 절대 Adapter를 의존하지 않는다.**

- ✅ `TicketController`(Inbound Adapter)가 `TicketReservationUseCase`(Inbound Port)를 의존 — 허용
- ✅ `JpaTicketRepositoryAdapter`(Outbound Adapter)가 `TicketRepository`(Outbound Port)를 구현 — 허용
- ❌ `TicketService`(Core)가 `JpaTicketRepositoryAdapter`나 `TicketEntity`, `@Repository` 같은 것을 import — **금지, 헥사고날 경계 위반**
- ❌ `Ticket`, `User` 같은 도메인 모델에 `@Entity`, `@Table` 같은 JPA 애노테이션을 붙이는 것 — **금지**. JPA 전용 클래스(`UserEntity`, `TicketEntity`)를 어댑터 쪽에 별도로 둔다.

## 리뷰 체크리스트 (AI 제안을 받으면 매번 확인)

1. Core 패키지(`ticket` 루트)에 새 import가 추가됐다면, 그게 `org.springframework.*`, `jakarta.persistence.*`, 어댑터 패키지(`ticket.adapter.*`) 중 하나인가? → 하나라도 해당하면 기각.
2. 새 Outbound Adapter가 도메인 객체(`Ticket`, `User`)를 그대로 저장하려 하는가, 아니면 별도 Entity로 매핑하는가? → 도메인 객체에 직접 JPA 애노테이션을 붙이려 한다면 기각.
3. 새 Inbound Adapter가 Port 인터페이스가 아니라 `TicketService` 구체 클래스를 직접 생성자로 받으려 하는가? → 기각, Port 인터페이스로 바꾸도록 요청.
