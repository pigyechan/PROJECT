package ticket.adapter.out.persistence;

import org.springframework.stereotype.Repository;

import ticket.User;
import ticket.UserRepository;

// Outbound Adapter: 도메인 포트 UserRepository 를 실제 Postgres(JPA)로 구현한다.
// Core(ticket.TicketService)는 이 클래스가 존재하는지조차 모른다 — 포트 인터페이스만 안다.
@Repository
public class JpaUserRepositoryAdapter implements UserRepository {

    private final UserJpaRepository userJpaRepository;

    public JpaUserRepositoryAdapter(UserJpaRepository userJpaRepository) {
        this.userJpaRepository = userJpaRepository;
    }

    @Override
    public User findById(long id) {
        return userJpaRepository.findById(id)
                .map(entity -> new User(entity.getId(), entity.getName()))
                .orElse(null);
    }
}
