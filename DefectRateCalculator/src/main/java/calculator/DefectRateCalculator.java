package calculator;

/**
 * 불량률 계산기
 *
 * TDD 진행 순서 요약:
 *
 *   Cycle 1 GREEN  : calculateDefectRate() — 기본 공식
 *   Cycle 2 GREEN  : 추가 코드 없음 (공식이 경계값 자동 처리)
 *   Cycle 3 GREEN  : validate()에 total <= 0 검사 추가
 *   Cycle 4 GREEN  : validate()에 defective < 0 검사 추가
 *   Cycle 4 REFACTOR: Cycle 3·4 검증을 validate() 단일 메서드로 통합
 *   Cycle 5 GREEN  : validate()에 defective > total 검사 추가
 *   Cycle 6 GREEN  : evaluateGrade() — if-else 분기
 *   Cycle 6 REFACTOR: 임계값을 상수로 추출 (매직 넘버 제거)
 */
public class DefectRateCalculator {

    // Cycle 6 REFACTOR: 매직 넘버 → 이름 있는 상수
    private static final double WARNING_THRESHOLD = 1.0;
    private static final double DEFECT_THRESHOLD  = 5.0;

    // ── Cycle 1 GREEN ─────────────────────────────────────────────
    // 최소 구현: 공식만 반환
    // 이후 Cycle 3~5에서 validate() 호출이 앞에 붙으며 최종 형태 완성
    // ─────────────────────────────────────────────────────────────
    public double calculateDefectRate(int defective, int total) {
        validate(defective, total);                      // Cycle 3 추가
        return (double) defective / total * 100;
    }

    // ── Cycle 6 GREEN → REFACTOR ──────────────────────────────────
    // GREEN  : if-else 분기로 문자열 반환
    // REFACTOR: 1.0, 5.0 → WARNING_THRESHOLD, DEFECT_THRESHOLD 상수
    // ─────────────────────────────────────────────────────────────
    public String evaluateGrade(double defectRate) {
        if (defectRate < 0 || defectRate > 100) {
            throw new IllegalArgumentException("불량률은 0 ~ 100 사이여야 합니다.");
        }
        if (defectRate < WARNING_THRESHOLD) return "양호";
        if (defectRate < DEFECT_THRESHOLD)  return "주의";
        return "불량";
    }

    // ── Cycle 3 GREEN → Cycle 4 GREEN → Cycle 5 REFACTOR ─────────
    // Cycle 3 GREEN  : if (total <= 0) 추가
    // Cycle 4 GREEN  : if (defective < 0) 추가
    // Cycle 5 REFACTOR: 세 검사를 validate() 하나로 묶고 순서 정리
    // ─────────────────────────────────────────────────────────────
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
