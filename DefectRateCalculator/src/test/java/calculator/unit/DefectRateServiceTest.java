package calculator.unit;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * Mock 을 언제 쓰는가?
 *   → 외부 시스템(DB, API 등)과 연결되는 부분에서 사용한다.
 *
 * 이 테스트에서 DefectRateRepository 는 실제 DB 가 없어도 동작한다.
 * Mockito 가 가짜 구현체를 만들어서 원하는 값을 대신 돌려주기 때문이다.
 *
 * 덕분에 Service 의 비즈니스 로직(조회 → 계산 → 저장)만 빠르고 정확하게 검증할 수 있다.
 */
@ExtendWith(MockitoExtension.class)             // Mockito 를 JUnit 5 에 연결
@DisplayName("DefectRateService — Mock 단위 테스트")
class DefectRateServiceTest {

    // @Mock : "이 인터페이스를 가짜로 만들어 줘"
    // 실제 DB 구현체가 없어도 된다.
    @Mock
    DefectRateRepository repository;

    DefectRateService service;

    @BeforeEach
    void setUp() {
        // 가짜 repository 를 Service 에 주입
        service = new DefectRateService(repository, new DefectRateCalculator());
    }

    // ══════════════════════════════════════════════════════
    // RED    : DefectRateService 없으므로 컴파일 에러



    // GREEN  : Service 구현 — findById → 계산 → saveResult
    // REFACTOR: null 처리를 Service 안에서 명시적 예외로 분리
    // ══════════════════════════════════════════════════════

    @Nested
    @DisplayName("정상 — 조회 후 계산")
    class 정상_케이스 {

        @Test
        @DisplayName("Repository 에서 데이터를 가져와 불량률을 계산한다")
        void 조회_후_불량률_계산() {
            // given
            // "findById(1L) 을 호출하면 이 값을 돌려줘" 라고 가짜 행동 설정
            when(repository.findById(1L))
                    .thenReturn(new ProductionRecord(10, 100));

            // when
            double result = service.calculate(1L);

            // then
            assertEquals(10.0, result);
        }

        @Test
        @DisplayName("계산 결과를 Repository 에 저장한다")
        void 계산_결과_저장() {
            // given
            when(repository.findById(1L))
                    .thenReturn(new ProductionRecord(10, 100));

            // when
            service.calculate(1L);

            // then
            // verify : "saveResult 가 이 인자로 실제로 호출됐는지" 검증
            verify(repository).saveResult(1L, 10.0, "불량");
        }

        @Test
        @DisplayName("findById 는 딱 한 번만 호출된다")
        void 저장소_조회_횟수_검증() {
            // given
            when(repository.findById(1L))
                    .thenReturn(new ProductionRecord(10, 100));

            // when
            service.calculate(1L);

            // then
            verify(repository).findById(1L);
        }
    }

    @Nested
    @DisplayName("예외 — 데이터 없음")
    class 예외_케이스 {

        @Test
        @DisplayName("Repository 가 null 을 반환하면 IllegalArgumentException 발생")
        void 데이터_없을_때_예외() {
            // given
            // "findById(999L) 을 부르면 null 을 줘" 라고 가짜 행동 설정
            when(repository.findById(999L)).thenReturn(null);

            // when & then
            assertThrows(IllegalArgumentException.class,
                    () -> service.calculate(999L));
        }

        @Test
        @DisplayName("데이터 없으면 saveResult 는 호출되지 않는다")
        void 데이터_없으면_저장_안_함() {
            // given
            when(repository.findById(999L)).thenReturn(null);

            // when
            assertThrows(IllegalArgumentException.class,
                    () -> service.calculate(999L));

            // then
            // verifyNoMoreInteractions : saveResult 가 아예 호출되지 않았는지 검증
            verify(repository, never()).saveResult(any(), anyDouble(), anyString());
        }
    }
}
