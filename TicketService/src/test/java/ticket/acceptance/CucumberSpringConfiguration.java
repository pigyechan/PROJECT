package ticket.acceptance;

import io.cucumber.spring.CucumberContextConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;

// Cucumber 스텝 정의(TicketReservationStepDefinitions)가 Spring 컨테이너에 올라온
// 진짜 빈(Bean)들(TicketReservationUseCase, JpaUserRepositoryAdapter 등)을
// @Autowired로 그대로 주입받을 수 있게 해주는 연결 지점.
@CucumberContextConfiguration
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.NONE)
@Import({TestcontainersConfiguration.class, ControllablePaymentGateway.Config.class})
public class CucumberSpringConfiguration {
}
