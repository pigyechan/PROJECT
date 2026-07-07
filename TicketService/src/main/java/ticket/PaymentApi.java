package ticket;

// 특정 결제사(Toss)의 구체 API. PaymentGateway 포트의 어댑터(Adapter).
public class PaymentApi implements PaymentGateway {

    @Override
    public boolean charge(int amount, PaymentInfo info) {
        // kata 단순화를 위해 항상 성공 처리. 실제로는 외부 API 호출부.
        return true;
    }
}
