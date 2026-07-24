# C-5 에서 Cucumber-JVM 으로 실제 실행될 Feature.
# When 절은 Inbound Port 하나(TicketReservationUseCase.reserveTicket)와 1:1로 대응한다.
Feature: 티켓 예약

  사용자가 결제 수단(카드/포인트)에 상관없이 티켓을 예약할 수 있어야 한다.
  예약 가능한 티켓 + 존재하는 사용자 + 결제 성공이라는 조건이 갖춰지면
  티켓은 그 사용자에게 예약된 상태로 바뀐다.

  Background:
    Given 사용자 "1"번이 존재한다
    And 가격이 50000원인 예약 가능한 티켓 "100"번이 존재한다

  Scenario: 결제에 성공하면 티켓 예약이 완료된다
    Given 결제 수단이 정상적으로 준비되어 있다
    When 사용자 "1"번이 티켓 "100"번을 예약한다
    Then 티켓 "100"번은 사용자 "1"번에게 예약된 상태가 된다
    And 결제가 정상적으로 처리된다
