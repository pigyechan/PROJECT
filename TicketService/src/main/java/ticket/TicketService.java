package ticket;

// [원본 상태]
// SRP 위반: 유저 조회 + 티켓 검증 + 결제 처리 + 영속화가 한 메서드에 절차적으로 나열.
public class TicketService {

    private final UserRepository userRepository;
    private final TicketRepository ticketRepository;
    private final PaymentGateway paymentGateway;

    public TicketService(UserRepository userRepository, TicketRepository ticketRepository, PaymentGateway paymentGateway) {
        this.userRepository = userRepository;
        this.ticketRepository = ticketRepository;
        this.paymentGateway = paymentGateway;
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

        boolean paid = paymentGateway.charge(ticket.getPrice(), info);
        if (!paid) {
            throw new PaymentFailedException("결제에 실패했습니다.");
        }

        ticket.reserve(userId);
        ticketRepository.save(ticket);

        return true;
    }
}
