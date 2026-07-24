package ticket.acceptance;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.fail;

import io.cucumber.java.Before;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.Then;
import io.cucumber.java.en.When;
import org.springframework.beans.factory.annotation.Autowired;

import ticket.PaymentFailedException;
import ticket.PaymentInfo;
import ticket.TicketAlreadyReservedException;
import ticket.TicketReservationUseCase;
import ticket.UserNotFoundException;
import ticket.adapter.out.persistence.TicketEntity;
import ticket.adapter.out.persistence.TicketJpaRepository;
import ticket.adapter.out.persistence.UserEntity;
import ticket.adapter.out.persistence.UserJpaRepository;

// 인수테스트가 Inbound Port(TicketReservationUseCase)를 호출하는 지점.
// Outbound Adapter(JpaUserRepositoryAdapter, JpaTicketRepositoryAdapter)는 Mock이 아니라
// TestcontainersConfiguration이 띄운 실제 Postgres 컨테이너와 통신한다.
public class TicketReservationStepDefinitions {

    // Background에서 "이미 다른 사용자에게 예약되어 있다"고 할 때 쓰는, 예약을 선점한 사용자.
    // FK 제약이 없는 단순 컬럼이라 User 로우를 따로 만들지 않아도 된다.
    private static final long OTHER_USER_ID = 2L;

    @Autowired
    private TicketReservationUseCase ticketReservationUseCase;

    @Autowired
    private UserJpaRepository userJpaRepository;

    @Autowired
    private TicketJpaRepository ticketJpaRepository;

    @Autowired
    private ControllablePaymentGateway paymentGateway;

    private Long lastTicketId;
    private Boolean reservationResult;
    private RuntimeException thrownException;

    @Before
    public void resetState() {
        ticketJpaRepository.deleteAll();
        userJpaRepository.deleteAll();
        paymentGateway.succeed();
        lastTicketId = null;
        reservationResult = null;
        thrownException = null;
    }

    // ── Given ─────────────────────────────────────────────────────────

    @Given("사용자 {string}번이 존재한다")
    public void 사용자가_존재한다(String userId) {
        userJpaRepository.save(new UserEntity(Long.parseLong(userId), "테스트유저" + userId));
    }

    @Given("가격이 {int}원인 예약 가능한 티켓 {string}번이 존재한다")
    public void 예약_가능한_티켓이_존재한다(int price, String ticketId) {
        ticketJpaRepository.save(new TicketEntity(Long.parseLong(ticketId), price, false, null));
    }

    @Given("결제 수단이 정상적으로 준비되어 있다")
    public void 결제_수단이_준비되어_있다() {
        paymentGateway.succeed();
    }

    @Given("결제 수단이 준비되지 않아 결제가 실패한다")
    public void 결제가_실패한다() {
        paymentGateway.fail();
    }

    @Given("티켓 {string}번이 이미 다른 사용자에게 예약되어 있다")
    public void 티켓이_이미_예약되어_있다(String ticketId) {
        long id = Long.parseLong(ticketId);
        TicketEntity existing = ticketJpaRepository.findById(id)
                .orElseThrow(() -> new IllegalStateException("먼저 티켓이 존재해야 합니다. id=" + id));
        ticketJpaRepository.save(new TicketEntity(existing.getId(), existing.getPrice(), true, OTHER_USER_ID));
    }

    // ── When ──────────────────────────────────────────────────────────

    @When("사용자 {string}번이 티켓 {string}번을 예약한다")
    public void 티켓을_예약한다(String userId, String ticketId) {
        lastTicketId = Long.parseLong(ticketId);
        try {
            reservationResult = ticketReservationUseCase.reserveTicket(
                    Long.parseLong(userId), lastTicketId, new PaymentInfo("1234-5678-0000-0000"));
        } catch (RuntimeException e) {
            thrownException = e;
        }
    }

    // ── Then ──────────────────────────────────────────────────────────

    @Then("티켓 {string}번은 사용자 {string}번에게 예약된 상태가 된다")
    public void 티켓이_예약된_상태가_된다(String ticketId, String userId) {
        TicketEntity ticket = ticketJpaRepository.findById(Long.parseLong(ticketId)).orElseThrow();
        assertThat(ticket.isReserved()).isTrue();
        assertThat(ticket.getUserId()).isEqualTo(Long.parseLong(userId));
    }

    @Then("결제가 정상적으로 처리된다")
    public void 결제가_정상적으로_처리된다() {
        assertThat(thrownException).isNull();
        assertThat(reservationResult).isTrue();
    }

    @Then("예약은 {string} 사유로 거부된다")
    public void 예약이_거부된다(String reason) {
        assertThat(thrownException)
                .as("'%s' 사유로 예약이 거부될 것으로 기대했지만, 예외가 발생하지 않았다", reason)
                .isNotNull();

        switch (reason) {
            case "사용자를 찾을 수 없음" -> assertThat(thrownException).isInstanceOf(UserNotFoundException.class);
            case "이미 예약된 티켓" -> assertThat(thrownException).isInstanceOf(TicketAlreadyReservedException.class);
            case "결제 실패" -> assertThat(thrownException).isInstanceOf(PaymentFailedException.class);
            default -> fail("알 수 없는 거부 사유: " + reason);
        }
    }

    @Then("기존 예약자 정보는 그대로 유지된다")
    public void 기존_예약자_정보가_유지된다() {
        TicketEntity ticket = ticketJpaRepository.findById(lastTicketId).orElseThrow();
        assertThat(ticket.isReserved()).isTrue();
        assertThat(ticket.getUserId()).isEqualTo(OTHER_USER_ID);
    }

    @Then("티켓 {string}번은 여전히 예약 가능한 상태로 남아있다")
    public void 티켓이_여전히_예약_가능하다(String ticketId) {
        TicketEntity ticket = ticketJpaRepository.findById(Long.parseLong(ticketId)).orElseThrow();
        assertThat(ticket.isReserved()).isFalse();
    }
}
