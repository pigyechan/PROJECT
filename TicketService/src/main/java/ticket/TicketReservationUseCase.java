package ticket;

// Inbound Port: 드라이빙 어댑터(REST 컨트롤러, Cucumber Step 등)가 Core 를 호출할 때 쓰는 계약.
// TicketService 가 이 인터페이스를 구현함으로써, 바깥(어댑터)은 구체 클래스가 아니라
// 이 포트 하나에만 의존하면 된다 (의존성 역전).
public interface TicketReservationUseCase {

    boolean reserveTicket(long userId, long ticketId, PaymentInfo info);
}
