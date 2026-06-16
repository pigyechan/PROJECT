package calculator;

import io.cucumber.java.en.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class DefectRateStepDefinitions {

    private final DefectRateCalculator calculator = new DefectRateCalculator();
    private DefectRateRepository repository;
    private DefectRateService service;

    private int defective;
    private int total;
    private double defectRate;
    private double result;
    private String grade;
    private long productionId;
    private Exception thrownException;

    // ── Given ─────────────────────────────────────────────────────────

    @Given("전체 생산 수량이 {int}개이고 불량 수량이 {int}개일 때")
    public void setTotalAndDefective(int total, int defective) {
        this.total = total;
        this.defective = defective;
    }

    @Given("불량률이 {double}%일 때")
    public void setDefectRate(double defectRate) {
        this.defectRate = defectRate;
    }

    @Given("생산 실적 ID {long}번에 불량 {int}개, 전체 {int}개가 저장되어 있을 때")
    public void setupDbRecord(long id, int defective, int total) {
        this.productionId = id;
        repository = mock(DefectRateRepository.class);
        service = new DefectRateService(repository, calculator);
        when(repository.findById(id)).thenReturn(new ProductionRecord(defective, total));
    }

    @Given("전체 생산 수량이 {int}개일 때")
    public void setTotalOnly(int total) {
        this.total = total;
        this.defective = 0;
    }

    @Given("불량 수량이 {int}개일 때")
    public void setDefectiveOnly(int defective) {
        this.defective = defective;
        this.total = 100;
    }

    @Given("생산 실적 ID {long}번이 DB에 존재하지 않을 때")
    public void setupMissingRecord(long id) {
        repository = mock(DefectRateRepository.class);
        service = new DefectRateService(repository, calculator);
        when(repository.findById(id)).thenReturn(null);
    }

    // ── When ──────────────────────────────────────────────────────────

    @When("불량률 계산을 요청하면")
    public void calculateDefectRate() {
        try {
            result = calculator.calculateDefectRate(defective, total);
        } catch (IllegalArgumentException e) {
            thrownException = e;
        }
    }

    @When("품질 등급 판정을 요청하면")
    public void evaluateGrade() {
        try {
            grade = calculator.evaluateGrade(defectRate);
        } catch (IllegalArgumentException e) {
            thrownException = e;
        }
    }

    @When("서비스에 ID {long}번 계산을 요청하면")
    public void calculateViaService(long id) {
        try {
            result = service.calculate(id);
        } catch (IllegalArgumentException e) {
            thrownException = e;
        }
    }

    // ── Then ──────────────────────────────────────────────────────────

    @Then("불량률은 {double}%여야 한다")
    public void verifyDefectRate(double expected) {
        assertEquals(expected, result);
    }

    @Then("등급은 {string}이어야 한다")
    public void verifyGrade(String expected) {
        assertEquals(expected, grade);
    }

    @Then("불량률 {double}%와 등급 {string}이 DB에 저장되어야 한다")
    public void verifySaved(double expectedRate, String expectedGrade) {
        verify(repository).saveResult(anyLong(), eq(expectedRate), eq(expectedGrade));
    }

    @Then("불량률은 {double}%여야 하고 예외는 발생하지 않아야 한다")
    public void verifyDefectRateNoException(double expected) {
        assertNull(thrownException);
        assertEquals(expected, result);
    }

    @Then("{string} 오류가 발생해야 한다")
    public void verifyException(String expectedMessage) {
        assertNotNull(thrownException, "예외가 발생해야 합니다: " + expectedMessage);
        assertTrue(thrownException.getMessage().contains(expectedMessage));
    }

    @And("결과 저장은 호출되지 않아야 한다")
    public void verifySaveNotCalled() {
        verify(repository, never()).saveResult(anyLong(), anyDouble(), anyString());
    }
}
