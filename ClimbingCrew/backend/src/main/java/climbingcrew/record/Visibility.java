package climbingcrew.record;

/**
 * Record 리소스의 공개 범위. OpenAPI 계약의 Record.visibility / RecordCreateRequest.visibility /
 * RecordUpdateRequest.visibility 와 동일한 값 집합을 가진다.
 */
public enum Visibility {
    PUBLIC,
    CREW_ONLY,
    PRIVATE
}
