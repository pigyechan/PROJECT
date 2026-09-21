package climbingcrew.record;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
public class RecordService {

    /**
     * 이 프로젝트에는 아직 인증/사용자 시스템이 없다. OpenAPI 계약은 authorId 가 어떻게
     * 채워지는지 규정하지 않으므로(과제 지침에 따라), 모든 레코드는 이 고정된 placeholder
     * 사용자가 작성한 것으로 취급한다. 실제 인증이 도입되면 이 부분을 SecurityContext 등에서
     * 얻은 사용자 ID로 교체하면 된다.
     */
    static final String PLACEHOLDER_AUTHOR_ID = "placeholder-user";

    private final RecordRepository recordRepository;

    public RecordService(RecordRepository recordRepository) {
        this.recordRepository = recordRepository;
    }

    public RecordResponse create(String idempotencyKey, RecordCreateRequest request) {
        Optional<RecordEntity> existing = recordRepository.findByIdempotencyKey(idempotencyKey);
        if (existing.isPresent()) {
            // 같은 Idempotency-Key 로 재시도된 요청: 새로 만들지 않고 기존 결과를 그대로 반환한다.
            return toResponse(existing.get());
        }

        boolean duplicate = recordRepository.existsByAuthorIdAndGymNameAndVisitDate(
                PLACEHOLDER_AUTHOR_ID, request.getGymName(), request.getVisitDate());
        if (duplicate) {
            throw new DuplicateRecordException(request.getGymName(), request.getVisitDate());
        }

        Instant now = Instant.now();
        RecordEntity entity = new RecordEntity();
        entity.setId(UUID.randomUUID().toString());
        entity.setAuthorId(PLACEHOLDER_AUTHOR_ID);
        entity.setGymName(request.getGymName());
        entity.setVisitDate(request.getVisitDate());
        entity.setRating(request.getRating());
        entity.setReview(request.getReview());
        entity.setVisibility(request.getVisibility() != null ? request.getVisibility() : Visibility.CREW_ONLY);
        entity.setMediaStatus(MediaStatus.NONE);
        entity.setMediaUrls(new ArrayList<>());
        entity.setLiked(false);
        entity.setIdempotencyKey(idempotencyKey);
        entity.setCreatedAt(now);
        entity.setUpdatedAt(now);

        RecordEntity saved = recordRepository.save(entity);
        return toResponse(saved);
    }

    public RecordListResponse list(String gymName, int page, int size) {
        if (page < 0) {
            throw new RecordValidationException("page must be >= 0");
        }
        if (size < 1 || size > 100) {
            throw new RecordValidationException("size must be between 1 and 100");
        }

        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        Page<RecordEntity> result = (gymName != null && !gymName.isBlank())
                ? recordRepository.findByGymNameContainingIgnoreCase(gymName, pageable)
                : recordRepository.findAll(pageable);

        RecordListResponse response = new RecordListResponse();
        response.setItems(result.getContent().stream().map(this::toResponse).collect(Collectors.toList()));
        response.setPage(page);
        response.setSize(size);
        response.setTotalCount(result.getTotalElements());
        return response;
    }

    public RecordResponse get(String recordId) {
        return toResponse(findOrThrow(recordId));
    }

    /**
     * PATCH 는 "보낸 필드만 갱신"해야 하고, rating/review 는 명시적으로 null 을 보내 값을
     * 지울 수 있어야 한다(둘 다 nullable: true). 평범한 POJO + Bean Validation 으로는
     * "필드를 안 보냄"과 "필드를 null 로 보냄"을 구분할 수 없으므로, 원본 JSON 트리(JsonNode)를
     * 받아 각 필드의 존재 여부(has)와 null 여부(isNull)를 직접 검사한다.
     */
    public RecordResponse update(String recordId, JsonNode patch) {
        RecordEntity entity = findOrThrow(recordId);

        if (patch.has("gymName")) {
            JsonNode node = patch.get("gymName");
            if (node.isNull()) {
                throw new RecordValidationException("gymName must not be null");
            }
            String gymName = node.asText();
            if (gymName.isEmpty() || gymName.length() > 100) {
                throw new RecordValidationException("gymName must be between 1 and 100 characters");
            }
            entity.setGymName(gymName);
        }

        if (patch.has("visitDate")) {
            JsonNode node = patch.get("visitDate");
            if (node.isNull()) {
                throw new RecordValidationException("visitDate must not be null");
            }
            try {
                entity.setVisitDate(LocalDate.parse(node.asText()));
            } catch (DateTimeParseException e) {
                throw new RecordValidationException("visitDate must be a valid date (yyyy-MM-dd)");
            }
        }

        if (patch.has("rating")) {
            JsonNode node = patch.get("rating");
            if (node.isNull()) {
                entity.setRating(null);
            } else {
                if (!node.isInt()) {
                    throw new RecordValidationException("rating must be an integer");
                }
                int rating = node.asInt();
                if (rating < 1 || rating > 5) {
                    throw new RecordValidationException("rating must be between 1 and 5");
                }
                entity.setRating(rating);
            }
        }

        if (patch.has("review")) {
            JsonNode node = patch.get("review");
            if (node.isNull()) {
                entity.setReview(null);
            } else {
                String review = node.asText();
                if (review.length() > 30) {
                    throw new RecordValidationException("review must be at most 30 characters");
                }
                entity.setReview(review);
            }
        }

        if (patch.has("visibility")) {
            JsonNode node = patch.get("visibility");
            if (node.isNull()) {
                throw new RecordValidationException("visibility must not be null");
            }
            try {
                entity.setVisibility(Visibility.valueOf(node.asText()));
            } catch (IllegalArgumentException e) {
                throw new RecordValidationException("visibility must be one of PUBLIC, CREW_ONLY, PRIVATE");
            }
        }

        entity.setUpdatedAt(Instant.now());
        RecordEntity saved = recordRepository.save(entity);
        return toResponse(saved);
    }

    public void delete(String recordId) {
        if (!recordRepository.existsById(recordId)) {
            throw new RecordNotFoundException(recordId);
        }
        recordRepository.deleteById(recordId);
    }

    public void like(String recordId) {
        RecordEntity entity = findOrThrow(recordId);
        if (!entity.isLiked()) {
            entity.setLiked(true);
            entity.setUpdatedAt(Instant.now());
            recordRepository.save(entity);
        }
    }

    public void unlike(String recordId) {
        RecordEntity entity = findOrThrow(recordId);
        if (entity.isLiked()) {
            entity.setLiked(false);
            entity.setUpdatedAt(Instant.now());
            recordRepository.save(entity);
        }
    }

    private RecordEntity findOrThrow(String recordId) {
        return recordRepository.findById(recordId)
                .orElseThrow(() -> new RecordNotFoundException(recordId));
    }

    private RecordResponse toResponse(RecordEntity entity) {
        RecordResponse response = new RecordResponse();
        response.setId(entity.getId());
        response.setAuthorId(entity.getAuthorId());
        response.setGymName(entity.getGymName());
        response.setVisitDate(entity.getVisitDate());
        response.setRating(entity.getRating());
        response.setReview(entity.getReview());
        response.setVisibility(entity.getVisibility().name());
        response.setMediaStatus(entity.getMediaStatus().name());
        response.setMediaUrls(new ArrayList<>(entity.getMediaUrls()));
        response.setLikeCount(entity.getLikeCount());
        response.setCreatedAt(entity.getCreatedAt());
        response.setUpdatedAt(entity.getUpdatedAt());
        return response;
    }
}
