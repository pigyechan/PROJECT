package ticket;

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

    // Move Method: TicketService 에 절차적으로 나열되어 있던
    // "이미 예약됐는지 검증" + "예약 상태로 전환"을 Ticket 으로 이동.
    public void reserve(long userId) {
        if (this.reserved) {
            throw new TicketAlreadyReservedException("이미 예약된 티켓입니다. id=" + this.id);
        }
        this.reserved = true;
        this.userId = userId;
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
