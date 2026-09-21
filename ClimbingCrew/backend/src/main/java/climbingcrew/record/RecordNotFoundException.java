package climbingcrew.record;

/**
 * 존재하지 않거나 삭제된 기록을 참조할 때 던진다. -> 404 RECORD_NOT_FOUND
 */
public class RecordNotFoundException extends RuntimeException {

    public RecordNotFoundException(String recordId) {
        super("Record not found: " + recordId);
    }
}
