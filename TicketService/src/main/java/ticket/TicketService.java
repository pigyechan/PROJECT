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
