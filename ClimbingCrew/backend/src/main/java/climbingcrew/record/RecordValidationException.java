package climbingcrew.record;

/**
 * 요청 필드 형식/범위 오류(주로 PATCH 의 수동 검증, 쿼리 파라미터 검증)에 대해 던진다.
 * -> 400 VALIDATION_ERROR
 */
public class RecordValidationException extends RuntimeException {

    public RecordValidationException(String message) {
        super(message);
    }
}
