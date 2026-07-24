package ticket.acceptance;

import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;

import ticket.PaymentGateway;
import ticket.PaymentInfo;

// 결제사(Toss)는 Testcontainers로 띄울 수 있는 "인프라"가 아니라 외부 SaaS라서,
// 실제 결제망 대신 시나리오별로 성공/실패를 직접 제어할 수 있는 테스트 전용 어댑터를 쓴다.
// @Primary로 등록해서, 운영용 TossPaymentAdapter 빈보다 테스트에서 우선 선택되게 한다.
public class ControllablePaymentGateway implements PaymentGateway {

    private boolean shouldSucceed = true;

    @Override
    public boolean charge(int amount, PaymentInfo info) {
        return shouldSucceed;
    }

    public void succeed() {
        this.shouldSucceed = true;
    }

    public void fail() {
        this.shouldSucceed = false;
    }

    @TestConfiguration
    public static class Config {

        @Bean
        @Primary
        ControllablePaymentGateway controllablePaymentGateway() {
            return new ControllablePaymentGateway();
        }
    }
}
