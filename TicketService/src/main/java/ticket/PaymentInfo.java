package ticket;

public class PaymentInfo {

    private final String cardNumber;

    public PaymentInfo(String cardNumber) {
        this.cardNumber = cardNumber;
    }

    public String getCardNumber() {
        return cardNumber;
    }
}
