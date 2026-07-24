package ticket.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import ticket.PaymentGateway;
import ticket.TicketRepository;
import ticket.TicketReservationUseCase;
import ticket.TicketService;
import ticket.TossPaymentAdapter;
import ticket.UserRepository;

// Core(TicketService, Ticket, User ...)는 Spring 애노테이션을 전혀 모른다.
// 이 클래스가 Core 객체를 직접 new 해서 Spring 컨테이너에 등록하는, Core와 프레임워크 사이의 조립 지점이다.
@Configuration
public class BeanConfiguration {

    @Bean
    public PaymentGateway paymentGateway() {
        return new TossPaymentAdapter();
    }

    @Bean
    public TicketReservationUseCase ticketReservationUseCase(UserRepository userRepository,
                                                               TicketRepository ticketRepository,
                                                               PaymentGateway paymentGateway) {
        return new TicketService(userRepository, ticketRepository, paymentGateway);
    }
}
