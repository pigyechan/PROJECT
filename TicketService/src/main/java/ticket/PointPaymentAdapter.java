package ticket;

// 새 요구사항: 포인트 결제. PaymentGateway 포트의 또 다른 어댑터.
// TicketService 는 이 클래스의 존재를 몰라도 된다 — 생성자에 무엇을 넘기느냐의 문제일 뿐이다.
public class PointPaymentAdapter implements PaymentGateway {

    private int balance;

    public PointPaymentAdapter(int balance) {
        this.balance = balance;
    }

    @Override
    public boolean charge(int amount, PaymentInfo info) {
        if (balance < amount) {
            return false;
        }
        balance -= amount;
        return true;
    }

    public int getBalance() {
        return balance;
    }
}
