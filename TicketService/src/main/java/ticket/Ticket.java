package ticket;

// [원본 상태] Anemic Domain Model — 검증/상태 전이 규칙 없이 getter/setter만 노출.
// "예약 가능한가"와 "예약 상태로 바꾼다"는 지식은 전부 TicketService 쪽에 있다.
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
