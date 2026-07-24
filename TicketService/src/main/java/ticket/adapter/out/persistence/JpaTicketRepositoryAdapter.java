package ticket.adapter.out.persistence;

import org.springframework.stereotype.Repository;

import ticket.Ticket;
import ticket.TicketRepository;

// Outbound Adapter: 도메인 포트 TicketRepository 를 실제 Postgres(JPA)로 구현한다.
//
// ticket.Ticket 은 "Remove Setting Method" 리팩토링으로 reserve(userId) 외에는
// 예약 상태를 바꿀 방법이 없다(불변식 보호). DB에서 이미 예약된 티켓을 읽어올 때도
// 새 생성자 대신 기존 reserve() 를 그대로 재사용해서 상태를 재구성한다 — Core 코드는 한 글자도 안 바꿨다.
@Repository
public class JpaTicketRepositoryAdapter implements TicketRepository {

    private final TicketJpaRepository ticketJpaRepository;

    public JpaTicketRepositoryAdapter(TicketJpaRepository ticketJpaRepository) {
        this.ticketJpaRepository = ticketJpaRepository;
    }

    @Override
    public Ticket findById(long id) {
        TicketEntity entity = ticketJpaRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("티켓을 찾을 수 없습니다. id=" + id));

        Ticket ticket = new Ticket(entity.getId(), entity.getPrice());
        if (entity.isReserved()) {
            ticket.reserve(entity.getUserId());
        }
        return ticket;
    }

    @Override
    public void save(Ticket ticket) {
        Long userId = ticket.isReserved() ? ticket.getUserId() : null;
        ticketJpaRepository.save(new TicketEntity(ticket.getId(), ticket.getPrice(), ticket.isReserved(), userId));
    }
}
