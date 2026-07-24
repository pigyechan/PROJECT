package ticket.adapter.out.persistence;

import org.springframework.data.jpa.repository.JpaRepository;

// Spring Data JPA가 findById/save 같은 기본 SQL을 자동으로 만들어주는 인터페이스.
// 우리가 SQL을 직접 안 짜도 된다.
public interface UserJpaRepository extends JpaRepository<UserEntity, Long> {
}
