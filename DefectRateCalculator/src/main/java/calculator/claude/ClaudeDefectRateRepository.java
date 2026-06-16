package calculator.claude;

public interface ClaudeDefectRateRepository {
    ClaudeProductionRecord findById(Long id);
    void saveResult(Long productionId, double defectRate, String grade);
}
