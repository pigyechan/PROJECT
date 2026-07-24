package ticket.adapter.in.web;

import java.util.Map;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import ticket.PaymentFailedException;
import ticket.TicketAlreadyReservedException;
import ticket.UserNotFoundException;

// Core가 던지는 도메인 예외를 HTTP 상태 코드로 번역하는 곳.
// Core(TicketService)는 HTTP가 뭔지 몰라도 된다 — 이 번역은 Inbound Adapter의 책임이다.
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<Map<String, String>> handleUserNotFound(UserNotFoundException e) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("message", e.getMessage()));
    }

    @ExceptionHandler(TicketAlreadyReservedException.class)
    public ResponseEntity<Map<String, String>> handleTicketAlreadyReserved(TicketAlreadyReservedException e) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of("message", e.getMessage()));
    }

    @ExceptionHandler(PaymentFailedException.class)
    public ResponseEntity<Map<String, String>> handlePaymentFailed(PaymentFailedException e) {
        return ResponseEntity.status(HttpStatus.PAYMENT_REQUIRED).body(Map.of("message", e.getMessage()));
    }
}
