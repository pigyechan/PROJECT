package calculator;

public interface DefectRateRepository {

    ProductionRecord findById(Long id);

    void saveResult(Long productionId, double defectRate, String grade);
}
