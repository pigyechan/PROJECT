package ticket.adapter.out.persistence;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

// DB의 "users" 테이블 한 행(row)을 그대로 표현하는 JPA 전용 클래스.
// 도메인 클래스 ticket.User 와 일부러 분리했다 — Core(ticket.User)가 JPA(@Entity 등)를 몰라야 하기 때문이다.
@Entity
@Table(name = "users")
public class UserEntity {

    @Id
    private Long id;

    private String name;

    protected UserEntity() {
    }

    public UserEntity(Long id, String name) {
        this.id = id;
        this.name = name;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }
}
