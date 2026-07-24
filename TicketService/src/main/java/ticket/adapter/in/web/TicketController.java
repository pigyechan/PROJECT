package ticket.adapter.in.web;

import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import ticket.PaymentInfo;
import ticket.TicketReservationUseCase;
import ticket.adapter.in.web.dto.ReserveTicketRequest;
import ticket.adapter.in.web.dto.ReserveTicketResponse;

// Inbound Adapter(Driving): HTTP 요청을 Inbound Port(TicketReservationUseCase) 호출로 옮겨준다.
// 이 클래스는 TicketService 를 몰라도 된다 — 포트 인터페이스 하나만 의존한다.
@RestController
public class TicketController {

    private final TicketReservationUseCase ticketReservationUseCase;

    public TicketController(TicketReservationUseCase ticketReservationUseCase) {
        this.ticketReservationUseCase = ticketReservationUseCase;
    }

    @PostMapping("/tickets/{ticketId}/reserve")
    public ReserveTicketResponse reserve(@PathVariable long ticketId, @RequestBody ReserveTicketRequest request) {
        boolean reserved = ticketReservationUseCase.reserveTicket(
                request.userId(), ticketId, new PaymentInfo(request.cardNumber()));
        return new ReserveTicketResponse(reserved);
    }
}
