package climbingcrew.record;

import jakarta.persistence.CollectionTable;
import jakarta.persistence.Column;
import jakarta.persistence.ElementCollection;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Table;

import java.time.Instant;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * 방문 기록(Record) JPA 엔티티.
 *
 * 이름을 RecordEntity 로 둔 이유: java.lang.Record (Java 16+ 의 record 키워드/타입)와의
 * 이름 충돌 및 혼동을 피하기 위함.
 *
 * 이 프로젝트에는 아직 인증/크루 멤버십 시스템이 없으므로, authorId 는 서비스 계층에서
 * 고정된 placeholder 값으로 채워진다 (RecordService.PLACEHOLDER_AUTHOR_ID 참고).
 *
 * "좋아요"는 사용자별로 구분되지 않고 이 레코드에 대한 단일 boolean(liked)로 표현한다.
 * 실제 다중 사용자 좋아요를 구분하려면 별도의 Like 엔티티(recordId + userId)가 필요하지만,
 * 인증 시스템이 없는 현재 상태에서는 "누가 눌렀는지"를 구분할 방법이 없으므로 최소 구현으로
 * boolean 하나만 두었다. 이 값은 POST/DELETE /likes 의 멱등성 요구사항(이미 눌렀어도 204,
 * 안 눌려있어도 204)을 만족시키기에 충분하다.
 */
@Entity
@Table(name = "records")
public class RecordEntity {

    @Id
    private String id;

    @Column(nullable = false)
    private String authorId;

    @Column(nullable = false, length = 100)
    private String gymName;

    @Column(nullable = false)
    private LocalDate visitDate;

    private Integer rating;

    @Column(length = 30)
    private String review;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Visibility visibility;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private MediaStatus mediaStatus;

    @ElementCollection
    @CollectionTable(name = "record_media_urls", joinColumns = @JoinColumn(name = "record_id"))
    @Column(name = "url")
    private List<String> mediaUrls = new ArrayList<>();

    @Column(nullable = false)
    private boolean liked;

    /**
     * 클라이언트가 POST /records 요청 시 보낸 Idempotency-Key. 같은 키로 재시도하면
     * 새로 생성하지 않고 기존 레코드를 그대로 반환하기 위해 저장해 둔다.
     */
    @Column(nullable = false, unique = true)
    private String idempotencyKey;

    @Column(nullable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getAuthorId() {
        return authorId;
    }

    public void setAuthorId(String authorId) {
        this.authorId = authorId;
    }

    public String getGymName() {
        return gymName;
    }

    public void setGymName(String gymName) {
        this.gymName = gymName;
    }

    public LocalDate getVisitDate() {
        return visitDate;
    }

    public void setVisitDate(LocalDate visitDate) {
        this.visitDate = visitDate;
    }

    public Integer getRating() {
        return rating;
    }

    public void setRating(Integer rating) {
        this.rating = rating;
    }

    public String getReview() {
        return review;
    }

    public void setReview(String review) {
        this.review = review;
    }

    public Visibility getVisibility() {
        return visibility;
    }

    public void setVisibility(Visibility visibility) {
        this.visibility = visibility;
    }

    public MediaStatus getMediaStatus() {
        return mediaStatus;
    }

    public void setMediaStatus(MediaStatus mediaStatus) {
        this.mediaStatus = mediaStatus;
    }

    public List<String> getMediaUrls() {
        return mediaUrls;
    }

    public void setMediaUrls(List<String> mediaUrls) {
        this.mediaUrls = mediaUrls;
    }

    public boolean isLiked() {
        return liked;
    }

    public void setLiked(boolean liked) {
        this.liked = liked;
    }

    public int getLikeCount() {
        return liked ? 1 : 0;
    }

    public String getIdempotencyKey() {
        return idempotencyKey;
    }

    public void setIdempotencyKey(String idempotencyKey) {
        this.idempotencyKey = idempotencyKey;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
