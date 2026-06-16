// [AI 작성 — Claude Sonnet 4.6] 인수테스트 판정 실험용 구현체
package calculator.claude;

public class ClaudeDefectRateCalculator {

    private static final double WARNING_THRESHOLD = 1.0;
    private static final double DEFECT_THRESHOLD  = 5.0;

    public double calculateDefectRate(int defective, int total) {
        validate(defective, total);
        return (double) defective / total * 100;
    }

    public String evaluateGrade(double defectRate) {
        if (defectRate < 0 || defectRate > 100) {
            throw new IllegalArgumentException("불량률은 0 ~ 100 사이여야 합니다.");
        }
        if (defectRate < WARNING_THRESHOLD) return "양호";
        if (defectRate < DEFECT_THRESHOLD)  return "주의";
        return "불량";
    }

    private void validate(int defective, int total) {
        if (defective < 0) {
            throw new IllegalArgumentException("불량 수는 0 이상이어야 합니다.");
        }
        if (total <= 0) {
            throw new IllegalArgumentException("전체 수는 1 이상이어야 합니다.");
        }
        if (defective > total) {
            throw new IllegalArgumentException("불량 수는 전체 수를 초과할 수 없습니다.");
        }
    }
}
