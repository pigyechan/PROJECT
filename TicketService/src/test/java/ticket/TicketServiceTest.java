package ticket;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;

/**
 * 리팩토링 전 원본 TicketService 의 동작을 고정하는 특성화 테스트.
 * 구조를 바꾸기 전, 지금 동작하는 그대로를 안전망으로 남긴다.
 */
@ExtendWith(MockitoExtension.class)
@DisplayName("TicketService — 특성화 테스트 (리팩토링 전 동작 고정)")
class TicketServiceTest {

    @Mock
    UserRepository userRepository;

    @Mock
    TicketRepository ticketRepository;

    @Mock
    PaymentGateway paymentGateway;

    TicketService service;

    PaymentInfo paymentInfo;

    @BeforeEach
    void setUp() {
        service = new TicketService(userRepository, ticketRepository, paymentGateway);
        paymentInfo = new PaymentInfo("1234-5678-0000-0000");
    }

    @Nested
    @DisplayName("정상 — 예약 성공")
    class 정상_케이스 {

        @Test
        @DisplayName("유저 존재 + 미예약 티켓 + 결제 성공 시 예약에 성공하고 true 를 반환한다")
        void 예약_성공() {
            // given
            when(userRepository.findById(1L)).thenReturn(new User(1L, "채민"));
            Ticket ticket = new Ticket(100L, 50_000);
            when(ticketRepository.findById(100L)).thenReturn(ticket);
            when(paymentGateway.charge(50_000, paymentInfo)).thenReturn(true);

            // when
            boolean result = service.reserveTicket(1L, 100L, paymentInfo);

            // then
            assertThat(result).isTrue();
            assertThat(ticket.isReserved()).isTrue();
            assertThat(ticket.getUserId()).isEqualTo(1L);
        }

        @Test
        @DisplayName("예약 성공 시 티켓을 저장소에 저장한다")
        void 예약_성공시_저장() {
            // given
            when(userRepository.findById(1L)).thenReturn(new User(1L, "채민"));
            Ticket ticket = new Ticket(100L, 50_000);
            when(ticketRepository.findById(100L)).thenReturn(ticket);
            when(paymentGateway.charge(50_000, paymentInfo)).thenReturn(true);

            // when
            service.reserveTicket(1L, 100L, paymentInfo);

            // then
            verify(ticketRepository).save(ticket);
        }
    }

    @Nested
    @DisplayName("예외 — 유저를 찾을 수 없음")
    class 유저_없음_케이스 {

        @Test
        @DisplayName("유저가 없으면 UserNotFoundException 을 던진다")
        void 유저_없으면_예외() {
            // given
            when(userRepository.findById(999L)).thenReturn(null);

            // when & then
            assertThrows(UserNotFoundException.class,
                    () -> service.reserveTicket(999L, 100L, paymentInfo));
        }

        @Test
        @DisplayName("유저가 없으면 티켓 조회조차 하지 않는다")
        void 유저_없으면_티켓_조회_안함() {
            // given
            when(userRepository.findById(999L)).thenReturn(null);

            // when
            assertThrows(UserNotFoundException.class,
                    () -> service.reserveTicket(999L, 100L, paymentInfo));

            // then
            verify(ticketRepository, never()).findById(anyLong());
        }
    }

    @Nested
    @DisplayName("예외 — 이미 예약된 티켓")
    class 이미_예약된_케이스 {

        @Test
        @DisplayName("이미 예약된 티켓이면 TicketAlreadyReservedException 을 던진다")
        void 이미_예약이면_예외() {
            // given
            when(userRepository.findById(1L)).thenReturn(new User(1L, "채민"));
            Ticket reservedTicket = new Ticket(100L, 50_000);
            reservedTicket.setReserved(true);
            when(ticketRepository.findById(100L)).thenReturn(reservedTicket);

            // when & then
            assertThrows(TicketAlreadyReservedException.class,
                    () -> service.reserveTicket(1L, 100L, paymentInfo));
        }

        @Test
        @DisplayName("이미 예약된 티켓이면 결제를 시도하지 않는다")
        void 이미_예약이면_결제_안함() {
            // given
            when(userRepository.findById(1L)).thenReturn(new User(1L, "채민"));
            Ticket reservedTicket = new Ticket(100L, 50_000);
            reservedTicket.setReserved(true);
            when(ticketRepository.findById(100L)).thenReturn(reservedTicket);

            // when
            assertThrows(TicketAlreadyReservedException.class,
                    () -> service.reserveTicket(1L, 100L, paymentInfo));

            // then
            verify(paymentGateway, never()).charge(anyInt(), any());
        }
    }

    @Nested
    @DisplayName("예외 — 결제 실패")
    class 결제_실패_케이스 {

        @Test
        @DisplayName("결제가 실패하면 PaymentFailedException 을 던진다")
        void 결제_실패하면_예외() {
            // given
            when(userRepository.findById(1L)).thenReturn(new User(1L, "채민"));
            Ticket ticket = new Ticket(100L, 50_000);
            when(ticketRepository.findById(100L)).thenReturn(ticket);
            when(paymentGateway.charge(50_000, paymentInfo)).thenReturn(false);

            // when & then
            assertThrows(PaymentFailedException.class,
                    () -> service.reserveTicket(1L, 100L, paymentInfo));
        }

        @Test
        @DisplayName("결제가 실패하면 티켓 상태는 그대로이고 저장하지 않는다")
        void 결제_실패하면_상태_유지_저장_안함() {
            // given
            when(userRepository.findById(1L)).thenReturn(new User(1L, "채민"));
            Ticket ticket = new Ticket(100L, 50_000);
            when(ticketRepository.findById(100L)).thenReturn(ticket);
            when(paymentGateway.charge(50_000, paymentInfo)).thenReturn(false);

            // when
            assertThrows(PaymentFailedException.class,
                    () -> service.reserveTicket(1L, 100L, paymentInfo));

            // then
            assertThat(ticket.isReserved()).isFalse();
            verify(ticketRepository, never()).save(any());
        }
    }
}
