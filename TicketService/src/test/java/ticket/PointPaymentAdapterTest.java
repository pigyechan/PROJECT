package ticket;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

@DisplayName("PointPaymentAdapter — 단위 테스트")
class PointPaymentAdapterTest {

    PaymentInfo paymentInfo = new PaymentInfo("N/A");

    @Nested
    @DisplayName("잔액이 충분할 때")
    class 잔액_충분 {

        @Test
        @DisplayName("결제에 성공하고 잔액이 차감된다")
        void 결제_성공_잔액_차감() {
            // given
            PointPaymentAdapter adapter = new PointPaymentAdapter(10_000);

            // when
            boolean result = adapter.charge(3_000, paymentInfo);

            // then
            assertThat(result).isTrue();
            assertThat(adapter.getBalance()).isEqualTo(7_000);
        }
    }

    @Nested
    @DisplayName("잔액이 부족할 때")
    class 잔액_부족 {

        @Test
        @DisplayName("결제에 실패하고 잔액은 그대로다")
        void 결제_실패_잔액_유지() {
            // given
            PointPaymentAdapter adapter = new PointPaymentAdapter(1_000);

            // when
            boolean result = adapter.charge(3_000, paymentInfo);

            // then
            assertThat(result).isFalse();
            assertThat(adapter.getBalance()).isEqualTo(1_000);
        }
    }
}
