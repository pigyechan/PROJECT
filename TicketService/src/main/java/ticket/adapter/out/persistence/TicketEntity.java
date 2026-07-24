package ticket.adapter.out.persistence;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

// DB의 "tickets" 테이블 한 행을 표현하는 JPA 전용 클래스. ticket.Ticket(도메인)과 분리되어 있다.
@Entity
@Table(name = "tickets")
public class TicketEntity {

    @Id
    private Long id;

    private int price;

    private boolean reserved;

    private Long userId;

    protected TicketEntity() {
    }

    public TicketEntity(Long id, int price, boolean reserved, Long userId) {
        this.id = id;
        this.price = price;
        this.reserved = reserved;
        this.userId = userId;
    }

    public Long getId() {
        return id;
    }

    public int getPrice() {
        return price;
    }

    public boolean isReserved() {
        return reserved;
    }

    public Long getUserId() {
        return userId;
    }
}
