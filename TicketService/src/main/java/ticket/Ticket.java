package ticket;

// Remove Setting Method: setReserved/setUserId 를 제거해 외부에서 상태를
// 직접 대입할 수 없게 막았다. 상태 변경은 reserve(userId) 하나로만 가능
// (Tell, Don't Ask) — 예약 규칙을 우회할 방법이 코드상 존재하지 않는다.
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

    public long getUserId() {
        return userId;
    }
}
