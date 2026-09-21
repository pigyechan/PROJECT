package climbingcrew.record;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.Optional;

public interface RecordRepository extends JpaRepository<RecordEntity, String> {

    Optional<RecordEntity> findByIdempotencyKey(String idempotencyKey);

    boolean existsByAuthorIdAndGymNameAndVisitDate(String authorId, String gymName, LocalDate visitDate);

    Page<RecordEntity> findByGymNameContainingIgnoreCase(String gymName, Pageable pageable);
}
