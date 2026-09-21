package climbingcrew.record;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/records")
public class RecordController {

    private final RecordService recordService;

    public RecordController(RecordService recordService) {
        this.recordService = recordService;
    }

    @PostMapping
    public ResponseEntity<RecordResponse> create(
            @RequestHeader("Idempotency-Key") String idempotencyKey,
            @Valid @RequestBody RecordCreateRequest request) {
        RecordResponse response = recordService.create(idempotencyKey, request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping
    public ResponseEntity<RecordListResponse> list(
            @RequestParam(required = false) String crewId,
            @RequestParam(required = false) String gymName,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        // crewId: 이 구현에는 아직 크루/멤버십 시스템이 없고(Record 스키마에도 crewId 필드가
        // 없음), RecordCreateRequest 에도 crewId 를 받을 방법이 없어 레코드를 크루에
        // 연결할 데이터 자체가 없다. 계약과의 호환을 위해 파라미터는 받아들이되 필터링에는
        // 사용하지 않는다 (최종 보고서에 기재).
        RecordListResponse response = recordService.list(gymName, page, size);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{recordId}")
    public ResponseEntity<RecordResponse> get(@PathVariable String recordId) {
        return ResponseEntity.ok(recordService.get(recordId));
    }

    @PatchMapping("/{recordId}")
    public ResponseEntity<RecordResponse> update(@PathVariable String recordId, @RequestBody JsonNode patch) {
        return ResponseEntity.ok(recordService.update(recordId, patch));
    }

    @DeleteMapping("/{recordId}")
    public ResponseEntity<Void> delete(@PathVariable String recordId) {
        recordService.delete(recordId);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{recordId}/likes")
    public ResponseEntity<Void> like(@PathVariable String recordId) {
        recordService.like(recordId);
        return ResponseEntity.noContent().build();
    }

    @DeleteMapping("/{recordId}/likes")
    public ResponseEntity<Void> unlike(@PathVariable String recordId) {
        recordService.unlike(recordId);
        return ResponseEntity.noContent().build();
    }
}
