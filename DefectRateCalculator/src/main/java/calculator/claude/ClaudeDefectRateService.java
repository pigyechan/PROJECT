// [AI 작성 — Claude Sonnet 4.6] 인수테스트 판정 실험용 구현체
package calculator.claude;

public class ClaudeDefectRateService {

    private final ClaudeDefectRateRepository repository;
    private final ClaudeDefectRateCalculator calculator;

    public ClaudeDefectRateService(ClaudeDefectRateRepository repository,
                                   ClaudeDefectRateCalculator calculator) {
        this.repository = repository;
        this.calculator = calculator;
    }

    public double calculate(Long productionId) {
        ClaudeProductionRecord record = repository.findById(productionId);
        if (record == null) {
            throw new IllegalArgumentException("생산 실적을 찾을 수 없습니다. id=" + productionId);
        }
        double defectRate = calculator.calculateDefectRate(
                record.getDefectiveCount(), record.getTotalCount());
        String grade = calculator.evaluateGrade(defectRate);
        repository.saveResult(productionId, defectRate, grade);
        return defectRate;
    }
}
