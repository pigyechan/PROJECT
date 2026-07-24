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

티켓이 예약되었는지 여부와 그 티켓을 예약한 사용자 정보 같은 예약상태를 앱 컨테이너 안에 두지 않고, 외부 DB에 저장하도록 했다. 데이터는 영속성이 유지되어야 하기 때문에, 앱이 가상화된 컨테이너 위에서 실행되더라도 데이터를 실제로 저장하고 불러올 수 있는 DB라는 실체가 반드시 있어야 한다. 또한 앱 컨테이너를 여러 개 띄워서 트래픽을 분산시키는 경우에도, 만약 각 컨테이너가 예약 정보를 자기 메모리에 따로 들고 있다면 데이터의 무결성이 깨진다. 서버가 여러 개로 분산되더라도 모든 컨테이너가 같은 정보를 바라보고 있어야 하는데, 컨테이너마다 따로 저장하는 메모리가 있다면 데이터는 신뢰도를 잃게 된다.

## 3. 헬스 체크

`spring-boot-starter-actuator` 의존성이 `/actuator/health` 엔드포인트를 자동으로 만들어준다. DB 연결까지 포함해서 상태를 보여준다(`management.endpoint.health.show-details: always`).

**컨테이너가 정상 기동했는지 확인하는 방법**

1. `docker compose ps` — `app`, `db` 두 서비스의 `STATUS` 칸에 `healthy`가 뜨는지 확인한다. (compose 파일에 `healthcheck`를 걸어뒀기 때문에 자동으로 판단된다.)
2. 브라우저나 `curl`로 직접 확인: `curl http://localhost:8080/actuator/health` → `{"status":"UP", ...}` 이 오면 정상.
3. `docker inspect --format='{{json .State.Health}}' <app 컨테이너 ID>` 로 헬스체크 이력(성공/실패 로그)을 직접 볼 수도 있다.

`app`의 healthcheck는 `curl -f http://localhost:8080/actuator/health`이며, `start_period: 30s`를 둬서 Spring Boot가 뜨는 동안(DB 연결, JPA 초기화 등)의 워밍업 시간 동안은 실패해도 컨테이너를 죽이지 않도록 했다.
