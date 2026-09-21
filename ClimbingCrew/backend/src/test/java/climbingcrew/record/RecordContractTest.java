package climbingcrew.record;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.hamcrest.Matchers.nullValue;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

// 명세(openapi.yaml)를 코드로 옮긴 계약 테스트. 구현이 아직 없어도 먼저 작성한다
// ("명세 먼저, 구현은 나중" — E-5 핵심 의식).
@SpringBootTest
@AutoConfigureMockMvc
class RecordContractTest {

    @Autowired
    private MockMvc mockMvc;

    // Happy Path: 필수 필드(암장 이름, 날짜)만 보내도 생성되어야 한다.
    // (E-2 컨셉 "부담 없는 기록"이 실제로 지켜지는지 확인하는 핵심 케이스)
    @Test
    void 필수_필드만_보내도_기록이_생성된다() throws Exception {
        String requestBody = """
                {
                  "gymName": "클라이밍파크 강남점",
                  "visitDate": "2026-09-22"
                }
                """;

        mockMvc.perform(post("/records")
                        .header("Idempotency-Key", java.util.UUID.randomUUID().toString())
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.gymName").value("클라이밍파크 강남점"))
                .andExpect(jsonPath("$.visitDate").value("2026-09-22"))
                .andExpect(jsonPath("$.id").isNotEmpty())
                .andExpect(jsonPath("$.visibility").value("CREW_ONLY"))
                // rating을 안 보냈어도 응답 JSON에 필드 자체는 존재해야 한다(값은 null).
                // 주의: jsonPath(...).exists()는 "키가 null값으로 존재"와 "키가 아예 없음"을
                // 구분하지 못하는 것으로 확인됨 — value(nullValue())가 이 경우엔 더 정확하다.
                .andExpect(jsonPath("$.rating").value(nullValue()));
    }

    // Unhappy Path: 필수 필드(gymName)가 없으면 400 VALIDATION_ERROR여야 한다.
    // (error-codes.md에 정의된 비즈니스 에러 코드 체계를 실제로 지키는지 확인)
    @Test
    void 필수_필드_gymName이_없으면_400을_반환한다() throws Exception {
        String requestBody = """
                {
                  "visitDate": "2026-09-22"
                }
                """;

        mockMvc.perform(post("/records")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(requestBody))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("VALIDATION_ERROR"));
    }
}
