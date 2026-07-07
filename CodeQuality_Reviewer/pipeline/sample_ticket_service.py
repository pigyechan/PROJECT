"""
B-2 TicketService 원본("죽은 코드") 샘플 입력 생성기.
실행: python pipeline/sample_ticket_service.py

TicketService/(B-5에서 수작업으로 리팩토링한 실제 프로젝트) 커밋 e3b74ab 시점의
원본 코드를 그대로 브리핑에 담는다. test_project_dir 은 실제 TicketService/ 를
가리키므로, Validate 단계는 "지금 이 저장소의 테스트 스위트가 GREEN인가"를
진짜로 실행해서 확인한다 (Test_Writer sample_defect_rate.py 패턴 재사용).
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

# 커밋 e3b74ab (TicketService kata: 원본 코드 + 특성화 테스트 GREEN) 시점의 원본.
DEAD_CODE = '''// FILE: Ticket.java
package ticket;

// [원본 상태] Anemic Domain Model — 검증/상태 전이 규칙 없이 getter/setter만 노출.
// "예약 가능한가"와 "예약 상태로 바꾼다"는 지식은 전부 TicketService 쪽에 있다.
public class Ticket {

    private final long id;
    private final int price;
    private boolean reserved;
    private long userId;

    public Ticket(long id, int price) {
        this.id = id;
        this.price = price;
    }

    public long getId() {
        return id;
    }

    public int getPrice() {
        return price;
    }

    public boolean isReserved() {
        return reserved;
    }

    public void setReserved(boolean reserved) {
        this.reserved = reserved;
    }

    public long getUserId() {
        return userId;
    }

    public void setUserId(long userId) {
        this.userId = userId;
    }
}

// FILE: TicketService.java
package ticket;

// [원본 상태]
// SRP 위반: 유저 조회 + 티켓 검증 + 결제 처리 + 영속화가 한 메서드에 절차적으로 나열.
// DIP 위반: 고수준 정책(TicketService)이 저수준 구체 클래스(PaymentApi)에 직접 의존.
public class TicketService {

    private final UserRepository userRepository;
    private final TicketRepository ticketRepository;
    private final PaymentApi paymentApi;

    public TicketService(UserRepository userRepository, TicketRepository ticketRepository, PaymentApi paymentApi) {
        this.userRepository = userRepository;
        this.ticketRepository = ticketRepository;
        this.paymentApi = paymentApi;
    }

    public boolean reserveTicket(long userId, long ticketId, PaymentInfo info) {
        User user = userRepository.findById(userId);
        if (user == null) {
            throw new UserNotFoundException("유저를 찾을 수 없습니다. id=" + userId);
        }

        Ticket ticket = ticketRepository.findById(ticketId);
        if (ticket.isReserved()) {
            throw new TicketAlreadyReservedException("이미 예약된 티켓입니다. id=" + ticketId);
        }

        boolean paid = paymentApi.charge(ticket.getPrice(), info);
        if (!paid) {
            throw new PaymentFailedException("결제에 실패했습니다.");
        }

        ticket.setReserved(true);
        ticket.setUserId(userId);
        ticketRepository.save(ticket);

        return true;
    }
}

// FILE: PaymentApi.java
package ticket;

// [원본 상태 — DIP 위반] 특정 결제사(Toss)의 구체 API. TicketService가 이 구체 클래스를
// 직접 의존한다 — 고수준 정책이 저수준 구현에 종속된 상태.
public class PaymentApi {

    public boolean charge(int amount, PaymentInfo info) {
        // kata 단순화를 위해 항상 성공 처리. 실제로는 외부 API 호출부.
        return true;
    }
}
'''

BRIEF = {
    "feature_name": "TicketService (B-2 원본, 커밋 e3b74ab)",
    "code": DEAD_CODE,
    "context": (
        "Java 21. Gradle + JUnit5 + Mockito 프로젝트. "
        "UserRepository/TicketRepository는 인터페이스, User/PaymentInfo는 값 객체(생략). "
        "이 코드에 대한 특성화 테스트(TicketServiceTest, 8케이스)가 이미 존재하며 GREEN 상태다. "
        "SOLID 위반과 Anemic Domain 여부를 진단하고, Fowler 카탈로그 기법으로 리팩토링 방향을 제안하라."
    ),
    # 실제 TicketService 프로젝트 경로. Validate 단계가 여기서 gradle test 를 실행해
    # "지금 이 저장소가 GREEN인가"를 코드로 확인한다.
    "test_project_dir": str(Path(__file__).parent.parent.parent / "TicketService"),
}


def main() -> None:
    brief_hash = hashlib.sha256(
        json.dumps(BRIEF, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()[:16]

    payload = {
        "brief_hash": brief_hash,
        "brief": BRIEF,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:8]
    run_dir = Path("runs") / f"{timestamp}_{short_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    output_path = run_dir / "01_input.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"생성 완료: {output_path}")
    print(f"brief_hash: {brief_hash}")
    print(f"test_project_dir: {BRIEF['test_project_dir']}")
    print(f"\n실행: python pipeline/main.py {run_dir}")


if __name__ == "__main__":
    main()
