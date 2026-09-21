package climbingcrew.record;

/**
 * 사진/동영상 비동기 업로드 상태. OpenAPI 계약의 Record.mediaStatus 와 동일한 값 집합을 가진다.
 * 이 구현체는 실제 파일 업로드를 처리하지 않으므로, 생성 시점에는 항상 NONE 으로 시작한다.
 */
public enum MediaStatus {
    NONE,
    UPLOADING,
    READY,
    FAILED
}
