# C-4: 재현 가능한 환경 (Docker, Stateless, docker-compose)

## 1. 1-command 기동

```bash
docker compose up --build
```

`db`(PostgreSQL 컨테이너)가 먼저 뜨고, `pg_isready`로 준비 완료가 확인된 뒤에야 `app`(TicketService) 컨테이너가 시작된다(`depends_on: condition: service_healthy`로 강제). 앱이 뜨면서 `data.sql`이 실행되어 데모용 유저(`id=1`)와 티켓(`id=100`)이 자동으로 채워진다.

기동 후 예약 API 호출 예시:

```bash
curl -X POST http://localhost:8080/tickets/100/reserve \
  -H "Content-Type: application/json" \
  -d '{"userId": 1, "cardNumber": "1234-5678-0000-0000"}'
```

## 2. Stateless(무상태) 설계 메모

이 서비스가 상태(state)를 어떻게, 왜 외부화했는지 정리한다.

**무엇을 외부화했는가.** 예약 도메인 상태(`Ticket.reserved`, `Ticket.userId`, `User` 정보)는 애플리케이션 컨테이너 안의 메모리(예: `Map`)가 아니라, 별도 컨테이너로 띄운 PostgreSQL에 저장한다. `JpaTicketRepositoryAdapter`/`JpaUserRepositoryAdapter`가 이 DB에 접근하는 유일한 통로이고, `TicketService`(Core)는 이 어댑터의 존재 자체를 모른다 — `TicketRepository`/`UserRepository` 포트 인터페이스만 안다. 또한 DB 접속 정보(호스트, 포트, 계정)도 이미지에 하드코딩하지 않고 `DB_HOST`, `DB_PORT`, `DB_USERNAME`, `DB_PASSWORD` 환경변수로 외부화했다 — 같은 이미지를 dev/stage/prod 어디서든 환경변수만 바꿔서 재사용할 수 있다.

**왜 외부화했는가.** 컨테이너 자체는 언제든 재시작되거나, 트래픽이 늘면 여러 개로 복제(scale out)될 수 있어야 한다. 만약 예약 상태를 컨테이너 내부 메모리에 들고 있었다면, ① 컨테이너가 재시작되는 순간 모든 예약 정보가 사라지고, ② 인스턴스를 2개 이상 띄웠을 때 요청이 어느 인스턴스로 가느냐에 따라 "어떤 티켓이 이미 예약됐는지"에 대한 답이 인스턴스마다 달라지는 정합성 문제가 생긴다. 상태를 컨테이너 바깥의 공유 저장소(PostgreSQL)로 빼두면, 애플리케이션 컨테이너는 "요청을 처리하고 버리는" 순수한 실행 단위가 되어 몇 개를 띄우든 모두 같은 진실(DB의 데이터)을 보게 된다. 이것이 수평 확장(horizontal scaling)이 가능한 구조의 전제 조건이다. REST API 쪽도 세션 쿠키 없이 매 요청에 필요한 정보(userId, ticketId, 결제정보)를 전부 담아 보내는 방식이라, 어느 인스턴스가 요청을 받아도 상관없다(로드밸런서 뒤에서 sticky session이 필요 없다).

## 3. 헬스 체크

`spring-boot-starter-actuator` 의존성이 `/actuator/health` 엔드포인트를 자동으로 만들어준다. DB 연결까지 포함해서 상태를 보여준다(`management.endpoint.health.show-details: always`).

**컨테이너가 정상 기동했는지 확인하는 방법**

1. `docker compose ps` — `app`, `db` 두 서비스의 `STATUS` 칸에 `healthy`가 뜨는지 확인한다. (compose 파일에 `healthcheck`를 걸어뒀기 때문에 자동으로 판단된다.)
2. 브라우저나 `curl`로 직접 확인: `curl http://localhost:8080/actuator/health` → `{"status":"UP", ...}` 이 오면 정상.
3. `docker inspect --format='{{json .State.Health}}' <app 컨테이너 ID>` 로 헬스체크 이력(성공/실패 로그)을 직접 볼 수도 있다.

`app`의 healthcheck는 `curl -f http://localhost:8080/actuator/health`이며, `start_period: 30s`를 둬서 Spring Boot가 뜨는 동안(DB 연결, JPA 초기화 등)의 워밍업 시간 동안은 실패해도 컨테이너를 죽이지 않도록 했다.
