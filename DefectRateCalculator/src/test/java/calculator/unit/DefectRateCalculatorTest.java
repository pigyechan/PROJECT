package calculator.unit;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

@DisplayName("불량률 계산기 — 단위 테스트")
class DefectRateCalculatorTest {

    private final DefectRateCalculator calculator = new DefectRateCalculator();

    // ══════════════════════════════════════════════════════
    // 전략 1 : 불량률 계산 로직
    // RED    : calculateDefectRate() 없으므로 컴파일 에러
    // GREEN  : return (double) defective / total * 100
    // REFACTOR: 없음 — 공식 한 줄로 충분
    // ══════════════════════════════════════════════════════
    @Nested
    @DisplayName("불량률 계산 로직")
    class 불량률_계산_로직 {

        @Test
        @DisplayName("불량 10개 / 전체 100개 → 10.0%")
        void 정상_계산() {
            assertEquals(10.0, calculator.calculateDefectRate(10, 100));
        }

        @Test
        @DisplayName("불량 3개 / 전체 200개 → 1.5%  (정수 나눗셈 함정 확인)")
        void 소수점_계산() {
            assertEquals(1.5, calculator.calculateDefectRate(3, 200));
        }
    }

    // ══════════════════════════════════════════════════════
    // 전략 2 : 생산 수량이 0인 경우 예외 처리
    // RED    : Cycle 1 코드는 total=0 에서 예외를 던지지 않음
    // GREEN  : if (total <= 0) throw new IllegalArgumentException(...)
    // REFACTOR: 검증 코드를 validate() 메서드로 분리
    // ══════════════════════════════════════════════════════
    @Nested
    @DisplayName("생산 수량 0 예외 처리")
    class 생산_수량_0_예외 {

        @Test
        @DisplayName("생산 수량 0 → IllegalArgumentException 발생")
        void 생산_수량이_0이면_예외() {
            assertThrows(IllegalArgumentException.class,
                    () -> calculator.calculateDefectRate(0, 0));
        }

        @Test
        @DisplayName("예외 메시지에 '전체 수' 포함")
        void 예외_메시지_확인() {
            IllegalArgumentException ex = assertThrows(IllegalArgumentException.class,
                    () -> calculator.calculateDefectRate(0, 0));
            assertTrue(ex.getMessage().contains("전체 수"));
        }
    }

    // ══════════════════════════════════════════════════════
    // 전략 3 : 불량 수량이 생산 수량보다 많은 경우 예외 처리
    // RED    : 전략 2 코드는 불량 > 전체 케이스를 허용 (101.0% 반환)
    // GREEN  : if (defective > total) throw new IllegalArgumentException(...)
    // REFACTOR: validate() 안으로 병합 — 검증 3개를 한 곳에서 관리
    // ══════════════════════════════════════════════════════
    @Nested
    @DisplayName("불량 수량 > 생산 수량 예외 처리")
    class 불량_수량_초과_예외 {

        @Test
        @DisplayName("불량 101개 / 전체 100개 → IllegalArgumentException 발생")
        void 불량이_전체_초과하면_예외() {
            assertThrows(IllegalArgumentException.class,
                    () -> calculator.calculateDefectRate(101, 100));
        }

        @Test
        @DisplayName("불량 == 전체 → 예외 없음 (100% 불량은 실제로 발생 가능)")
        void 불량과_전체_같으면_허용() {
            assertDoesNotThrow(() -> calculator.calculateDefectRate(100, 100));
        }
    }

    // ══════════════════════════════════════════════════════
    // 전략 4 : 경계값 검증
    // RED    : 경계값이 올바르게 처리되는지 명시적으로 확인 필요
    // GREEN  : 기존 공식이 자동으로 처리 (추가 코드 없음)
    // REFACTOR: 없음
    // ══════════════════════════════════════════════════════
    @Nested
    @DisplayName("경계값 검증")
    class 경계값 {

        @Test
        @DisplayName("불량 0건 → 0.0%")
        void 불량_0건() {
            assertEquals(0.0, calculator.calculateDefectRate(0, 100));
        }

        @Test
        @DisplayName("불량률 100% → 100.0%")
        void 불량률_100퍼센트() {
            assertEquals(100.0, calculator.calculateDefectRate(100, 100));
        }

        @Test
        @DisplayName("음수 입력 → IllegalArgumentException 발생")
        void 음수_입력() {
            assertThrows(IllegalArgumentException.class,
                    () -> calculator.calculateDefectRate(-1, 100));
        }
    }

    // ══════════════════════════════════════════════════════
    // 추가 : 품질 등급 판정 (양호 / 주의 / 불량)
    // RED    : evaluateGrade() 없으므로 컴파일 에러
    // GREEN  : if-else 분기로 등급 문자열 반환
    // REFACTOR: 임계값 1.0, 5.0 → 상수(WARNING_THRESHOLD, DEFECT_THRESHOLD)
    // ══════════════════════════════════════════════════════
    @Nested
    @DisplayName("품질 등급 판정")
    class 품질_등급_판정 {

        @Test
        @DisplayName("불량률 0.9% → 양호")
        void 양호() {
            assertEquals("양호", calculator.evaluateGrade(0.9));
        }

        @Test
        @DisplayName("불량률 1.0% — 주의 시작 경계 → 주의")
        void 주의_하한_경계() {
            assertEquals("주의", calculator.evaluateGrade(1.0));
        }

        @Test
        @DisplayName("불량률 4.9% → 주의")
        void 주의() {
            assertEquals("주의", calculator.evaluateGrade(4.9));
        }

        @Test
        @DisplayName("불량률 5.0% — 불량 시작 경계 → 불량")
        void 불량_하한_경계() {
            assertEquals("불량", calculator.evaluateGrade(5.0));
        }

        @Test
        @DisplayName("불량률 10.0% → 불량")
        void 불량() {
            assertEquals("불량", calculator.evaluateGrade(10.0));
        }
    }
}
