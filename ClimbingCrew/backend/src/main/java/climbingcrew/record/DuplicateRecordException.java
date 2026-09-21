package climbingcrew.record;

import java.time.LocalDate;

/**
 * 같은 작성자가 같은 날 같은 암장으로 이미 기록을 가지고 있을 때 던진다. -> 409 DUPLICATE_RECORD
 */
public class DuplicateRecordException extends RuntimeException {

    public DuplicateRecordException(String gymName, LocalDate visitDate) {
        super("A record for gym '" + gymName + "' on " + visitDate + " already exists");
    }
}
