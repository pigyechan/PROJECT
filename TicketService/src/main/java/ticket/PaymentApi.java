package ticket;

// [원본 상태 — DIP 위반] 특정 결제사(Toss)의 구체 API. TicketService가 이 구체 클래스를
// 직접 의존한다 — 고수준 정책이 저수준 구현에 종속된 상태.
public class PaymentApi {

    public boolean charge(int amount, PaymentInfo info) {
        // kata 단순화를 위해 항상 성공 처리. 실제로는 외부 API 호출부.
        return true;
    }
}
