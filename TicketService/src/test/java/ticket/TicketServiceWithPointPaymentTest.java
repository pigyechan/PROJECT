package ticket;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.when;

/**
 * TicketService 가 TossPaymentAdapter 뿐 아니라 새로 추가한 PointPaymentAdapter 로도
 * 수정 없이 동작하는지 확인한다 — OCP 검증용 통합 테스트.
 * TicketService.java 는 이 테스트를 위해 단 한 줄도 바뀌지 않았다.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("TicketService — PointPaymentAdapter 로 예약 (OCP 검증)")
class TicketServiceWithPointPaymentTest {

    @Mock
    UserRepository userRepository;

    @Mock
    TicketRepository ticketRepository;

    @Test
    @DisplayName("포인트 잔액이 충분하면 PointPaymentAdapter 로도 예약에 성공한다")
    void 포인트_결제로_예약_성공() {
        // given
        PointPaymentAdapter pointPaymentAdapter = new PointPaymentAdapter(100_000);
        TicketService service = new TicketService(userRepository, ticketRepository, pointPaymentAdapter);

        when(userRepository.findById(1L)).thenReturn(new User(1L, "채민"));
        Ticket ticket = new Ticket(100L, 50_000);
        when(ticketRepository.findById(100L)).thenReturn(ticket);

        // when
        boolean result = service.reserveTicket(1L, 100L, new PaymentInfo("N/A"));

        // then
        assertThat(result).isTrue();
        assertThat(ticket.isReserved()).isTrue();
        assertThat(pointPaymentAdapter.getBalance()).isEqualTo(50_000);
    }
}
