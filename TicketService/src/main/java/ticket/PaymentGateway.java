package ticket;

// Extract Interface: PaymentApi 의 공개 계약만 뽑아낸 포트(Port).
// TicketService 는 이제 이 인터페이스에만 의존한다 (DIP).
public interface PaymentGateway {

    boolean charge(int amount, PaymentInfo info);
}
