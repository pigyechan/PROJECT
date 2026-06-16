package calculator;

public class DefectRateService {

    private final DefectRateRepository repository;
    private final DefectRateCalculator calculator;

    public DefectRateService(DefectRateRepository repository, DefectRateCalculator calculator) {
        this.repository = repository;
        this.calculator = calculator;
    }

    public double calculate(Long productionId) {
        ProductionRecord record = repository.findById(productionId);
        if (record == null) {
            throw new IllegalArgumentException("생산 실적을 찾을 수 없습니다. id=" + productionId);
        }
        double defectRate = calculator.calculateDefectRate(record.getDefectiveCount(), record.getTotalCount());
        String grade      = calculator.evaluateGrade(defectRate);
        repository.saveResult(productionId, defectRate, grade);
        return defectRate;
    }
}
