package climbingcrew.record;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.time.LocalDate;

/**
 * POST /records 요청 바디. OpenAPI RecordCreateRequest 스키마와 동일하게
 * gymName, visitDate 만 필수이고 나머지는 전부 선택 필드다.
 */
public class RecordCreateRequest {

    @NotNull(message = "gymName is required")
    @Size(min = 1, max = 100, message = "gymName must be between 1 and 100 characters")
    private String gymName;

    @NotNull(message = "visitDate is required")
    private LocalDate visitDate;

    @Min(value = 1, message = "rating must be >= 1")
    @Max(value = 5, message = "rating must be <= 5")
    private Integer rating;

    @Size(max = 30, message = "review must be at most 30 characters")
    private String review;

    /**
     * 선택 필드. null 이면 서비스 계층에서 계약상의 기본값인 CREW_ONLY 로 채운다.
     */
    private Visibility visibility;

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
}
